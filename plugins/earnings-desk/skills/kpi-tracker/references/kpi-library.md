# KPI library by industry

For each industry: the KPIs that move the stock (★ = usually the swing KPI), what "good" looks like, how they're usually disclosed, and the traps. "Where" codes: **PR** = earnings press release (8-K Ex.99), **Deck** = investor presentation (often Ex.99.2 or IR site), **MD&A** = 10-Q/10-K Item 2/Item 7, **Notes** = financial statement footnotes, **XBRL** = standard us-gaap tag available via `edgar.py concept`, **Call** = earnings call only.

Thresholds are rules of thumb for orientation, not data. Always compare a company first with its own history, then with direct peers.

Common SIC mapping hints (from `edgar.py profile`): 7372/7370-7379 software & internet, 3674 semis, 5311-5999 retail, 6021-6029 banks, 6311-6411 insurance, 6798 REITs, 2834-2836 pharma/biotech, 4512-4522 airlines, 7011 hotels, 4813-4899 telecom/media, 1311 E&P, 3711-3714 autos, 3720-3728 aerospace, 3560-3569/3530s machinery, 4911-4991 utilities. SIC codes are coarse; classify by business model.

---

## 1. Software / SaaS
| KPI | Good | Where | Notes |
|---|---|---|---|
| ★ cRPO growth (y/y) | ≥ revenue growth | Notes (RPO footnote), PR | cRPO = RPO × % next-12-months; XBRL `RevenueRemainingPerformanceObligation` + `...Percentage` |
| ★ Net new ARR | Growing y/y | PR, Deck | Leads revenue 2-4 quarters |
| Net revenue / dollar retention (NRR) | > 120% elite, 105-115% healthy | PR, 10-K, Call | Often TTM and disclosed annually; definitions vary |
| Gross retention | > 90% | 10-K, Deck | Rarely disclosed; strong signal when it is |
| Customers > $100K ARR | Growing faster than total customers | PR | Threshold changes are a red flag |
| Calculated billings | ≥ revenue growth | Derived: revenue + Δ deferred revenue (XBRL `ContractWithCustomerLiability*`) | Distorted by billing-term changes |
| Rule of 40 | Revenue growth % + FCF margin % ≥ 40 | Derived | Use FCF after SBC for a stricter view |
| Non-GAAP op margin, SBC % revenue | Expanding; SBC < 15% | PR | |
Traps: annual-to-monthly billing shifts, multi-year prepaid deals inflating RPO, ARR definition changes, usage-based models where NRR swings with consumption.

## 2. Internet / digital advertising
| KPI | Good | Where | Notes |
|---|---|---|---|
| ★ Ad revenue growth (constant currency) | Stable/accelerating | PR | |
| Impressions / paid clicks growth vs. price per ad | Balanced growth | PR, 10-Q MD&A | Price-only growth is fragile |
| DAU / MAU, DAU/MAU ratio | Growing; ratio > 50% sticky | PR | Definition changes are common |
| ARPU by region | Rising in mature regions | PR, 10-Q | |
| Engagement (time spent) | Up | Call, Deck | Usually qualitative |
| ★ Capex guide and capex/revenue | Matches revenue trajectory | PR, Call | AI-era capex is a swing factor for margins and FCF |
| Traffic acquisition cost (TAC) % revenue | Stable | 10-Q | |

## 3. E-commerce / marketplaces / payments
| KPI | Good | Where | Notes |
|---|---|---|---|
| ★ GMV / TPV growth | ≥ industry growth | PR | |
| ★ Take rate (revenue / GMV) | Stable or rising with GMV growth | Derived | Rising take rate + slowing GMV = monetizing a maturing base |
| Active buyers / customers, frequency | Growing | PR | |
| Contribution margin / transaction margin | Stable | PR | Payments: transaction margin dollars is the key line |
| Order growth, AOV | Volume-led | PR, Deck | |
| Fulfillment cost % revenue | Falling | 10-Q | |
| Credit losses (BNPL, payments) | Stable | 10-Q Notes | |

## 4. Semiconductors
| KPI | Good | Where | Notes |
|---|---|---|---|
| ★ Next-quarter revenue guide vs. consensus | Above | PR | What the stock trades on |
| ★ Gross margin and GM guide | Stable/expanding | PR | Mix, utilization, pricing |
| Segment/end-market revenue (data center, auto, PC, mobile, industrial) | Growth where the bull case lives | PR, 10-Q | |
| Inventory days (DIO) | Stable or falling | Derived (XBRL `InventoryNet`) | Rising DIO + falling GM = correction coming |
| Channel inventory weeks | Within stated target range | Call | |
| Book-to-bill (equipment/analog) | > 1.0 | PR, Call | |
| Capex intensity (fabs/foundries) | Matches demand | PR | |
| Wafer-fab utilization (foundry/IDM) | > 80% | Call | |

