---
name: comps-valuation
description: >-
  Comparable-company (comps) valuation - builds a defensible peer set and a multiples table straight from SEC XBRL (no API key), then tells you whether the stock's premium or discount is earned. Computes EV/Sales, EV/EBIT, EV/EBITDA, P/E, P/B, FCF yield (pre and post SBC), TTM revenue growth, gross/operating/FCF margins, ROIC and Rule of 40 per peer, peer medians, and a regression of EV/Sales on growth to show who is rich or cheap for their growth. Use when the user asks "how does it compare to peers", "relative valuation", "comps", "trading multiples", "is it cheap vs competitors", "peer multiples", "EV/EBITDA vs peers", "P/E vs the sector", "why does it trade at a premium", "Rule of 40", or "which stock in the group is cheapest". Works for banks via P/E and P/B vs ROE.
license: MIT
compatibility: Requires Python 3.8+ (standard library only) and internet access to sec.gov. Prices via --prices (cited) or market.py (keyless best-effort; optional FMP_API_KEY / FINNHUB_API_KEY).
metadata:
  category: "4-valuation-competition"
  version: "1.0.0"
  author: "earnings-desk"
---

# comps-valuation · cheap vs. peers, or cheap for a reason?

A multiple only means something next to the right peers and the right fundamentals. This skill builds the peer set deliberately, computes every multiple from primary filings, and then asks the real question: **is the premium or discount justified by growth, margins and returns?**

## When to use
- "Is MSFT expensive vs. peers?", "comps for CRWD", "which semi is cheapest?", "why does COST trade at 50x?".
- As a cross-check on `reverse-dcf`: the market's relative pricing vs. its absolute expectations.
- **Not** for absolute value (use `reverse-dcf`) or for competitive-position quality (use `moat-analysis`, then come back here to judge whether the premium is earned).

## Inputs
- Target `TICKER` (required); optional peer list (otherwise built in step 1).
- Prices: `--prices "AAPL=230,MSFT=500"` with a citation is preferred. Without it, market.py quote is used (keyless, may be rate-limited).
- Optional `--target` if the target isn't listed first.

## Workflow
Commands are relative to this skill folder.

1. **Raw universe.** `python3 ../sec-edgar/scripts/edgar.py peers TICKER --limit 25` returns companies sharing the SIC code. Treat this as a starting list only, because SIC codes are coarse and often stale.
2. **Understand the target's business model.** `python3 ../sec-edgar/scripts/edgar.py filing-text TICKER --form 10-K --section 1` gives Item 1 Business. Note the segments, revenue model (recurring vs. transactional), customers, end markets, and the competitors the company names itself (search the saved file for "compet").
3. **Construct the peer set (5–10 names) with explicit judgment.** Add named competitors and business-model twins that SIC misses, and drop SIC matches that don't fit. Record a one-line reason for **every** inclusion and exclusion (see the framework below). If segments differ wildly, consider two peer groups, or sum-of-the-parts.
4. **Prices.** For each ticker, use a cited price (market.py quote, or web search with site and time). Use the same date for every name.
5. **Run the table:**
   ```bash
   python3 scripts/comps.py TARGET PEER1 PEER2 PEER3 PEER4 --prices "TARGET=123.4,PEER1=56.7,..."
   ```
   Add `--no-quote` to skip keyless price lookups entirely. Missing prices never abort the run: fundamentals still print, price multiples are `null`, and the reason appears in `flags`.
   Output: `rows[]` (per-ticker multiples and fundamentals, `ttm_periods`, `accessions`, `flags`), `peer_medians_ex_target`, `target_vs_median` (premium %), `regression_ev_sales_on_growth` (slope, intercept, r², fitted value and premium to the line per ticker), and `errors[]`.
