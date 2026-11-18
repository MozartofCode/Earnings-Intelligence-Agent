# Valuation memo · MSFT · 2026-11-17
```scorecard
lens: valuation
price: $508.29 (Yahoo unofficial endpoint close, 2026-11-18 [D6])
implied_growth_y1: 42.4% (10y CAGR 22.0%) at 13.7% FCF margin (TTM, post-SBC); 24.3% (10y CAGR 13.4%) at 25% normalized margin, 8.5% WACC
implied_margin: 31.1% at 19% y1 growth (8.5% WACC); 37.4% at 17% (9% WACC)
expectations: Demanding
scenarios: bear $185 (-64%) | base $403 (-21%) | bull $656 (+29%)
skew: Unfavorable
confidence: Medium
```

## Bottom line
At $508.29 the market cannot be pricing today's capex-depressed 13.7% post-SBC FCF margin: that would need a 22% revenue CAGR for ten years on a $346B base, which is heroic [V1]. On a normalized 25% margin it needs about a 13.4% ten-year CAGR, roughly MSFT's 5-year record of 14.6%, from a base twice as large [V2][V7]. My base case is worth about $403 (-21%), and it hinges on where FCF margin settles after the AI capex cycle.

## Key findings
1. **TTM FCF after SBC is $47.4B, a 13.7% margin and a 1.26% yield.** Capex is $135.9B, or 39% of revenue, vs. 12.0% in FY22 [V1][V7]. Post-SBC margin has fallen from 25.8% (FY24) to 16.4% (FY26) [V7].
2. **Finance leases add capital intensity that is not in the model.** Finance-lease assets added were about $20.7B TTM (6% of revenue). Finance-lease liabilities are $71.0B vs. $35.5B of debt [V5][V6][D2]. Net of lease additions, the post-SBC FCF yield is about 0.7% (est.).
3. **Implied expectations depend heavily on the margin assumption.** At today's margin: 42.4% year-1 growth, 22.0% CAGR, 7.3x revenue in year 10 [V1]. At 25%: 14.6% CAGR (9% WACC) or 13.4% (8.5%) [V2]. Over 15 years (8.5%, 25%) the implied year-1 growth is 17.8%, about today's 17.9% [V2][V4].
4. **History.** Revenue CAGR is 16.1% over 3 years (FY23–FY26) and 14.6% over 5 years (FY21–FY26). The best post-SBC FCF margin in the data is 29.1% (FY22). ROIC is 28.8% (FY26) [V7]. FY27 Q1 revenue grew +18.8% and commercial RPO +73% to $677B [D2]. Web consensus for FY27 Q2 is $96.6–98.5B, +19–21% y/y [D12].
5. **Relative value.** EV/EBIT is 23.0x vs. a 21.1x peer median (+9%). EV/Sales is 10.8x vs. 4.2x, 84% above the growth regression line (r² 0.18, n = 6, so the line explains little). Operating margin is 47.1% vs. 32.1%; ROIC 35.2% vs. 30.3%. Operating P/E (EBIT taxed at 18%) is about 28.3x (est.) vs. GAAP 26.5x [V4].
6. **Sensitivity.** At base assumptions, value equals price at a 7.5% WACC ($512). ±1 pt of WACC moves value +24% / -17%; ±4 pts of margin ±15%; ±4 pts of growth about ±16% [V3].

## Evidence
**Scenarios** (dcf.py, SBC as a cost, linear growth fade to terminal over 10 years. Values deduct $9.53/share of finance-lease liabilities by hand: $71.0B / 7.446B shares) [V3][V5]
| Case | Growth y1 | FCF margin y5 | WACC / TG | 10y rev CAGR | Value/share | vs. price | Prob. (judgment) |
|---|---|---|---|---|---|---|---|
| Bear | 12% | 18% | 9.0% / 2.5% | 7.2% | $185 | -64% | 25% |
| Base | 19% | 25% | 8.5% / 3.0% | 10.9% | $403 | -21% | 50% |
| Bull | 24% | 30% | 8.0% / 3.0% | 13.3% | $656 | +29% | 25% |
| Weighted | | | | | $412 | -19% | |

Assumptions (judgment): **Bear:** Azure slows, capacity competition keeps capex at 30%+ of revenue, margin stays near FY26's 16.4%. **Base:** growth at the FY27 Q1 run-rate and consensus (+19% [D2][D12]). Capex eases from 39% to about 27% of revenue (OCF about 55%, SBC 3.6% [V7]). WACC 8.5%, the top of the mega-cap range [V8]. **Bull:** RPO converts at +24%, and margin exceeds FY22's 29.1%.

**Growth × margin grid**, value/share before the lease deduction, 8.5% WACC [V3]
| y1 growth \ y5 margin | 21% | 25% | 29% |
|---|---|---|---|
| 15% | $297 | $351 | $404 |
| 19% | $349 | $412 | $475 |
| 23% | $409 | $483 | $557 |

