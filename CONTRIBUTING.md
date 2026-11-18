# Contributing to earnings-desk

Thanks for helping build the best open research desk for stocks and earnings. This page is the authoring standard every skill follows. Please read it before opening a PR.

## Repo map
```
.claude-plugin/marketplace.json          marketplace catalog (one plugin: earnings-desk)
plugins/earnings-desk/
  .claude-plugin/plugin.json             plugin manifest. Bump "version" on every release.
  agents/<name>.md                       the desk's specialist subagents
  skills/<skill-name>/SKILL.md           one folder per skill (flat, required for discovery)
    scripts/  references/  assets/       optional, per skill
```
Shared tooling lives in the `sec-edgar` skill (`skills/sec-edgar/scripts/edgar.py`, `market.py`, `render_report.py`, `assets/report-template.html`). Other skills call it at `../sec-edgar/scripts/...`. That relative path works both for plugin installs and for `npx skills add`, because skills are installed as sibling folders.

## Skill authoring standard

### Frontmatter
```yaml
---
name: earnings-recap            # lowercase-hyphenated, must equal the folder name, ≤ 64 chars
description: >-                 # ≤ 1024 chars. Say WHAT it does + WHEN to use it + trigger phrases.
  ...
license: MIT
compatibility: Requires Python 3.8+ and internet access to sec.gov.   # only if scripts/network are needed
metadata:
  category: "2-earnings-season" # 0-orchestration | 1-data-foundations | 2-earnings-season | 3-forensics-quality | 4-valuation-competition | 5-thesis-desk
  version: "1.0.0"
  author: "earnings-desk"
---
```
The description is the only thing an agent sees before deciding to load a skill, so make it trigger-rich. Include the words a user would actually type ("did they beat", "earnings call", "is it overvalued").

### Body (≤ ~300 lines; move depth to `references/`)
Use these sections, in this order:
1. **`# <skill> · <one-line promise>`** plus a 1–2 sentence pitch
2. **When to use** (and when *not* to, pointing to the better skill)
3. **Inputs**: ticker plus optional parameters, with defaults
4. **Workflow**: numbered and concrete. Name the exact commands (`python3 ../sec-edgar/scripts/edgar.py facts TICKER`). Say what to look for at each step, not just what to fetch.
5. **Analysis framework**: the actual expertise, i.e. formulas, thresholds, heuristics and the questions a great analyst asks
6. **Output**: the report's sections, KPIs and verdict, then render with `python3 ../sec-edgar/scripts/render_report.py`
7. **Quality bar & pitfalls**: what separates great output from generic output
8. Footer: `_Not investment advice..._`

### Non-negotiables
- **Primary sources first.** Use SEC filings via `sec-edgar`. Web search is allowed for consensus, transcripts, news and prices, and must be cited with site and date.
- **Every number has a source** in the report's `sources` array (accession number, URL, or "web search: site, date").
- **Facts vs. judgment** are visibly separated. Estimates are labeled.
- **No fabricated data.** If a number can't be found, say "not disclosed / not found" and move on.
- **Free-first.** Nothing may *require* a paid key. Keys (`FMP_API_KEY`, `FINNHUB_API_KEY`, `ALPHAVANTAGE_API_KEY`) only enhance results.
- **Scripts:** Python 3.8+, standard library only, `--help`, JSON on stdout, clear errors, no retry loops against rate limits.
- Every report ends with the not-investment-advice footer (the template adds it automatically).

## Agents
`agents/<name>.md` with frontmatter `name`, `description` (when the orchestrator should use it), optional `tools` and `model`. The body is the agent's system prompt: its role, the skills it leans on, its output contract (what it returns to the orchestrator), and its standards.

## Before you open a PR
```bash
claude plugin validate .                       # marketplace + manifest
claude plugin validate ./plugins/earnings-desk # plugin, skills and agents
```
Check that your skill's `name` matches its folder and its description is ≤ 1024 characters. Then run the skill on two very different tickers (e.g. a mega-cap and a small-cap, or a bank and a software company) and attach the HTML reports to the PR.

## Releasing
Bump `version` in `plugins/earnings-desk/.claude-plugin/plugin.json` (Claude Code only updates installed plugins when the version changes) and add a CHANGELOG entry.
