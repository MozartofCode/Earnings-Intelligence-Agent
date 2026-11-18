#!/usr/bin/env python3
"""Normalized financial statements + ratio trends from SEC XBRL. Stdlib only.

Usage
  python3 statements.py TICKER [--years 5] [--quarters 8]

Output JSON:
  annual[]     one row per fiscal year: core lines + margins, growth, returns, efficiency
  quarterly[]  one row per quarter with y/y growth (quarter vs. same quarter last year)
  ttm          trailing-twelve-month totals from the last 4 quarters
  sources      accession numbers used
Depends on ../../sec-edgar/scripts/edgar.py (sibling skill).
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for _base in (os.path.join(HERE, "..", ".."), os.path.join(HERE, "..", "vendor")):  # sibling skill, or bundled copy
    sys.path.insert(0, os.path.join(_base, "sec-edgar", "scripts"))
import edgar  # noqa: E402


def div(a, b):
    try:
        if a is None or b in (None, 0):
            return None
        return a / b
    except TypeError:
        return None


def pct(x):
    return None if x is None else round(100 * x, 2)


def r2(x):
    return None if x is None else round(x, 2)


def index_by_end(series):
    return {r["end"]: r for r in series or []}


def nearest(series_idx, end, tol_days=20):
    if end in series_idx:
        return series_idx[end]["val"]
    for k, r in series_idx.items():
        if abs(edgar._days(k, end)) <= tol_days:
            return r["val"]
    return None


def build_rows(facts, which):
    data = facts[which]
    flows = ["revenue", "cost_of_revenue", "gross_profit", "rnd", "sga", "operating_income", "interest_expense", "pretax_income", "income_tax",
             "net_income", "eps_diluted", "shares_diluted", "da", "sbc", "operating_cash_flow", "capex", "acquisitions", "buybacks", "dividends_paid"]
    stocks = ["cash", "short_term_investments", "receivables", "inventory", "current_assets", "ppe_net", "goodwill", "total_assets", "accounts_payable",
              "current_liabilities", "long_term_debt", "short_term_debt", "total_liabilities", "retained_earnings", "equity", "shares_outstanding"]
    idx = {m: index_by_end(data.get(m)) for m in flows + stocks}
    spine = data.get("revenue") or data.get("net_income") or []
    rows = []
    for r in spine:
        end = r["end"]
        row = {"period_end": end, "fy": int(end[:4])}
        for m in flows + stocks:
            row[m] = nearest(idx[m], end)
        if row["gross_profit"] is None and row["revenue"] is not None and row["cost_of_revenue"] is not None:
            row["gross_profit"] = row["revenue"] - row["cost_of_revenue"]
        row["accn"] = r.get("accn")
        row["derived_quarter"] = r.get("derived", False)
        rows.append(row)
    return rows


def enrich(rows, periods_per_year):
    for i, r in enumerate(rows):
        rev = r["revenue"]
        fcf = None if r["operating_cash_flow"] is None else r["operating_cash_flow"] - (r["capex"] or 0)
        r["fcf"] = fcf
        r["fcf_after_sbc"] = None if fcf is None else fcf - (r["sbc"] or 0)
        r["ebitda"] = None if r["operating_income"] is None else r["operating_income"] + (r["da"] or 0)
        debt = (r["long_term_debt"] or 0) + (r["short_term_debt"] or 0)
        liquid = (r["cash"] or 0) + (r["short_term_investments"] or 0)
        r["total_debt"] = debt
        r["net_debt"] = debt - liquid
        r["gross_margin_pct"] = pct(div(r["gross_profit"], rev))
        r["operating_margin_pct"] = pct(div(r["operating_income"], rev))
        r["net_margin_pct"] = pct(div(r["net_income"], rev))
        r["fcf_margin_pct"] = pct(div(fcf, rev))
        r["rnd_pct_rev"] = pct(div(r["rnd"], rev))
        r["sbc_pct_rev"] = pct(div(r["sbc"], rev))
        r["capex_pct_rev"] = pct(div(r["capex"], rev))
        r["cash_conversion"] = r2(div(fcf, r["net_income"]))          # FCF / net income
        r["ocf_to_ni"] = r2(div(r["operating_cash_flow"], r["net_income"]))  # operating cash flow / net income
        r["tax_rate_pct"] = pct(div(r["income_tax"], r["pretax_income"]))
        r["current_ratio"] = r2(div(r["current_assets"], r["current_liabilities"]))
        r["interest_coverage"] = r2(div(r["operating_income"], r["interest_expense"]))
        ann = periods_per_year
        r["net_debt_to_ebitda"] = r2(div(r["net_debt"], (r["ebitda"] or 0) * ann)) if r["ebitda"] else None
        days = 365.0 / ann
        r["dso"] = r2(div(r["receivables"], rev) * days) if div(r["receivables"], rev) is not None else None
        cogs = r["cost_of_revenue"] or ((rev - r["gross_profit"]) if rev is not None and r["gross_profit"] is not None else None)
        r["dio"] = r2(div(r["inventory"], cogs) * days) if div(r["inventory"], cogs) is not None else None
        r["dpo"] = r2(div(r["accounts_payable"], cogs) * days) if div(r["accounts_payable"], cogs) is not None else None
        # Returns on average capital need the prior balance sheet
        prev = rows[i - 1] if i > 0 else None  # prior period's balance sheet
        if prev:
            avg_eq = div((r["equity"] or 0) + (prev["equity"] or 0), 2)
            r["roe_pct"] = pct(div(r["net_income"] * ann if r["net_income"] is not None else None, avg_eq)) if avg_eq and avg_eq > 0 else None
            nopat = None if r["operating_income"] is None else r["operating_income"] * (1 - min(max((div(r["income_tax"], r["pretax_income"]) or 0.21), 0), 0.35))
            # Invested capital = equity + debt. Cash is NOT subtracted: for cash-rich
            # companies that makes the denominator tiny and ROIC meaningless.
            ic = lambda x: (x["equity"] or 0) + (x["total_debt"] or 0)
            avg_ic = div(ic(r) + ic(prev), 2)
            r["roic_pct"] = pct(div(nopat * ann if nopat is not None else None, avg_ic)) if avg_ic and avg_ic > 0 else None
        # Growth vs. one year earlier
        yago = rows[i - periods_per_year] if i - periods_per_year >= 0 else None
        if yago:
            for m in ("revenue", "gross_profit", "operating_income", "net_income", "eps_diluted", "fcf"):
                base = yago.get(m)
                r[m + "_yoy_pct"] = pct(div((r[m] - base) if r.get(m) is not None and base is not None else None, abs(base) if base else None))
            r["share_count_yoy_pct"] = pct(div((r["shares_diluted"] - yago["shares_diluted"]) if r["shares_diluted"] and yago["shares_diluted"] else None, yago["shares_diluted"]))
            if r["share_count_yoy_pct"] is not None and abs(r["share_count_yoy_pct"]) > 50:
                r["share_count_note"] = "share count moved >50% y/y: likely a stock split not restated in older filings"
    return rows


def ttm(qrows):
    last4 = qrows[-4:]
    if len(last4) < 4:
        return None
    out = {"periods": [r["period_end"] for r in last4]}
    for m in ("revenue", "gross_profit", "operating_income", "net_income", "eps_diluted", "operating_cash_flow", "capex", "sbc", "fcf", "ebitda", "buybacks", "dividends_paid", "da"):
        vals = [r.get(m) for r in last4]
        out[m] = round(sum(vals), 4) if all(v is not None for v in vals) else None
    latest = qrows[-1]
    for m in ("cash", "short_term_investments", "total_debt", "net_debt", "equity", "shares_outstanding", "shares_diluted"):
        out[m] = latest.get(m)
    out["fcf_margin_pct"] = pct(div(out["fcf"], out["revenue"]))
    out["operating_margin_pct"] = pct(div(out["operating_income"], out["revenue"]))
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("ticker")
    p.add_argument("--years", type=int, default=5)
    p.add_argument("--quarters", type=int, default=8)
    a = p.parse_args()
    co = edgar.resolve(a.ticker)
    facts = edgar.build_facts(co["cik"], n_quarters=a.quarters + 4, n_years=a.years + 1)
    annual = enrich(build_rows(facts, "annual"), 1)
    quarterly = enrich(build_rows(facts, "quarterly"), 4)
    out = dict(co, units="USD (raw); per-share in USD; shares in units", ttm=ttm(quarterly),
               annual=annual[-a.years:], quarterly=quarterly[-a.quarters:],
               missing_metrics=[m for m in edgar.METRICS if m not in facts["tags_used"]],
               sources=sorted(set(r["accn"] for r in annual[-a.years:] + quarterly[-a.quarters:] if r.get("accn"))),
               notes=["Quarters flagged derived_quarter=true were computed as FY or YTD minus prior periods (EDGAR reports cash flows year-to-date).",
                      "fy = calendar year in which the fiscal period ends (e.g. NVDA FY26 ends Jan 2026 -> 2026). A few retailers name their year after the prior calendar year; check the 10-K cover.",
                      "FCF = operating cash flow - capex. cash_conversion = FCF / net income; ocf_to_ni = operating cash flow / net income.",
                      "ROIC = NOPAT / average (equity + total debt); cash is not subtracted. Verify unusual values against the filing."])
    sic = str(edgar.submissions(co["cik"]).get("sic") or "")
    if sic[:2] in ("60", "61", "62", "63", "64", "67"):
        out["is_financial"] = True
        out["notes"].append("Financial company (SIC %s): debt, net debt, gross margin, working-capital days, FCF and ROIC are not meaningful for banks/insurers "
                            "(deposits and funding sit outside these tags). Use capital ratios, credit costs, NIM/combined ratio and book value instead." % sic)
    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    main()
