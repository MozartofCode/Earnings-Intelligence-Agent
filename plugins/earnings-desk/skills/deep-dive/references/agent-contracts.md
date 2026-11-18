# Desk agent contracts

This is the exact output contract for every role in a deep dive. Agents read it, and so does the orchestrator when it plays the roles itself in sequential fallback mode. A contract exists so that the next reader (another analyst, the PM, the user) can find the same thing in the same place every time.

---

## 1. Run directory layout
```
.earnings-desk/runs/<TICKER>-<YYYY-MM-DD>/
├── README.md              # manifest: ticker, mode, focus, absolute tool paths, file index   (orchestrator, Phase 0)
├── DATA-BRIEF.md          # cited fact sheet + data-quality log                               (data-analyst, Phase 1)
├── data/                  # raw script JSON: quote, profile, filings, facts, statements, scores,
│   │                      # reactions, estimates, surprises, calendar, insiders, peers, release-*,
│   │                      # 10k-*, 10q-*; later dcf-*.json, comps.json, diff-*.json added by specialists
│   └── text/              # plain-text sections: 10k-business, 10k-risk, 10k-mdna, 10q-mdna, release-0, release-1
├── memos/                 # earnings.md · forensics.md · valuation.md · industry.md         (Phase 2)
├── debate/                # bull.md · bear.md · bull-rebuttal.md · bear-rebuttal.md         (Phase 3)
└── pm/                    # decision.md · report.json                                        (Phase 4)
```
Rules: **append, don't overwrite** another role's file. A specialist that fetches extra data saves it to `data/` with a descriptive name and lists it in its memo's Sources, so later roles can reuse it.

## 2. README.md manifest (orchestrator writes it in Phase 0)
```markdown
# Deep dive · NVDA · 2026-11-16
- Company: NVIDIA Corp (CIK 0001045810, Nasdaq) · FY ends late January
- Mode: full | quick · Focus: none | earnings | valuation | forensics
- Run dir (absolute): /path/to/project/.earnings-desk/runs/NVDA-2026-11-16
- Keys: FMP no · Finnhub yes · Alpha Vantage no · SEC_USER_AGENT set   (from market.py status)

## Tools (absolute paths: agents' cwd is the user's project, not the plugin)
S=/abs/path/to/plugins/earnings-desk/skills
RUN=/abs/path/to/project/.earnings-desk/runs/NVDA-2026-11-16
python3 $S/sec-edgar/scripts/edgar.py · market.py · render_report.py
python3 $S/financial-statements/scripts/statements.py
python3 $S/forensic-accounting/scripts/scores.py
python3 $S/reverse-dcf/scripts/dcf.py
python3 $S/comps-valuation/scripts/comps.py
python3 $S/filing-diff/scripts/diff_sections.py
Contracts: $S/deep-dive/references/agent-contracts.md · Memo template: $S/deep-dive/references/memo-template.md

## File index
(updated after each phase: file, owner, status)
```

## 3. Rules for every role
1. **Cite every number** with a source ID. IDs are prefixed by role so the PM can merge them without collisions: data `[D#]`, earnings `[E#]`, forensics `[F#]`, valuation `[V#]`, industry `[I#]`, bull `[BU#]`, bear `[BE#]`, PM `[PM#]`. Reusing another role's ID is encouraged. Every ID is defined in the file's **Sources** section as one of: `form, period, filed date, accn, URL`; `data/<file>.json (<script>, <date>)`; or `web search: <site>, <retrieved date>`.
2. **Fact vs. judgment:** facts go in Key findings and Evidence. Opinions go in **Judgment**, or are prefixed `Judgment:`. Estimates are labeled `(est.)`.
3. **No fabrication.** Missing means "not disclosed / not found". A role that cannot do a test says so in Open questions.
4. **Skeptical by default.** Management adjectives are not evidence. Third-party allegations are labeled as allegations.
5. **No advice language** in any file: no buy, sell, short, target price or position sizing. Scenario values are "value if assumptions hold".
6. **Human number formats:** `$96.2B`, `$2.46`, `+106% y/y`, `+40 bps`, `24.5x`. Fiscal labels plus period-end dates.
7. **Length limits** exclude tables and Sources. Going over means you did not prioritize.

## 4. Return summary (every agent → orchestrator, 200 words or fewer)
```
FILE: <absolute path>
SCORECARD: <the scorecard block collapsed to one line>
TOP FINDINGS: 1) … 2) … 3) …   (each with a number and source ID)
OPEN QUESTION: …
DATA ISSUES: … | none
```

## 5. DATA-BRIEF.md (data-analyst, 900 words or fewer)
Sections in order: Identity · Market snapshot · Financial snapshot (5 FY + 8 quarters + TTM table) · Latest print (incl. the guidance sentence quoted verbatim) · Scores at a glance (values only) · Insiders and peers · File index (incl. `saved_to` full-filing paths) · **Data-quality log** · Sources `[D#]`.

