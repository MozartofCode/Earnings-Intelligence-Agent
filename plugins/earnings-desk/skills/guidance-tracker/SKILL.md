---
name: guidance-tracker
description: >-
  Management credibility scorecard built from primary sources. Collects every metric a company has guided (revenue, gross or operating margin, EPS, capex, free cash flow, segment and KPI targets) from past 8-K earnings releases and calls, matches each guide with the actual reported the following quarter or year, and computes the hit rate, average beat versus its own guide, midpoint bias and how guidance evolves through the year. Classifies management as sandbagger, straight shooter or over-promiser, and flags metrics that were withdrawn, narrowed, widened or quietly dropped (a company that stops guiding a metric is telling you something). Use it when the user asks "can I trust management's guidance", "do they sandbag", "how good is their guidance", "guidance track record", "do they usually beat and raise", "is this guide conservative", "management credibility", or "they stopped guiding X, why". Ends with a "Guidance credibility" verdict.
license: MIT
compatibility: Requires Python 3.8+ and internet access to sec.gov. Web search optional for call-only guidance.
metadata:
  category: "2-earnings-season"
  version: "1.0.0"
  author: "earnings-desk"
---

# guidance-tracker · does management's word hold?

A guide is only as good as the team that issues it. Some managements set bars they can clear by 3% every quarter; some guide to hope and cut in Q3. Knowing which one you own changes how you read every number they give. This skill builds the record from the company's own filings.

## When to use
- Before trusting a new guide (on its own, or inside `earnings-preview` / `earnings-recap`).
- When a company changes how it guides: drops a metric, switches to annual-only, moves from GAAP to adjusted, widens ranges.
- When management changes (new CEO/CFO): compare the guiding style before and after.
- **Not** for a single quarter's beat/miss (use `earnings-recap`) or call language (use `transcript-decoder`).

## Inputs
- `TICKER` (required).
- `lookback` (optional): number of quarterly releases, default 12 (3 years), max ~20.
- `metrics` (optional): restrict to specific metrics; default is every guided metric found.

> **Paths:** `${CLAUDE_SKILL_DIR}` is this skill's own folder. Claude Code fills it in automatically; in other tools, replace it with the folder that contains this `SKILL.md`. Sibling skills such as `${CLAUDE_SKILL_DIR}/../sec-edgar` are installed next to it.

## Workflow
1. **Inventory the releases.**
   `python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/edgar.py filings TICKER --forms 8-K --limit 80` and keep those with items containing `2.02`. Then pull each release, saving to disk to protect context:
   ```bash
   for i in $(seq 0 11); do python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/edgar.py earnings-release TICKER --index $i --max-chars 150000 > /tmp/TICKER-er$i.json; done
   ```
   Some companies give guidance only on the call or in a separate investor presentation (often filed as Ex.99.2, which `earnings-release` includes when present). For call-only guidance, web search the transcript (IR site first) and cite it. Some guide only at an annual investor day: capture that too, with the date.
2. **Extract every guide.** Search each release for "outlook", "guidance", "expects", "anticipates", "for the fourth quarter", "full year", "fiscal 20", "range", "approximately". For each statement record: issue date, accession, period guided (Q or FY, with fiscal label), metric, basis (GAAP / non-GAAP / constant currency / organic), low, high, midpoint, and any stated assumptions (FX rate, tax rate, share count, M&A excluded). Store as a table. Point estimates have low = high; "at least X" gets low = X and no high (note it).
3. **Get the actuals.** For each guided period, the actual comes from the release reporting that period (same basis as the guide). Cross-check revenue, margins, EPS, capex with XBRL: `python3 ${CLAUDE_SKILL_DIR}/../financial-statements/scripts/statements.py TICKER --years 5 --quarters 12` or `python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/edgar.py facts TICKER --periods 12 --annual 5`. Non-GAAP actuals come from the release reconciliation only.
4. **Score each guide-actual pair** (framework below). Build the guidance evolution path for each fiscal year (initial FY guide → each update → actual).
5. **Look for regime changes.** Metrics added, dropped, switched basis, ranges widened, guidance suspended, cadence changed (quarterly → annual), and management changes in the window (8-K Item 5.02, `python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/edgar.py filings TICKER --forms 8-K --limit 80` and check items).
6. **Optional context.** `python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/market.py reactions TICKER --n 12` to see whether guide raises or cuts drove the reactions. Consensus at guide time (web search, cited) tells you whether the guide landed above or below the street.
7. Write and render the report.

