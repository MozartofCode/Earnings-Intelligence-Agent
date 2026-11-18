# Industry memo · MSFT · 2026-11-17
```scorecard
lens: industry
moat: Wide
moat_trend: Stable
primary_power: Switching costs
industry_structure: Deteriorating
biggest_threat: AI-lab customer concentration: OpenAI is 10.8% of revenue and is now free to run on any cloud (1–3 yrs)
confidence: Medium
```

## Bottom line
The moat is wide and rests on switching costs: Microsoft 365 commercial cloud grew 17% on 5% seat growth, which is pricing power over a locked-in base [I2]. Azure is a scale business in a worsening structure. OpenAI alone supplied $10.0B (10.8%) of FY27 Q1 revenue [I2] and since April 2026 can buy compute from any cloud [I12], while capex intensity rises and neoclouds take share [I11].

## Key findings
1. **Profit pool.** Agents and Infra earned $40.6B of operating income on $76.8B of revenue (52.9% margin). That is 88% of segment operating income. Devices and Consumer earned $5.4B on $15.5B (34.8%), with revenue down 3% [I3].
2. **Pricing power in the locked-in base.** Microsoft 365 commercial cloud revenue grew +17% while seats grew +5%. Microsoft attributes the gap to upsell to Copilot, E5 and E7 [I2]. Paid Microsoft 365 Copilot seats reached over 30M, against about 450M commercial seats (≈6.7%, est.) [I14].
3. **OpenAI concentration is rising.** OpenAI revenue (including revenue share) was $24.1B in FY26, or 7.3% of revenue [I1]. In FY27 Q1 alone it was $10.0B, or 10.8% [I2]. Receivables from OpenAI rose from $6.0B to $7.2B in one quarter. Microsoft owns about 24% of OpenAI, down from 25% [I1][I2].
4. **Exclusivity has gone.** Under the reported April 27, 2026 amendment, Microsoft's IP license is non-exclusive through 2032, OpenAI can sell on any cloud (Azure keeps first launch), and OpenAI's revenue share is capped and runs through 2030 [I12]. OpenAI has reported cloud commitments with Oracle (~$300B) and AWS (~$138B) on top of its incremental $250B with Azure [I17].
5. **Cloud share (est.).** Synergy estimates Microsoft's share of cloud infrastructure at 19% in Q3 2026, down from 20% a year earlier. Over the same period AWS fell from 29% to 26% and Google rose from 13% to 16%, in a market that grew +55% y/y to ~$168B [I11]. Azure's +48% growth [I2] is below Synergy's market growth rate.
6. **Margin cost of the AI mix.** Microsoft Cloud gross margin fell to 66% on the shift toward Azure [I2]. Company gross margin was 67.7% TTM, versus 69.8% in FY24 [D5]. TTM capex of $135.9B is 39% of revenue and excludes finance leases [D5].
7. **Model layer (est.).** Menlo Ventures (an Anthropic investor) estimates enterprise LLM API spend shares at Anthropic 55%, OpenAI 31% and Google 9% [I16]. Microsoft's hedge: Anthropic committed $30B to Azure compute, Microsoft committed up to $5B of investment [I13], and Microsoft booked a $3.2B gain on the stake [I4]. AWS remains Anthropic's primary cloud [I13].

## Evidence
**Table 1. Competitive scoreboard (latest quarter; TTM ratios from comps.py).** [I3][I5][I6][I7][I8][I9][I10]
| Co. | Relevant unit, latest Q | Unit growth | Unit op. margin | TTM rev growth | TTM op. margin | TTM FCF margin | ROIC |
|---|---|---|---|---|---|---|---|
| MSFT | Azure ≈$33.3B (est., from +$10.8B / +48%) | +48% | n/d (A&I segment 52.9%) | +17.9% | 47.1% | 17.3%* | 35.2% |
| AMZN | AWS $46.0B (Q3, Sep-26) | +39% | 38.7% (34.6% a year earlier) | +15.4% | 13.1% | -5.9% | 16.1% |
| GOOGL | Google Cloud $30.7B (Q3, Sep-26) | +103% | 36.2% (23.7%) | +22.2% | 33.3% | 4.2% | 30.3% |
| ORCL | OCI $7.4B (FQ1, Aug-26); RPO $664B | +121% | n/d | +21.6% | 32.1% | -40.0% | 85.0%** |
| CRM | Revenue $11.3B (FQ2, Jul-26); Agentforce ARR >$1.5B | +11% | 20.5% GAAP | +11.2% | 19.9% | 34.5% | 11.3% |
| ADBE | Revenue $6.76B (FQ3, Aug-26); ARR $27.5B | +13% | 34.8% GAAP | +12.0% | 35.7% | 40.8% | 59.4% |

