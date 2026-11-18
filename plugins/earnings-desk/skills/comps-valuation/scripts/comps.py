#!/usr/bin/env python3
"""Comparable-company multiples table from SEC XBRL + prices. Stdlib only.

Usage
  python3 comps.py AAPL MSFT GOOGL META [--prices "AAPL=230,MSFT=500"] [--no-quote]
                   [--target AAPL]

For every ticker it pulls trailing-twelve-month (TTM) fundamentals from SEC XBRL
(via the sibling financial-statements / sec-edgar skills) and a price from
--prices (preferred when you have a cited price) or market.py quote. Missing
prices never abort the run: fundamentals are still returned and price-based
multiples are null.

Output JSON:
  rows[]        per ticker: price, market cap, EV, EV/Sales, EV/EBIT, EV/EBITDA,
                P/E, P/B, FCF yield (pre- and post-SBC), revenue growth (TTM vs prior
                TTM), gross / operating / FCF margin, ROIC, Rule of 40, flags
  medians       peer medians per metric (excluding the --target ticker if given)
  regression    OLS of EV/Sales on TTM revenue growth (pct): slope, intercept,
                r2, n, and each ticker's fitted EV/Sales and premium/discount
                to the line
  errors[]      tickers that could not be processed and why
Definitions:
  EV = market cap + total debt - cash - short-term investments (leases, minority
  interests, pensions and preferred are NOT included; adjust by hand when big).
  ROIC = TTM EBIT x (1 - tax rate, clamped 0-35%, default 21%) / average of
  (equity + debt - cash) now and four quarters ago.
  Rule of 40 = revenue growth % + FCF margin %.
  Financials (SIC 6000-6799): EV multiples, FCF yield and ROIC are nulled (debt is
  raw material for a bank); compare P/E and P/B against ROE instead.
"""
import argparse
import contextlib
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for _base in (os.path.join(HERE, "..", ".."), os.path.join(HERE, "..", "vendor")):  # sibling skill, or bundled copy
    sys.path.insert(0, os.path.join(_base, "sec-edgar", "scripts"))
for _base in (os.path.join(HERE, "..", ".."), os.path.join(HERE, "..", "vendor")):  # sibling skill, or bundled copy
    sys.path.insert(0, os.path.join(_base, "financial-statements", "scripts"))
import edgar  # noqa: E402
import statements as st  # noqa: E402

FLOW_KEYS = ("revenue", "gross_profit", "operating_income", "net_income", "pretax_income", "income_tax",
             "operating_cash_flow", "capex", "sbc", "da", "eps_diluted")

METRICS = ("ev_sales", "ev_ebit", "ev_ebitda", "pe", "pb", "fcf_yield_pct", "fcf_after_sbc_yield_pct", "revenue_growth_pct",
           "gross_margin_pct", "operating_margin_pct", "fcf_margin_pct", "roic_pct", "rule_of_40")


def quiet(fn, *args, **kw):
    """Run fn while capturing stdout (edgar.die prints JSON and exits)."""
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            return fn(*args, **kw), None
    except SystemExit:
        txt = buf.getvalue().strip()
        try:
            return None, json.loads(txt).get("error", txt)
        except ValueError:
            return None, txt or "exited"
    except Exception as e:  # network errors, malformed data
        return None, "%s: %s" % (type(e).__name__, e)


def sum4(rows, key):
    vals = [r.get(key) for r in rows]
    return sum(vals) if len(vals) == 4 and all(v is not None for v in vals) else None


def rnd(x, n=2):
    return None if x is None else round(x, n)


def parse_prices(s):
    out = {}
    for part in (s or "").split(","):
        if "=" in part:
            k, v = part.split("=", 1)
            try:
                out[k.strip().upper()] = float(v)
            except ValueError:
                pass
    return out


