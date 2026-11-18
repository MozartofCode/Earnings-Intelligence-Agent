---
name: bull-bear-debate
description: >-
  Adversarial bull vs bear stock debate - dispatches independent bull-analyst and bear-analyst subagents to steelman each side with sourced evidence (SEC filings, earnings releases, cited data), runs a rebuttal round where each side answers the other's top 3 points, then a judge synthesis that names the 2-3 variables that decide who is right, what evidence would settle each, a probability-weighted view, a pre-mortem and a pre-parade. Verdict like "Edge: Bulls (60/40)". No strawmen. Use when the user asks for "bull vs bear", "bull case and bear case", "steelman the short", "what's the bear case", "argue both sides", "devil's advocate", "stress-test my thesis", "why could this stock fail", "red team my idea", "should I buy or sell", or "what am I missing".
license: MIT
compatibility: Uses the bull-analyst and bear-analyst subagents when available; Python 3.8+ and internet access to sec.gov for the data scripts.
metadata:
  category: "5-thesis-desk"
  version: "1.0.0"
  author: "earnings-desk"
---

# bull-bear-debate · steelman both sides, then decide what actually matters

Most research is a bull case wearing a lab coat. This skill forces real adversarial work: two analysts who each **fully commit** to opposite sides and build their case from evidence, a rebuttal round, and a judge who has to name the few variables that decide the outcome and what would change the verdict.

