---
name: financial-statements
description: >-
  Three-statement analysis of any US-listed company from SEC XBRL data with no API key, covering the income statement, balance sheet and cash flow over 5+ years and 8 quarters. Computes growth, margin structure and margin bridges, ROIC and ROE, cash conversion (FCF vs. net income), capital intensity, working capital days (DSO, DIO, DPO), leverage and liquidity, stock-based compensation and dilution, and quarterly acceleration or deceleration, then explains what changed and why using MD&A. Use it when the user asks to "analyze the financials", "break down the income statement / balance sheet / cash flow", "how are margins trending", "is growth accelerating", "what's the ROIC", "does earnings turn into cash", "how much SBC / dilution", "is the balance sheet healthy", "show me the numbers", or wants ratios, trends or a fundamental review of a ticker.
license: MIT
compatibility: Requires Python 3.8+ (standard library only) and internet access to sec.gov.
metadata:
  category: "1-data-foundations"
  version: "1.0.0"
  author: "earnings-desk"
---

# financial-statements · what the numbers say, and why they moved

A disciplined three-statement read: growth, profitability, returns, cash and balance sheet, then the narrative from MD&A that explains each move. The goal is not a wall of ratios. It is the four or five facts that define the business's economics and the direction they are heading.

## When to use
- "Analyze the financials", "how are margins trending", "is growth accelerating", "what's ROIC", "does it convert to cash", "how bad is dilution".
- Before valuation (`reverse-dcf`, `comps-valuation`) or forensics (`forensic-accounting`), so they start from clean numbers.

**Not for:** a one-page overview (`company-tearsheet`), last-quarter beat or miss vs. consensus (`earnings-recap`), manipulation risk scores (`forensic-accounting`), or where the cash went over a decade (`capital-allocation`).

## Inputs
- `TICKER` (required).
- `--years` (default 5; use 10 for cyclicals so you see a full cycle) and `--quarters` (default 8).
- Optional focus: "margins only", "balance sheet", "cash flow".

## Workflow
1. **Pull normalized statements**
   ```bash
   python3 scripts/statements.py TICKER --years 5 --quarters 8 > /tmp/TICKER-st.json
   ```
   Output: `annual[]` and `quarterly[]` rows with core lines plus computed ratios, `ttm`, `missing_metrics`, `sources` (accession numbers) and `notes`. Field reference:
   - Lines: `revenue, cost_of_revenue, gross_profit, rnd, sga, operating_income, interest_expense, pretax_income, income_tax, net_income, eps_diluted, shares_diluted, da, sbc, operating_cash_flow, capex, acquisitions, buybacks, dividends_paid`, and balance sheet items `cash, short_term_investments, receivables, inventory, current_assets, ppe_net, goodwill, total_assets, accounts_payable, current_liabilities, long_term_debt, short_term_debt, total_liabilities, retained_earnings, equity, shares_outstanding`.
   - Computed: `fcf` (OCF − capex), `fcf_after_sbc`, `ebitda` (EBIT + D&A), `total_debt`, `net_debt`, `*_margin_pct`, `rnd_pct_rev`, `sbc_pct_rev`, `capex_pct_rev`, `cash_conversion` (FCF/NI), `tax_rate_pct`, `current_ratio`, `interest_coverage`, `net_debt_to_ebitda`, `dso`, `dio`, `dpo`, `roe_pct`, `roic_pct`, and growth `*_yoy_pct` for revenue, gross profit, operating income, net income, EPS, FCF and `share_count_yoy_pct`.
   - Quarterly rows annualize returns (×4) and compare growth with the same quarter a year earlier. `derived_quarter: true` means the quarter was computed as FY or YTD minus earlier quarters.

