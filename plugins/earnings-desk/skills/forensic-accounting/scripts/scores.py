#!/usr/bin/env python3
"""Forensic accounting scores from SEC XBRL. Stdlib only.

Usage
  python3 scores.py TICKER [--market-cap 2.9e12]

Computes, for the latest fiscal year vs. the prior one:
  Beneish M-score (8-variable)      > -1.78 = elevated manipulation risk (Beneish 1999)
  Altman Z (original) and Z''       distress zones; Z'' used for non-manufacturers
  Piotroski F-score (0-9)           financial strength; <=3 weak, >=7 strong
  Sloan accrual ratio               (NI - CFO) / avg total assets; > 10% is a warning
  Working-capital drift             DSO / DIO / DPO trend over up to 5 years
  Cash conversion, SBC burden, non-cash earnings share
Every component is returned so the analyst can see what drives a score.
Missing inputs are reported, never silently filled.
"""
import argparse
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


def d(a, b):
    return st.div(a, b)


def r3(x):
    return None if x is None else round(x, 3)


def need(row, keys):
    return [k for k in keys if row.get(k) is None]


def beneish(t, p):
    missing = need(t, ["receivables", "revenue", "gross_profit", "current_assets", "ppe_net", "total_assets", "net_income", "operating_cash_flow"]) + \
        ["prior." + k for k in need(p, ["receivables", "revenue", "gross_profit", "current_assets", "ppe_net", "total_assets"])]
    if missing:
        return {"available": False, "missing": missing}
    dsri = d(d(t["receivables"], t["revenue"]), d(p["receivables"], p["revenue"]))
    gmi = d(d(p["gross_profit"], p["revenue"]), d(t["gross_profit"], t["revenue"]))
    aq = lambda x: 1 - d(x["current_assets"] + x["ppe_net"], x["total_assets"])
    aqi = d(aq(t), aq(p))
    sgi = d(t["revenue"], p["revenue"])
    dep = lambda x: d(x["da"], x["da"] + x["ppe_net"]) if x.get("da") else None
    depi = d(dep(p), dep(t)) if dep(p) and dep(t) else 1.0
    sga = lambda x: d(x["sga"], x["revenue"]) if x.get("sga") else None
    sgai = d(sga(t), sga(p)) if sga(t) and sga(p) else 1.0
    lev = lambda x: d((x["current_liabilities"] or 0) + (x["long_term_debt"] or 0), x["total_assets"])
    lvgi = d(lev(t), lev(p)) if lev(p) else 1.0
    tata = d(t["net_income"] - t["operating_cash_flow"], t["total_assets"])
    comps = {"DSRI": dsri, "GMI": gmi, "AQI": aqi, "SGI": sgi, "DEPI": depi, "SGAI": sgai, "LVGI": lvgi, "TATA": tata}
    if any(v is None for v in comps.values()):
        return {"available": False, "missing": [k for k, v in comps.items() if v is None]}
    m = -4.84 + 0.920 * dsri + 0.528 * gmi + 0.404 * aqi + 0.892 * sgi + 0.115 * depi - 0.172 * sgai + 4.679 * tata - 0.327 * lvgi
    defaults = [k for k, x in (("DEPI", dep(t)), ("SGAI", sga(t))) if not x]
    return {"available": True, "m_score": r3(m), "zone": "elevated risk" if m > -1.78 else "low risk",
            "threshold": -1.78, "components": {k: r3(v) for k, v in comps.items()},
            "defaulted_to_1": defaults,
            "read": "Components above ~1.1 (DSRI, GMI, AQI, SGI) or TATA > 0.03 point to where pressure sits."}


def altman(t, market_cap, manufacturer):
    missing = need(t, ["current_assets", "current_liabilities", "retained_earnings", "operating_income", "total_assets", "total_liabilities", "revenue"])
    if missing:
        return {"available": False, "missing": missing}
    ta = t["total_assets"]
    wc = t["current_assets"] - t["current_liabilities"]
    x1, x2, x3 = d(wc, ta), d(t["retained_earnings"], ta), d(t["operating_income"], ta)
    x5 = d(t["revenue"], ta)
    out = {"available": True}
    if market_cap:
        x4 = d(market_cap, t["total_liabilities"])
        z = 1.2 * x1 + 1.4 * x2 + 3.3 * x3 + 0.6 * x4 + 1.0 * x5
        out["z_original"] = r3(z)
        out["z_original_zone"] = "safe" if z > 2.99 else "grey" if z >= 1.81 else "distress"
        out["components_original"] = {"X1 WC/TA": r3(x1), "X2 RE/TA": r3(x2), "X3 EBIT/TA": r3(x3), "X4 MVE/TL": r3(x4), "X5 Sales/TA": r3(x5)}
    else:
        out["z_original"] = None
        out["z_original_note"] = "Pass --market-cap (or get it from market.py quote) to compute the original Z."
    bv = (t["equity"] or 0)
    x4b = d(bv, t["total_liabilities"])
    z2 = 6.56 * x1 + 3.26 * x2 + 6.72 * x3 + 1.05 * x4b
    out["z_double_prime"] = r3(z2)
    out["z_double_prime_zone"] = "safe" if z2 > 2.6 else "grey" if z2 >= 1.1 else "distress"
    out["preferred"] = "z_original" if manufacturer and market_cap else "z_double_prime"
    out["note"] = "Altman Z is calibrated on industrial firms; ignore it for banks, insurers and REITs."
    return out


