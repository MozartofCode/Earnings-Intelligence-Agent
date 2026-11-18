---
name: deep-dive
description: >-
  The flagship earnings-desk workflow. Runs a full institutional-grade research process on one stock with a desk of 8 specialist analysts. A data analyst builds one verified SEC fact pack. Earnings, forensic, valuation and industry analysts then work in parallel, bull and bear analysts debate with a rebuttal round, and a portfolio manager judges and writes the final investment memo as an HTML report. The memo covers the research view and conviction, business and moat, financial quality, what is priced in, key debates, catalysts, risks and kill criteria. Use when the user says "deep dive", "full research on NVDA", "investment memo", "build a thesis", "is this a good investment", "analyze this stock end to end", "should I look at TICKER", or wants the most thorough answer the plugin can give. Options are --quick (a 5-minute single-agent take) and --focus earnings, valuation or forensics. Free-first: runs on SEC EDGAR with no paid keys.
license: MIT
compatibility: Requires Python 3.8+ and internet access to sec.gov. Full mode uses Claude Code subagents and falls back to sequential role passes where subagents are unavailable (e.g. Claude.ai). Optional FMP_API_KEY, FINNHUB_API_KEY or ALPHAVANTAGE_API_KEY.
metadata:
  category: "0-orchestration"
  version: "1.0.0"
  author: "earnings-desk"
---

# deep-dive · the whole research desk on one stock

`/earnings-desk:deep-dive NVDA` runs the process a top buy-side desk uses for a new name. Everyone works from **one verified fact base**. Specialists work **independently and in parallel**. Advocates **argue both sides** under rules of evidence. A **portfolio manager judges** and commits to a view, the variables that decide it, and the evidence that would prove it wrong.

## When to use
- The user wants the most complete answer: "deep dive", "full workup", "investment memo", "build me a thesis on X".
- A new idea that passed a first look (`company-tearsheet`) and now deserves real work.
- **Not** for one narrow question. Route those instead: "did they beat?" → `earnings-recap`, "what's priced in?" → `reverse-dcf`, "red flags?" → `forensic-accounting`, "bull vs bear only" → `bull-bear-debate`, "quick snapshot" → `company-tearsheet`. If unsure, `help`.

## Inputs
| Input | Default | Notes |
|---|---|---|
| `TICKER` | required | Company name is fine. Resolve it in Phase 0. One ticker per run. |
| `--quick` | off | Single agent, about 5 minutes. See **Modes**. |
| `--focus earnings\|valuation\|forensics` | none | One lead lens goes deep, one supports it, the rest are skipped. |
| `--peers A,B,C` | auto | Overrides the valuation and industry analysts' peer set. |

## The desk
| Phase | Who | Runs | Writes (in the run dir) |
|---|---|---|---|
| 0 Setup | you (orchestrator) | sequential | `README.md` |
| 1 Data | `data-analyst` | 1 agent | `data/*`, `DATA-BRIEF.md` |
| 2 Lenses | `earnings-analyst`, `forensic-accountant`, `valuation-analyst`, `industry-analyst` | **4 in parallel** | `memos/*.md` |
| 3 Debate | `bull-analyst`, `bear-analyst` (case round, then rebuttal round) | **2 in parallel, twice** | `debate/*.md` |
| 4 Judgment | `portfolio-manager` | 1 agent | `pm/decision.md`, `pm/report.json` |
| 5 Deliver | you | sequential | HTML + MD report |

Agents are plugin subagents. Call them with `subagent_type: "earnings-desk:<name>"`, or the bare `<name>` if that is how your agent list shows them. Every output follows [references/agent-contracts.md](references/agent-contracts.md). The final memo follows [references/memo-template.md](references/memo-template.md).

## Workflow

### Phase 0 · Setup (you, about 1 minute)
1. **Resolve tool paths.** This skill's base directory is `.../skills/deep-dive`, so set `S` to its parent `.../skills`. If you don't know it, Glob `**/earnings-desk/**/skills/sec-edgar/scripts/edgar.py`. Use **absolute paths** everywhere, because subagents run in the user's project, not the plugin.
2. **Check setup:**
   ```bash
   python3 $S/sec-edgar/scripts/market.py status
   python3 $S/sec-edgar/scripts/edgar.py cik TICKER        # also proves SEC access works
   ```
   On a 403, stop and ask the user to `export SEC_USER_AGENT="Name email@example.com"`. Never invent one. A missing key is fine: say once which enhancements are off (consensus, surprises) and continue.
