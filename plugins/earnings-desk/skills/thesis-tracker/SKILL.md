---
name: thesis-tracker
description: >-
  Living investment-thesis tracker - writes and maintains a thesis file per stock at .earnings-desk/theses/TICKER.md with a 3-sentence thesis, pillars tied to measurable KPIs and thresholds, pre-committed kill criteria ("I'm wrong if..."), a catalyst calendar, user-owned position notes and a dated log. On every re-run it pulls the latest SEC data (XBRL facts, earnings release, filing changes), scores each pillar intact / weakening / broken, flags any kill criterion hit, logs what changed and updates conviction. Verdict "Thesis: Intact / Under pressure / Broken". Use when the user says "track my thesis", "write down my thesis", "update my thesis", "is my thesis still intact", "check my position after earnings", "kill criteria", "investment journal", "review my holdings thesis", "did anything break", or "why do I own this".
license: MIT
compatibility: Requires Python 3.8+ (standard library only) and internet access to sec.gov. Writes files under ./.earnings-desk/theses/ in the current directory.
metadata:
  category: "5-thesis-desk"
  version: "1.0.0"
  author: "earnings-desk"
---

# thesis-tracker · write it down, define "wrong", check it every quarter

The most expensive mistake in investing is a thesis that quietly changes so you never have to admit it broke. This skill keeps a dated, version-controlled record of *why* you own (or watch) a stock, what has to stay true, and what would prove you wrong. Each earnings season it checks the record against fresh primary data.

## When to use
- **Create:** after deciding to own or watch a stock, or right after a `bull-bear-debate` (its debate variables become your pillars).
- **Update:** after every earnings release, 10-Q/10-K, major news, or when the user asks "is my thesis still intact?".
- **Not** for first-pass research (use `deep-dive`, `bull-bear-debate`) or for a one-off print analysis (`earnings-recap`). This skill consumes those.

## Inputs
- `TICKER` (required). Mode is automatic: **create** if `.earnings-desk/theses/TICKER.md` doesn't exist, **update** otherwise.
- Create mode: the user's thesis in their own words (ask for it if it's missing; never invent a position), horizon (default 2–3 years), direction (long / short / watch).
- Update mode: optional trigger event ("Q3 print", "CEO left").

> **Paths:** `${CLAUDE_SKILL_DIR}` is this skill's own folder. Claude Code fills it in automatically; in other tools, replace it with the folder that contains this `SKILL.md`. Sibling skills such as `${CLAUDE_SKILL_DIR}/../sec-edgar` are installed next to it.

## Workflow

### Create mode
1. **Get the user's thesis.** Ask what they believe and why, in plain words. If a recent `bull-bear-debate`, `moat-analysis` or `reverse-dcf` report exists in `earnings-desk-reports/`, use its key variables and implied expectations as raw material, and confirm them with the user.
2. **Establish baselines** (commands relative to this skill folder):
   ```bash
   python3 ${CLAUDE_SKILL_DIR}/../financial-statements/scripts/statements.py TICKER --years 5 --quarters 8
   python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/edgar.py earnings-release TICKER
   python3 ${CLAUDE_SKILL_DIR}/../reverse-dcf/scripts/dcf.py TICKER --price P          # what's priced in at the reference price
   python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/market.py quote TICKER
   python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/market.py calendar TICKER          # next earnings date (key or web fallback)
   ```
3. **Draft the file** from [assets/thesis-template.md](assets/thesis-template.md): the 3-sentence thesis, 3–5 pillars (each with a KPI, source, baseline and *intact / weakening / broken* thresholds), 3–5 kill criteria, a catalyst calendar, and a blank position-notes section for the user. Show the draft and get the user's sign-off on thresholds and kill criteria **before** writing them. They have to be the user's commitments.
4. **Write** `.earnings-desk/theses/TICKER.md` (create the directory if needed; use an uppercase ticker). Add the first log entry with the reference price and its source.

### Update mode
1. **Read** `.earnings-desk/theses/TICKER.md`. Note `last_reviewed`, each pillar's KPI and thresholds, the kill criteria and catalyst dates.
2. **Pull what's new since `last_reviewed`:**
   ```bash
   python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/edgar.py filings TICKER --forms 10-K,10-Q,8-K --limit 10   # anything filed since last review?
   python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/edgar.py facts TICKER --periods 8 --annual 3               # latest reported KPIs
   python3 ${CLAUDE_SKILL_DIR}/../financial-statements/scripts/statements.py TICKER --years 3 --quarters 8     # margins, growth, share count
   python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/edgar.py earnings-release TICKER                           # results + guidance
   python3 ${CLAUDE_SKILL_DIR}/../filing-diff/scripts/diff_sections.py TICKER --form 10-Q --section mdna        # what changed in MD&A
   python3 ${CLAUDE_SKILL_DIR}/../filing-diff/scripts/diff_sections.py TICKER --form 10-K --section 1A          # new risks (annual)
   python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/edgar.py insiders TICKER --days 120
   python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/market.py quote TICKER
   ```
   For KPIs that aren't in XBRL (segment revenue, NRR, units), read them from the earnings release or the 10-Q segment note. Check `../forensic-accounting/scripts/scores.py TICKER` once a year, or if a kill criterion mentions accounting.