def fundamentals(ticker):
    co = edgar.resolve(ticker)
    facts = edgar.build_facts(co["cik"], n_quarters=12, n_years=3)
    q = st.enrich(st.build_rows(facts, "quarterly"), 4)
    if len(q) < 4:
        raise ValueError("fewer than 4 quarters of XBRL data")
    last4, prior4 = q[-4:], q[-8:-4] if len(q) >= 8 else []
    t = {k: sum4(last4, k) for k in FLOW_KEYS}
    latest, yago = q[-1], (q[-5] if len(q) >= 5 else None)
    t["fcf"] = None if t["operating_cash_flow"] is None else t["operating_cash_flow"] - (t["capex"] or 0)
    t["ebitda"] = None if t["operating_income"] is None else t["operating_income"] + (t["da"] or 0)
    prev_rev = sum4(prior4, "revenue") if prior4 else None
    growth = st.div(t["revenue"] - prev_rev, abs(prev_rev)) if (t["revenue"] is not None and prev_rev) else None
    growth_basis = "TTM vs prior TTM"
    if growth is None and latest.get("revenue_yoy_pct") is not None:
        growth, growth_basis = latest["revenue_yoy_pct"] / 100, "latest quarter y/y (prior TTM incomplete)"
    tax = st.div(t["income_tax"], t["pretax_income"])
    tax = 0.21 if tax is None else min(max(tax, 0), 0.35)
    ic = lambda r: (r.get("equity") or 0) + (r.get("total_debt") or 0) - (r.get("cash") or 0) - (r.get("short_term_investments") or 0)
    ics = [ic(latest)] + ([ic(yago)] if yago else [])
    avg_ic = sum(ics) / len(ics)
    roic = st.div(t["operating_income"] * (1 - tax), avg_ic) if (t["operating_income"] is not None and avg_ic > 0) else None
    flags = []
    if any(r.get("derived_quarter") for r in last4):
        flags.append("some TTM quarters derived from FY/YTD figures")
    if latest.get("equity") is not None and latest["equity"] <= 0:
        flags.append("negative equity: ROIC/ROE not meaningful")
    if t["revenue"] is None:
        flags.append("TTM revenue missing (bank/insurer or unusual tags?)")
    sic = None
    try:
        sic = int(edgar.submissions(co["cik"]).get("sic") or 0) or None
    except Exception:
        pass
    financial = sic is not None and 6000 <= sic <= 6799
    if financial:
        flags.append("financial company (SIC %d): EV multiples and ROIC are not meaningful and are nulled; use P/E and P/B vs ROE" % sic)
        roic = None
    return {
        "ticker": co["ticker"], "name": co["name"], "cik": co["cik"],
        "ttm_periods": [r["period_end"] for r in last4],
        "revenue": t["revenue"], "gross_profit": t["gross_profit"], "ebit": t["operating_income"], "ebitda": t["ebitda"],
        "net_income": t["net_income"], "eps_diluted_ttm": rnd(t["eps_diluted"], 3), "fcf": t["fcf"], "sbc": t["sbc"],
        "fcf_after_sbc": None if t["fcf"] is None else t["fcf"] - (t["sbc"] or 0),
        "total_debt": latest.get("total_debt"), "cash_and_st_investments": (latest.get("cash") or 0) + (latest.get("short_term_investments") or 0),
        "net_debt": latest.get("net_debt"), "shares": latest.get("shares_outstanding") or latest.get("shares_diluted"),
        "shares_basis": "shares outstanding (latest)" if latest.get("shares_outstanding") else "diluted weighted average (latest quarter)",
        "revenue_growth_pct": rnd(None if growth is None else growth * 100), "growth_basis": growth_basis,
        "gross_margin_pct": rnd(st.pct(st.div(t["gross_profit"], t["revenue"]))),
        "operating_margin_pct": rnd(st.pct(st.div(t["operating_income"], t["revenue"]))),
        "fcf_margin_pct": rnd(st.pct(st.div(t["fcf"], t["revenue"]))),
        "roic_pct": rnd(st.pct(roic)),
        "equity": latest.get("equity"), "sic": sic, "financial": financial,
        "accessions": sorted(set(r["accn"] for r in last4 if r.get("accn"))),
        "flags": flags,
    }


def add_valuation(row, price, source):
    row["price"], row["price_source"] = price, source
    keys = ("market_cap", "ev", "ev_sales", "ev_ebit", "ev_ebitda", "pe", "pb", "fcf_yield_pct", "fcf_after_sbc_yield_pct")
    for k in keys:
        row[k] = None
    if price is None or not row.get("shares"):
        return row
    mcap = price * row["shares"]
    ev = mcap + (row["net_debt"] or 0)
    pos = lambda x: x if (x is not None and x > 0) else None  # multiples on negative denominators are not meaningful
    row["market_cap"], row["ev"] = round(mcap), round(ev)
    row["ev_sales"] = rnd(st.div(ev, pos(row["revenue"])))
    row["ev_ebit"] = rnd(st.div(ev, pos(row["ebit"])), 1)
    row["ev_ebitda"] = rnd(st.div(ev, pos(row["ebitda"])), 1)
    row["pe"] = rnd(st.div(mcap, pos(row["net_income"])), 1)
    row["pb"] = rnd(st.div(mcap, pos(row.get("equity"))))
    if row.get("financial"):
        row["ev"] = row["ev_sales"] = row["ev_ebit"] = row["ev_ebitda"] = None
        return row
    row["fcf_yield_pct"] = rnd(st.pct(st.div(row["fcf"], mcap)))
    row["fcf_after_sbc_yield_pct"] = rnd(st.pct(st.div(row["fcf_after_sbc"], mcap)))
    return row


