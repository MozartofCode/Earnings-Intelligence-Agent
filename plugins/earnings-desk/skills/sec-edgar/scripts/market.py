#!/usr/bin/env python3
"""earnings-desk market data helper. Python 3.8+, standard library only.

Free-first: SEC data never needs a key. Keyless prices come from a public chart
endpoint on a best-effort basis (it may rate-limit; we never retry around that). Optional
free-tier keys unlock more, and are tried in this order:
  FMP_API_KEY           https://site.financialmodelingprep.com  (quotes, estimates, calendar)
  FINNHUB_API_KEY       https://finnhub.io                      (quotes, EPS surprises, calendar)
  ALPHAVANTAGE_API_KEY  https://www.alphavantage.co             (quotes, earnings history)

If a source can't answer, the JSON says so ("available": false) and gives a
hint. Skills then fall back to web search and must label those numbers as such.

Commands
  status                      Which keys are configured
  quote TICKER                Last price, change, market cap (price x SEC shares)
  history TICKER [--range 1y] Daily closes (range: 1mo 3mo 6mo 1y 2y 5y 10y max)
  reaction TICKER --date YYYY-MM-DD [--window 1]
                              Stock move around an event date (e.g. an earnings release)
  reactions TICKER [--n 8]    Moves after the last N earnings releases (8-K Item 2.02 dates)
  estimates TICKER            Consensus revenue/EPS estimates (needs FMP or Finnhub key)
  surprises TICKER            Historical EPS actual vs. estimate (Finnhub / Alpha Vantage)
  calendar TICKER             Next earnings date (FMP / Finnhub; otherwise a hint)
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import edgar  # noqa: E402

KEYS = {k: os.environ.get(k) for k in ("FMP_API_KEY", "FINNHUB_API_KEY", "ALPHAVANTAGE_API_KEY")}
CLIENT_UA = "earnings-desk/1.0 (+https://github.com/MozartofCode/earnings-desk)"


def get_json(url, ttl_hours=1, ua=CLIENT_UA):
    """Cached GET for non-SEC hosts."""
    import hashlib
    os.makedirs(edgar.CACHE_DIR, exist_ok=True)
    safe = url
    for k, v in KEYS.items():
        if v:
            safe = safe.replace(v, "KEY")
    path = os.path.join(edgar.CACHE_DIR, "m-" + hashlib.sha1(safe.encode()).hexdigest())
    if os.path.exists(path) and time.time() - os.path.getmtime(path) < ttl_hours * 3600:
        with open(path) as f:
            return json.load(f)
    req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.loads(r.read().decode("utf-8", "replace"))
    with open(path, "w") as f:
        json.dump(data, f)
    return data


def _try(fn):
    try:
        return fn()
    except Exception as e:  # network errors, bad keys, plan limits
        return {"_error": "%s: %s" % (type(e).__name__, e)}


# ---------------------------------------------------------------- prices

def yahoo_chart(ticker, rng="1y"):
    url = "https://query1.finance.yahoo.com/v8/finance/chart/%s?range=%s&interval=1d&includePrePost=false" % (urllib.parse.quote(ticker.replace(".", "-")), rng)
    d = get_json(url, ttl_hours=1)
    res = d["chart"]["result"][0]
    ts = res.get("timestamp") or []
    closes = res["indicators"]["quote"][0].get("close") or []
    adj = (res["indicators"].get("adjclose") or [{}])[0].get("adjclose") or closes
    rows = []
    for t, c, a in zip(ts, closes, adj):
        if c is None:
            continue
        rows.append({"date": datetime.fromtimestamp(t, tz=timezone.utc).strftime("%Y-%m-%d"), "close": round(c, 4), "adj_close": round(a, 4) if a else None})
    return {"source": "Yahoo Finance public chart endpoint (unofficial, best-effort)", "currency": res["meta"].get("currency"), "rows": rows, "meta": res["meta"]}


def history(ticker, rng="1y"):
    if KEYS["FMP_API_KEY"]:
        days = {"1mo": 31, "3mo": 92, "6mo": 183, "1y": 366, "2y": 731, "5y": 1827, "10y": 3653}.get(rng, 366)
        frm = (date.today() - timedelta(days=days)).isoformat()
        r = _try(lambda: get_json("https://financialmodelingprep.com/stable/historical-price-eod/light?symbol=%s&from=%s&apikey=%s" % (ticker, frm, KEYS["FMP_API_KEY"])))
        if isinstance(r, list) and r:
            rows = sorted(({"date": x["date"], "close": x.get("price") or x.get("close")} for x in r), key=lambda x: x["date"])
            return {"source": "FMP", "rows": rows}
    r = _try(lambda: yahoo_chart(ticker, rng))
    if "_error" in r:
        return {"available": False, "error": r["_error"], "hint": "Keyless price source unavailable or rate-limited. Set FINNHUB_API_KEY or FMP_API_KEY (both free tiers) for reliable prices, or use web search and cite the source and time."}
    r.pop("meta", None)
    return r


def quote(ticker):
    out = {"ticker": ticker.upper()}
    price, src = None, None
    if KEYS["FMP_API_KEY"]:
        r = _try(lambda: get_json("https://financialmodelingprep.com/stable/quote?symbol=%s&apikey=%s" % (ticker, KEYS["FMP_API_KEY"]), ttl_hours=0.1))
        if isinstance(r, list) and r:
            q = r[0]
            price, src = q.get("price"), "FMP"
            out.update({"change_pct": q.get("changePercentage"), "market_cap": q.get("marketCap"), "year_high": q.get("yearHigh"), "year_low": q.get("yearLow"), "volume": q.get("volume")})
    if price is None and KEYS["FINNHUB_API_KEY"]:
        r = _try(lambda: get_json("https://finnhub.io/api/v1/quote?symbol=%s&token=%s" % (ticker, KEYS["FINNHUB_API_KEY"]), ttl_hours=0.1))
        if isinstance(r, dict) and r.get("c"):
            price, src = r["c"], "Finnhub"
            out.update({"change_pct": r.get("dp"), "day_high": r.get("h"), "day_low": r.get("l"), "prev_close": r.get("pc")})
    if price is None:
        r = _try(lambda: yahoo_chart(ticker, "1y"))
        if "_error" not in r and r["rows"]:
            m = r["meta"]
            price, src = m.get("regularMarketPrice") or r["rows"][-1]["close"], r["source"]
            closes = [x["close"] for x in r["rows"]]
            prev = closes[-2] if len(closes) > 1 else None
            out.update({"change_pct": round((price / prev - 1) * 100, 2) if prev else None, "year_high": max(closes), "year_low": min(closes),
                        "as_of": datetime.fromtimestamp(m.get("regularMarketTime", 0), tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")})
    if price is None:
        return dict(out, available=False, hint="No quote source reachable. Set FMP_API_KEY or FINNHUB_API_KEY, or use web search and cite it.")
    out.update({"price": price, "source": src})
    if not out.get("market_cap"):
        try:
            co = edgar.resolve(ticker)
            f = edgar.build_facts(co["cik"], 2, 1)
            sh = (f["quarterly"].get("shares_outstanding") or [{}])[-1].get("val")
            if sh:
                out["shares_outstanding"] = sh
                out["market_cap"] = round(price * sh)
                out["market_cap_note"] = "price x latest SEC-reported shares outstanding"
        except SystemExit:
            pass
    return out


def _close_on_or_before(rows, d):
    prior = [r for r in rows if r["date"] <= d]
    return prior[-1] if prior else None


def _close_after(rows, d, n=1):
    after = [r for r in rows if r["date"] > d]
    return after[n - 1] if len(after) >= n else None


def reaction(ticker, d, window=1, rows=None):
    """Move from the close before the event to `window` sessions after.

    Earnings released after the close on day D show up in D+1's move, so the
    base is the close on or before D and the end is the close `window` sessions later.
    """
    if rows is None:
        h = history(ticker, "10y")
        if not h.get("rows"):
            return h
        rows = h["rows"]
    base = _close_on_or_before(rows, d)
    end = _close_after(rows, d, window)
    if not base or not end:
        return {"date": d, "available": False}
    return {"event_date": d, "base_date": base["date"], "base_close": base["close"], "end_date": end["date"], "end_close": end["close"],
            "move_pct": round((end["close"] / base["close"] - 1) * 100, 2)}


def reactions(ticker, n=8):
    co = edgar.resolve(ticker)
    rel = [r for r in edgar.recent_filings(co["cik"], {"8-K"}, limit=300) if "2.02" in (r.get("items") or "")][:n]
    h = history(ticker, "5y")
    if not h.get("rows"):
        return h
    out = []
    for r in rel:
        x = reaction(ticker, r["filed"], 1, h["rows"])
        x["filing"] = r["url"]
        out.append(x)
    moves = [abs(x["move_pct"]) for x in out if x.get("move_pct") is not None]
    return {"ticker": co["ticker"], "source": h.get("source"), "events": out,
            "avg_abs_move_pct": round(sum(moves) / len(moves), 2) if moves else None,
            "note": "Event date = 8-K filing date. If results came out pre-market, the move belongs to that same day; check the release time."}


# ---------------------------------------------------------------- estimates

def estimates(ticker):
    if KEYS["FMP_API_KEY"]:
        out = {}
        for period in ("quarter", "annual"):
            r = _try(lambda: get_json("https://financialmodelingprep.com/stable/analyst-estimates?symbol=%s&period=%s&limit=8&apikey=%s" % (ticker, period, KEYS["FMP_API_KEY"]), ttl_hours=12))
            if isinstance(r, list):
                out[period] = [{"date": x.get("date"), "revenue_avg": x.get("revenueAvg"), "revenue_low": x.get("revenueLow"), "revenue_high": x.get("revenueHigh"),
                                "eps_avg": x.get("epsAvg"), "eps_low": x.get("epsLow"), "eps_high": x.get("epsHigh"), "n_analysts_eps": x.get("numAnalystsEps")} for x in r]
            else:
                out[period + "_error"] = r.get("_error") if isinstance(r, dict) else str(r)
        if out.get("quarter") or out.get("annual"):
            return dict(out, source="FMP")
    if KEYS["FINNHUB_API_KEY"]:
        r = _try(lambda: get_json("https://finnhub.io/api/v1/stock/eps-estimate?symbol=%s&freq=quarterly&token=%s" % (ticker, KEYS["FINNHUB_API_KEY"]), ttl_hours=12))
        if isinstance(r, dict) and r.get("data"):
            return {"source": "Finnhub", "quarter": r["data"][:8]}
    return {"available": False, "hint": "Consensus needs FMP_API_KEY or FINNHUB_API_KEY. Otherwise web-search '<TICKER> consensus EPS revenue estimate <quarter>' and label the figures 'consensus per <source>, <date>'."}


def surprises(ticker):
    if KEYS["FINNHUB_API_KEY"]:
        r = _try(lambda: get_json("https://finnhub.io/api/v1/stock/earnings?symbol=%s&token=%s" % (ticker, KEYS["FINNHUB_API_KEY"]), ttl_hours=12))
        if isinstance(r, list) and r:
            return {"source": "Finnhub", "rows": [{"period": x.get("period"), "eps_actual": x.get("actual"), "eps_estimate": x.get("estimate"), "surprise_pct": x.get("surprisePercent")} for x in r]}
    if KEYS["ALPHAVANTAGE_API_KEY"]:
        r = _try(lambda: get_json("https://www.alphavantage.co/query?function=EARNINGS&symbol=%s&apikey=%s" % (ticker, KEYS["ALPHAVANTAGE_API_KEY"]), ttl_hours=12))
        if isinstance(r, dict) and r.get("quarterlyEarnings"):
            return {"source": "Alpha Vantage", "rows": [{"period": x.get("fiscalDateEnding"), "reported_date": x.get("reportedDate"), "eps_actual": x.get("reportedEPS"),
                                                          "eps_estimate": x.get("estimatedEPS"), "surprise_pct": x.get("surprisePercentage")} for x in r["quarterlyEarnings"][:12]]}
    return {"available": False, "hint": "EPS surprise history needs FINNHUB_API_KEY or ALPHAVANTAGE_API_KEY. Otherwise compare reported EPS (sec-edgar facts) with consensus found by web search."}


def calendar(ticker):
    today = date.today()
    if KEYS["FINNHUB_API_KEY"]:
        r = _try(lambda: get_json("https://finnhub.io/api/v1/calendar/earnings?symbol=%s&from=%s&to=%s&token=%s" % (ticker, today, today + timedelta(days=120), KEYS["FINNHUB_API_KEY"]), ttl_hours=6))
        if isinstance(r, dict) and r.get("earningsCalendar"):
            return {"source": "Finnhub", "upcoming": r["earningsCalendar"]}
    if KEYS["FMP_API_KEY"]:
        r = _try(lambda: get_json("https://financialmodelingprep.com/stable/earnings-calendar?from=%s&to=%s&apikey=%s" % (today, today + timedelta(days=90), KEYS["FMP_API_KEY"]), ttl_hours=6))
        if isinstance(r, list):
            hits = [x for x in r if str(x.get("symbol", "")).upper() == ticker.upper()]
            if hits:
                return {"source": "FMP", "upcoming": hits}
    # Keyless estimate: same cadence as the last releases (8-K Item 2.02 dates)
    try:
        co = edgar.resolve(ticker)
        rel = [r["filed"] for r in edgar.recent_filings(co["cik"], {"8-K"}, limit=300) if "2.02" in (r.get("items") or "")][:5]
    except SystemExit:
        rel = []
    est = None
    if rel:
        last = datetime.strptime(rel[0], "%Y-%m-%d").date()
        est = last + timedelta(days=91)
        while est < today:
            est += timedelta(days=91)
    return {"available": False, "past_release_dates": rel, "estimated_next": est.isoformat() if est else None,
            "hint": "Estimate assumes a ~91-day cadence. Confirm the date on the company's investor-relations site or by web search."}


def status():
    out = {k: bool(v) for k, v in KEYS.items()}
    out["SEC_USER_AGENT"] = bool(os.environ.get("SEC_USER_AGENT"))
    out["note"] = "Everything works with no keys; keys add consensus estimates, surprises, calendars and sturdier quotes."
    return out


def main(argv=None):
    p = argparse.ArgumentParser(description="earnings-desk market data (JSON output).", formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    sp = p.add_subparsers(dest="cmd")
    sp.add_parser("status")
    sp.add_parser("quote").add_argument("ticker")
    h = sp.add_parser("history"); h.add_argument("ticker"); h.add_argument("--range", default="1y")
    r = sp.add_parser("reaction"); r.add_argument("ticker"); r.add_argument("--date", required=True); r.add_argument("--window", type=int, default=1)
    rs = sp.add_parser("reactions"); rs.add_argument("ticker"); rs.add_argument("--n", type=int, default=8)
    sp.add_parser("estimates").add_argument("ticker")
    sp.add_parser("surprises").add_argument("ticker")
    sp.add_parser("calendar").add_argument("ticker")
    a = p.parse_args(argv)
    if not a.cmd:
        p.print_help()
        return
    if a.cmd == "status":
        out = status()
    elif a.cmd == "quote":
        out = quote(a.ticker)
    elif a.cmd == "history":
        out = history(a.ticker, a.range)
    elif a.cmd == "reaction":
        out = reaction(a.ticker, a.date, a.window)
    elif a.cmd == "reactions":
        out = reactions(a.ticker, a.n)
    elif a.cmd == "estimates":
        out = estimates(a.ticker)
    elif a.cmd == "surprises":
        out = surprises(a.ticker)
    elif a.cmd == "calendar":
        out = calendar(a.ticker)
    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    main()