**Comps, TTM** (prices: MSFT [D6]; peers market.py quote 2026-11-18) [V4]
| Ticker | Why it's in | EV/Sales | EV/EBIT | P/E | FCF yld post-SBC | Growth | Op. m. | ROIC | Rule of 40 |
|---|---|---|---|---|---|---|---|---|---|
| **MSFT** | target | 10.8x | 23.0x | 26.5x (~28x op.) | 1.3% | 17.9% | 47.1% | 35.2% | 35 |
| GOOGL | hyperscaler, AI capex, Workspace vs. M365 | 7.1x | 21.2x | 14.7x* | -0.3% | 22.2% | 33.3% | 30.3% | 26 |
| AMZN | AWS is Azure's main rival (flag: retail dominates revenue) | 3.7x | 28.4x | 21.5x | -2.3% | 15.4% | 13.1% | 16.1% | 9 |
| ORCL | OCI + database/apps, AI-infra capex (flag: debt reads $0) | 4.3x† | 13.3x† | 18.2x | -9.7% | 21.6% | 32.1% | 85%† | -18 |
| CRM | enterprise SaaS apps vs. Dynamics/agents | 4.2x | 21.1x | 16.2x | 7.3% | 11.2% | 19.9% | 11.3% | 46 |
| ADBE | subscription productivity software | 3.4x | 9.6x | 12.1x | 9.6% | 12.0% | 35.7% | 59.4% | 53 |
| Median ex-MSFT | | 4.2x | 21.1x | 16.2x | -0.3% | 15.4% | 32.1% | 30.3% | 26 |

\* GOOGL net income exceeds EBIT (investment gains), so its P/E is understated. † ORCL debt pulls as $0 from XBRL, so its EV and ROIC are unreliable. Fixing it would not move the EV/EBIT median. Lease-adjusted MSFT EV/EBIT is about 23.5x (est., adding $92.7B of leases [V5][D2]). Peers are not lease-adjusted.

## Judgment
- Judgment: **Demanding, not heroic.** The price needs MSFT to *hold* about 18% growth for roughly 15 years with margins back at 25%. Base rates say a decade of mid-teens growth at this size is rare [V8]. The $677B RPO is the best evidence it could be the exception [D2].
- Judgment: the +9% EV/EBIT premium is earned: margin is 15 pts above the median, ROIC 5 pts above, with net cash. The EV/Sales premium is the margin gap. The whole AI-capex group is priced on future cash, not current cash.
- Judgment: the skew is unfavorable (-64% vs. +29%). The bear needs only capex that never normalizes, not a collapse. The 7.5% break-even WACC shows the market discounts MSFT like a bond-like compounder.
- The lever: **normalized FCF margin after the capex cycle.** At 19% year-1 growth and 8.5% WACC, the break-even year-5 margin is 31.1% [V3], above any post-SBC margin in the FY22–26 data (best 29.1% [V7]). WACC moves value more mechanically, but margin is the business variable in debate.

## Debate fodder
- Strongest bull point from this lens: over 15 years at 25% margins, the price needs only about 17.8% year-1 growth, today's rate, backed by RPO +73% [V2][D2].
- Strongest bear point from this lens: the 31% break-even margin exceeds MSFT's best post-SBC margin in five years (29.1%), before about $20.7B a year of finance-lease capex [V3][V5][V7].

## Open questions
- FY27/FY28 capex guidance is given on the call, not in the release [D2]. The transcript is needed.
- RPO concentration (OpenAI share) and duration were not checked.
- Consensus is single-source [D12], peer prices are unofficial, and ORCL debt needs a 10-Q check.

## What would change my mind
- FY27 Q2 (around 2027-01-27): capex flat-to-down q/q with Azure at 40%+ points to bull margins.
- Two quarters of post-SBC FCF margin above 22% lifts the base toward the price.
- Revenue growth below 15% while capex still rises moves the base toward the bear.

## Sources
- [V1] data/dcf-reverse.json, dcf-reverse-wacc8.json, dcf-reverse-wacc10.json (dcf.py, 2026-11-18)
- [V2] data/dcf-reverse-norm25.json, dcf-reverse-norm25-wacc8.5.json, dcf-reverse-norm25-15y.json, dcf-reverse-g17.json (dcf.py, 2026-11-18)
- [V3] data/dcf-bear.json, dcf-base.json, dcf-bull.json, dcf-base-wacc7.5.json, dcf-base-wacc9.5.json, dcf-grid.json (dcf.py, 2026-11-18)
- [V4] data/comps.json (comps.py, 2026-11-18; peer prices market.py quote / Yahoo unofficial endpoint, 2026-11-18)
- [V5] 10-Q, FY27 Q1 (2026-09-30), filed 2026-10-28, accn 0001193125-26-436133, https://www.sec.gov/Archives/edgar/data/789019/000119312526436133/msft-20260930.htm (lease note)
- [V6] 10-K, FY26 (2026-06-30), filed 2026-07-29, accn 0001193125-26-323660, https://www.sec.gov/Archives/edgar/data/789019/000119312526323660/msft-20260630.htm (lease note)
- [V7] data/statements.json (statements.py, 2026-11-18)
- [V8] reference: Mauboussin & Callahan, *The Base Rate Book* (Credit Suisse, 2016), and the WACC ranges in the reverse-dcf skill notes; approximate, not re-verified
- [D2] 8-K Ex. 99.1 earnings release FY27 Q1, filed 2026-10-28, accn 0001193125-26-436122, https://www.sec.gov/Archives/edgar/data/789019/000119312526436122/msft-ex99_1.htm
- [D6] data/quote.json (market.py quote, 2026-11-18)
- [D12] web search: benzinga.com and chartmill.com (MSFT estimates pages), retrieved 2026-11-18