6. **Quality check the rows.** Read `flags`. Derived quarters are normal (Q4 = FY − 9M). Watch for mismatched fiscal calendars (`ttm_periods`), negative equity (ROIC is meaningless), financials (EV multiples are nulled by design), and one-offs inflating TTM EBIT (impairments, gains). Check the big ones with `python3 ../financial-statements/scripts/statements.py TICKER`.
7. **Adjust where it matters.** Add leases, minority interests and pensions to EV by hand if they're material (see [../reverse-dcf/references/valuation-notes.md](../reverse-dcf/references/valuation-notes.md) §5–6). Use consensus forward estimates if you have them (`python3 ../sec-edgar/scripts/market.py estimates TICKER` with a key, or web search, cited). Forward multiples matter more than trailing ones for fast growers.
8. **Judge the premium, make the call, render.**

## Analysis framework

**Peer-set construction (the most important step).** A good peer shares most of these:
1. **Business model and revenue quality**: subscription vs. license vs. hardware vs. ad-supported. Recurring revenue deserves a higher multiple.
2. **End market and customer**: enterprise vs. SMB vs. consumer; cyclical vs. defensive demand.
3. **Growth and margin profile**: within roughly ±15 pts of growth, or explicitly flagged as an outlier.
4. **Scale**: over a 10–20x size gap, the economics usually differ (purchasing power, distribution).
5. **Geography and regulation**: regulated utilities, China exposure and so on.

Exclude conglomerates whose relevant segment is under ~30% of revenue, recent IPOs with under 4 reported quarters, companies in M&A limbo, and foreign filers without comparable XBRL. If needed, note them qualitatively. **Show the inclusion/exclusion table in the report.** Peer selection is where comps get gamed.

**Which multiple for which business**

| Business | Primary | Secondary | Avoid |
|---|---|---|---|
| Mature profitable (staples, industrials) | EV/EBIT, P/E, FCF yield | EV/EBITDA | EV/Sales |
| Capital-intensive (telecom, semis fabs) | EV/EBITDA *and* EV/(EBITDA − capex) | FCF yield | P/E (D&A distortions) |
| High-growth software / internet | EV/Sales vs. growth, Rule of 40, EV/gross profit | FCF-after-SBC yield | Trailing P/E |
| Banks | P/B vs. ROE, P/E | P/TBV | EV anything |
| Insurers | P/B vs. ROE, combined ratio | P/E | EV anything |
| REITs | P/AFFO, implied cap rate | NAV discount | P/E |
| Cyclicals | EV/EBIT on mid-cycle earnings | P/B at trough | Peak-earnings P/E |

**Growth-adjusted views**
- **EV/Sales vs. growth regression** (from comps.py): the slope is the turns of EV/Sales the group pays per point of growth. Read each name's `premium_to_line_pct`, but only when n ≥ 6 and r² ≥ ~0.3. Otherwise say the line explains little and lean on margins and ROIC. A positive premium often reflects higher margins or durability. Check whether it does before calling it "expensive".
- **Rule of 40** (software): revenue growth % + FCF margin %. 40+ is healthy, 60+ is elite, under 25 needs a turnaround story. Compare EV/Sales with Rule-of-40 rank. Use FCF *after* SBC when SBC is above 10% of revenue, or the score flatters.
- **PEG (P/E ÷ growth): use with caution.** It assumes a linear relationship between multiple and growth, ignores ROIC and durability, and breaks for low or negative growth. Prefer the regression or a reverse DCF.
- **ROIC vs. multiple:** value creation needs ROIC > WACC. Among peers, a higher EV/EBIT is usually justified when ROIC is higher *and* growth is similar. (Value ∝ growth × (1 − g/ROIC).)

