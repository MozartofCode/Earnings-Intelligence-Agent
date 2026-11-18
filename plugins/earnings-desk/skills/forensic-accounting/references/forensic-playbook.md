# Forensic playbook

The reference behind `forensic-accounting`. It covers each quantitative score (formula, thresholds, interpretation, academic origin, known blind spots) and 25 red flags with where to look in the filings. Scores are screens. A finding needs a screen **plus** corroborating evidence from the filings.

## Contents
1. Beneish M-score
2. Altman Z-score and Z''
3. Piotroski F-score
4. Sloan accrual ratio
5. Working-capital days (DSO, DIO, DPO)
6. Supporting metrics (cash conversion, SBC burden, non-GAAP gap)
7. 25 red flags and where to look
8. Where things live in a 10-K
9. EDGAR event checklist
10. Writing up findings

---

## 1. Beneish M-score (8-variable)
**Origin:** Messod D. Beneish, "The Detection of Earnings Manipulation", *Financial Analysts Journal* (1999). Estimated on firms subject to SEC enforcement for earnings manipulation (1982–1992) against matched controls. Cornell MBA students famously used it to flag Enron in 1998.

**Formula** (t = latest fiscal year, t−1 = prior):

| Index | Formula | What it captures | Manipulator mean | Non-manipulator mean |
|---|---|---|---|---|
| DSRI | (AR_t / Sales_t) / (AR_t−1 / Sales_t−1) | Receivables outgrowing sales (revenue inflation) | 1.465 | 1.031 |
| GMI | GM_t−1 / GM_t | Gross margin deterioration (pressure to manipulate) | 1.193 | 1.014 |
| AQI | (1 − (CA_t + PPE_t) / TA_t) / same for t−1 | Growth in "soft" non-current assets (capitalized costs) | 1.254 | 1.039 |
| SGI | Sales_t / Sales_t−1 | Growth (pressure and capital-market incentives) | 1.607 | 1.134 |
| DEPI | Dep rate_t−1 / Dep rate_t, where rate = Dep / (Dep + PPE) | Slowing depreciation (lengthened useful lives) | 1.077 | 1.001 |
| SGAI | (SGA_t / Sales_t) / (SGA_t−1 / Sales_t−1) | SG&A efficiency falling | 1.041 | 1.054 |
| LVGI | Leverage_t / Leverage_t−1, where leverage = (CL + LTD) / TA | Rising leverage (debt-covenant incentives) | 1.111 | 1.037 |
| TATA | (Net income − CFO) / TA_t | Accruals (earnings not backed by cash) | 0.031 | 0.018 |

M = −4.84 + 0.920·DSRI + 0.528·GMI + 0.404·AQI + 0.892·SGI + 0.115·DEPI − 0.172·SGAI + 4.679·TATA − 0.327·LVGI

**Thresholds:** scores.py uses −1.78, the cut-off from Beneish's original 8-variable model. Many practitioners quote −2.22 as a more conservative cut-off (it comes from later work and the 5-variable version). Treat −2.22 to −1.78 as grey.

**Implementation notes (scores.py):**
- Depreciation is proxied by `da` (D&A), not pure depreciation.
- DEPI and SGAI default to 1.0 when inputs are missing, and are listed in `defaulted_to_1`. LVGI defaults to 1.0 if prior leverage can't be computed.
- TATA uses net income rather than income from continuing operations.

**Interpretation:**
- DSRI, AQI, DEPI and TATA are the manipulation-type drivers. SGI, GMI and LVGI are pressure-type drivers. A score driven by SGI alone describes a growth company, not a manipulator.
- Always run the sensitivity: recompute with SGI = 1.0, i.e. subtract 0.892 × (SGI − 1). If the score drops below −1.78, growth explains the flag. For example, a score of −1.20 with SGI 1.60 becomes about −1.74: still elevated, so the remaining drivers (often AQI and TATA) need explaining.
- **Blind spots:** acquisitions (AQI, DSRI and SGI all jump), hyper-growth, business-model shifts (hardware to subscription), years with large one-offs. Not for financial firms.

