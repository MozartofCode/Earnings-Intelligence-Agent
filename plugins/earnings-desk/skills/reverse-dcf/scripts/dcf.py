#!/usr/bin/env python3
"""Reverse DCF ("what's priced in") + scenario DCF. Stdlib only.

Usage
  python3 dcf.py TICKER [--price 410.5] [--wacc 9] [--terminal-growth 3] [--years 10]
                 [--target-margin 30] [--growth 15] [--sbc-as-cost | --sbc-ignore]
  python3 dcf.py --manual --revenue 3.4e11 --fcf-margin 25 --net-debt -3e10 --shares 7.4e9 --price 410

Model (FCF to equity-holders, simple and transparent):
  * Revenue grows at g1 in year 1 and fades linearly to the terminal growth rate by the final year.
  * FCF margin moves linearly from today's TTM margin to the target margin by year 5, then holds.
  * FCF = OCF - capex, minus SBC by default (SBC is a real cost to shareholders).
  * Equity value = PV(FCF) + PV(terminal) - net debt. Discount rate = --wacc.
Reverse mode solves for the year-1 growth (holding the target margin) and for the
target margin (holding growth) that justify today's price.
Pulls TTM inputs from SEC XBRL (via the sibling sec-edgar skill) and the price from
market.py unless --price is given.
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


def project(rev0, m0, g1, gT, m_target, years, wacc, ramp=5):
    """Return (equity-free PV of FCF incl. terminal, yearly rows)."""
    rows, pv, rev = [], 0.0, rev0
    for y in range(1, years + 1):
        g = g1 + (gT - g1) * (y - 1) / max(years - 1, 1)
        rev *= 1 + g
        m = m0 + (m_target - m0) * min(y, ramp) / ramp
        fcf = rev * m
        df = (1 + wacc) ** -y
        pv += fcf * df
        rows.append({"year": y, "growth_pct": round(g * 100, 2), "revenue": round(rev), "fcf_margin_pct": round(m * 100, 2), "fcf": round(fcf), "pv_fcf": round(fcf * df)})
    if wacc <= gT:
        raise ValueError("WACC must exceed terminal growth")
    tv = rows[-1]["fcf"] * (1 + gT) / (wacc - gT)
    pv_tv = tv * (1 + wacc) ** -years
    return pv + pv_tv, pv_tv, rows


def cagr(g1, gT, years):
    """Compound annual revenue growth over the horizon when growth fades linearly from g1 to gT."""
    f = 1.0
    for y in range(1, years + 1):
        f *= 1 + (g1 + (gT - g1) * (y - 1) / max(years - 1, 1))
    return f ** (1.0 / years) - 1, f


def per_share(ev_pv, net_debt, shares):
    return (ev_pv - net_debt) / shares


def solve(f, lo, hi, target, iters=80):
    """Bisection for f(x) = target on [lo, hi]; f increasing in x."""
    flo, fhi = f(lo), f(hi)
    if (flo - target) * (fhi - target) > 0:
        return None
    for _ in range(iters):
        mid = (lo + hi) / 2
        if (f(mid) - target) * (flo - target) > 0:
            lo, flo = mid, f(mid)
        else:
            hi = mid
    return (lo + hi) / 2


def load_inputs(a):
    import edgar
    import statements as st
    co = edgar.resolve(a.ticker)
    facts = edgar.build_facts(co["cik"], n_quarters=8, n_years=3)
    q = st.enrich(st.build_rows(facts, "quarterly"), 4)
    ttm = st.ttm(q)
    if not ttm or not ttm.get("revenue"):
        edgar.die("Not enough quarterly XBRL data for TTM inputs; use --manual.")
    fcf = ttm["fcf"]
    if fcf is None:
        edgar.die("Missing operating cash flow or capex in XBRL; use --manual.")
    if not a.sbc_ignore and ttm.get("sbc"):
        fcf -= ttm["sbc"]
    shares = ttm.get("shares_diluted") or ttm.get("shares_outstanding")
    price = a.price
    price_src = "user input"
    if price is None:
        import market
        qt = market.quote(co["ticker"])
        price, price_src = qt.get("price"), qt.get("source")
        if price is None:
            edgar.die("No price available. Pass --price (and cite where it came from).", hint=qt.get("hint"))
    return dict(ticker=co["ticker"], name=co["name"], revenue=ttm["revenue"], fcf=fcf, fcf_margin=fcf / ttm["revenue"], net_debt=ttm["net_debt"] or 0,
                shares=shares, price=price, price_source=price_src, ttm_periods=ttm["periods"], sbc_deducted=not a.sbc_ignore, sbc=ttm.get("sbc"))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("ticker", nargs="?")
    p.add_argument("--manual", action="store_true")
    p.add_argument("--revenue", type=float); p.add_argument("--fcf-margin", type=float, help="percent"); p.add_argument("--net-debt", type=float); p.add_argument("--shares", type=float)
    p.add_argument("--price", type=float)
    p.add_argument("--wacc", type=float, default=9.0, help="percent, default 9")
    p.add_argument("--terminal-growth", type=float, default=3.0, help="percent, default 3")
    p.add_argument("--years", type=int, default=10)
    p.add_argument("--growth", type=float, help="base-case year-1 revenue growth, percent")
    p.add_argument("--target-margin", type=float, help="base-case FCF margin by year 5, percent (default: today's)")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--sbc-as-cost", action="store_true", default=True)
    g.add_argument("--sbc-ignore", action="store_true")
    a = p.parse_args()

    if a.manual:
        miss = [k for k in ("revenue", "fcf_margin", "net_debt", "shares", "price") if getattr(a, k) is None]
        if miss:
            print(json.dumps({"error": "--manual needs " + ", ".join("--" + m.replace("_", "-") for m in miss)}))
            sys.exit(1)
        inp = dict(ticker=a.ticker or "MANUAL", revenue=a.revenue, fcf_margin=a.fcf_margin / 100, net_debt=a.net_debt, shares=a.shares, price=a.price, price_source="user input")
    else:
        if not a.ticker:
            p.error("TICKER required unless --manual")
        inp = load_inputs(a)

    wacc, gT, N = a.wacc / 100, a.terminal_growth / 100, a.years
    m0 = inp["fcf_margin"]
    m_target = (a.target_margin / 100) if a.target_margin is not None else max(m0, 0.01)
    rev0, nd, sh, price = inp["revenue"], inp["net_debt"], inp["shares"], inp["price"]
    mcap = price * sh

    val = lambda g1, mt: per_share(project(rev0, m0, g1, gT, mt, N, wacc)[0], nd, sh)
    implied_g = solve(lambda g1: val(g1, m_target), -0.5, 1.5, price)
    implied_m = solve(lambda mt: val(a.growth / 100 if a.growth is not None else 0.10, mt), -0.2, 0.9, price)

    base_g = a.growth / 100 if a.growth is not None else (implied_g if implied_g is not None else 0.08)
    scenarios = {}
    for name, dg, dm in (("bear", -0.5, -0.25), ("base", 0.0, 0.0), ("bull", 0.5, 0.2)):
        g1 = base_g * (1 + dg) if base_g > 0 else base_g + dg * 0.1
        mt = m_target * (1 + dm)
        ev, pv_tv, rows = project(rev0, m0, g1, gT, mt, N, wacc)
        ps = per_share(ev, nd, sh)
        scenarios[name] = {"year1_growth_pct": round(g1 * 100, 2), "revenue_cagr_pct": round(cagr(g1, gT, N)[0] * 100, 2),
                           "target_fcf_margin_pct": round(mt * 100, 2), "value_per_share": round(ps, 2),
                           "upside_pct": round((ps / price - 1) * 100, 1), "terminal_share_of_value_pct": round(pv_tv / ev * 100, 1) if ev else None}
        if name == "base":
            scenarios[name]["projection"] = rows

    sens = {"rows_wacc_pct": [], "cols_terminal_growth_pct": [], "values": []}
    gs = [gT - 0.01, gT - 0.005, gT, gT + 0.005, gT + 0.01]
    ws = [wacc - 0.02, wacc - 0.01, wacc, wacc + 0.01, wacc + 0.02]
    sens["cols_terminal_growth_pct"] = [round(x * 100, 2) for x in gs]
    for w in ws:
        sens["rows_wacc_pct"].append(round(w * 100, 2))
        row = []
        for gg in gs:
            try:
                row.append(round(per_share(project(rev0, m0, base_g, gg, m_target, N, w)[0], nd, sh), 2))
            except ValueError:
                row.append(None)
        sens["values"].append(row)

    out = {
        "inputs": dict(inp, market_cap=round(mcap), wacc_pct=a.wacc, terminal_growth_pct=a.terminal_growth, years=N,
                       current_fcf_margin_pct=round(m0 * 100, 2), target_fcf_margin_pct=round(m_target * 100, 2)),
        "reverse": {
            "implied_year1_growth_pct": None if implied_g is None else round(implied_g * 100, 2),
            "implied_revenue_cagr_pct": None if implied_g is None else round(cagr(implied_g, gT, N)[0] * 100, 2),
            "cagr_horizon_years": N,
            "implied_final_year_revenue": None if implied_g is None else round(rev0 * cagr(implied_g, gT, N)[1]),
            "implied_revenue_multiple_vs_today": None if implied_g is None else round(cagr(implied_g, gT, N)[1], 2),
            "implied_growth_holding_margin_pct": round(m_target * 100, 2),
            "implied_target_fcf_margin_pct": None if implied_m is None else round(implied_m * 100, 2),
            "implied_margin_holding_growth_pct": a.growth if a.growth is not None else 10.0,
            "implied_margin_note": "implied_target_fcf_margin_pct is solved holding year-1 growth at implied_margin_holding_growth_pct (pass --growth to set it).",
            "margin_basis": ("FCF margins are after deducting stock-based compensation" if inp.get("sbc_deducted", True) else "FCF margins exclude stock-based compensation") + "; capex excludes finance leases.",
            "default_margin_warning": None if a.target_margin is not None else "No --target-margin given: the solve holds today's TTM FCF margin. If capex or a one-off depresses it, pass a normalized --target-margin.",
            "implied_fcf_yield_pct": round(inp["fcf_margin"] * rev0 / mcap * 100, 2),
            "read": "Year-1 growth fades linearly to terminal growth. Compare implied numbers with history and guidance: is the market asking for more than the company has ever delivered?",
        },
        "scenarios": scenarios,
        "sensitivity_value_per_share": sens,
        "caveats": ["Simple FCF-to-equity model; adjust for leases, pensions, minority interests and cyclicality where they matter.",
                    "Not meaningful for banks/insurers (use P/B vs. ROE) or for companies with negative FCF and no path to positive (use EV/Sales vs. growth)."],
    }
    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    main()
