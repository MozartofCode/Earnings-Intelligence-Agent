# Scores look scary, the filings mostly don't

**NVDA · NVIDIA Corp** · `/forensic-accounting` · 2026-11-17

_FY26 (year ended Jan 25, 2026) vs FY25 · 10-K filed Feb 25, 2026_

> **Forensic verdict: Watch** (Growth-driven screens · 3 judgment areas)

| Beneish M | Altman Z'' | Piotroski F | Sloan accruals | OCF / net income |
|---|---|---|---|---|
| −1.15 (−1.95 ex growth & goodwill) | 12.9 (safe (> 2.6)) | 5 / 9 (neutral) | 10.9% (warning (> 10%)) | 0.86 (FY26 · 0.88 FY25) |

## The short version

On the raw screens NVDA looks alarming: a Beneish M-score of **−1.15** sits in the "elevated" zone and Sloan accruals are **10.9%**. Decompose them and most of the alarm is **hyper-growth** (sales +65%) plus one accounting event: **$14.4B of goodwill booked on a non-exclusive license-and-hire deal with Groq**. Receivables quality is clean (DSRI 1.01), there are no restatements, auditor changes or late filings, and controls were found effective. The verdict is **Watch, not Red**, driven by three judgment areas: inventory and purchase-commitment provisions (the auditor's only critical audit matter, $7.2B of provisions in FY26), the Groq goodwill, and **$27B of multi-year cloud commitments**.

## Scorecard

- Beneish M (−1.15; risk above −1.78): **−1.15 elevated**
- Altman Z'' (12.9; distress below 1.1): **12.9 safe**
- Piotroski F (5/9): **5 neutral**
- Sloan accrual ratio: **10.9% warning**
- DIO drift (FY25 → FY26): **113 → 125 days**

**Qualitative checklist**

| Item | Status | Evidence | Source |
|---|---|---|---|
| Revenue recognition | Clean | Receivables +67% vs revenue +65% (DSRI 1.01); DSO flat at ~65 days | XBRL via scores.py |
| Reserves & provisions | Watch | Inventory + purchase-obligation provisions $7.2B (FY25 $3.7B), incl. $4.5B H20 charge; net GM impact −2.6 pts. Sole CAM | 10-K MD&A; auditor's report |
| Capitalization / M&A | Watch | Groq non-exclusive license + hires recorded as a business combination: $14.4B goodwill + $2.5B intangible; no equity or customers acquired | 10-K Note on business combination |
| Off-balance commitments | Watch | $27B multi-year cloud service commitments through FY32; capacity purchase obligations and possible financial guarantees disclosed as a risk | 10-K commitments note; Item 1A |
| Auditor | Clean | PwC since 2004; unqualified ICFR opinion | 10-K Item 8 / 9A |
| Restatements & controls | Clean | No 8-K 4.01/4.02 in 62 8-Ks (Nov 2020–Nov 2026); no 10-K/A, 10-Q/A or NT filings | EDGAR filing index |
| Dilution & SBC | Clean | SBC 3.0% of revenue (10.0% in FY23); diluted shares −1.2% y/y | XBRL |
| Management turnover | Not reviewed | 16 8-Ks with Item 5.02 since 2020; not reviewed individually in this run | EDGAR filing index |

## Beneish decomposition

- **Known false positive: growth**: SGI carries a 0.892 weight. With SGI set to 1.0 the score is **−1.74**, right at the line.
- **Then strip the Groq goodwill**: Also setting AQI to 1.0 gives **−1.95**, inside the low-risk zone. What remains is **TATA**, which the accruals section below examines.

| Component | Value | Concern above | Read |
|---|---|---|---|
| DSRI (receivables vs sales) | 1.01 | 1.20 | Clean |
| GMI (gross margin decline) | 1.06 | 1.10 | Mild: Blackwell mix + H20 charge |
| AQI (asset quality) | 1.52 | 1.20 | Groq goodwill/intangible |
| SGI (sales growth) | 1.66 | pressure only | Hyper-growth |
| DEPI (depreciation) | 1.06 | 1.10 | Clean |
| SGAI (SG&A vs sales) | 0.79 | 1.10 | Clean |
| LVGI (leverage) | 0.81 | 1.10 | Clean |
| TATA (accruals / assets) | 0.084 | 0.031 | NI ahead of OCF |

_Recomputations are estimates from the published Beneish weights applied to scores.py components._

## Distress and strength

**Altman (original Z = 50.1 is distorted by market cap: X4 = 75.7; Z'' is the fairer read)**

| Component | Value |
|---|---|
| X1 working capital / assets | 0.45 |
| X2 retained earnings / assets | 0.71 |
| X3 EBIT / assets | 0.63 |
| X4 market value / liabilities | 75.7 |
| X5 sales / assets | 1.04 |
| Z'' (non-manufacturer form) | 12.85 · safe |

**Piotroski F = 5**

| Check | Result |
|---|---|
| ROA > 0 | Pass |
| CFO > 0 | Pass |
| ROA improving | Pass |
| CFO > net income | Fail |
| Leverage falling | Pass |
| Current ratio rising | Fail |
| No dilution | Pass |
| Gross margin rising | Fail |
| Asset turnover rising | Fail |

Piotroski was built for cheap value stocks. Three of NVDA's four fails (gross margin, asset turnover, current ratio) are typical of a company at peak margins scaling its balance sheet. The fourth, **CFO < net income**, is the same signal as TATA and Sloan.

## Accruals and working capital

Net income has run **ahead of operating cash flow for three straight years** ($17.4B gap in FY26). Where that gap comes from matters: **inventory doubled to $21.4B** (+112% vs cost of revenue +91%) and payables days fell, so working capital absorbed cash as the Blackwell ramp built ahead of demand. Receivables are *not* the issue. This is a real but explainable accrual pattern for a company in a hyper-growth build cycle. It becomes a red flag only if inventory keeps outgrowing cost of revenue once growth slows.

| Fiscal year | DSO | DIO | DPO | FCF / NI | SBC % rev |
|---|---|---|---|---|---|
| FY22 | 63 | 101 | 69 | 0.83 | 7.5% |
| FY23 | 52 | 162 | 37 | 0.87 | 10.0% |
| FY24 | 60 | 116 | 59 | 0.91 | 5.8% |
| FY25 | 65 | 113 | 71 | 0.83 | 3.6% |
| FY26 | 65 | 125 | 57 | 0.81 | 3.0% |

_Chart: Net income vs operating cash flow ($B) (see HTML report)_

## Filing evidence

- **Critical audit matter: inventory provisions**: PwC's only CAM covers provisions for excess or obsolete inventory and excess purchase commitments, citing *significant judgment* on future demand and export restrictions. FY26 provisions were **$7.2B** (incl. the $4.5B H20 charge) vs $3.7B in FY25.
- **Groq: a license booked as goodwill**: In December 2025 NVIDIA signed a **non-exclusive** license for Groq's LPU technology and hired certain Groq employees. *No customer contracts, existing products, or equity interests were purchased*, yet it recorded **$14.4B of goodwill** and a $2.5B intangible. Goodwill is not amortized, so this choice keeps the cost off future income statements unless it is impaired.
- **$27B of cloud commitments**: Multi-year cloud service agreements ($7B due in FY27, tapering through FY32) to support R&D, plus disclosed capacity purchase obligations and requests to finance partners' datacenter buildouts. Watch for any circularity between capacity NVIDIA buys and revenue it books from the same partners.
- **Clean on the hard red flags**: No auditor change, no restatement (8-K 4.02), no 10-K/A or 10-Q/A, no late filings, and an unqualified opinion on internal control as of Jan 25, 2026.

## Non-GAAP gap

This example run did not tabulate the GAAP-to-non-GAAP reconciliation from the last 4–8 earnings releases (workflow step 5). With SBC at just 3.0% of revenue, the gap is likely modest, but **verify it** before relying on adjusted EPS: `edgar.py earnings-release NVDA --index 0` through `--index 7`.

## What would change our mind

- **Upgrade to Clean**: OCF catches up with net income (OCF/NI ≥ 1.0) as Blackwell inventory sells through, and DIO returns below ~110 days.
- **Downgrade to Red**: Inventory keeps outgrowing cost of revenue while revenue growth slows; DSO starts rising; large provision *releases* boost gross margin; or any impairment, restatement or auditor change around the Groq accounting.

**Next:** `filing-diff NVDA --section 1A` to see how the export-control and supply language evolved, `insider-ownership` for selling into the numbers, and `capital-allocation` to judge the Groq deal and buybacks.

## Sources

1. [NVIDIA 10-K for FY ended 2026-01-25, filed 2026-02-25 (accn 0001045810-26-000021): MD&A, auditor's report, business combination and commitments notes](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001045810&type=10-K)
2. [SEC XBRL company facts for scores and multi-year statements (scores.py, statements.py)](https://data.sec.gov/api/xbrl/companyfacts/CIK0001045810.json)
3. [EDGAR filing index: 62 8-Ks Nov 2020–Nov 2026; no NT, 10-K/A or 10-Q/A filings](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001045810&type=8-K)
4. Price and market cap: Yahoo Finance public chart endpoint via market.py (unofficial, best-effort) × SEC-reported shares outstanding, retrieved 2026-11-17
5. Beneish (1999), Altman (1968; Z'' 1995), Piotroski (2000), Sloan (1996) per the skill's forensic playbook


---
_Not investment advice. Generated by AI from public data; verify before acting._