2. **Sanity-check before analyzing.** Look at `missing_metrics` (for example `sga` is missing for companies that don't tag it, so compute opex as gross profit − operating income). Look for tag seams: a sudden jump in one line with no MD&A explanation usually means a tag switch or restatement. Use `python3 ../sec-edgar/scripts/edgar.py facts TICKER` to see `tags_used`, and `edgar.py concept TICKER <Tag>` to inspect a raw series.

3. **Get management's explanation**
   ```bash
   python3 ../sec-edgar/scripts/edgar.py filing-text TICKER --form 10-K --section 7 --max-chars 40000
   python3 ../sec-edgar/scripts/edgar.py filing-text TICKER --form 10-Q --section mdna --max-chars 30000
   ```
   For each big move in your numbers, find the MD&A sentence that explains it (price vs. volume vs. mix vs. FX vs. acquisitions, one-offs, restructuring). Quote briefly and cite. Where MD&A is silent on a large move, say so, because silence is itself a finding.

4. **Optional context.** The latest press release (`edgar.py earnings-release TICKER`) gives non-GAAP reconciliations and segment KPIs. `market.py quote TICKER` gives price if you add valuation context.

5. **Build the analysis** in the order of the framework below, then write the report.

## Analysis framework
Definitions, formulas, benchmarks by business model and common distortions are in [references/ratio-guide.md](references/ratio-guide.md). The core moves are:

**1. Growth quality.** Revenue CAGR (5y and 3y) vs. the last 4 quarters' y/y. Break growth into price, volume, mix, FX and M&A where MD&A allows (if `acquisitions` spend is large, organic growth is lower than reported). Check that gross profit grows at least as fast as revenue; if it doesn't, growth is being bought with price or mix.

**2. Margin structure and bridge.** Gross → operating → net, and FCF margin. Build a bridge for the latest year vs. the prior year in percentage points of revenue: gross margin change, R&D % change, SG&A % change (or other opex), giving the operating margin change. Then tax and below-the-line items give the net margin. Look for **operating leverage**: incremental operating margin = Δ operating income / Δ revenue. Above the current margin means leverage is working; negative while revenue grows is a red flag.

**3. Returns.** ROIC (NOPAT / average invested capital) vs. a ~8–10% cost of capital. The spread and its trend matter more than the level. DuPont the ROE: net margin × asset turnover × equity multiplier. ROE driven by leverage or buybacks shrinking equity is lower quality than ROE driven by margin. If equity is negative (heavy buybacks), ROE is meaningless (`roe_pct` is null), so use ROIC or return on tangible assets.

**4. Cash conversion.** `cash_conversion` (FCF/NI) above 1.0 is healthy for asset-light firms. Persistently below 0.8 needs an explanation (growth capex, working capital build, or accruals). Separate maintenance from growth capex: maintenance ≈ D&A as a first proxy. Use FCF after SBC when SBC is material. Compare OCF growth with net income growth across 3+ years.

**5. Capital intensity.** `capex_pct_rev` and capex / D&A. Above 1.5x is investing for growth (or an arms race, as with hyperscaler AI capex). Below 1.0x for long stretches means the asset base is aging and margins may be flattered. Asset turnover (revenue / total assets) trend.

**6. Working capital.** DSO, DIO, DPO and the cash conversion cycle (DSO + DIO − DPO). Rising DSO faster than revenue growth means looser credit or pulled-forward sales. Rising DIO with slowing sales means obsolescence or demand-miss risk. A falling CCC driven only by stretching DPO is borrowed cash that reverses.

**7. Balance sheet and leverage.** Net debt / EBITDA, interest coverage, current ratio, goodwill / total assets, equity trend. Debt here excludes leases. For lease-heavy retailers and airlines, add operating lease liabilities from the 10-K (grep "operating lease liabilit").

**8. SBC and dilution.** `sbc_pct_rev` (above 10% is heavy and above 20% is a business model question), `share_count_yoy_pct` (net of buybacks), and buybacks / SBC (how much cash just offsets dilution). "Adjusted" margins that exclude SBC overstate economics by exactly this amount.

**9. Quarterly trajectory.** Lay out 8 quarters of y/y revenue growth, gross margin and operating margin. Acceleration means y/y growth rising for 2+ quarters; deceleration means 2+ falling. Use 2-year stacked growth (sum of this year's and last year's y/y for the same quarter) to strip easy or hard comparisons. Note sequential seasonality: compare a quarter only with the same quarter.

**10. What changed and why.** For the 3–5 biggest changes, give the number, management's explanation from MD&A (cited), and your judgment on whether it is durable (structural), cyclical, or one-off. Keep fact and judgment visibly separate.

**Questions to ask:** Is margin expansion from price, mix, scale or cost cuts, and which of those repeats? Is the growth being funded by the balance sheet (rising debt, falling DPO, factoring)? What would FCF look like at maintenance capex? How much of EPS growth is buybacks vs. net income? Did anything get reclassified (segments, opex lines) that breaks comparability?

## Output
Write `/tmp/TICKER-financial-statements.json` per `../sec-edgar/references/report-schema.md`, `"skill": "financial-statements"`.

- **title**: the headline economic fact, e.g. `"Margins *still expanding* at scale"` or `"Growth is *costing more* cash"`.
- **verdict**: `{"label": "Financial profile", "value": "Strong | Solid | Mixed | Weak | Deteriorating", "sub": "e.g. high ROIC, FCF lagging", "tone": "pos|neutral|warn|neg"}`.
- **kpis** (4–6): TTM revenue and y/y, operating margin and its change in bps, ROIC, FCF margin or cash conversion, net debt / EBITDA (or net cash), SBC % of revenue or share-count change.
- **sections** (5–8):
  1. *Growth*: annual table plus a bar chart of revenue with a y/y % line; organic vs. acquired note.
  2. *Margins and the bridge*: margin table, bps bridge table (gross → R&D → SG&A → operating), incremental margin.
  3. *Returns*: ROIC and ROE table with DuPont, ROIC line chart, `scores` bars are optional.
  4. *Cash conversion and capital intensity*: NI vs. OCF vs. FCF vs. FCF after SBC (bar chart), capex / D&A.
  5. *Working capital and balance sheet*: DSO/DIO/DPO/CCC table, leverage and liquidity table, callouts for anything breaching thresholds.
  6. *SBC and dilution*: SBC %, share count trend, buybacks vs. SBC.
  7. *Quarterly trajectory*: 8-quarter table and line chart of y/y growth and operating margin; accelerating or decelerating callout.
  8. *What changed and why*: callouts, each one "Fact (source)" then "Our read (judgment)".
- **sources**: every accession from statements.py `sources`, plus the 10-K and 10-Q MD&A filings used.

```bash
python3 ../sec-edgar/scripts/render_report.py /tmp/TICKER-financial-statements.json --out-dir earnings-desk-reports
```
**In chat** give the verdict, a compact KPI table, 3–5 bullets on what changed and why, one "watch next quarter" item, and the report paths.

## Quality bar & pitfalls
- **Insight over inventory.** Twenty ratios with no story is a failure. Every table should support a stated conclusion.
- **Derived quarters.** Q4 (and quarters derived from YTD cash flows) are computed. Derived EPS is approximate because share counts differ. Flag it.
- **Splits and restatements.** A share-count jump of 10x or 4x is usually a stock split in an unrestated older filing, not dilution (NVDA's FY23 row shows +889%). Restated prior years can differ from originally reported numbers. statements.py takes one value per period, so cite the accession.
- **Tax-rate assumption in ROIC.** NOPAT uses the effective tax rate clamped to 0–35%, and falls back to 21% when the rate is missing or zero. Net-cash companies get a small invested capital and therefore very high ROIC. Say so.
- **Fiscal calendars.** Label periods by end date or company fiscal label.
- **Business-model fit.** Gross margin, DIO and capex ratios mean different things for software, retailers and utilities. Banks and insurers need different metrics entirely (NIM, efficiency ratio, CET1, combined ratio), so say so instead of printing nonsense.
- **M&A distorts everything.** Acquisitions inflate growth, add goodwill, and change margins and DSO. Isolate them before concluding.

## Next skills
- `/earnings-desk:forensic-accounting` if conversion, DSO or accruals looked off
- `/earnings-desk:capital-allocation` to see where the cash goes
- `/earnings-desk:kpi-tracker` and `/earnings-desk:guidance-tracker` for operating KPIs and management's track record
- `/earnings-desk:reverse-dcf` or `/earnings-desk:comps-valuation` to put a price on these economics
- `/earnings-desk:moat-analysis` to test whether high returns can last

_Not investment advice. Data is from public filings and may contain errors; verify before acting._
