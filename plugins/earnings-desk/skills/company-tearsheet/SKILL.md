---
name: company-tearsheet
description: >-
  The "start here" one-page snapshot of any US-listed stock, built from SEC filings with no API key. Covers what the company does and how it makes money (segments from the 10-K), a 5-year key financials table and chart, a valuation snapshot (P/E, EV/Sales, EV/EBIT, FCF yield on trailing-twelve-month numbers), balance sheet health, insider and ownership snapshot, upcoming catalysts and the next earnings date, plus 3 bull points, 3 bear points and the key debate. Use it when the user asks "tell me about TICKER", "what does this company do", "give me a quick overview / snapshot / tearsheet / one-pager", "is this stock worth a look", "how does it make money", "what's the bull and bear case in brief", or names a ticker with no other context. It is the first step before deeper earnings-desk work.
license: MIT
compatibility: Requires Python 3.8+ (standard library only) and internet access to sec.gov. Optional FMP_API_KEY, FINNHUB_API_KEY or ALPHAVANTAGE_API_KEY improve quotes and the earnings calendar.
metadata:
  category: "1-data-foundations"
  version: "1.0.0"
  author: "earnings-desk"
---

# company-tearsheet · the whole company on one page

Everything a portfolio manager wants in the first five minutes: what the business is, how it earns money, what the numbers look like, what the market is paying for it, and what the argument is about. Every number comes from a filing or a cited source.

## When to use
- First look at a ticker: "what is this company", "quick overview", "one-pager", "is it worth a look".
- Before any deeper skill, so later work starts from a shared factual base.

**Not for:** a full ratio deep-dive (`financial-statements`), "is it cheap?" in depth (`reverse-dcf`, `comps-valuation`), what happened in the last print (`earnings-recap`), or a complete research report (`deep-dive`).

## Inputs
- `TICKER` (required). US-listed SEC filers. Foreign private issuers file 20-F, so use `--form 20-F` where a command takes `--form`.
- Optional: years of history (default 5), focus (for example "just the segments").

> **Paths:** `${CLAUDE_SKILL_DIR}` is this skill's own folder. Claude Code fills it in automatically; in other tools, replace it with the folder that contains this `SKILL.md`. Sibling skills such as `${CLAUDE_SKILL_DIR}/../sec-edgar` are installed next to it.

## Workflow
Scripts are relative to this skill folder. Set `SEC_USER_AGENT` first (see `sec-edgar`). If a command returns 403, ask the user for a name and email; never invent one.

1. **Identity and filing cadence**
   ```bash
   python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/edgar.py profile TICKER
   ```
   Note SIC description, fiscal year end (`fiscalYearEnd` is MMDD), state of incorporation and the latest 10-K, 10-Q, 8-K and DEF 14A. If the SIC is a bank, insurer or REIT (SIC 60–67), switch the KPI set (see Analysis framework).

2. **Business and segments** (how it makes money)
   ```bash
   python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/edgar.py filing-text TICKER --form 10-K --section 1 --max-chars 25000
   ```
   Read Item 1 for products, customers, go-to-market and revenue model (one-time vs. recurring, unit vs. subscription vs. usage vs. transaction). For segment revenue and operating income, grep the full 10-K that was saved to `saved_to` (XBRL segment data is not in the companyfacts API, so this is text work):
   ```bash
   grep -n -i -E "reportable segment|segment information|revenue by (geograph|product|segment)|disaggregat" "<saved_to>" | head -40
   ```
   Then read around the hits for the segment note table (usually Note "Segment Information" in Item 8) and the disaggregated-revenue table. Also capture customer concentration ("accounted for 10%" or "% of total revenue").

3. **Five-year financials and trailing twelve months**
   ```bash
   python3 ${CLAUDE_SKILL_DIR}/../financial-statements/scripts/statements.py TICKER --years 5 --quarters 8
   ```
   Use `annual[]` for the table (revenue, growth, gross and operating margin, net income, diluted EPS, FCF, FCF margin, ROIC, diluted shares) and `ttm` for valuation. Check `missing_metrics` and `derived_quarter` flags.

4. **Price and market cap**
   ```bash
   python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/market.py quote TICKER
   ```
   Record `price`, `source`, `as_of` and `market_cap` (plus `market_cap_note`: keyless market cap is price times the latest SEC shares outstanding). If `available: false`, use web search and cite site and date.