## 5. Semicap & hardware / IT infrastructure
| KPI | Good | Where | Notes |
|---|---|---|---|
| ★ Orders / bookings, book-to-bill | > 1.0, rising | PR | |
| Backlog and deferred revenue | Growing | 10-Q Notes | |
| China revenue % | Watch export-control exposure | 10-Q (geographic note) | |
| Services / installed-base revenue | Growing steadily | PR | |
| Gross margin by segment | Stable | PR | |

## 6. Retail (general, specialty, grocery)
| KPI | Good | Where | Notes |
|---|---|---|---|
| ★ Comparable / same-store sales | Positive, traffic-led | PR | Split traffic vs. ticket; use 2-year stacks |
| Traffic (transactions) vs. ticket | Traffic positive | PR, Call | |
| ★ Gross margin (bps y/y) | Stable/up | PR | Markdowns, freight, shrink |
| Inventory growth vs. sales growth | Inventory ≤ sales growth | PR, 10-Q | Inventory > sales + 10 pts = markdown risk |
| Store count, openings/closings | Per plan | PR, XBRL `NumberOfStores` (verify scope) | |
| E-commerce penetration / digital growth | Rising | PR | |
| Sales per square foot | Rising | 10-K | |
Traps: 53-week years, calendar shifts (Easter, holiday timing), comps definitions that exclude remodeled stores.

## 7. Restaurants
| KPI | Good | Where | Notes |
|---|---|---|---|
| ★ Same-store sales (system / company / franchise) | Positive, traffic-led | PR | |
| Traffic vs. price/mix | Traffic flat or better | Call | |
| Restaurant-level margin (four-wall) | Stable/up | PR | Food & paper, labor, occupancy % sales |
| Unit growth (net new units) | Per guide | PR | |
| AUV (average unit volume) | Rising | 10-K | |
| Digital / loyalty mix | Rising | PR | |

## 8. Consumer staples / brands
| KPI | Good | Where | Notes |
|---|---|---|---|
| ★ Organic sales growth: volume vs. price/mix | Volume ≥ 0 | PR | Price-only growth fades |
| Gross margin | Recovering/stable | PR | Input cost, pricing lag |
| Market share (scanner data) | Holding | Call, Deck | Third-party data; cite |
| A&P spend % sales | Stable | Call | Cutting it flatters margins |
| Emerging-market growth, FX | | PR | |

## 9. Subscription media / streaming / telecom
| KPI | Good | Where | Notes |
|---|---|---|---|
| ★ Net subscriber adds (paid memberships, postpaid phone net adds) | Positive, above street | PR | Some companies stopped reporting quarterly: a signal |
| ARPU / ARM | Rising | PR | |
| Churn (monthly) | Falling; postpaid phone < 1% | PR | |
| Content spend / cash content amortization | Below revenue growth | 10-Q | |
| Fiber/broadband net adds, penetration | Rising | PR | |
| Capex intensity | Declining after build | PR | |
| Engagement hours | Rising | Deck | |

## 10. Banks
| KPI | Good | Where | Notes |
|---|---|---|---|
| ★ Net interest income (NII) and guide | Growing | PR | |
| ★ Net interest margin (NIM) | Stable/expanding | PR | |
| Deposit growth, cost of deposits, cumulative deposit beta | Low beta | PR, Deck | |
| Loan growth | Mid-single-digit, quality intact | PR | |
| Provision expense, net charge-offs (NCO ratio), NPAs | NCO stable | PR | CRE office exposure: read the deck |
| CET1 ratio | Above requirement + buffer | PR | |
| Efficiency ratio | < 60% (lower is better) | PR | |
| ROTCE | > 15% | PR | |
| AOCI / unrealized securities losses | | 10-Q | |
Traps: gross margin, DSO, Altman Z are meaningless here.

## 11. Insurance (P&C, life)
| KPI | Good | Where | Notes |
|---|---|---|---|
| ★ Combined ratio (P&C) | < 100%, ideally < 95% | PR | Split current-year ex-cat, cats, prior-year development |
| Net premiums written growth, rate increases | Rate > loss trend | PR, Call | |
| Prior-year reserve development | Favorable | PR, 10-Q | Adverse development = reserve weakness |
| Net investment income, book yield | Rising | PR | |
| Book value per share growth | Steady | PR | |
| Life: new business margins, persistency, spread | Stable | PR, Deck | |