3. **Resolve the ticker.** For a company name or a miss, use `suggestions` from the error and confirm with the user if ambiguous. Foreign filers use 20-F/6-K. Note it in the manifest.
4. **Create the run dir:** `RUN=$PWD/.earnings-desk/runs/<TICKER>-$(date +%F)` with `data/text`, `memos`, `debate` and `pm`. If it already exists from today, ask: reuse its `data/` (fast) or start fresh (`<TICKER>-<date>-2`).
5. **Write `RUN/README.md`** (the manifest template is in agent-contracts §2): ticker, CIK, FY end, mode, focus, key status, **absolute `S` and `RUN`**, the script list, contract paths, and an empty file index.
6. **Tell the user the plan** in 2 lines: the 8 analysts, the phases, and the expected time (full mode usually takes 15–40 minutes).

### Phase 1 · Data pack (`data-analyst`, 1 agent)
Dispatch with the task template from agent-contracts §10. It runs the shared pack (profile, filings, facts, `statements.py`, quote, `scores.py`, reactions, estimates, surprises, calendar, insiders, peers, the 10-K business/risk/MD&A sections, the 10-Q MD&A, and the last two earnings releases) into `RUN/data/`, verifies it, and writes `DATA-BRIEF.md`.
**Gate:** `DATA-BRIEF.md` exists, has a price and the latest 10-K/10-Q accession numbers, and has a **Data-quality log**. If the price is missing, run `market.py quote` or a web search yourself and add it, labeled. Read the log and pass any material issue to Phase 2 agents in their prompts.

### Phase 2 · Four lenses in parallel
**Launch these four agents in ONE message (four Agent tool calls in the same turn) so they run concurrently.** Never one after another.
| Agent | Writes | Key question |
|---|---|---|
| `earnings-analyst` | `memos/earnings.md` | Is earnings power accelerating, and is management credible? |
| `forensic-accountant` | `memos/forensics.md` | How far can we trust the numbers? |
| `valuation-analyst` | `memos/valuation.md` | What does the price imply? What are bear/base/bull worth? |
| `industry-analyst` | `memos/industry.md` | Why does it earn what it earns? Is the moat widening? |
Each prompt states `RUN_DIR`, the output path, contract §6, "do not re-fetch `data/`", any `--peers`, and data issues from the Phase 1 log. Lenses stay **independent**: they do not read each other's memos.
**Gate (per memo):** the file exists, the `scorecard` block is filled, there are ≥3 sourced Key findings, and *What would change my mind* is present. If a memo is missing or hollow, re-dispatch that one agent once with the specific gap. If it fails again, play the role yourself (fallback rules) and note it in the README.