5. **Insiders** (snapshot only; use `insider-ownership` for the full read)
   ```bash
   python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/edgar.py insiders TICKER --days 180
   ```
   Report open-market buys (code P) vs. sales (code S), unique buyers and total values. Ignore grants (A), tax withholding (F) and gifts (G) for signal purposes.

6. **Catalysts**
   ```bash
   python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/market.py calendar TICKER
   python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/edgar.py filings TICKER --forms 8-K --limit 15
   ```
   If the calendar is keyless (`available: false`), present `estimated_next` as an **estimate** and confirm it by web search on the investor-relations site. Scan recent 8-K `items` for M&A (1.01, 2.01), leadership changes (5.02), guidance updates (7.01 or 2.02) and auditor events (4.01, 4.02). Add known events from the 10-K and press releases: product launches, investor days, debt maturities, regulatory decisions, lock-up expiries.

7. **Bull, bear and the debate.** Write these last, from the evidence above. Optionally pull the latest press release for management's framing:
   ```bash
   python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/edgar.py earnings-release TICKER --max-chars 15000
   ```

## Analysis framework

**Business model in one sentence.** "X sells Y to Z, charged as W, and the moat (if any) is V." If you can't write it, you haven't understood Item 1 yet. Then classify the revenue model, because it decides which metrics matter:

| Model | What matters most |
|---|---|
| Subscription / SaaS | Net revenue retention, RPO growth, gross margin above 75%, FCF margin, SBC % of revenue |
| Transaction / marketplace | Volume (GMV, TPV) × take rate, take-rate trend, contribution margin |
| Unit sales / hardware / semis | Units × ASP, gross margin through the cycle, inventory days, customer concentration |
| Consumer brands / retail | Same-store sales, traffic vs. ticket, gross margin, inventory turns |
| Industrials | Backlog and book-to-bill, price vs. volume, incremental margins |
| Banks / insurers | NIM, credit costs, CET1, combined ratio, book value growth. Skip gross margin, EV and FCF yield |

**Segments.** For each one give revenue, % of total, growth and operating margin where disclosed. Name the profit engine (often not the biggest revenue line) and say which segment the debate is about.

**Valuation snapshot** (TTM from `statements.py`, price and market cap from `market.py`):
- EV = market cap + `ttm.total_debt` − `ttm.cash` − `ttm.short_term_investments` (= market cap + `ttm.net_debt`). Debt excludes leases and minority interest, so say so.
- P/E = market cap / `ttm.net_income` (or price / `ttm.eps_diluted`). Show "n/m" if earnings are ≤ 0.
- EV/Sales = EV / `ttm.revenue`. EV/EBIT = EV / `ttm.operating_income`. EV/EBITDA = EV / `ttm.ebitda`.
- FCF yield = `ttm.fcf` / market cap. Also show FCF-after-SBC yield when SBC is above 5% of revenue.
- Frame, don't judge: put the multiples next to the company's own growth and margins. "28x EBIT for 18% growth and 47% margins." Peer context comes from `comps-valuation`, and what the price implies from `reverse-dcf`.

**Balance sheet health.**
- Net cash or net debt, net debt / EBITDA (above 3x is levered for non-financials and above 5x is stressed), interest coverage (EBIT / interest, below 3x is a concern), current ratio.
- Upcoming maturities and covenants: grep the 10-K for "matur" and "covenant".
- Goodwill as a % of total assets (above 40% means acquisition-built, so impairment risk).

**Ownership snapshot.** Insider buying and selling in 180 days, insider and founder stakes, and dual-class control from the DEF 14A ("Security Ownership of Certain Beneficial Owners"). Institutional and short interest only from a cited web source.

**Bull / bear / debate rules.**
- Each point is specific, falsifiable and tied to a number: "Data Center is 88% of revenue and grew 117%, so the cycle extends if hyperscaler capex grows in 2027", not "strong AI demand".
- Bear points must be real risks the bulls would have to answer (concentration, margin peak, competition, regulation, leverage, valuation), not boilerplate risk factors.
- **Key debate** is one question whose answer moves the stock: "Are 75% gross margins durable once custom silicon ramps?" Say what evidence would settle it and when (next print, product cycle, contract renewal).

