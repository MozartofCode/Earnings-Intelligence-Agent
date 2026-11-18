# Ratio guide

Definitions, the exact formula `statements.py` uses (where it computes the ratio), what good and bad look like by business model, and the distortions that fool people. Benchmarks are rules of thumb for US large caps, not laws. The trend and the comparison with direct peers beat any absolute threshold.

## Contents
1. Growth
2. Margins
3. Returns
4. Cash flow and conversion
5. Capital intensity
6. Working capital
7. Leverage and liquidity
8. SBC and dilution
9. Per-share and quality checks
10. Benchmarks by business model
11. Common distortions
12. Sector-specific metrics (when the standard set doesn't apply)

---

## 1. Growth

| Metric | Formula | Notes |
|---|---|---|
| Revenue y/y | `revenue / revenue_{t-1} − 1` (`revenue_yoy_pct`) | Quarterly rows compare with the same quarter last year |
| CAGR | `(end / start)^(1/years) − 1` | Use 3y and 5y; for cyclicals use peak-to-peak or trough-to-trough |
| 2-year stack | `yoy_t + yoy_{t−4q}` | Strips easy and hard comparisons. A rising stack means real acceleration |
| Organic growth | Reported − acquired − FX | From MD&A. Acquired revenue = target's revenue post-close for the first 12 months |
| Incremental margin | `Δ operating income / Δ revenue` | Above the current margin = operating leverage; negative while growing = alarm |

**Good:** gross profit growing ≥ revenue, OCF growing ≈ net income, growth mostly organic.
**Bad:** revenue up with gross profit flat (price cuts or mix shift), growth only from M&A, a re-accelerating headline with a decelerating 2-year stack.

## 2. Margins

| Metric | Formula (`statements.py` field) |
|---|---|
| Gross margin | `gross_profit / revenue` (`gross_margin_pct`); gross profit = revenue − cost of revenue when not tagged |
| Operating margin | `operating_income / revenue` (`operating_margin_pct`) |
| Net margin | `net_income / revenue` (`net_margin_pct`) |
| FCF margin | `(OCF − capex) / revenue` (`fcf_margin_pct`) |
| EBITDA margin | `(operating_income + D&A) / revenue` |
| R&D intensity | `rnd / revenue` (`rnd_pct_rev`) |
| Effective tax rate | `income_tax / pretax_income` (`tax_rate_pct`) |

**Margin bridge (in bps of revenue):** Δ gross margin − Δ (R&D % rev) − Δ (SG&A % rev) − Δ (other opex % rev) = Δ operating margin. Then Δ interest and other, Δ tax gives Δ net margin. State the top two drivers.

**Distortions:** cost classification differs between companies (some put fulfillment or depreciation in COGS, others in opex), restructuring charges inside operating income, gains on asset sales or equity investments in net income (check `net_income` vs. `operating_income` gaps), tax-rate swings from one-off benefits.

## 3. Returns

| Metric | Formula used | Notes |
|---|---|---|
| ROIC | `NOPAT × periods_per_year / avg(equity + total_debt − cash − ST investments)`; NOPAT = operating income × (1 − tax rate clamped 0–35%, 21% fallback) | Null if average invested capital ≤ 0 |
| ROE | `net_income × periods_per_year / avg(equity)` | Null if average equity ≤ 0 |
| ROA | `net_income / total_assets` | Compute by hand. Best for banks |
| DuPont | ROE = net margin × asset turnover (revenue / assets) × equity multiplier (assets / equity) | Shows whether ROE is margin, efficiency or leverage |
| ROIC − WACC spread | ROIC − ~8–10% | Value is created only when the spread is positive. Its trend matters more than its level |
| Incremental ROIC | `Δ NOPAT / Δ invested capital` over 3–5 years | Tells you what new investment earns, which matters for growth value |

**Good:** ROIC above 15% that is stable or rising; incremental ROIC ≥ average ROIC.
**Bad:** ROIC below WACC for 3+ years; ROE high only because buybacks shrank equity.
**Distortions:** goodwill from M&A inflates invested capital (compute ROIC ex-goodwill to see the organic business); net-cash firms get tiny or negative invested capital (huge or null ROIC); operating leases excluded from debt understate capital for retailers and airlines; R&D expensed rather than capitalized understates invested capital for software and pharma (ROIC looks higher than economic reality).

## 4. Cash flow and conversion

| Metric | Formula |
|---|---|
| FCF | `operating_cash_flow − capex` (`fcf`) |
| FCF after SBC | `fcf − sbc` (`fcf_after_sbc`) |
| Cash conversion | `fcf / net_income` (`cash_conversion`) |
| OCF / net income | compute by hand. Above 1 is normal for firms with D&A and SBC |
| Accruals (balance-sheet-free) | `(net_income − OCF) / avg total assets`, i.e. the Sloan ratio (see `forensic-accounting`) |

**Good:** FCF/NI ≥ 1.0 for asset-light firms and ≥ 0.8 for capital-intensive firms over a cycle.
**Bad:** persistently below 0.8 without a growth-capex explanation; OCF flattered by working capital release (falling inventory and receivables during a downturn is temporary), supplier finance programs, receivable factoring, or by classifying capitalized software or content outside capex.
**Watch:** some companies put customer-financing, capitalized software or content spending in investing or "other" lines. Read the cash flow statement, not just the tags.

## 5. Capital intensity

| Metric | Formula | Read |
|---|---|---|
| Capex % revenue | `capex / revenue` (`capex_pct_rev`) | Software 2–6%, semis fabless 2–5%, retail 2–4%, telecom and utilities 15–30%, hyperscaler cloud 25%+ |
| Capex / D&A | `capex / da` | Above 1.5 = growth or arms race; below 1.0 for years = underinvestment |
| Maintenance capex | ≈ D&A (first proxy); better from management commentary | FCF at maintenance capex = OCF − D&A |
| Asset turnover | `revenue / total_assets` | Falling turnover with rising capex = returns at risk |

## 6. Working capital

| Metric | Formula used (annual rows; quarterly uses 91.25-day periods) |
|---|---|
| DSO | `receivables / revenue × 365` (`dso`), period-end balances |
| DIO | `inventory / COGS × 365` (`dio`) |
| DPO | `accounts_payable / COGS × 365` (`dpo`) |
| Cash conversion cycle | DSO + DIO − DPO |

Period-end balances, not averages. Seasonality makes quarterly DSO noisy, so compare the same quarter y/y.
**Good:** stable or falling DSO and DIO, a CCC that is stable or improving through operations.
**Bad:** DSO rising faster than revenue (channel stuffing, extended terms, collection problems), DIO rising while sales slow (excess inventory, write-down risk), CCC improvement purely from stretching DPO (reverses, and suppliers may be financing you through supply-chain finance).
**Note:** for software, DPO and DIO are mostly meaningless. Watch deferred revenue and RPO instead (they are not in statements.py, so grep the 10-K for "remaining performance obligations").

## 7. Leverage and liquidity

| Metric | Formula used | Thresholds (non-financials) |
|---|---|---|
| Total debt | `long_term_debt + short_term_debt` (excludes leases) | |
| Net debt | `total_debt − cash − short_term_investments` | Negative = net cash |
| Net debt / EBITDA | `net_debt / (ebitda × periods_per_year)` | Below 1x conservative, 1–3x normal, 3–5x levered, above 5x stressed |
| Interest coverage | `operating_income / interest_expense` | Above 8x comfortable, 3–8x okay, below 3x concerning, below 1.5x distress |
| Current ratio | `current_assets / current_liabilities` | Below 1.0 fine for retailers or subscription firms with deferred revenue; concerning for industrials |
| Goodwill / assets | `goodwill / total_assets` | Above 40% = acquisition-built, so test for impairment risk |

**Distortions:** leases (add operating lease liabilities for retail, airlines, restaurants), pension deficits, preferred stock and minority interest, cash trapped overseas or held as customer funds (payments companies), and the `interest_expense` tag sometimes being net of interest income.

## 8. SBC and dilution

| Metric | Formula | Read |
|---|---|---|
| SBC % revenue | `sbc / revenue` (`sbc_pct_rev`) | Below 3% light; 3–10% normal for tech; above 10% heavy; above 20% means adjusted profits are largely an accounting choice |
| Net dilution | `share_count_yoy_pct` (diluted weighted average) | Below 0 = buybacks exceed issuance |
| Buybacks / SBC | `buybacks / sbc` | Close to 1 means buybacks just offset dilution and are not returning capital |
| SBC % of FCF | `sbc / fcf` | Above 30%: FCF overstates owner earnings |

## 9. Per-share and quality checks
- EPS growth − net income growth ≈ buyback contribution.
- Diluted vs. basic shares gap: a widening gap means more options or RSUs in the money.
- Tax rate: a sharp drop that boosts EPS is low quality unless it is structural.
- Below-the-line items: interest income on a large cash pile can be 10%+ of pretax income when rates are high, and it is not operating performance.

## 10. Benchmarks by business model (rough ranges for healthy firms)

| Model | Gross margin | Op. margin | FCF margin | ROIC | Capex % rev | Key extra metrics |
|---|---|---|---|---|---|---|
| Mature software / SaaS | 75–85% | 25–45% | 25–40% | 20%+ (ex-goodwill) | 2–6% | NRR, RPO, Rule of 40 (growth % + FCF margin %) |
| High-growth SaaS | 70–80% | negative to 10% | 0–20% | n/m | 2–6% | Rule of 40, CAC payback, SBC % |
| Fabless semis | 55–75% | 25–60% | 20–45% | 20–50%+ | 2–5% | Inventory days, customer concentration |
| Integrated semis / foundry | 40–60% | 20–40% | volatile | 10–25% | 20–45% | Utilization, capex cycle |
| Consumer staples | 35–55% | 15–25% | 10–18% | 12–25% | 3–5% | Organic growth = price + volume/mix |
| Retail (general) | 25–40% | 4–10% | 3–7% | 10–20% | 2–4% | Comps, inventory turns, sales per sq ft |
| Industrials | 25–40% | 10–20% | 8–15% | 10–20% | 2–5% | Backlog, book-to-bill, incremental margin |
| Marketplaces / payments | 40–80% | 15–45% | 15–35% | high | 1–5% | Take rate, GMV or TPV |
| Telecom / utilities | 40–60% | 15–30% | 0–15% | 5–8% | 15–30% | Regulated rate base, payout ratio |
| Pharma (big) | 65–80% | 25–40% | 20–35% | 15–30% | 3–6% | Patent cliffs, pipeline |

## 11. Common distortions (check before concluding)
1. **Acquisitions:** inflate growth; add goodwill and amortization; reset margins and DSO. Isolate them.
2. **Divestitures and discontinued operations:** prior years may be restated. Compare like with like.
3. **Stock splits:** unrestated older filings make share counts and EPS jump by the split ratio.
4. **Tag switches in XBRL:** a metric can change concept (for example `Revenues` → `RevenueFromContractWithCustomer...`), so check `tags_used` at the seam.
5. **Derived quarters:** Q4 = FY − 9-month YTD, so it absorbs year-end adjustments (true-ups, impairments, audit adjustments).
6. **53-week years:** retailers and some semis add an extra week every 5–6 years (+~2% revenue in that year).
7. **FX:** large swings in reported growth for multinationals. Use constant-currency figures from MD&A.
8. **One-offs:** restructuring, litigation, impairments, gains on investments, tax benefits. Show "as reported" and "ex-items" separately, and label the latter as an adjustment.
9. **Accounting changes:** ASC 606 (2018), ASC 842 leases (2019), capitalized R&D for tax (Section 174 from 2022) affecting cash taxes.
10. **Interest income in a high-rate world:** inflates net income for cash-rich companies versus operating reality.
11. **Supply-chain finance and factoring:** flatter OCF and DPO. Grep "supplier finance" (disclosure required since 2023) and "factoring".

## 12. Sector-specific metrics (when the standard set doesn't apply)
- **Banks:** NIM, efficiency ratio (noninterest expense / revenue, below 60% is good), provision / average loans, NCO rate, CET1 ratio, loan / deposit ratio, ROTCE, P/TBV.
- **Insurers:** combined ratio (below 100% = underwriting profit), reserve development (favorable or adverse prior-year development), investment yield, book value per share growth.
- **REITs:** FFO and AFFO per share, occupancy, same-store NOI growth, debt / EBITDAre, payout of AFFO.
- **E&P / commodities:** production growth, realized price vs. benchmark, finding and development costs, reserve life, breakeven price; ratios swing with the commodity, so judge through the cycle.