def piotroski(t, p):
    checks = {}
    roa = d(t["net_income"], p["total_assets"])
    roa_p = None
    checks["1 ROA > 0"] = roa is not None and roa > 0
    checks["2 CFO > 0"] = (t["operating_cash_flow"] or 0) > 0
    # prior-year ROA uses prior-prior assets; approximate with prior assets
    roa_p = d(p["net_income"], p["total_assets"])
    checks["3 ROA improving"] = roa is not None and roa_p is not None and roa > roa_p
    checks["4 CFO > net income (quality)"] = t["operating_cash_flow"] is not None and t["net_income"] is not None and t["operating_cash_flow"] > t["net_income"]
    lev = lambda x: d(x["long_term_debt"] or 0, x["total_assets"])
    checks["5 Leverage falling"] = lev(t) is not None and lev(p) is not None and lev(t) <= lev(p)
    cr = lambda x: d(x["current_assets"], x["current_liabilities"])
    checks["6 Current ratio rising"] = cr(t) is not None and cr(p) is not None and cr(t) > cr(p)
    ratio = d(t.get("shares_diluted"), p.get("shares_diluted"))
    split_suspect = ratio is not None and (ratio > 1.5 or ratio < 0.67)  # likely an unrestated stock split
    checks["7 No dilution"] = ratio is not None and not split_suspect and ratio <= 1.005
    gm = lambda x: d(x["gross_profit"], x["revenue"])
    checks["8 Gross margin rising"] = gm(t) is not None and gm(p) is not None and gm(t) > gm(p)
    at = lambda x: d(x["revenue"], x["total_assets"])
    checks["9 Asset turnover rising"] = at(t) is not None and at(p) is not None and at(t) > at(p)
    score = sum(1 for v in checks.values() if v)
    notes = ["Share count changed %.1fx y/y: probably a stock split not restated in the prior filing. Check 7 counted as a fail; verify manually." % ratio] if split_suspect else []
    return {"f_score": score, "zone": "strong" if score >= 7 else "weak" if score <= 3 else "neutral", "checks": checks, "split_warnings": notes,
            "note": "Signals with missing data count as fails; check the 'checks' map before reading too much into a low score."}


def sloan(t, p):
    if None in (t["net_income"], t["operating_cash_flow"], t["total_assets"], p["total_assets"]):
        return {"available": False}
    ratio = d(t["net_income"] - t["operating_cash_flow"], (t["total_assets"] + p["total_assets"]) / 2)
    return {"available": True, "accrual_ratio_pct": round(ratio * 100, 2),
            "zone": "warning" if ratio > 0.10 else "watch" if ratio > 0.05 else "clean" if ratio < 0 else "normal",
            "read": "Positive = earnings running ahead of cash. Persistent > 10% has historically predicted weaker future returns (Sloan 1996)."}


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("ticker")
    p.add_argument("--market-cap", type=float, help="equity market value in USD (for Altman Z original)")
    a = p.parse_args()
    co = edgar.resolve(a.ticker)
    facts = edgar.build_facts(co["cik"], n_quarters=8, n_years=6)
    rows = st.enrich(st.build_rows(facts, "annual"), 1)
    if len(rows) < 2:
        edgar.die("Need at least two fiscal years of XBRL data for %s" % co["ticker"])
    t, pr = rows[-1], rows[-2]
    sic = str(edgar.submissions(co["cik"]).get("sic") or "")
    manufacturer = sic[:1] in ("2", "3")
    financial = sic[:2] in ("60", "61", "62", "63", "64", "67")
    trend = [{"fy_end": r["period_end"], "dso": r["dso"], "dio": r["dio"], "dpo": r["dpo"], "cash_conversion": r["cash_conversion"],
              "sbc_pct_rev": r["sbc_pct_rev"], "gross_margin_pct": r["gross_margin_pct"], "share_count_yoy_pct": r.get("share_count_yoy_pct")} for r in rows[-5:]]
    flags = []
    win = "%s→%s" % (trend[0]["fy_end"][:4], trend[-1]["fy_end"][:4])
    def drift(k, label):
        a, b = trend[0][k], trend[-1][k]
        if a and b and b > a * 1.2:
            yoy = trend[-2][k] if len(trend) > 1 else None
            one = (" (last year: %+.0f%%)" % ((b / yoy - 1) * 100)) if yoy else ""
            flags.append("%s up %.0f%% over FY%s%s: %s" % (k.upper(), (b / a - 1) * 100, win, one, label))
    drift("dso", "receivables growing faster than sales")
    drift("dio", "inventory building faster than cost of sales")
    if t["cash_conversion"] is not None and t["cash_conversion"] < 0.8:
        flags.append("Cash conversion (FCF/NI) below 0.8 in the latest year")
    if t["sbc_pct_rev"] and t["sbc_pct_rev"] > 10:
        flags.append("SBC above 10% of revenue: GAAP vs. adjusted earnings gap likely large")
    na = {"available": False, "reason": "not designed for banks/insurers (SIC %s)" % sic}
    if financial:
        flags = []
    out = dict(co, fiscal_year=t["period_end"], prior_year=pr["period_end"], sic=sic, is_financial=financial,
               beneish=na if financial else beneish(t, pr), altman=na if financial else altman(t, a.market_cap, manufacturer),
               piotroski=na if financial else piotroski(t, pr), sloan=na if financial else sloan(t, pr),
               working_capital_trend=[] if financial else trend, quick_flags=flags,
               caveats=(["Financial company (SIC %s): Beneish, Altman and Piotroski are not designed for banks/insurers. Use credit-quality, reserve and capital metrics instead." % sic] if financial else []) +
                       ["Scores flag where to dig, not conclusions. Confirm in the 10-K notes (revenue recognition, reserves, capitalization policies)."],
               sources=sorted(set(x for x in (t.get("accn"), pr.get("accn")) if x)))
    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    main()