**Questions a great analyst asks on page one.** Who pays and why can't they switch? What share of profit comes from one segment or one customer? Is growth organic or bought? Does FCF track net income? Is the share count falling or rising? What is the one number management will be judged on next quarter?

## Output
Write `/tmp/TICKER-company-tearsheet.json` per `../sec-edgar/references/report-schema.md`, with `"skill": "company-tearsheet"`.

- **title**: the company's essence with an accent, e.g. `"The *picks-and-shovels* of AI compute"`. **subtitle**: "Company tearsheet · FY ends <month> · data through <latest period>".
- **meta**: price with source and date, market cap, EV, sector (SIC), next earnings date (marked estimate if keyless).
- **verdict**: `{"label": "First look", "value": "Quality compounder | Cyclical at peak | Turnaround | Speculative | Value trap risk | Worth a deep dive", "tone": ...}`. It is a classification, not a buy or sell call.
- **kpis** (4–6): TTM revenue (y/y growth), operating margin, FCF (margin), P/E or EV/Sales, net cash or net debt, ROIC.
- **sections**:
  1. *What they do and how they make money*: business-model sentence, revenue-model class, segment table (revenue, % of total, growth, margin), doughnut chart of the revenue mix, concentration callout.
  2. *Five-year financials*: table (FY columns or rows) plus a bar chart of revenue with an operating-margin line (≤ 3 datasets).
  3. *Valuation snapshot*: multiples table with the inputs shown (market cap, EV, TTM figures), framed against growth and margins.
  4. *Balance sheet health*: net debt, leverage, coverage, liquidity, goodwill share, maturities. Callouts for anything concerning.
  5. *Ownership and insiders*: 180-day insider activity table, notable holders and control structure.
  6. *Catalysts*: dated table (event, date, why it matters, source); estimated dates are labeled.
  7. *Bull / bear / key debate*: three `pos` callouts, three `neg` callouts, one `accent` callout for the debate. Label this section as judgment.
- **sources**: 10-K and 10-Q accessions (from `sources` in statements.py output and the filing `accession`), quote source with timestamp, and every web search (site, date).

Render and fix any warnings:
```bash
python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/render_report.py /tmp/TICKER-company-tearsheet.json --out-dir earnings-desk-reports
```
**In chat** print the business-model sentence, the KPI row as a compact table, the three bulls and three bears in a few words each, the key debate, the next catalyst date, then the HTML and Markdown paths.

## Quality bar & pitfalls
- **One page means ruthless.** A tearsheet that copies Item 1 has failed. Lead with how money is made, then what it's worth, then what the argument is.
- **TTM must be four real quarters.** Check `ttm.periods` covers four consecutive quarters and note any `derived_quarter`. Q4 is usually derived (FY minus 9-month YTD).
- **Fiscal labels.** Label by period end or the company's fiscal year ("FY26, ended Jan 25, 2026"), never by an assumed calendar year.
- **Share-count seams.** Stock splits can show up as a huge share-count jump (NVDA's FY23 `share_count_yoy_pct` reads +889% because of an unrestated older filing). Check split history before calling it dilution.
- **Market cap source matters.** For multi-class companies, keyless market cap (price × SEC shares outstanding) may count only one class. Cross-check with the cover-page share counts.
- **Net cash inflates ROIC.** `statements.py` subtracts cash from invested capital, so cash-rich firms show very high ROIC. Say so when you quote it.
- **Financials.** For banks, insurers and REITs, replace EV, gross margin and FCF yield with P/B, P/TBV, ROE, NIM, combined ratio and FFO, and say why.
- Never fill a missing number from memory. Write "not disclosed" and move on.

## Next skills
- `/earnings-desk:financial-statements` for the full three-statement breakdown
- `/earnings-desk:earnings-preview` or `/earnings-desk:earnings-recap` around the next print
- `/earnings-desk:reverse-dcf` and `/earnings-desk:comps-valuation` to judge whether the price is reasonable
- `/earnings-desk:moat-analysis` and `/earnings-desk:bull-bear-debate` to stress-test the debate
- `/earnings-desk:forensic-accounting` if anything in the numbers looked too good
- `/earnings-desk:deep-dive` for the full research report

_Not investment advice. Data is from public filings and cited sources and may contain errors; verify before acting._