## 2. Altman Z-score and Z''
**Origin:** Edward I. Altman, "Financial Ratios, Discriminant Analysis and the Prediction of Corporate Bankruptcy", *Journal of Finance* (1968), built on 66 US manufacturers. Z'' comes from later Altman work (1983, revised for emerging markets in 1995) for non-manufacturers. It drops the sales/assets term, which varies widely by industry.

**Original Z (public manufacturers):** Z = 1.2·X1 + 1.4·X2 + 3.3·X3 + 0.6·X4 + 1.0·X5
- X1 = working capital / total assets (liquidity)
- X2 = retained earnings / total assets (cumulative profitability and age)
- X3 = EBIT / total assets (operating productivity; scores.py uses operating income)
- X4 = market value of equity / total liabilities (market cushion)
- X5 = sales / total assets (asset turnover)
- Zones: above 2.99 safe, 1.81–2.99 grey, below 1.81 distress.

**Z'' (non-manufacturers):** Z'' = 6.56·X1 + 3.26·X2 + 6.72·X3 + 1.05·X4', where X4' = book equity / total liabilities.
- Zones: above 2.6 safe, 1.1–2.6 grey, below 1.1 distress. The emerging-market version adds +3.25; scores.py does not.

**Interpretation:**
- Works best 1–2 years before distress, for industrials.
- Weak for asset-light, high-buyback firms. Buybacks charged against retained earnings, or negative equity, push X2 and X4' down for healthy companies.
- X4 dominates for richly valued firms (NVDA: X4 = 89, original Z = 58), so a "safe" original Z can hide a deteriorating business. Prefer Z'' for non-manufacturers, as scores.py's `preferred` field does.
- Not for banks, insurers, REITs or utilities.

## 3. Piotroski F-score
**Origin:** Joseph D. Piotroski, "Value Investing: The Use of Historical Financial Statement Information to Separate Winners from Losers", *Journal of Accounting Research* (2000). It was designed to separate winners from losers among high book-to-market (value) stocks.

**Nine binary signals** (1 = pass):
- Profitability: (1) ROA > 0; (2) CFO > 0; (3) ROA up y/y; (4) CFO > net income (accrual quality).
- Leverage and liquidity: (5) long-term debt / assets down; (6) current ratio up; (7) no new shares issued.
- Efficiency: (8) gross margin up; (9) asset turnover up.

**Zones:** the paper uses 8–9 as strong and 0–1 as weak. scores.py uses 7+ strong, 4–6 neutral and 3 or below weak.

**Implementation notes:**
- ROA uses prior-year total assets, not a beginning-of-year average.
- "ROA improving" compares with prior NI / prior assets (the same denominator), which is an approximation.
- "No dilution" tolerates +0.5% growth in diluted shares.
- "Leverage falling" passes when both years have no long-term debt.
- Missing data counts as a fail.

**Interpretation:** a low F-score is expected for growth stocks, which dilute and see the current ratio fall as cash is deployed. The score is most useful as a deterioration signal in mature, cheap companies. Read which checks failed, not just the sum.

## 4. Sloan accrual ratio
**Origin:** Richard G. Sloan, "Do Stock Prices Fully Reflect Information in Accruals and Cash Flows about Future Earnings?", *The Accounting Review* (1996). It showed that the accrual component of earnings is less persistent than the cash component and that investors overweight it, which became known as the "accrual anomaly".

**Formula (scores.py, cash-flow version):** (Net income − CFO) / average total assets.

**Zones:** above 10% warning, 5–10% watch, 0–5% normal, below 0 clean (cash exceeds earnings).

**Interpretation:**
- Persistently high accruals predict earnings declines and underperformance.
- Benign causes include rapid growth funded by working capital, an acquisition year, or a large tax receivable.
- Look at several years. One year above 10% during hyper-growth (when a working-capital build explains it) is less worrying than three years in a row in a flat business.
- Cross-check by hand with the balance-sheet version: (Δ non-cash working capital − D&A) / average assets.