\*Overstated: finance-lease-funded capacity is not in capex [D5]. **Distorted by Oracle's small equity base.

**Table 2. Cloud infrastructure share (estimates).** Synergy Research, via techinsights.com and datacenterknowledge.com [I11]
| Provider | Q3 2025 | Q3 2026 | Δ |
|---|---|---|---|
| AWS | 29% | 26% | -3 pts |
| Microsoft | 20% | 19% | -1 pt |
| Google | 13% | 16% | +3 pts |
| Market size | ~$107B | ~$168B | +55% |

**Table 3. 7 Powers scorecard.** [I1][I2][I3][I5]
| Power | Benefit (numbers) | Barrier | Verdict |
|---|---|---|---|
| Switching costs | M365 revenue/seat growth ≈ +11% (17% − 5%, est.); commercial RPO $677B, 2.3-yr duration | Identity, data, workflows and admin tied across Office, Teams, Entra and security | **Strong, primary** |
| Scale economies | A&I margin 52.9%; 47.1% company operating margin vs 13–36% for peers | $135.9B/yr capex; the 10-K cites per-unit datacenter cost advantages | Real, but shared with AMZN, GOOGL and ORCL |
| Network effects | GitHub; LinkedIn; Windows developers | Ecosystem breadth | Moderate. Windows OEM -22% shows the edge is fading |
| Cornered resource | OpenAI IP rights to 2032 | Now non-exclusive [I12] | **Weakened** |
| Branding / Process / Counter-positioning | Enterprise trust; distribution through the channel | Hard to measure | Secondary |

## Judgment
Judgment: These are two businesses with different moat trends. **Productivity and security is strengthening.** Revenue per seat is rising about 11 points a year, and Copilot covers under 7% of seats. **AI infrastructure is commoditizing.** Four hyperscalers plus neoclouds sell the same NVIDIA-class capacity. Oracle's RPO ($664B) is close to Microsoft's ($677B) [I8][I2], which suggests much of the industry's backlog comes from the same few AI labs. Buyers are concentrated and suppliers (GPUs, power) are strong, so I rate structure Deteriorating even while demand booms.

OpenAI has gone from a cornered resource to a large customer that can now shift incremental workloads to Oracle and AWS, with its revenue share capped. Microsoft's answer is to be model-agnostic (Anthropic is on Foundry and in Copilot). That means its edge is distribution into about 450M seats, not models.

Five forces: rivalry **High, rising**; buyers **High, rising** (the force most likely to change); suppliers **High**; substitutes **Medium** (AI-native apps and agents); entry **Medium** (neoclouds).

TAM: Gartner puts IaaS at ~$287B in 2026 and ~$360B in 2027 [I15]. An Azure run rate of ≈$133B (est.) is already a large share of that, so above-market growth depends on AI capacity deals. I found no Microsoft-stated TAM to test against.

## Debate fodder
- Strongest bull point from this lens: M365 commercial cloud +17% on +5% seats. Pricing power over a captive base, with Copilot at about 6.7% penetration (est.) [I2][I14].
- Strongest bear point from this lens: OpenAI is 10.8% of revenue and is no longer exclusive. Microsoft also lost 1 point of cloud share (est.) while capex reached 39% of revenue [I2][I12][I11][D5].

## Open questions
- How much of the $677B RPO is OpenAI's $250B commitment? Not disclosed.
- The revenue-share cap and OpenAI's prior-year Q1 revenue are not disclosed. Both are needed to separate OpenAI from organic Azure growth.
- The amendment terms come from secondary press only [I12].
- The size of the Nov 4, 2026 debt offering was not extracted [I18].