## Analysis framework

### Pair-level metrics
For each guided metric and period:
- `surprise_vs_mid % = (actual − midpoint) / |midpoint|`. For margins, use bps: `actual − midpoint`.
- `position`: below low / low half / high half / above high. **Hit** = actual ≥ low (for costs like capex or opex, "hit" means within range; overshoot is not automatically good).
- `range_width % = (high − low) / midpoint`. Track it over time.
- For EPS guides, separate how much of the beat came from the tax rate and share count vs. operations (reuse `earnings-recap` attribution when the data allows).

### Company-level metrics
- **Hit rate** = hits / guides, per metric and overall. Report `n` (fewer than 6 pairs = low confidence; say so).
- **Average beat vs. own guide** = mean of `surprise_vs_mid`, and the median (less sensitive to one blow-out quarter).
- **Consistency** = standard deviation of `surprise_vs_mid`. Low std + positive mean = a deliberate cushion.
- **Above-high rate** = share of actuals above the top of the range. > 75% means the range is a floor in practice, and the street knows it.
- **FY guide drift** = (final actual − initial FY midpoint) / initial midpoint. Shows whether the year starts conservative.
- **Raise pattern**: share of quarters with an FY raise; average raise size vs. the quarterly beat size. "Raise by the beat" (raise ≈ beat) means the remainder of the year is unchanged; "raise by less than the beat" means an implied cut to later quarters.

### Bias classification
| Class | Rule of thumb (revenue/EPS, ≥ 6 pairs) |
|---|---|
| **Sandbagger** | Hit rate ≥ 90%, mean beat vs. midpoint ≥ +2% (revenue) or ≥ +5% (EPS), above-high rate ≥ 60% |
| **Straight shooter** | Hit rate 70-90%, mean beat within ±1.5% (revenue) / ±4% (EPS), actuals cluster within the range |
| **Over-promiser** | Hit rate < 70%, or mean beat < −1% (revenue) / < −3% (EPS), or ≥ 2 FY guide cuts in 3 years |
| **Erratic** | Std of surprise > 2× the mean absolute surprise; big beats and misses alternate |
State the class per metric when they differ (e.g. sandbags revenue, over-promises margin, a common pattern when growth investments are under-budgeted).

**Why it matters:** for a sandbagger, consensus already sits above the guide and a "beat" of the usual size is neutral; a smaller beat is a miss. For an over-promiser, haircut the guide by the historical average shortfall before comparing with consensus. Provide that **credibility-adjusted guide** for the current period: `adjusted = current midpoint × (1 + median historical surprise)`. Label it an estimate.

### Red flags (each one gets a callout)
- **Dropped metric:** guided for ≥ 4 quarters, then gone. Check what the metric did just before (it usually deteriorated). Treat as a negative signal until management explains it on the record.
- **Basis switch:** GAAP → non-GAAP, reported → organic/constant currency, EPS → "adjusted EBITDA". Often hides a deterioration on the old basis.
- **Cadence downgrade:** quarterly → annual-only, or guidance suspended ("given macro uncertainty"). Compare with peers: if peers still guide, it's company-specific.
- **Range widening** ≥ 50% vs. prior year at the same point in the year = falling visibility.
- **Q4 hockey stick:** FY guide maintained while YTD actuals imply an H2 or Q4 that is far above the run-rate (implied Q4 growth > 1.5× YTD growth).
- **Assumption creep:** tax rate, FX or share-count assumptions that conveniently changed to hold EPS guidance.
- **Long-term targets** (investor-day "2028 targets") quietly re-dated or no longer mentioned.
- **New management resets:** the first guide after a CEO/CFO change is often deliberately low ("kitchen sink"). Don't let one reset skew the classification; show pre/post separately.