## 6. Specialist memo contract (memos/earnings.md, forensics.md, valuation.md, industry.md)
900 words or fewer (1,400 for the **lead** lens in focus mode; 450 for a **support** lens). Sections in this order, with these exact headings:
````markdown
# <Lens> memo · <TICKER> · <date>
```scorecard
lens: …
<lens-specific keys, see below>
confidence: High | Medium | Low
```
## Bottom line
≤ 3 sentences. The answer for this lens, with the single most important number.
## Key findings
3–7 numbered findings. Each: claim → number(s) → source ID. Facts only.
## Evidence
Tables (time series, scores, scenarios, comps). Each table has a caption and sources.
## Judgment
The analyst's interpretation, clearly labeled. What the facts mean for the investment case.
## Debate fodder
- Strongest bull point from this lens: … [ID]
- Strongest bear point from this lens: … [ID]
## Open questions
What could not be verified, and what would resolve it.
## What would change my mind
2–4 observable, ideally dated, triggers that would flip this lens's conclusion.
## Sources
[E1] 10-Q for quarter ended 2026-10-26, filed 2026-11-19, accn 0001045810-26-000101, https://www.sec.gov/…
````
**Scorecard keys by lens:**
| Lens | Keys |
|---|---|
| earnings | `trajectory` (Accelerating/Stable/Decelerating/Inflecting down), `trajectory_score` 1–5, `guidance_credibility` H/M/L, `beat_quality` H/M/L, `next_print` |
| forensics | `quality_rating` (Clean/Watch/Red flags), `beneish_m`, `altman`, `piotroski`, `accruals_sloan`, `cash_conversion_5y`, `top_flag` |
| valuation | `price`, `implied_growth_y1`, `implied_margin`, `expectations` (Easy/Plausible/Demanding/Heroic), `scenarios` (bear / base / bull $ and %), `skew` (Favorable/Balanced/Unfavorable) |
| industry | `moat` (Wide/Narrow/None), `moat_trend` (Strengthening/Stable/Eroding), `primary_power`, `industry_structure` (Improving/Stable/Deteriorating), `biggest_threat` |

## 7. Debate files
**debate/bull.md and debate/bear.md** (900 words or fewer each), with headings: Thesis (one falsifiable sentence) · Variant perception / What the market is missing · Pillars (3–5; each: claim, evidence with IDs, mechanism or what has to be true, early-warning metric and date) · Scenario (inputs, value per share, % vs. price) · Catalysts (dated) · Steelman of the other side (their best argument, plus your answer or an admission that you have none) · What would make me abandon this case · Sources.

**debate/bull-rebuttal.md and debate/bear-rebuttal.md** (500 words or fewer each): one entry per opposing pillar, labeled **Concede** (and what it costs) / **Contest** (counter-evidence) / **Reframe** (right fact, wrong implication). Then `Updated probability: NN%` and `Deciding question: …`. No new pillars.

**Banned moves:** strawmanning (rebutting a weaker version than the one written), unsourced claims, "it's priced in" without valuation-memo numbers, adjectives as evidence, and new pillars in a rebuttal.

## 8. PM files
**pm/decision.md** (900 words or fewer): Debate scorecard table (Pillar · Side · Survived/Weakened/Refuted · Why) · Key debate variables (2–4; bull view, bear view, PM call, resolving evidence, date) · Scenario table (Case · Probability · Value/share · vs. price) plus the probability-weighted arithmetic · Verdict and conviction with rationale (incl. overrides applied) · Kill criteria · Unresolved.
**pm/report.json**: exactly per `memo-template.md`.

## 9. Role cards (for sequential fallback without subagents)
When you cannot spawn agents, play each role in its own pass. Start each pass with a banner line `━━ ROLE: <name> · reads: <files> · writes: <file> ━━`, read only the files that role may read, write its file per the contract above, then close the pass. Do not let a later role's conclusions leak into an earlier file.
| Role | Reads | Writes | Mandate in one line |
|---|---|---|---|
| data-analyst | nothing (fetches) | data/, DATA-BRIEF.md | One verified, cited fact base. Facts only, plus a data-quality log. |
| earnings-analyst | brief, statements, releases, MD&A, reactions, surprises | memos/earnings.md | Is earnings power accelerating, and does management's guidance hold up? |
| forensic-accountant | brief, scores, statements, risk text, full filings, insiders | memos/forensics.md | How far can we trust the numbers? Decompose the scores, redline the disclosures. |
| valuation-analyst | brief, quote, statements, estimates, peers | memos/valuation.md | What does the price imply? Bear/base/bull values, comps, the one input that matters. |
| industry-analyst | brief, 10-K business/risk, peers | memos/industry.md | Why does it earn what it earns? 7 Powers, five forces, competitors, TAM check. |
| bull-analyst | brief + all memos | debate/bull.md, bull-rebuttal.md | The strongest evidence-backed upside case. Steelman the bear. |
| bear-analyst | brief + all memos | debate/bear.md, bear-rebuttal.md | What the market is missing on the downside. Steelman the bull. |
| portfolio-manager | everything | pm/decision.md, pm/report.json | Judge, don't average. Set the variables, probabilities, verdict and kill criteria. |
In fallback, write the bull case and the bear case **before** either rebuttal, and write both rebuttals before the PM pass.

## 10. Task prompt template (orchestrator → agent)
```
You are the <role> for an earnings-desk deep dive on <TICKER> (<Company>).
RUN_DIR: <absolute run dir>. Read RUN_DIR/README.md first (tools + context), then RUN_DIR/DATA-BRIEF.md.
Mode: <case|rebuttal> (bull/bear only) · Lens weight: <standard|lead|support> (focus mode only)
Write your file to RUN_DIR/<path> following the contract in <abs path to agent-contracts.md>, section <N>.
Do not re-fetch data that already exists in RUN_DIR/data. Save any new fetches to RUN_DIR/data/.
Return a summary of 200 words or fewer in the section-4 format.
```
