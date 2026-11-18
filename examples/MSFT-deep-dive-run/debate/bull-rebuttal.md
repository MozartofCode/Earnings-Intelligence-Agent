# Bull rebuttal · MSFT · 2026-11-18 · price $508.29 [D6]

## Pillar 1: "The backlog depends on one non-exclusive counterparty, and it has stalled." **Reframe (partial concede)**
- **Accepted:** OpenAI is ≥ ~32% of RPO (lower bound checks), non-exclusive [I12], with new "renegotiation" language [F2].
- **Contested:** ex-OpenAI RPO (up to ~$460B, est.) grew +25%. All FY26 Q4 sequential RPO growth, and "nearly 90%" of FY26 Microsoft Cloud revenue ($214B), came from non-frontier-lab customers [E4].
- **Receivable:** $7.2B on $10.0B quarterly revenue is ~65 days (est.), inside Microsoft's 81–91-day DSO band [D1][F-F6].
- **"Flat" RPO** rose +8% in three quarters while Azure burned +48% growth out of it (judgment: bookings ≈ burn).
- **Conceded:** bookings −12% [E7] and no FY27 Q1 ex-OpenAI figure [E-OQ]. Cost: probability, not value.

## Pillar 2: "Reported FCF overstates cash, increasingly." **Concede**
- I already could not answer the lease wave: $364.6B uncommenced, depreciation $11.1B vs $7.1B [D1].
- **One item contested:** forensics judges the $26.6B TTM component outflow a timing item [F-Table 1, Judgment], so run-rate lease-loaded FCF is nearer $39.3B than $12.7B.
- Depreciation rose $4.0B y/y as operating margin *expanded* 48.9% → 49.8% [D5]. The $25B bond leaves net cash unchanged at issuance [BE2].
- **Cost:** on the bear's lease-loaded basis my bull falls from $605 to ~$474 (−7%) (below).

## Pillar 3: "The price needs margins Microsoft has never earned post-SBC, on a lease-loaded basis." **Reframe (partial concede)**
- **Horizon:** the 31.1% break-even assumes a 10-year fade; on 15 years the price needs 17.8% growth at 25%, today's rate [V2].
- The bear's own inputs at the desk's base 8.5% / 3.0% on 15 years give $334, not $226 [BU4]: ~$108 of its $282 gap is discount-rate and horizon choice, not business evidence.
- **Multiple:** de-rating to 21.1x peer EV/EBIT is −8%, and the premium is earned (margin +15 pts, ROIC +5 pts) [V4].
- **Conceded:** lease-loaded, my 20% growth needs a 22.6% margin to justify price; duration is judgment (my 10-year fade: $443) [BU1].

| Lease-loaded run (start 7.7%, net debt $42.0B, 8.5% / 3.0%, 15 yrs) [BU4] | Value | vs price |
|---|---|---|
| Bear inputs: g 15%, m 20% | $334 | −34% |
| Bull, lease-loaded: g 20%, m 21% (≈27% ex-leases) | $474 | −7% |
| g 20%, m 22% | $496 | −2% |

## Pillar 4: "AI-infrastructure structure is worsening; Microsoft is losing share." **Reframe**
- **Share:** the 1-pt loss is real (est.); AWS lost 3 [I11]. Azure's +48% uses the FY27 recast definition, so the comparison is not clean [E-Table 1 †] (judgment).
- **Margins:** gross margin fell 69.8% → 67.7% [D5], but opex +6% with headcount −2% lifted operating margin [E-F2].
- **Conceded:** structure is Deteriorating; Oracle's $664B RPO sits on the same labs [I8]. The bear accepts M365 pricing power [I2].

Updated probability: 20% (from the desk's 25% [V3]); bull value marked to $474 lease-loaded, $605 if lease additions fade.

Deciding question: by the FY28 capex framework (late July 2027), does capex plus finance-lease additions fall as a share of revenue while ex-OpenAI RPO still grows +25% or more?

## Sources
- [BU1] data/dcf-bu-15y-g20-m27.json, dcf-bu-10y-g20-m27.json (dcf.py, 2026-11-18)
- [BU4] data/bull-rebuttal-dcf-leaseloaded-15y-g15-m20.json, -g20-m21.json, -g20-m22.json (dcf.py --manual --exclude-leases, revenue $346.4B, FCF margin 7.7%, net debt $42.0B incl. $71.0B leases, 7.446B shares, 2026-11-18)
- [E4] data/web/transcript-FY26Q4.txt (Microsoft FY26 Q4 call, 2026-07-29), lines on RPO and Microsoft Cloud mix
- [D1] [D5] [D6], [E7], [E-OQ], [E-Table 1], [E-F2], [F2], [F-F6], [F-Table 1], [V2] [V3] [V4], [I2] [I8] [I11] [I12], [BE2]: as defined in DATA-BRIEF.md, memos/*.md and debate/bear.md