## What would change my mind
- OpenAI revenue below ~$8B/quarter, or OpenAI receivables still outpacing its revenue (FY27 Q2 10-Q, late Jan 2027).
- Synergy showing Microsoft's share ≥ 20% for two quarters → Structure "Stable".
- M365 commercial cloud growth below +12% with seats flat → moat trend "Eroding".
- Microsoft Cloud gross margin back above 68% with capex intensity flat.

## Sources
- [D5] data/statements.json (statements.py, 2026-11-18)
- [I1] 10-K FY26 (2026-06-30), filed 2026-07-29, accn 0001193125-26-323660, https://www.sec.gov/Archives/edgar/data/789019/000119312526323660/msft-20260630.htm (Item 1, Item 1A, OpenAI related-party note)
- [I2] 10-Q FY27 Q1 (2026-09-30), filed 2026-10-28, accn 0001193125-26-436133, https://www.sec.gov/Archives/edgar/data/789019/000119312526436133/msft-20260930.htm
- [I3] 8-K Ex. 99.1 FY27 Q1 release, filed 2026-10-28, accn 0001193125-26-436122, https://www.sec.gov/Archives/edgar/data/789019/000119312526436122/msft-ex99_1.htm
- [I4] 8-K Ex. 99.1 FY26 Q4 release, filed 2026-07-29, accn 0001193125-26-323632, https://www.sec.gov/Archives/edgar/data/789019/000119312526323632/msft-ex99_1.htm
- [I5] data/comps-industry.json (comps.py MSFT GOOGL AMZN ORCL CRM ADBE --no-quote, 2026-11-18)
- [I6] Alphabet 8-K Item 2.02, Q3 2026, filed 2026-10-28, accn 0001652044-26-000080, https://www.sec.gov/Archives/edgar/data/1652044/000165204426000080/ (data/peer-release-GOOGL.json)
- [I7] Amazon 8-K Item 2.02, Q3 2026, filed 2026-10-29, accn 0001018724-26-000038, https://www.sec.gov/Archives/edgar/data/1018724/000101872426000038/ (data/peer-release-AMZN.json)
- [I8] Oracle 8-K Item 2.02, FQ1 FY27, filed 2026-09-10, accn 0001193125-26-387905, https://www.sec.gov/Archives/edgar/data/1341439/000119312526387905/ (data/peer-release-ORCL.json)
- [I9] Salesforce 8-K Item 2.02, FQ2 FY27, filed 2026-08-26, accn 0001108524-26-000187, https://www.sec.gov/Archives/edgar/data/1108524/000110852426000187/ (data/peer-release-CRM.json)
- [I10] Adobe 8-K Item 2.02, FQ3 FY26, filed 2026-09-10, accn 0000796343-26-000147, https://www.sec.gov/Archives/edgar/data/796343/000079634326000147/ (data/peer-release-ADBE.json)
- [I11] web search: techinsights.com and datacenterknowledge.com (Synergy Research Q3 2026 cloud market), retrieved 2026-11-18; Q3 2025 baseline via techtarget.com
- [I12] web search: qz.com, eweek.com, yourstory.com (OpenAI–Microsoft amendment of 2026-04-27; secondary reporting), retrieved 2026-11-18
- [I13] web search: techradar.com, pureai.com (Anthropic–Microsoft–NVIDIA partnership, 2025-11-18), retrieved 2026-11-18
- [I14] web search: nojitter.com, directionsonmicrosoft.com (Copilot paid seats; FY26 Q2–Q4 calls), retrieved 2026-11-18
- [I15] web search: digit.fyi (Gartner IaaS forecast, Aug 2026), gartner.com, retrieved 2026-11-18
- [I16] web search: menlovc.com (2026 State of Enterprise AI, 2026-11-03), letsdatascience.com, retrieved 2026-11-18
- [I17] web search: builtin.com, implicator.ai, intuitionlabs.ai (OpenAI cloud commitments), retrieved 2026-11-18
- [I18] data/8k-2026-11-04.json (edgar.py earnings-release MSFT --accession 0001193125-26-447173, 2026-11-18): debt underwriting agreement
