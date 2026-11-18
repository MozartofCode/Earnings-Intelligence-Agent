# PM decision · MSFT · 2026-11-18 · price $508.29 [D6]

**Research view: Unattractive · Conviction: Medium** (a view on risk/reward at today's price, not advice).

## Input audit
- **Useful lives (traced):** forensics says server lives are unchanged (2–6 yrs) [F-F6]; earnings and bear cite a 15→25-yr extension. Both are right. The FY26 Q4 call extends *datacenter and office building* lives from 15 to 25 years, with a "minimal benefit to FY27 operating income". The larger effect moves future datacenter leases from finance to operating, so they drop out of reported capex. The CFO: "Outside of this useful life impact, our calendar year 2026 CapEx investment expectations remain unchanged" [E4, transcript l.166–167]. So forensics' "clean on lives" covers servers only.
- **OpenAI share of RPO (checked):** +84% total to $678B with ex-OpenAI +25% gives a lower bound of ~$217B, or 32% (est.) [E4]. The bear's arithmetic holds. The 45% figure is secondary and treated as an allegation [BE3].
- **Scenario basis:** I use the valuation memo's values (10-yr fade, 8.5% base WACC, finance-lease liabilities of $9.53/sh deducted) per rule 8 [V3]. dcf-base.json confirms $412.16 − $9.53 = $403. The bull's $605 (15-yr) and the bear's $226 (lease-loaded FCF) are cross-checks, not inputs.
- **Discounted:** consensus is single-source [D12]; the FY27 Q1 call is an automated transcript [E7]; FY27 Q1 ex-OpenAI RPO is not disclosed.

## Debate scorecard
| Pillar | Side | Outcome | Why |
|---|---|---|---|
| 1 Demand > supply; guidance is a floor | Bull | **Survived** (near term) | Revenue above the top of the guided range 4 of 4 times [E-T2]. The bear conceded that a Q2 miss is unlikely. It says nothing about duration |
| 2 Operating leverage proves payback | Bull | **Weakened** | The 49.8% is a seasonal Q1 high. The Q2 guide implies ~46.8% vs 47.1% y/y [E-T3]. D&A + lease amortization of $43.9B vs ~$160B of capacity spend [F-F1] |
| 3 Capex intensity can bend | Bull | **Refuted** (as evidence) | The ~$190B→$175B cut was a lease reclassification per the CFO [E4]. The bull concedes "no quarter yet shows intensity falling" |
| 4 Switching-cost franchise | Bull | **Survived** | M365 commercial cloud +17% on +5% seats [I2], conceded by the bear |
| 1 Backlog tied to non-exclusive OpenAI, stalled | Bear | **Survived** (receivable sub-point refuted) | ≥32% concentration, "renegotiation" language and bookings −12% were all conceded. The OpenAI receivable is ~65 days, inside the DSO band |
| 2 Reported FCF overstates cash | Bear | **Survived** | Conceded. Only the component outflow's timing is disputed ($39.3B vs $12.7B TTM) [F-T1] |
| 3 Price needs never-earned margins | Bear | **Weakened** | The 31.1% break-even holds at 10 years [V3], but on 15 years at 25% margin the price needs only 17.8% growth [V2]. ~$108 of the bear's gap is WACC and horizon choice [BU4] |
| 4 Infra structure deteriorating | Bear | **Survived** (low weight) | Bull conceded. The share loss is a 1-pt estimate on a recast Azure definition [I11] |

**Judgment:** The bull wins the next two quarters. The bear wins the cash and duration argument, and duration is what the price is about.

## Key debate variables
| Variable | Bull view | Bear view | PM call | Resolves with | When |
|---|---|---|---|---|---|
| Ex-OpenAI AI demand durability | Ex-OpenAI RPO +25%; ~90% of cloud revenue is non-frontier-lab [E4] | RPO flat 3 quarters; OpenAI can go elsewhere [I12] | **Open, slight bear lean** (bookings −12%, figure withheld) | Ex-OpenAI RPO and OpenAI revenue, FY27 Q2 | ~2027-01-27 (est.) |
| Normalized FCF margin after the cycle | ~27% post-SBC is reachable | Lease-loaded margin stays near 7.7% today | **Bear for 10-yr value** (break-even 31.1% > best-ever 29.1%) [V3][V7] | Capex + lease adds as % of revenue; FY28 capex framework | FY27 Q4 call, late Jul 2027 |
| Depreciation and lease absorption | Margin rose while depreciation +56% | $364.6B of leases not yet commenced [F-F3] | **Bear, slowly** | Operating margin vs ~46.8% guide | FY27 Q2–Q3 |

## Scenarios (10-yr fade, valuation memo's WACCs, lease liabilities deducted) [V3][PM1]
| Case | Probability | Value/share | vs price |
|---|---|---|---|
| Bear (12% g, 18% m, 9.0%) | 25% | $185 | −64% |
| Base (19% g, 25% m, 8.5%) | 55% | $403 | −21% |
| Bull (24% g, 30% m, 8.0%) | 20% | $656 | +29% |

PWV = 0.25×185 + 0.55×403 + 0.20×656 = 46.25 + 221.65 + 131.20 = **$399 (−21% vs $508.29)**.
Upside/downside = (656 − 508.29) / (508.29 − 185) = 147.71 / 323.29 = **0.46**.

The bull moves from 25% to 20%: its pillar 3 was refuted and the bull itself marked 20%. The bear stays at 25% rather than the bear's 30%, because the near-term revenue and M365 concessions survived. Sensitivity: at 30/50/20, PWV is $388 (−24%). At 20/50/30, PWV is $435 (−14%), but the ratio test still fails. Base value equals the price only at a 7.5% WACC ($512) [V3].

## Verdict and conviction
- **Rubric:** PWV $399 ≤ $432 (price − 15%), and the ratio of 0.46 is below 0.7. Both point to **Unattractive**, and the ratio test does not depend on the probabilities.
- **Overrides:** (1) No Red flags. (2) Forensics *Watch* caps conviction at Medium. (3) A data gap on a key variable (FY27 Q1 ex-OpenAI RPO not disclosed; automated transcript) caps it at Medium. (5) No deviation from the arithmetic.
- **Conviction Medium, not High:** the bear–bull range is 93% of price, and the earnings lens (Accelerating) conflicts with valuation (Unfavorable).
- **Not Low:** the lenses conflict on momentum, not on 10-year value. Every 10-year run in the file is below the price, including the bull's own $443 [BU1].
- **Strongest argument against:** on a 15-year fade at a 25% margin, the price needs only today's ~18% growth [V2], and at a 7.5% WACC the base case is worth $512. The verdict is a bet that a decade, not fifteen years, is the right horizon for an AI build-out this capital-intensive.

## Kill criteria
1. FY27 Q2 (~2027-01-27): commercial RPO ≥ $720B **and** disclosed ex-OpenAI RPO growth ≥ +25% y/y (8-K Ex. 99.1 / call).
2. Cash PP&E capex plus finance-lease ROU additions < 40% of revenue in two consecutive quarters, by the FY27 Q3 10-Q (~2027-04-30). FY27 Q1 was ~48% ($44.6B / $92.3B, est.) [E-F7]. Also check operating-lease additions, given the reclassification.
3. Lease-loaded post-SBC FCF margin (CFO − capex − SBC − finance-lease ROU additions) > 15% of revenue in two consecutive quarters, by the FY27 10-K (~late Jul 2027). TTM today is ~7.7% [BE1].
4. OpenAI revenue ≥ $10.0B a quarter in FY27 Q2 and Q3 with the OpenAI receivable < $6.0B (10-Q related-party note).
5. MSFT closes below $462. At that price the ratio reaches 0.7, so the arithmetic no longer supports Unattractive. Re-run the desk.

## Unresolved
- The OpenAI share of the $677B RPO and of the $364.6B of uncommenced leases (not disclosed).
- FY27 Q1 ex-OpenAI RPO and bookings; the FY27 Q2 guide is secondary-sourced only [E7][E8].
- The size of the FY27 useful-life benefit; the counterparty behind the component receivables and the $12.6B of restricted investments; the Anthropic carrying value.
- The 2026-11-05 8-K (Item 5.02) was not read. Insider data covers ~2.5 months only.
- Horizon (10 vs 15 years) is a judgment the data cannot settle.

## Sources
- [PM1] PM arithmetic on [V3] values (this file, 2026-11-18). All other IDs are as defined in DATA-BRIEF.md, memos/*.md and debate/*.md. [E4] = data/web/transcript-FY26Q4.txt (call 2026-07-29), lines 145–147 and 166–167.