## When to use
- "Bull vs. bear on TSLA", "steelman the short case on NVDA", "stress-test my thesis on COST", "what am I missing?".
- Before starting a position, or when conviction is high and nobody has argued back.
- **Not** for a quick valuation (`reverse-dcf`) or for ongoing monitoring (`thesis-tracker`, which can take this debate's output as its starting point).

## Inputs
- `TICKER` (required). Optional: the user's own thesis (to put on trial), a horizon (default 2 years), and focus areas.

> **Paths:** `${CLAUDE_SKILL_DIR}` is this skill's own folder. Claude Code fills it in automatically; in other tools, replace it with the folder that contains this `SKILL.md`. Sibling skills such as `${CLAUDE_SKILL_DIR}/../sec-edgar` are installed next to it.

## Workflow

### 1. Shared fact base (both sides use the same facts)
Build a compact fact pack *before* either side argues, so the debate is about interpretation, not about whose numbers are right. Commands are relative to this skill folder:
```bash
python3 ${CLAUDE_SKILL_DIR}/../financial-statements/scripts/statements.py TICKER --years 5 --quarters 8
python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/edgar.py earnings-release TICKER
python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/edgar.py filing-text TICKER --form 10-K --section 1A
python3 ${CLAUDE_SKILL_DIR}/../filing-diff/scripts/diff_sections.py TICKER --form 10-K --section 1A
python3 ${CLAUDE_SKILL_DIR}/../forensic-accounting/scripts/scores.py TICKER
python3 ${CLAUDE_SKILL_DIR}/../reverse-dcf/scripts/dcf.py TICKER --price P        # what's priced in (cite P)
python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/edgar.py insiders TICKER --days 365
python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/market.py quote TICKER
```
Summarize it in ≤ 40 lines: growth and margin trajectory, balance sheet, implied expectations (reverse DCF), latest guidance, notable risk-factor changes, forensic flags and insider activity. Every line cites its source. If prior earnings-desk reports exist in `earnings-desk-reports/` (moat, comps, recap), include their verdicts.

### 2. Independent opening cases (in parallel, blind to each other)
Dispatch the **`bull-analyst`** and **`bear-analyst`** subagents at the same time. Give each the ticker, horizon, fact pack and the rules below. **Neither sees the other's case.**
> If subagents are unavailable, write each case in a separate pass, fully committing to it. Write the full bull case first as if you were its most convinced advocate, then start the bear case fresh, without softening it to fit the bull case you just wrote.

Each opening case must contain:
- **Thesis in 3 sentences.**
- **3–5 pillars**, each with evidence (number plus source) and the mechanism (why it leads to the stock going up or down).
- **Valuation view:** what the price implies (from the reverse DCF) and why it's too low or too high, with a target or scenario values and explicit drivers.
- **Catalysts** with expected timing.
- **The strongest point against their own side, and why it doesn't change their view.** This is the anti-strawman check.

### 3. Rebuttal round
Send each side the other's opening case (via `SendMessage` to the same subagent, or a separate pass). Each answers the **other side's top 3 points** directly: concede, contest (with counter-evidence), or reframe (the point is true but immaterial or already priced in). No new pillars are allowed in this round. Concessions are a strength, not a failure.

### 4. Judge synthesis (you, neutral)
Score the arguments on evidence quality, not rhetoric. Produce:
1. **Key debate variables (2–3):** the few things that actually decide who is right, e.g. "Data-center capex durability past 2027", "Gross margin floor under competition". Most pillars collapse into these.
2. **For each variable:** bull view vs. bear view, current evidence, **what evidence would settle it** (a specific metric, threshold and date: "If Q2 FY27 gross margin < 70%, bears win this variable"), and the judge's lean.
3. **Probability-weighted view:** bull / base / bear scenario values (from reverse-dcf runs with each side's drivers), probabilities summing to 100%, the expected value vs. price, and the asymmetry (upside/downside ratio).
4. **Pre-mortem:** "It's 2 years from now and owning this was a disaster. Why?" List the 3 most plausible failure paths, each with an early-warning sign.
5. **Pre-parade:** "It's 2 years from now and this was a huge winner. Why?" List the 3 most plausible success paths and their early signs. (This keeps the judge from defaulting to cynicism.)
6. **Verdict:** `Edge: Bulls (60/40)` / `Edge: Bears (65/35)` / `Too close to call (50/50)`. The split is the judge's probability that the bull thesis plays out over the horizon.
7. **What would change the verdict:** 2–3 named, observable events. This is mandatory.

## Analysis framework

**Rules of engagement (strict)**
- **No strawmen.** Each side argues the *strongest* version of its case, the one a smart, informed holder or short-seller actually believes. The judge throws out any argument that misstates the other side.
- **Every claim cites evidence**: a filing (accession or section), a script output, or web data with site and date. An unsourced claim is labeled "assertion" and given no weight.
- **Same facts, different interpretations.** Disputes over facts go back to the primary source. Disputes over interpretation are the debate.
- **Steelman test:** each side must state the opposing case well enough that the other side would sign off on it.
- **The judge must name what would change the verdict.** A verdict that no evidence could change is an opinion, not research.

**Where good debates are won (what top analysts probe)**
- **Expectations vs. fundamentals:** a great company can be a bad stock. The bull must beat what's *priced in* (reverse DCF), not just show quality.
- **Second-order effects:** if bulls are right about demand, what happens to competition, capacity and pricing?
- **Duration:** bears often have the right facts on the wrong timing. Ask when the bear thesis shows up in the numbers.
- **Variant perception:** where exactly does each side differ from consensus, and why is the market wrong? A side that agrees with consensus has no edge.
- **Base rates:** how often do companies sustain the growth or margins the bull needs? How often do "obvious" short theses actually play out?
- **Accounting and incentives:** forensic flags, SBC, management compensation metrics, insider selling patterns.
- **Balance-sheet asymmetry:** leverage turns a bear thesis into a permanent capital loss.

**Weighting evidence:** primary filings > company-reported KPIs > cited third-party data > management commentary > sell-side or media opinion > anecdotes. Weight recent trend changes more than levels.

## Output
Report JSON per [../sec-edgar/references/report-schema.md](../sec-edgar/references/report-schema.md), `"skill": "bull-bear-debate"`.
- **Title idea:** `"The bulls have the *better evidence*"` / `"A debate about *one number*"`.
- **Verdict:** `{"label": "Edge", "value": "Bulls 60/40", "sub": "Decided by gross-margin durability", "tone": "pos" | "neg" | "neutral"}`.
- **KPIs (3–6):** price (cited), implied 10-yr growth (reverse DCF), bull / bear scenario values, probability-weighted value vs. price, upside/downside ratio.
- **Sections:**
  1. *Fact base*: a compact table (metric, value, source).
  2. *Bull case*: thesis, pillars as `pos` callouts with evidence, valuation, catalysts, strongest counterpoint.
  3. *Bear case*: the same structure with `neg` callouts.
  4. *Rebuttals*: a table (point, raised by, response: concede / contest / reframe, judge's ruling).
  5. *Key debate variables*: a table (variable, bull view, bear view, settling evidence + date, lean), plus `scores` bars for the judge's lean per variable.
  6. *Probability-weighted view*: a scenario table (case, drivers, value, probability) with the weighted value.
  7. *Pre-mortem & pre-parade*: `warn` and `pos` callouts, each with an early-warning sign.
  8. *What would change the verdict*: an `accent` callout.
- **Sources:** all accessions, script outputs, cited web sources (site, date). Note which side used which.

Render:
```bash
python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/render_report.py /tmp/TICKER-bull-bear-debate.json --out-dir earnings-desk-reports
```
**In chat:** "Edge: Bulls (60/40). The debate comes down to (1) … and (2) …. The verdict flips if …." Then the report paths, and an offer to save the key variables as KPIs with `/earnings-desk:thesis-tracker`.

## Quality bar & pitfalls
- Both cases should be good enough that a reader can't tell which one the judge favors until the synthesis.
- Don't split the difference by reflex. 50/50 is a valid verdict only when the evidence is genuinely balanced, and you must say why.
- Debate variables must be **observable** (a metric, date or event), not vibes like "execution".
- Don't let one side bring in uncited "facts". Send them back to the primary source.
- Keep the user's own thesis on trial like any other. Don't flatter it.
- Facts (fact base) vs. advocacy (cases) vs. judgment (synthesis) must be visibly separated.

## Next skills
`/earnings-desk:thesis-tracker` (turn the debate variables into tracked KPIs and kill criteria) · `/earnings-desk:reverse-dcf` (refine scenario values) · `/earnings-desk:moat-analysis` · `/earnings-desk:forensic-accounting` · `/earnings-desk:earnings-preview` (the next settling event).

_Not investment advice. Both cases are constructed arguments; the verdict is a judgment, not a recommendation. Do your own research._
