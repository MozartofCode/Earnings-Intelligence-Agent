---
ticker: TICKER
company: Company Name
created: YYYY-MM-DD
last_reviewed: YYYY-MM-DD
status: Intact            # Intact | Under pressure | Broken
conviction: 3             # 1 (low) to 5 (high); the user's call, updated with reasons
horizon: 2-3 years
direction: long           # long | short | watch
reference_price: 0.00     # price when the thesis was written (source, date in the log)
---

# TICKER · investment thesis

## Thesis (3 sentences)
1. **What the market misses:** <the variant perception, i.e. where you differ from consensus and why>
2. **Why it will happen:** <the mechanism: product, cycle, margin, capital allocation>
3. **Why now / what it's worth:** <catalyst path and the value it implies vs. what's priced in>

## Pillars and KPIs
Every pillar has a measurable KPI with explicit thresholds. "Weakening" and "broken" are defined in advance, not after the print.

| # | Pillar | KPI (source) | Baseline (date) | Intact if | Weakening if | Broken if | Latest | Status |
|---|---|---|---|---|---|---|---|---|
| P1 | <e.g. Data-center demand stays strong> | Data-center revenue y/y (10-Q segment note) | +X% (Qn FYxx) | ≥ +20% | +10% to +20% | < +10% for 2 qtrs | | Intact |
| P2 | <e.g. Pricing power holds> | Gross margin % (statements.py) | X% | ≥ 70% | 65–70% | < 65% | | Intact |
| P3 | <e.g. Capital returned sensibly> | Net share count y/y (statements.py) | -X% | ≤ 0% | 0 to +2% | > +2% | | Intact |

## Kill criteria (pre-committed: "I'm wrong if…")
Write these on day one, while you're unbiased. If one is hit, the thesis is **Broken** unless you write down, in the log, a reason it doesn't apply. That reason should be held to a high bar.
- [ ] K1: <e.g. Lose the #1 customer or any customer > 10% of revenue>
- [ ] K2: <e.g. Gross margin below 60% for two consecutive quarters>
- [ ] K3: <e.g. Management guides FY revenue growth below 10%>
- [ ] K4: <e.g. Forensic red flag: Beneish M-score > -1.78 or auditor change>

## What's priced in (reference)
- Reverse DCF at reference price: implied 10-yr revenue CAGR X%, implied FCF margin Y% (dcf.py, WACC Z%, date).
- Bull / base / bear values: $A / $B / $C (drivers in the log entry of DATE).

## Catalyst calendar
| Date (expected) | Event | What would confirm | What would hurt | Pillar |
|---|---|---|---|---|
| YYYY-MM-DD | Qn earnings | | | P1, P2 |
| YYYY-MM-DD | Investor day / product launch / regulatory decision | | | |

## Position notes (user-owned)
_Sizing, entry/exit levels and portfolio fit are the user's decisions. The tracker records them but doesn't set them._
- Size / max size:
- Add if:
- Trim if:

## Log (newest first)
### YYYY-MM-DD · Review after <event> · Status: Intact · Conviction: 3 → 3
- **Data pulled:** <filings / accessions, price + source>
- **Pillars:** P1 Intact (KPI value vs. threshold), P2 …, P3 …
- **Kill criteria:** none hit
- **What changed:** <new facts, with sources>
- **Conviction change and why:** <one line>
- **Next check:** <date / event>

### YYYY-MM-DD · Thesis created · Status: Intact · Conviction: 3
- **Origin:** <e.g. bull-bear-debate report earnings-desk-reports/TICKER-bull-bear-debate-DATE.html>
- **Reference price:** $X (source, date)