## 5. Working-capital days
- DSO = receivables / revenue × 365. DIO = inventory / COGS × 365. DPO = payables / COGS × 365. All use period-end balances.
- **Flags (scores.py `quick_flags`):** DSO or DIO up more than 20% between the first and last year in `working_capital_trend`.
- **Interpretation:**
  - DSO rising while revenue accelerates at quarter end suggests pull-forward or channel stuffing.
  - DIO rising while sales slow suggests obsolescence and margin risk (future write-downs).
  - DPO rising sharply may mean supply-chain financing or cash stress.
- Compare with peers. A semis company with 120 days of DIO can be normal; a retailer with 120 days would be alarming.

## 6. Supporting metrics
- **Cash conversion** (FCF / NI): scores.py flags anything below 0.8. Use 3-year sums to smooth timing.
- **SBC burden** (SBC / revenue): scores.py flags anything above 10%. Adjusted margins that add back SBC overstate owner economics.
- **Non-GAAP gap:** (Adjusted EPS − GAAP EPS) / |GAAP EPS|, tracked quarterly. Red flags:
  - the gap growing faster than revenue
  - "one-time" items every quarter
  - new add-back categories (for example "AI transformation costs")
  - changed definitions
  - adjusted metrics used to set executive pay
- **Non-cash earnings share:** (net income − OCF) / net income, the portion of reported profit that is accrual.

## 7. 25 red flags and where to look

| # | Red flag | What it looks like | Where to look |
|---|---|---|---|
| 1 | Receivables outgrowing revenue | DSO up 15%+ y/y; DSRI above 1.2 | Balance sheet, `statements.py` dso, MD&A liquidity |
| 2 | Unbilled receivables or contract assets rising | Revenue recognized ahead of billing | Revenue note ("contract assets", "unbilled"), balance sheet |
| 3 | Revenue recognition policy change | New wording on timing, principal vs. agent, variable consideration | Significant accounting policies note; `filing-diff --section "Critical Accounting"` |
| 4 | Bill-and-hold or extended terms | Sales recognized before shipment; longer payment terms | Revenue note, MD&A; grep "bill-and-hold", "extended payment" |
| 5 | Channel stuffing | Distributor inventory up, end-of-quarter revenue spikes, rising returns or rebate reserves | MD&A, Schedule II (valuation and qualifying accounts), distributor disclosures |
| 6 | Inventory build | DIO up while sales slow; reserves falling as % of inventory | Inventory note (raw materials, WIP, finished goods), Schedule II |
| 7 | Reserve releases | Allowance, warranty or returns reserves falling as % of base while EPS beats | Schedule II, allowance roll-forward, warranty note |
| 8 | Capitalizing operating costs | Rising capitalized software, contract or customer-acquisition costs; AQI above 1.2 | Intangibles note, "capitalized software", investing cash flows |
| 9 | Useful-life extensions | D&A falling as % of PPE; DEPI above 1 | PPE note; grep "change in estimate", "useful life" |
| 10 | Big-bath or recurring restructuring | "One-time" charges every year; reserves later reversed | Restructuring note roll-forward, non-GAAP reconciliations |
| 11 | Non-GAAP creep | Gap to GAAP widening; new add-backs | 8-K Ex. 99.1 reconciliation (`edgar.py earnings-release`) |
| 12 | Gross vs. net revenue shift | Revenue jumps while gross margin falls (or the reverse) | Revenue note, principal vs. agent policy |
| 13 | Auditor change | 8-K Item 4.01, especially a resignation or reported disagreements | `edgar.py filings --forms 8-K` items; the 8-K text and the auditor's Ex. 16 letter |
| 14 | Non-reliance or restatement | 8-K Item 4.02; 10-K/A with restated statements | 8-K items, amended filings |
| 15 | Material weakness or ineffective ICFR | "not effective" in Item 9A; adverse auditor ICFR opinion | Item 9A, auditor's report |
| 16 | Critical audit matters on judgmental areas | CAMs on revenue, reserves, goodwill, capitalized costs | Auditor's report at the start of Item 8 |
| 17 | Late filing | NT 10-K or NT 10-Q | `edgar.py filings --forms "NT 10-K,NT 10-Q"` |
| 18 | CFO, CAO or controller turnover | Departures near reporting dates | 8-K Item 5.02, proxy |
| 19 | Related-party transactions | Revenue from, leases from or loans to insiders or affiliates | Related-party note; DEF 14A "Certain Relationships and Related Transactions" |
| 20 | Segment re-casting | Segments merged or redefined as one weakens; KPI definitions changed | Segment note y/y; `filing-diff` on Item 1 and MD&A |
| 21 | Off-balance-sheet obligations | VIEs, guarantees, purchase commitments, unconsolidated JV debt | Commitments and contingencies note, VIE note, MD&A contractual obligations |
| 22 | Supplier finance and factoring | DPO up, or OCF flattered by financing | Supplier-finance program note (required since 2023); grep "factoring", "sale of receivables" |
| 23 | OCF from working-capital release or reclassification | OCF up while NI is flat; items moved between CFO and CFI | Cash flow statement line items y/y, changes in presentation |
| 24 | Avoided goodwill impairment | Market cap below book; weakening segment with no impairment; goodwill above 40% of assets | Goodwill note (reporting units, headroom), CAMs; `edgar.py concept TICKER GoodwillImpairmentLoss` |
| 25 | Pay tied to manipulable metrics, plus insider selling | Bonus on adjusted EPS or revenue just above target; heavy discretionary sales | DEF 14A CD&A; `edgar.py insiders` |

