# Forensics memo · MSFT · 2026-11-17
```scorecard
lens: forensics
quality_rating: Watch
beneish_m: -2.64 (corrected for SGAI 0.90; low risk; largest driver SGI 1.18 = real growth; TATA -0.065)
altman: Z'' = 4.59 (safe)
piotroski: 6
accruals_sloan: -7.1%
cash_conversion_5y: CFO/NI 1.31x (FCF/NI 0.72x; FY26 0.50x)
top_flag: Reported FCF ($67.0B FY26) leaves out $24.6B of finance-lease capacity and $19.9B of server-component cash outlays. On that basis FY26 FCF is about $22.5B (est.).
confidence: Medium
```

## Bottom line
Reported earnings look high quality: clean audit and controls, accruals of -7.1%, receivables in line with revenue, and no extension of server useful lives. The soft spots are cash and commitments. Reported FY26 FCF of $67.0B is about $22.5B (est.) once finance-lease additions and component-procurement outflows are counted, and $364.6B of datacenter leases are signed but not yet on the balance sheet. OpenAI, an equity-method related party, supplied 10.8% of FY27 Q1 revenue.

## Key findings
1. **Capex understates capacity spend (Material).** Besides $115.9B of FY26 capex, Microsoft added $24.6B of finance-lease assets (FY25 $20.5B) and spent $19.9B in investing "Other, net," "primarily to facilitate the purchase of components" (FY25: +$2.3B inflow). Total was about $160.4B (est.). TTM FCF is $60.0B reported, $39.3B after leases, and about $12.7B (est.) after component outflows. [D3 Note 13, cash-flow statement][D1 Note 12][D5]
2. **Server-component receivables are ballooning (Material).** "Other receivables related to activities to facilitate the purchase of server components" went from $8.2B (2025-06-30) to $27.8B (2026-06-30) to $35.7B (2026-09-30). There are also $12.6B of "restricted investments pursuant to a supplier agreement." [F4 Note 1][D3 Note 1][D1 Note 1, p.10]
3. **Uncommenced leases have quadrupled (Material).** They were $92.7B at FY25, $329.1B at FY26 and $364.6B at FY27 Q1 (77% of equity), commencing through FY2034, "with some arrangements subject to certain contractual conditions being met." Finance lease liabilities on the balance sheet are already $71.0B, against $35.5B of debt. [F4][D3 Note 13 p.78][D1 Note 12 p.22]
4. **OpenAI related-party concentration (Material, disclosed).** OpenAI revenue was $24.1B in FY26 (7.3% of revenue) and $10.0B in FY27 Q1 (10.8%). OpenAI owes $7.2B (11.6% of AR, up from $6.0B). Microsoft holds ~24%, accounted for using HLBV; $12.0B of $13.0B committed funding has been paid. The FY26 gain was $6.5B, "primarily...the dilution gain." [D3 Notes 1, 3][D1 Note 1 p.9]
5. **Non-GAAP is applied asymmetrically (Minor).** Only OpenAI is excluded, so FY26 Q4 adjusted EPS of $4.74 keeps a $3.2B Anthropic gain. [D4]
6. **Clean core tests.** Receivables grew +15.7% vs revenue +17.8% in FY26 (FY27 Q1: +17.4% vs +18.8%), and DSO has stayed between 81 and 91 days for 5 years. Server lives are unchanged at 2–6 years. Deloitte's opinions are unqualified and internal controls are effective; the critical audit matters are routine (revenue recognition, tax). No restatements and no late filings. [D7][D3 Note 1][F3][F4][D15]
7. **Disclosure changes.** New risk factor: "Overestimation of demand... may lead to impairment of assets," and partners that are "significant customers of Azure" may not deliver "expected consumption." The 10-Q adds RPO judgment on "potential renegotiation of commitments" and an equity-method "lag of up to three months." Azure and M365 metrics were redefined, and M365 seats now include GitHub seats. [F1][F2]

## Evidence
**Table 1. Cash conversion, FY22–FY26 and TTM ($B)** [D5][D3][D1]
| FY (end) | NI | CFO | CFO/NI | Capex | FCF | FCF/NI | Fin.-lease ROU adds | Other investing |
|---|---|---|---|---|---|---|---|---|
| FY22 (2022-06-30) | 72.7 | 89.0 | 1.22x | 23.9 | 65.1 | 0.90 | n/f | n/f |
| FY23 (2023-06-30) | 72.4 | 87.6 | 1.21x | 28.1 | 59.5 | 0.82 | n/f | n/f |
| FY24 (2024-06-30) | 88.1 | 118.5 | 1.35x | 44.5 | 74.1 | 0.84 | 11.6 | -1.3 |
| FY25 (2025-06-30) | 101.8 | 136.2 | 1.34x | 64.6 | 71.6 | 0.70 | 20.5 | +2.3 |
| FY26 (2026-06-30) | 133.7 | 182.9 | 1.37x | 115.9 | 67.0 | 0.50 | 24.6 | -19.9 |
| TTM 2026-09-30 | 142.6 | 195.9 | 1.37x | 135.9 | 60.0 | 0.42 | 20.7 | -26.6 |

n/f = not fetched. In FY26, CFO was helped by deferred taxes (+$14.2B, mostly tax on the non-cash OpenAI gain), payables (+$5.3B; AP +53% vs revenue +18%, DPO 115 to 146 days) and unearned revenue (+$9.4B). No supplier-finance or factoring program is disclosed (searched the 10-K). [D3][D7]