def median(xs):
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return None
    n = len(xs)
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2


def ols(points):
    """Least squares y = a + b x. points: [(ticker, x, y)]."""
    n = len(points)
    if n < 3:
        return {"available": False, "n": n, "note": "need at least 3 peers with both EV/Sales and growth"}
    xs, ys = [p[1] for p in points], [p[2] for p in points]
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0:
        return {"available": False, "n": n, "note": "no variation in growth"}
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    a = my - b * mx
    ss_tot = sum((y - my) ** 2 for y in ys)
    ss_res = sum((y - (a + b * x)) ** 2 for x, y in zip(xs, ys))
    fitted = []
    for t, x, y in points:
        f = a + b * x
        fitted.append({"ticker": t, "growth_pct": x, "ev_sales": y, "fitted_ev_sales": round(f, 2),
                       "premium_to_line_pct": round((y / f - 1) * 100, 1) if f > 0 else None})
    return {"available": True, "n": n, "slope_ev_sales_per_growth_pt": round(b, 4), "intercept": round(a, 3),
            "r2": round(1 - ss_res / ss_tot, 3) if ss_tot else None, "points": fitted,
            "read": "Slope = extra EV/Sales turns the group pays per point of growth. Low r2 (<0.3) or n<6 means the line explains little; "
                    "a positive premium means richer than growth alone justifies."}


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("tickers", nargs="+", help="target first, then peers (or use --target)")
    p.add_argument("--prices", default="", help='override prices, e.g. "AAPL=230,MSFT=500" (cite where they came from)')
    p.add_argument("--no-quote", action="store_true", help="do not call market.py for tickers missing from --prices")
    p.add_argument("--target", help="ticker excluded from peer medians (default: first ticker)")
    a = p.parse_args()

    prices = parse_prices(a.prices)
    tickers = []
    for t in a.tickers:
        for x in t.split(","):
            x = x.strip().upper()
            if x and x not in tickers:
                tickers.append(x)
    target = (a.target or tickers[0]).upper()
    market = None
    rows, errors = [], []
    for t in tickers:
        row, err = quiet(fundamentals, t)
        if err:
            errors.append({"ticker": t, "error": err})
            continue
        price, src = prices.get(t) or prices.get(row["ticker"]), "user input (--prices)"
        if price is None and not a.no_quote:
            if market is None:
                import market as market_mod
                market = market_mod
            qt, qerr = quiet(market.quote, row["ticker"])
            if qt and qt.get("price") is not None:
                price, src = qt["price"], qt.get("source")
            else:
                src = None
                row["flags"].append("no price: %s" % (qerr or (qt or {}).get("hint") or "quote unavailable"))
        elif price is None:
            src = None
            row["flags"].append("no price supplied")
        rows.append(add_valuation(row, price, src))

    peers = [r for r in rows if r["ticker"] != target] or rows
    medians = {m: rnd(median([r.get(m) for r in peers])) for m in METRICS}
    for r in rows:
        r["rule_of_40"] = rnd(r["revenue_growth_pct"] + r["fcf_margin_pct"]) if (r["revenue_growth_pct"] is not None and r["fcf_margin_pct"] is not None) else None
    medians["rule_of_40"] = rnd(median([r.get("rule_of_40") for r in peers]))
    tgt = next((r for r in rows if r["ticker"] == target), None)
    vs = {}
    if tgt:
        for m in ("ev_sales", "ev_ebit", "ev_ebitda", "pe"):
            if tgt.get(m) and medians.get(m):
                vs[m + "_premium_pct"] = round((tgt[m] / medians[m] - 1) * 100, 1)
    pts = [(r["ticker"], r["revenue_growth_pct"], r["ev_sales"]) for r in rows if r.get("ev_sales") is not None and r.get("revenue_growth_pct") is not None]
    out = {
        "target": target,
        "units": "USD raw; multiples in x; yields, margins and growth in %",
        "rows": rows,
        "peer_medians_ex_target": medians,
        "target_vs_median": vs,
        "regression_ev_sales_on_growth": ols(pts),
        "errors": errors,
        "notes": ["Multiples on negative or zero denominators are null (not meaningful).",
                  "EV excludes leases, minority interests, pensions and preferred; adjust by hand when material.",
                  "Fiscal years differ across peers; ttm_periods shows exactly which quarters feed each row.",
                  "Prices from --prices are only as good as their citation; keyless quotes are best-effort."],
    }
    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    main()