Also worth checking:
- pension assumption changes (discount rate, expected return on assets)
- tax-rate drops from uncertain tax positions
- equity-method income, which brings no cash
- investment gains booked in operating income
- frequent "other income" items

## 8. Where things live in a 10-K
- **Item 1** Business: segments, customers, concentration.
- **Item 1A** Risk factors: new risks (use `filing-diff`).
- **Item 3** Legal proceedings: often refers to the contingencies note.
- **Item 7** MD&A: critical accounting estimates, liquidity, non-GAAP discussion.
- **Item 8** Financial statements:
  - The auditor's report with CAMs comes first, then the statements.
  - The notes follow: accounting policies, revenue, receivables and allowances, inventory, PPE, goodwill and intangibles, debt, leases, commitments and contingencies, related parties, segments, subsequent events.
  - Schedule II (valuation and qualifying accounts) usually sits in Item 15.
- **Item 9** Changes in and disagreements with accountants.
- **Item 9A** Controls and procedures: the ICFR conclusion, material weaknesses, remediation.
- **Item 14** Principal accountant fees (often incorporated from the proxy). Non-audit fees that are large relative to audit fees can compromise independence.

## 9. EDGAR event checklist
```bash
python3 ../sec-edgar/scripts/edgar.py filings TICKER --forms 8-K,8-K/A --limit 200    # items: 4.01, 4.02, 5.02, 2.06
python3 ../sec-edgar/scripts/edgar.py filings TICKER --forms "NT 10-K,NT 10-Q,10-K/A,10-Q/A" --limit 20
python3 ../sec-edgar/scripts/edgar.py concept TICKER GoodwillImpairmentLoss
```
Relevant 8-K items:
- 1.01 material agreement
- 2.01 acquisition or disposition
- 2.02 results of operations
- 2.05 exit costs
- 2.06 material impairment
- 4.01 change in certifying accountant
- 4.02 non-reliance on previously issued financials
- 5.02 officer or director departures
- 7.01 Reg FD
- 8.01 other events

`filings` reads EDGAR's "recent" submissions set (roughly the latest 1,000 filings). For companies with heavy Form 4 traffic that can be only a few years, so state the date window you actually checked. `concept` returns raw companyconcept JSON. Filter it to `form == "10-K"` and `fp == "FY"` rows that carry a `frame` to get one value per year.

## 10. Writing up findings
- Structure each finding as: **Fact** (number or quote, with source) → **Why it matters** → **Benign explanation(s)** → **What would confirm or refute it**.
- Use calibrated language: "consistent with", "warrants scrutiny", "we could not find a benign explanation in the filings". Never write "fraud".
- List the clean checks too. A good forensic report shows what was ruled out.