**Table 2. Adjusted FY26 FCF (est.)** [D3]
| Step | $B |
|---|---|
| Reported FCF (CFO 182.9 − capex 115.9) | 67.0 |
| Alt. A: less finance-lease principal paid (3.1) | 63.9 |
| Alt. B: less finance-lease ROU additions (24.6), accrual view | 42.4 |
| Alt. B less component-procurement outflow ("Other, net" investing, 19.9) | **22.5** |
| ÷ NI ex-OpenAI ($128.8B) | 0.17x |

**Table 3. Beneish components (FY26 vs FY25)** [D7]; SGAI recomputed from the 10-K's S&M and G&A lines ($34.7B vs $32.9B) [D3 MD&A]
| DSRI | GMI | AQI | SGI | DEPI | SGAI | LVGI | TATA | M |
|---|---|---|---|---|---|---|---|---|
| 0.98 | 1.01 | 0.87 | 1.18 | 0.98 | 0.90 (was 1.0 default) | 0.90 | -0.065 | -2.64 |

The Piotroski fails (current ratio, gross margin -88 bps, asset turnover) all come from the AI build-out: PP&E rose +53% in FY26. [D7]

**Table 4. Capital allocation, FY26** [D3][D7][D9]
| Item | Value |
|---|---|
| SBC % revenue / % CFO | 3.7% / 6.8% |
| Buybacks vs SBC | $22.3B vs $12.4B; share count -0.16% y/y |
| Goodwill / equity | 27% |
| IRS NOPAs (FY2004–13) | $28.9B plus penalties and interest; long-term income taxes $29.2B |
| Insider sales (2026-08-31 to 2026-11-16 only) | 20 sales, $74.8M, 19 under 10b5-1 plans; 0 buys |

## Judgment
Judgment: The income statement can be trusted. The usual FCF shortcut cannot. Every adjustment is disclosed, so this is aggressive-by-convention, not concealment. Component receivables should convert to capex as servers arrive, so they are a timing item, but cash leaves before capex shows it. The forward risk is depreciation: D&A ($38.5B) plus lease amortization ($5.4B) badly trails roughly $160B of annual capacity spend, and $364.6B of leases will add liabilities and amortization through FY2034. Margins now depend on utilization, which the new impairment risk factor flags.

OpenAI is the judgment-heavy area. It is at once investee, top customer, debtor and funding recipient, with HLBV gains possibly booked on a lag, and the new "renegotiation" language touches the RPO it inflates. The desk should look at Azure and RPO growth with OpenAI separated where possible.

## Debate fodder
- Strongest bull point from this lens: Earnings quality is excellent. Accruals are -7.1%, CFO/NI has been 1.31x over 5 years, receivables trail revenue, depreciation lives are unchanged and audits are clean. [D7][D3]
- Strongest bear point from this lens: Fully loaded FCF was about $22.5B in FY26 (est.) and about $12.7B TTM (est.), against $142.6B of net income. Another $364.6B of lease commitments has not yet hit the balance sheet. [D3][D1]

## Open questions
- **How much of the $677B commercial RPO and the $364.6B of uncommenced leases is tied to OpenAI?** Not disclosed. It would be answered by OpenAI-specific RPO disclosure or by questions on the call.
- **Mechanics and settlement timing of the component receivables, and the counterparty behind the $12.6B restricted supplier investments.** Not disclosed. The FY27 Q2 10-Q would show whether they keep growing.
- **The Anthropic investment's carrying value, accounting method and gain detail.** Not found in the 10-K text searched.
- **What the 8-K Item 5.02 (2026-11-05, accn 0001193125-26-448357) covers.** Not read. Insider data covers only about 2.5 months.

## What would change my mind
- To **Red flags:** component receivables keep climbing past ~$45B in the FY27 Q2 10-Q (late Jan 2027) without capex absorbing them, an asset impairment, or a cut in OpenAI's commitments or RPO.
- To **Red flags:** any lengthening of server useful lives, which would flatter the coming depreciation wave.
- To **Clean:** component receivables and restricted investments fall while capex rises (the timing unwinds), and OpenAI revenue share stabilizes below ~10%.

## Sources
[D1] 10-Q, FY27 Q1 (2026-09-30), filed 2026-10-28, accn 0001193125-26-436133, https://www.sec.gov/Archives/edgar/data/789019/000119312526436133/msft-20260930.htm
[D3] 10-K, FY26 (2026-06-30), filed 2026-07-29, accn 0001193125-26-323660, https://www.sec.gov/Archives/edgar/data/789019/000119312526323660/msft-20260630.htm
[D4] 8-K Ex. 99.1 earnings release FY26 Q4, filed 2026-07-29, accn 0001193125-26-323632, https://www.sec.gov/Archives/edgar/data/789019/000119312526323632/msft-ex99_1.htm
[D5] data/statements.json (statements.py, 2026-11-18)
[D7] data/scores.json (scores.py, 2026-11-18)
[D9] data/insiders.json (edgar.py insiders, 2026-11-18)
[D15] data/profile.json, data/filings.json (edgar.py, 2026-11-18)
[F1] data/diff-10k-1a.json (diff_sections.py, 10-K Item 1A FY26 vs FY25, 2026-11-18)
[F2] data/diff-10q-mdna-yoy.json (diff_sections.py, 10-Q MD&A FY27 Q1 vs FY26 Q1 accn 0001193125-25-256321, 2026-11-18)
[F3] data/10k-9a.json (edgar.py filing-text --section 9A, 2026-11-18)
[F4] 10-K, FY25 (2025-06-30), filed 2025-07-30, accn 0000950170-25-100235, https://www.sec.gov/Archives/edgar/data/789019/000095017025100235/msft-20250630.htm