3. **Score each pillar** against its pre-set thresholds: **Intact / Weakening / Broken**, with the KPI value, period and source. If a KPI can't be found, mark it "Not updated (not disclosed)". Never guess.
4. **Check every kill criterion** literally. If one is hit, flag it at the top of the report and the log. The thesis status becomes **Broken** unless the user records an explicit, reasoned override.
5. **Status roll-up:**
   - **Intact**: all pillars intact (at most one weakening, with no trend), no kill criteria hit.
   - **Under pressure**: two or more pillars weakening, *or* one pillar broken, *or* the same pillar weakening two reviews in a row.
   - **Broken**: any kill criterion hit, or most pillars broken.
6. **Conviction.** Propose a change (±1 on a 1–5 scale) with a one-line reason tied to the evidence. The user owns the final number. Never update position notes on your own.
7. **Update the file:** pillar table "Latest" and "Status" columns, catalyst calendar (mark past events, add new dates), front-matter `last_reviewed` / `status` / `conviction`, and a **new log entry on top**. Don't rewrite or delete history; past log entries are immutable. If the user wants to change the thesis itself, record it as a dated "Thesis revised" entry that keeps the old text quoted. Silent edits are thesis drift.

## Analysis framework

**Good pillars are falsifiable.** Each has:
- a **KPI** the company actually reports (or that can be computed from filings), with a named source;
- a **baseline** with date;
- **thresholds** set *before* the data arrives. Use levels *and* trends (e.g. "< 65% for 2 quarters"), so one noisy quarter doesn't trip them.
- Bad: "Strong execution." Good: "Operating margin ≥ 30% (statements.py), weakening at 27–30%, broken below 27% for 2 quarters."

**Kill criteria: pre-commitment beats willpower.** Write them while unbiased. Typical categories: a core-growth failure (guidance below X), economics (margin or retention floor), a balance-sheet stress (net debt / EBITDA > 3x), governance or accounting (auditor change, restatement, material weakness, Beneish flag), and a thesis-specific event (lose a key customer, approval denied). Watch for the "it's temporary" rationalization: a kill criterion can only be overridden in writing, with reasons. Repeated overrides are themselves a signal.

**Distinguish noise from signal**
- One quarter of weakness in a seasonal or lumpy business is noise. Compare y/y, not q/q.
- A pillar weakening while the stock rises still means *Under pressure*. Price doesn't validate a thesis.
- A broken pillar that wasn't core to the variant perception matters less than a weakening pillar that was. Note which pillar carries the thesis.
- **New information outside the pillars** (a new competitor, regulation, management change) goes in the log under "What changed". Ask whether it needs a new pillar or kill criterion, and get the user's agreement first.

**Thesis drift detection:** compare today's thesis sentences with the original. If the reasons to own have changed (e.g. "AI growth" became "cheap on P/E"), call it out explicitly: *the original thesis may be broken, and a new one is being substituted.*

**Questions to ask every review**
1. If I didn't own this, would I buy it today at this price with what I now know?
2. Which pillar is the market most worried about, and is that the one weakening?
3. Has anything happened that I said in advance would prove me wrong?
4. Is the next catalyst still on the calendar, and what result would change the status?

## Output
1. **The thesis file** `.earnings-desk/theses/TICKER.md` (created or updated). This is the system of record.
2. **A report** per [../sec-edgar/references/report-schema.md](../sec-edgar/references/report-schema.md), `"skill": "thesis-tracker"`:
   - **Title idea:** `"Thesis *intact* after Q3"` / `"Two pillars *weakening*"` / `"Kill criterion *hit*"`.
   - **Verdict:** `{"label": "Thesis", "value": "Intact" | "Under pressure" | "Broken", "sub": "Conviction 4 → 3", "tone": "pos" | "warn" | "neg"}`.
   - **KPIs (3–6):** the most important pillar KPIs (latest value, delta vs. threshold as `tone`), price vs. reference price, days to next catalyst.
   - **Sections:** *Thesis* (3 sentences in a blockquote); *Pillar scorecard* (table: pillar, KPI, baseline, latest, thresholds, status pill; plus `scores` bars showing distance to the "broken" threshold); *Kill criteria* (table: criterion, status, evidence; any hit is a `neg` callout at the top); *What changed* (sourced callouts); *Catalyst calendar* (table); *Conviction & next check*.
   - **Sources:** accessions and URLs for every KPI value, and the price source.
   ```bash
   python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/render_report.py /tmp/TICKER-thesis-tracker.json --out-dir earnings-desk-reports
   ```
3. **In chat:** "Thesis: Under pressure. P2 (gross margin) is weakening at 66.8% vs. a 70% intact line; no kill criteria hit; conviction 4 → 3 proposed. Next check: Q4 print on DATE." Then give the thesis-file path and the report paths. Suggest committing `.earnings-desk/theses/` to git for an audit trail, but don't commit for the user.

## Quality bar & pitfalls
- **Never invent the user's thesis, conviction or position.** Propose, and let them decide.
- Thresholds are set before data and never moved after the fact without a dated log entry.
- Every KPI value has a period and source. "Not disclosed" is an acceptable answer; a guess is not.
- Keep the file human-readable Markdown. It should be useful without this tool.
- Log entries are append-only (newest first). History is the point.
- Facts (KPI values) vs. judgment (status, conviction) are visibly separated.
- Position sizing and trade decisions belong to the user.

## Next skills
`/earnings-desk:earnings-recap` (deep read of the print that triggered the review) · `/earnings-desk:guidance-tracker` · `/earnings-desk:kpi-tracker` · `/earnings-desk:filing-diff` · `/earnings-desk:bull-bear-debate` (re-argue the case when Under pressure) · `/earnings-desk:earnings-preview` (set expectations before the next catalyst).

_Not investment advice. The thesis, thresholds and decisions are the user's own; data is from public filings and may contain errors._
