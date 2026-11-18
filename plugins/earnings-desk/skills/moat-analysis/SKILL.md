---
name: moat-analysis
description: >-
  Competitive moat and durable-advantage analysis - scores a company on Hamilton Helmer's 7 Powers (scale economies, network effects, counter-positioning, switching costs, brand, cornered resource, process power) and Porter's five forces using hard evidence from SEC filings (10-K competition section, segment margins, ROIC persistence, gross-margin stability through cycles, customer concentration, R&D intensity) plus cited market-share data. Maps threats (disruptors, regulation, substitutes) and judges whether the moat is widening, stable or narrowing. Verdict "Moat: Wide/Narrow/None, Trend". Use when the user asks "does it have a moat", "competitive advantage", "economic moat", "pricing power", "how defensible is the business", "competitive position", "who are the competitors", "network effects", "switching costs", "can competitors catch up", or "is the advantage durable".
license: MIT
compatibility: Requires Python 3.8+ (standard library only) and internet access to sec.gov. Web search used for market share (cited).
metadata:
  category: "4-valuation-competition"
  version: "1.0.0"
  author: "earnings-desk"
---

# moat-analysis · is the advantage real, and is it getting wider?

A moat is not a good product or a famous name. It's a structural reason that **returns stay above the cost of capital despite competition**. This skill demands proof: persistent ROIC, stable margins through bad years, and a named mechanism (one of Helmer's 7 Powers) that explains why rivals can't copy it profitably.

## When to use
- "Does AAPL have a moat?", "how defensible is SNOW?", "can AMD catch NVDA?", "is COST's advantage durable?".
- Before underwriting the long forecast period that `reverse-dcf` says the price needs.
- To decide whether a premium in `comps-valuation` is earned.
- **Not** for valuation (`reverse-dcf`, `comps-valuation`) or for accounting quality (`forensic-accounting`). A moat built on inflated earnings isn't a moat.