## 12. REITs and real estate
| KPI | Good | Where | Notes |
|---|---|---|---|
| ★ FFO / AFFO per share | Growing | PR, supplemental | Non-GAAP; check definitions |
| ★ Same-property NOI growth | Positive | Supplemental | |
| Occupancy / leased % | High and stable | Supplemental | |
| Re-leasing spreads (cash / GAAP) | Positive | Supplemental | |
| Weighted average lease term, expirations | Laddered | 10-K | |
| Net debt / EBITDAre, interest coverage | < 6x | Supplemental | |
| Data-center/tower: leasing backlog, MW leased | Growing | Supplemental | |
Supplementals are usually Ex.99.2 or on the IR site.

## 13. Pharma / biotech / medtech
| KPI | Good | Where | Notes |
|---|---|---|---|
| ★ Key product revenue (by product, by region) | Above street | PR | |
| Prescriptions (TRx/NRx) | Rising | Third-party (cite) | |
| Gross-to-net discounts | Stable | Call | IRA pricing, rebates |
| Pipeline milestones (phase, readouts, PDUFA dates) | On time | PR, Deck | |
| Cash runway (biotech) | > 24 months | 10-Q | Cash / quarterly burn |
| Medtech: procedure volumes, organic growth, new product launches | | PR | |
| Loss of exclusivity timeline | | 10-K | |

## 14. Industrials / machinery / aerospace & defense
| KPI | Good | Where | Notes |
|---|---|---|---|
| ★ Orders, book-to-bill | > 1.0 | PR | |
| ★ Backlog (and % to convert in 12 months) | Growing, convertible | PR, 10-Q Notes (RPO) | Funded vs. unfunded for defense |
| Organic growth: price vs. volume | Volume ≥ 0 | PR | |
| Incremental / decremental margins | Incrementals 25-35% | Derived | |
| Aftermarket / services mix | Rising | PR | Higher margin, more stable |
| Aerospace: deliveries, production rate, aftermarket | Per plan | PR | |
| Dealer inventory (machinery, ag) | Normal weeks | Call | |

## 15. Transportation & travel (airlines, hotels, logistics)
| KPI | Good | Where | Notes |
|---|---|---|---|
| ★ Airlines: TRASM / PRASM, CASM-ex fuel | RASM ≥ CASM growth | PR | |
| Airlines: capacity (ASMs), load factor | Load > 80% | PR | |
| ★ Hotels: RevPAR (ADR × occupancy) | Positive | PR | |
| Hotels: net unit growth, pipeline | Rising | PR | |
| Trucking/rail: volumes, yield / revenue per unit, operating ratio | OR falling | PR | |
| Parcel: average daily volume, revenue per piece | | PR | |

## 16. Energy (E&P, midstream, refiners)
| KPI | Good | Where | Notes |
|---|---|---|---|
| ★ Production (boe/d) and guide | Per guide | PR | |
| Realized price vs. benchmark | Tight differential | PR | |
| Lease operating expense per boe | Falling | PR | |
| Capex and reinvestment rate | < 70% of CFO | Derived | |
| Reserve replacement, PV-10 | > 100% | 10-K | |
| Refiners: throughput, crack spread capture, utilization | > 90% utilization | PR | |
| Midstream: volumes, fee-based %, leverage | | PR | |

## 17. Autos and EVs
| KPI | Good | Where | Notes |
|---|---|---|---|
| ★ Deliveries / units | Above street | PR (often a separate deliveries release) | |
| Automotive gross margin ex-credits | Stable | PR | Regulatory credits flatter it |
| ASP and mix | Rising | Derived | |
| Inventory days supply | 50-70 days normal | Third-party, Call | |
| Warranty reserve % revenue | Stable | 10-Q | |

## 18. Utilities
| KPI | Good | Where | Notes |
|---|---|---|---|
| ★ Rate base growth | 6-8% | Deck | |
| Allowed vs. earned ROE | Earned ≈ allowed | Deck, rate filings | |
| Capex plan | Funded | Deck | |
| Rate-case outcomes and calendar | Constructive | PR | |
| Weather-normalized load growth | Positive (data centers) | Call | |

---

## Where to look, fastest first
1. The press release tables (`edgar.py earnings-release TICKER --index N`): most KPIs, every quarter.
2. 10-Q / 10-K MD&A (`edgar.py filing-text TICKER --form 10-Q --section mdna --index N`): definitions, Q4 values in the 10-K, price/volume splits.
3. Footnotes in the 10-Q/10-K (revenue, RPO, segments, geographic data); grep the `saved_to` file.
4. Supplemental / investor deck (Ex.99.2 or IR site; web search and cite).
5. Call transcript (some KPIs are said, never written; cite the call and date).