### Phase 3 · Debate (two parallel rounds)
1. **Case round:** launch `bull-analyst` (mode `case` → `debate/bull.md`) and `bear-analyst` (mode `case` → `debate/bear.md`) **in ONE message**. Both read the brief and all memos.
2. **Rebuttal round:** once both files exist, launch `bull-analyst` (mode `rebuttal` → `debate/bull-rebuttal.md`, reads `bear.md`) and `bear-analyst` (mode `rebuttal` → `debate/bear-rebuttal.md`, reads `bull.md`) **in ONE message**.
**Gate:** each case has 3–5 sourced pillars, a scenario value with inputs, and a *Steelman of the other side*. Each rebuttal labels every opposing pillar Concede, Contest or Reframe and ends with an updated probability. A strawman (rebutting something the other side didn't write) means re-dispatch with that note.

### Phase 4 · Judgment (`portfolio-manager`, 1 agent)
Dispatch with `RUN_DIR`, plus the paths to memo-template.md and agent-contracts §8. The PM reads everything, scores the debate pillar by pillar, names 2–4 key variables, assigns scenario probabilities, applies the **verdict rubric and overrides**, sets 3–5 kill criteria, and writes `pm/decision.md` and `pm/report.json`.
**Gate:** the verdict is one of Attractive / Fairly valued / Unattractive with a conviction level. The probabilities sum to 100%. The executive summary states the strongest argument *against* the view. Every KPI number appears in `sources`.

### Phase 5 · Render and deliver (you)
```bash
python3 $S/sec-edgar/scripts/render_report.py $RUN/pm/report.json --out-dir earnings-desk-reports
```
Fix any `warnings` (edit the JSON yourself; re-run). Update the README file index. Then reply in chat with:
- **Research view, conviction**, and the probability-weighted value vs. price in one line, with "research view, not investment advice".
- The 3-sentence executive summary, the key debates (one line each), and the kill criteria.
- Paths: the HTML, the Markdown, and the run dir (all intermediate memos are there for audit).
- **Offer:** "Save this thesis and its kill criteria with `/earnings-desk:thesis-tracker TICKER`?" Also suggest `earnings-preview` before the next print date.

## Modes

### `--quick` (no subagents, about 5 minutes)
Same Phase 0 and run dir, then do it yourself:
```bash
python3 $S/sec-edgar/scripts/edgar.py profile T            > $RUN/data/profile.json
python3 $S/sec-edgar/scripts/market.py quote T             > $RUN/data/quote.json
python3 $S/financial-statements/scripts/statements.py T --years 5 --quarters 8 > $RUN/data/statements.json
python3 $S/forensic-accounting/scripts/scores.py T --market-cap <mcap> > $RUN/data/scores.json
python3 $S/reverse-dcf/scripts/dcf.py T --price <price>    > $RUN/data/dcf-reverse.json
python3 $S/sec-edgar/scripts/edgar.py earnings-release T   > $RUN/data/release-0.json
```
Follow the `company-tearsheet` logic for the snapshot. Read the scores' drivers, decide whether the implied growth is easy, plausible, demanding or heroic, then write a **steelmanned** 3-bullet bull and bear case and 3 kill criteria. Use the quick-mode skeleton (memo-template §5). Conviction is capped at Medium and the verdict is labeled "(quick take)". End by offering the full deep dive.

### `--focus earnings|valuation|forensics`
| Focus | Lead lens (1,400 words) | Support lens (450 words) | Skipped |
|---|---|---|---|
| earnings | earnings-analyst | valuation-analyst (what the print must deliver) | forensic, industry |
| valuation | valuation-analyst | industry-analyst (does the moat justify the multiple?) | earnings, forensic |
| forensics | forensic-accountant | earnings-analyst (earnings quality, guidance honesty) | valuation, industry |
Phase 1 is unchanged. Phase 2 launches lead and support **in one message**. Phase 3 runs the case round only (no rebuttal). In Phase 4 the PM notes the skipped lenses as unresolved and caps conviction at Medium unless the focus lens is decisive. In forensics focus, the forensic memo also runs `insider-ownership` and `capital-allocation` checks.

### Fallback (no subagents: Claude.ai, API, or Agent tool unavailable)
Run the **same phases sequentially**, playing each role in its own clearly delimited pass using the role cards in agent-contracts §9. Open each pass with a banner `━━ ROLE: forensic-accountant · reads: … · writes: memos/forensics.md ━━`. Read only what that role may read, write its file per contract, then close. Lens passes don't read each other's memos. Write both cases before either rebuttal and both rebuttals before the PM pass. Where Bash is unavailable, use web search for figures and label every one `web search: site, date`. Tell the user the run used fallback mode.

## Analysis framework: why the desk is built this way
- **One fact base (Phase 1):** most research disagreements are really data disagreements. A shared, logged `DATA-BRIEF.md` removes them and stops 8 agents from hammering SEC with the same requests.
- **Independent lenses (Phase 2):** analysts who read each other anchor on each other. Independence first, synthesis later.
- **Adversarial debate (Phase 3):** steelman rules plus a rebuttal round expose which pillars survive contact. Concessions are the highest-signal output of the whole process.
- **A judge, not an average (Phase 4):** the PM must name the 2–4 variables that decide the outcome and commit to probabilities. Scenario-weighted value plus asymmetry beats a single point estimate.
- **Pre-committed kill criteria:** written *before* the market tests the view, so the user can tell a broken thesis from a bad week.

**Your job as orchestrator is quality control.** Between phases, check: Does every number have a source ID? Are facts and judgment separated? Did any agent use advice language (buy, sell, target)? Does the forensic rating actually constrain the verdict? Do the valuation scenarios use the same price as the brief? Fix it or send it back. Don't pass weak work forward.

## Output
`earnings-desk-reports/<TICKER>-deep-dive-<date>.html` plus `.md`. The memo sections are: verdict stamp → executive summary → Business & moat → Financial quality → Earnings trajectory → Forensic check → Valuation (priced in vs. desk view) → Bull vs. bear → Key debates → Catalysts & risks → Kill criteria & monitoring → Sources. The full audit trail stays in `.earnings-desk/runs/<TICKER>-<date>/`.

## Quality bar & pitfalls
- **Parallelism is the point.** Four sequential lens agents waste the user's time. Use one message with four tool calls.
- **Pass paths, not content.** Prompts carry `RUN_DIR` and file paths. Agents read files themselves. Never paste memos into prompts.
- **Same price everywhere.** The brief's cited price is the only price. Scenarios and comps use `--price` with it.
- **Fiscal labels:** NVDA's FY27 is not calendar 2027. Every period carries the company's label plus the period-end date.
- **Sector fit:** for banks, insurers and REITs, tell agents in the prompt which metrics don't apply (gross margin, Altman Z, FCF DCF).
- **Don't let eloquence win.** An unsourced pillar loses to a sourced one, however well written.
- **Verdict honesty:** "Fairly valued" is a legitimate, common answer. Don't manufacture conviction.
- **Long runs:** if the user interrupts, the run dir lets you resume from the last completed phase. Check the README file index.

_Not investment advice. earnings-desk produces research views from public filings and may contain errors; verify before acting._