## Inputs
- `TICKER` (required). Optional: up to 3 key competitors to benchmark (default: the 10-K's named competitors plus `edgar.py peers`), and the years of history (default 10, as available).

## Workflow
Commands are relative to this skill folder. Save long filing text to disk and grep it (the `saved_to` field).

1. **The outcome test first: returns and margins over time.**
   `python3 ../financial-statements/scripts/statements.py TICKER --years 10 --quarters 12`
   Extract annual ROIC, gross margin, operating margin, R&D % and SBC % of revenue, plus revenue growth. Look at the **worst year** (recession, down-cycle, competitive shock): did gross margin hold within ~3 pts? Did ROIC stay above ~10%?
2. **Benchmark against competitors.** `python3 ../comps-valuation/scripts/comps.py TICKER COMP1 COMP2 COMP3 --no-quote` returns TTM margins, ROIC and growth side by side (no prices needed). Superior economics vs. direct rivals is the signature of power. Parity suggests no moat, whatever the narrative says.
3. **What the company says about competition.** `python3 ../sec-edgar/scripts/edgar.py filing-text TICKER --form 10-K --section 1` (Business: grep "compet", "customer", "patent", "network", "switching", "brand", "scale"). `--section 1A` (Risk Factors: grep "competition", "pricing pressure", "concentration", "regulat", "substitut"). Note the named competitors and the basis of competition the company claims (price, performance, ecosystem, service).
4. **Segments and concentration.** `--section 7` (MD&A) and `--section 8` (Notes) for segment revenue and operating income, customer concentration (">10% of revenue" disclosures), backlog/RPO, retention or net revenue retention if disclosed, and pricing commentary. Search for "price increase", "mix", "net revenue retention", "churn", "renewal".
5. **Trend of the moat language.** `python3 ../filing-diff/scripts/diff_sections.py TICKER --form 10-K --section 1A` shows new competition, regulation and substitute risks added this year. New named competitors or a new "pricing pressure" paragraph are early narrowing signals.
6. **Market share (external, cited).** Web-search industry share data (IDC, Gartner, Counterpoint, company investor days, trade bodies) for 3–5 years. Cite site and date for every point. If no credible data exists, say so.
7. **Threat map.** Disruptors (new tech, new business models), regulation and antitrust, substitutes, and customer or supplier bargaining shifts. Use 10-K risk factors, the filing-diff output and cited news.
8. **Score, judge the trend, render.**

## Analysis framework

**Step 1: Does the outcome prove a moat?** Use these thresholds as heuristics, not laws:
- **ROIC − WACC spread** sustained for 5–10 years. Over 10 pts persistently is strong evidence; under 3 pts or volatile is weak. Use statements.py `roic_pct` and compare with a ~8–10% WACC.
- **ROIC persistence:** research on corporate performance (e.g. Mauboussin's work on ROIC fade) shows high returns usually decay toward the average. A company whose ROIC *hasn't* faded over a decade is the exception that needs explaining.
- **Gross-margin stability:** standard deviation of annual gross margin under ~2 pts, and holding in the worst year, means pricing power. Falling gross margin while revenue grows means buying growth.
- **Pricing power signals:** price increases disclosed without volume loss, gross margin up through input-cost inflation, low promotional intensity.
- **Reinvestment at high returns:** growth funded by high-ROIC reinvestment (not acquisitions and goodwill) suggests a widening moat.
- If outcomes don't show it, the default verdict is **no moat**, however good the story.

**Step 2: Name the mechanism (Helmer's 7 Powers).** Each power needs a *benefit* (better price or lower cost) and a *barrier* (why rivals can't copy it profitably). Score each 0–5 with evidence:

| Power | Benefit / barrier | Evidence to look for | Red flags |
|---|---|---|---|
| **Scale economies** | Lower unit cost / rivals face share loss when matching | Fixed costs large vs. revenue (R&D, distribution, content); cost per unit falls with volume; op margin above smaller peers | Variable-cost business; subscale leader with peer-level margins |
| **Network economies** | Value per user rises with users / late entrants can't reach critical mass | Two-sided marketplace metrics, take-rate stability, user growth with flat S&M % | Multi-homing is easy; local or fragmented networks; falling take rates |
| **Counter-positioning** | Superior new model / incumbent won't copy for fear of cannibalizing | Incumbent's 10-K defending the legacy model; share shifting to the challenger | Incumbent has already copied it; challenger's economics unproven |
| **Switching costs** | Retention, price increases / customers face losses if they switch | Net revenue retention >110%, gross retention >90%, multi-year contracts, data or workflow lock-in, RPO growth | Rising churn disclosures; customers dual-sourcing; open standards eroding lock-in |
| **Branding** | Price premium for the same product / built over time, can't be bought quickly | Price premium vs. private label or generics, stable gross margin, low marketing % relative to the premium | Premium eroding; heavy promo; brand under ~10 years old |
| **Cornered resource** | Preferential access to a valuable asset / exclusive | Patents with remaining life, licenses, spectrum, unique talent, mineral rights, regulatory approvals | Patent cliff dates in the 10-K; key-person risk |
| **Process power** | Embedded organizational know-how / slow to replicate (years) | Persistent cost or quality lead (yields, turns, logistics), manufacturing benchmarks | Lead shrinking; competitors hiring the talent |

Scoring: **0** absent · **1** weak or anecdotal · **2** present but contestable · **3** clear, with evidence · **4** strong and quantified · **5** dominant and widening. A wide moat usually needs at least one power at 4+ backed by Step 1 outcomes. Helmer's point is that one real power beats several weak ones.

**Step 3: Porter's five forces (industry structure).** Rate each Low / Medium / High pressure with one line of evidence:
- *Rivalry*: number of players, growth rate, fixed-cost intensity, history of price wars.
- *Threat of entry*: capital needs, regulation, scale and network barriers.
- *Buyer power*: customer concentration (>10% customers), switching costs, buyer price sensitivity.
- *Supplier power*: single-source inputs (grep "sole source", "single supplier"), labor or union, key licensors.
- *Substitutes*: different technology meeting the same need. Price-performance trend of the substitute.
A great company in a brutal industry still has to fight. Industry structure caps the moat.

**Step 4: Moat trajectory.**
- *Widening:* market share rising with stable or rising margins, ROIC rising, retention up, new powers forming (e.g. scale turning into network effects).
- *Stable:* share and margins flat, returns high and steady.
- *Narrowing:* share loss, gross margin compression, new competitors named in risk factors, rising S&M % to defend share, regulatory action, a technology shift that makes the barrier obsolete.

**Analyst questions**
1. If a well-funded competitor (big tech, PE, China) attacked tomorrow, what exactly would stop them? How long would it take, and what would it cost?
2. Would customers notice, and care, if the company disappeared?
3. Is the advantage at the level of the company, the product, or a person?
4. What has to happen for ROIC to fade to WACC, and is it happening somewhere already?
5. Is the moat priced in? Cross-check the forecast horizon in `reverse-dcf`.

## Output
Report JSON per [../sec-edgar/references/report-schema.md](../sec-edgar/references/report-schema.md), `"skill": "moat-analysis"`.
- **Title idea:** `"A moat that keeps *widening*"` / `"Great product, *no moat*"`.
- **Verdict:** `{"label": "Moat", "value": "Wide" | "Narrow" | "None", "sub": "Trend: Widening | Stable | Narrowing", "tone": "pos" | "warn" | "neg"}`.
- **KPIs (3–6):** 10-yr median ROIC (and spread over an assumed WACC), gross-margin range (min–max), worst-year op margin, market-share trend (cited), top power score, R&D % of revenue.
- **Sections:**
  1. *Outcome test*: a line chart of ROIC % and gross margin % over 10 years; a table of the worst year vs. the average; peer comparison table from comps.py.
  2. *7 Powers scorecard*: `scores` bars (pct = score × 20, value "3/5") plus a table (power, score, evidence, source).
  3. *Five forces*: a table (force, pressure, evidence).
  4. *Market share*: a table or chart (cited, with year and source per point).
  5. *Threat map*: callouts by tone (disruptor, regulation, substitute), each with likelihood and timing.
  6. *Trajectory and what would change it*: callouts for the signals to watch, which become `thesis-tracker` KPIs.
- **Sources:** 10-K accessions and sections, statements.py accessions, market-share sources (site, date).

Render:
```bash
python3 ../sec-edgar/scripts/render_report.py /tmp/TICKER-moat-analysis.json --out-dir earnings-desk-reports
```
**In chat:** "Moat: Narrow, Trend: Stable. The power is switching costs (4/5: NRR 115%, 3-yr contracts); ROIC has held 25–30% for 8 years. The main threat is X." Then the report paths.

## Quality bar & pitfalls
- **Evidence, not adjectives.** Each score cites a number or a filing passage. "Strong brand" without a price premium scores 1 at most.
- Separate company-reported claims (10-K marketing language) from verified outcomes (margins, retention numbers).
- Watch for goodwill-inflated or buyback-distorted ROIC (negative equity). Use the operating-asset view and say so.
- High margins in a hot cycle aren't a moat. Check the down years.
- Market-share figures vary by source and definition. Cite them, and note the definition (units vs. revenue, segment scope).
- Don't confuse size with scale economies. Big but with peer-level margins means no scale advantage.
- Facts (filings, cited data) and judgment (scores, trajectory) are visibly separated.

## Next skills
`/earnings-desk:reverse-dcf` (does the price assume the moat lasts?) · `/earnings-desk:comps-valuation` (is the premium earned?) · `/earnings-desk:capital-allocation` (is the moat being reinvested in?) · `/earnings-desk:bull-bear-debate` · `/earnings-desk:thesis-tracker` (track the trajectory signals).

_Not investment advice. Competitive assessments involve judgment; verify sources and do your own research._