### Questions a great analyst asks
1. Is the cushion constant (deliberate) or shrinking (losing visibility, or running out of conservatism)?
2. Which metric does management guide most conservatively, and is that the metric the stock trades on?
3. When they missed, was it macro (peers missed too, see `read-through`) or execution?
4. Did they ever withdraw a metric right before it turned negative?
5. Does the current guide sit above or below the credibility-adjusted level?

### Verdict (Guidance credibility)
`High (reliable sandbagger)`, `High (straight shooter)`, `Medium`, `Low (over-promiser)`, or `Low (erratic)`, with the sub-label naming the dominant pattern and confidence (pairs counted).

## Output
Write `/tmp/<TICKER>-guidance-tracker.json` per `../sec-edgar/references/report-schema.md`.
- `skill`: `"guidance-tracker"`; `title` e.g. `"A *reliable* sandbagger"` or `"Guides to hope, *cuts in Q3*"`; `subtitle`: "12 quarters of guidance, Q1 FY24 - Q4 FY26".
- `verdict`: `{label: "Guidance credibility", value: "High | Medium | Low", sub: "Sandbagger · 11/12 above midpoint", tone: pos | neutral | neg}`.
- `kpis` (4-6): Revenue hit rate (n), Avg beat vs. own midpoint, Above-high rate, FY guide drift (avg), # dropped metrics, Credibility-adjusted current guide.
- `sections`:
  1. **Scorecard by metric** — table: metric, basis, # pairs, hit rate, mean/median surprise, above-high rate, class; `scores` bars for hit rate per metric.
  2. **Guide vs. actual** — chart: bar (actual) + line (guide midpoint) for revenue per quarter; table of all pairs (period, issued, low, high, actual, surprise pill).
  3. **How the year evolves** — table per fiscal year: initial FY guide, each update, actual; FY drift.
  4. **Regime changes and red flags** — callouts: dropped/added metrics, basis switches, cadence changes, management changes.
  5. **Reading the current guide** — current guide, consensus (cited), credibility-adjusted guide (labeled estimate), what it implies.
  6. **Method** — matching rules, basis, sample size caveats.
- `sources`: every 8-K accession used (one per release), 10-Q/10-K accessions for XBRL actuals, transcript URLs for call-only guidance.

Render:
```bash
python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/render_report.py /tmp/<TICKER>-guidance-tracker.json --out-dir earnings-desk-reports
```
Fix warnings. In chat: verdict, hit rate and mean beat for revenue and EPS, any dropped metric, the credibility-adjusted current guide, and the HTML + Markdown paths.

## Quality bar & pitfalls
- **Match bases exactly.** Non-GAAP EPS guide vs. non-GAAP actual; constant-currency guide vs. constant-currency actual.
- Use the **latest guide before the period ended** for quarter scoring, and the initial guide for FY drift. Say which.
- M&A: a guide that excluded a later acquisition must be compared with the actual excluding it (or flagged).
- Restatements and recasts (segment changes) break series; note seams.
- Fewer than 6 pairs: classify as "insufficient history" rather than forcing a label.
- Don't count qualitative guidance ("we expect growth to accelerate") as a numeric pair, but do log it and grade it (happened / didn't).
- Every pair cites two accessions: where the guide was issued and where the actual was reported.

Next: `/earnings-desk:earnings-preview` to apply the credibility-adjusted guide to the coming print, `/earnings-desk:transcript-decoder` to hear how management talks about the guide, `/earnings-desk:thesis-tracker` to log credibility as a thesis input.

_Not investment advice. Data is from public filings and may contain errors; verify before acting._