**Premium or discount: earned or not?** Explain the gap in the target's multiple vs. the peer median with fundamentals, then judge what's left over:
- Growth gap (pts above or below the median), margin gap, ROIC gap, revenue quality (recurring %), balance sheet (net cash vs. levered), and moat (from `moat-analysis`).
- *Earned premium:* superior on 2–3 of these, consistently, for 3+ years.
- *Unearned premium:* the multiple rests on narrative, fundamentals are at or below the median, or growth is decelerating while the multiple holds.
- *Value trap discount:* cheap because earnings are at peak (cyclical), share is being lost, or secular decline. Check revenue trend, gross margin trend and the 10-K risk factors.
- *Opportunity discount:* fundamentals are at or above the median, the discount comes from a temporary issue (one-off charge, overhang, misclassification), and a catalyst exists.

**Questions to answer**
1. Would a generalist PM accept this peer set? Which peer is most debatable, and does dropping it change the answer?
2. Where does the target rank on growth, margin and ROIC vs. where it ranks on multiple? Rank mismatch is the signal.
3. Is the whole group rich or cheap? Relative value can be "cheapest house in an expensive neighborhood". Cross-check with `reverse-dcf`.
4. What would make the gap close: a catalyst, re-rating, or convergence of fundamentals?

## Output
Report JSON per [../sec-edgar/references/report-schema.md](../sec-edgar/references/report-schema.md), `"skill": "comps-valuation"`.
- **Title idea:** `"A premium it has *earned*"` / `"Cheap for a *reason*"` / `"The group's *best value*"`.
- **Verdict:** `{"label": "Relative value", "value": "Cheap" | "Fair" | "Rich", "sub": "EV/EBIT 22x vs 26x median; ROIC +10 pts", "tone": "pos" | "neutral" | "neg"}`.
- **KPIs (3–6):** target's primary multiple vs. peer median (premium %), growth vs. median, operating or FCF margin vs. median, ROIC vs. median, regression premium to line, Rule of 40 (for software).
- **Sections:**
  1. *Peer set*: an inclusion/exclusion table (ticker, why in or out).
  2. *Multiples table*: ticker, price, mkt cap, EV/Sales, EV/EBIT, P/E, FCF yield, growth, op margin, ROIC; peer median row; target row highlighted with pills (pos/neg vs. median).
  3. *Growth-adjusted*: an EV/Sales vs. growth bar chart, or a table of fitted vs. actual; slope, r², n; Rule of 40 ranking.
  4. *Premium decomposition*: callouts for each fundamental gap, with `scores` bars (target percentile within the peer group for growth, margin, ROIC and multiple).
  5. *The call*: earned or unearned, the catalyst for convergence, what would change the view.
- **Sources:** each peer's XBRL accessions (from `rows[].accessions`), price sources with date and time, consensus source if used.

Render:
```bash
python3 ../sec-edgar/scripts/render_report.py /tmp/TICKER-comps-valuation.json --out-dir earnings-desk-reports
```
**In chat:** the relative-value call in one line ("Trades at 22x EV/EBIT vs. a 26x peer median despite +8 pts better ROIC: looks cheap relative to the group"), the most debatable peer choice, and the report paths.

## Quality bar & pitfalls
- **Same price date for all peers.** Mixed dates create fake spreads.
- Trailing multiples on fast growers mislead. Show forward estimates when available (cited), and say which you used.
- Don't average multiples that include negatives or outliers. comps.py uses medians and nulls negative-denominator multiples.
- EV in comps.py excludes leases, minority interests and pensions. Adjust lease-heavy or holdco peers by hand, and say so.
- Fiscal-year mismatch (e.g. NVDA's January FY vs. AMD's December FY) is acceptable for TTM. Note it in the report.
- A regression on 4 points is an anecdote. Say so.
- No fabricated prices. If a price is missing and can't be cited, leave the multiple blank.

## Next skills
`/earnings-desk:reverse-dcf` (absolute expectations) · `/earnings-desk:moat-analysis` (is the premium durable?) · `/earnings-desk:forensic-accounting` (is the "cheap" earnings base real?) · `/earnings-desk:bull-bear-debate` · `/earnings-desk:thesis-tracker`.

_Not investment advice. Multiples are computed from public filings and cited prices and may contain errors; verify before acting._
