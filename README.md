<p align="center">
  <img src="docs/banner.svg" alt="earnings-desk: an AI research desk for stocks and earnings" width="100%">
</p>

<p align="center">
  <b>20 skills · 8 specialist agents · zero paid data</b><br>
  Turn Claude into a skeptical buy-side research desk that reads the filings and checks the math for you.
</p>

<p align="center">
  <a href="#install">Install</a> ·
  <a href="#the-skills">Skills</a> ·
  <a href="#the-desk">Agents</a> ·
  <a href="#examples">Examples</a> ·
  <a href="#faq">FAQ</a>
</p>

---

```text
> /earnings-desk:deep-dive NVDA

  ▸ data-analyst        pulled 6y XBRL, 10-K risk factors, Q2 release, Form 4s
  ▸ earnings-analyst    ┐
  ▸ forensic-accountant │ working in parallel…
  ▸ valuation-analyst   │
  ▸ industry-analyst    ┘
  ▸ bull-analyst  vs  bear-analyst   rebuttal round
  ▸ portfolio-manager   verdict + kill criteria

  ✔ earnings-desk-reports/NVDA-deep-dive-2026-11-16.html
```

## Why earnings-desk

Most "AI stock analysis" summarizes headlines. earnings-desk works from the **primary sources** and acts like an analyst who doesn't trust anyone:

- 🧾 **Free, primary-source data.** Official SEC EDGAR filings and XBRL financials with no API key. Optional free tiers (Finnhub, FMP, Alpha Vantage) add consensus and prices.
- 🔍 **Forensic by default.** It redlines 10-Ks against last year, scores management's guidance track record, flags evasive answers on calls, and runs Beneish, Altman, Piotroski and Sloan checks.
- ⚔️ **Adversarial.** Bull and bear agents argue independently, rebut each other, and a portfolio-manager agent judges, naming the 2–3 variables that decide who is right.
- 📐 **Real math, tested scripts.** Reverse DCF ("what's priced in?"), peer comps with growth regression, and true quarterly cash flows (EDGAR reports them year-to-date).
- 🖨️ **Reports worth sharing.** Every skill renders an editorial HTML report (light/dark, charts, print-ready) plus Markdown, and every number links back to its source.

## Install

**Claude Code** (recommended: gets all 20 skills and the 8-agent desk)
```bash
claude plugin marketplace add MozartofCode/earnings-desk
claude plugin install earnings-desk@earnings-desk
```
Or inside a session: `/plugin marketplace add MozartofCode/earnings-desk`, then `/plugin install earnings-desk@earnings-desk`.

**Any agent that supports Agent Skills** (Claude Code, Cursor, Codex, Gemini CLI, and more)
```bash
npx skills add MozartofCode/earnings-desk
```

**Claude.ai / Claude Desktop:** download a skill zip from [Releases](https://github.com/MozartofCode/earnings-desk/releases) and upload it under *Settings → Capabilities → Skills*.

### One-time setup
SEC asks automated tools to identify themselves with a name and email:
```bash
export SEC_USER_AGENT="Your Name you@example.com"
```
Optional free keys unlock consensus estimates, EPS surprise history, earnings dates and reliable quotes ([`.env.example`](.env.example)):
```bash
export FINNHUB_API_KEY=...   # finnhub.io (free)
export FMP_API_KEY=...       # financialmodelingprep.com (free tier)
```
Not sure where to start? Run **`/earnings-desk:help`**.

## The skills

| Desk | Skill | Ask it… |
|---|---|---|
| **0 · Orchestration** | [`deep-dive`](plugins/earnings-desk/skills/deep-dive/SKILL.md) | "Do a full deep dive on NVDA" (the whole desk, in parallel) |
| | [`help`](plugins/earnings-desk/skills/help/SKILL.md) | "What can you do? Which skill should I use?" |
| **1 · Data & foundations** | [`sec-edgar`](plugins/earnings-desk/skills/sec-edgar/SKILL.md) | "Pull Apple's last 12 quarters from the 10-Qs" |
| | [`company-tearsheet`](plugins/earnings-desk/skills/company-tearsheet/SKILL.md) | "Give me a one-pager on Costco" |
| | [`financial-statements`](plugins/earnings-desk/skills/financial-statements/SKILL.md) | "Break down Microsoft's margins, ROIC and cash conversion" |
| | [`filing-diff`](plugins/earnings-desk/skills/filing-diff/SKILL.md) | "What changed in Tesla's risk factors this year?" |
| **2 · Earnings season** | [`earnings-preview`](plugins/earnings-desk/skills/earnings-preview/SKILL.md) | "What's the setup into Nvidia's print?" |
| | [`earnings-recap`](plugins/earnings-desk/skills/earnings-recap/SKILL.md) | "Did Amazon beat? Was it a quality beat?" |
| | [`transcript-decoder`](plugins/earnings-desk/skills/transcript-decoder/SKILL.md) | "Was management dodging questions on the call?" |
| | [`guidance-tracker`](plugins/earnings-desk/skills/guidance-tracker/SKILL.md) | "Does this CEO sandbag or over-promise?" |
| | [`kpi-tracker`](plugins/earnings-desk/skills/kpi-tracker/SKILL.md) | "Chart Netflix's subscribers and ARPU" |
| | [`read-through`](plugins/earnings-desk/skills/read-through/SKILL.md) | "What does TSMC's print mean for AMD and Apple?" |
| **3 · Forensics & quality** | [`forensic-accounting`](plugins/earnings-desk/skills/forensic-accounting/SKILL.md) | "Any accounting red flags at this company?" |
| | [`capital-allocation`](plugins/earnings-desk/skills/capital-allocation/SKILL.md) | "Are the buybacks actually creating value?" |
| | [`insider-ownership`](plugins/earnings-desk/skills/insider-ownership/SKILL.md) | "Are insiders buying or dumping?" |
| **4 · Valuation & competition** | [`reverse-dcf`](plugins/earnings-desk/skills/reverse-dcf/SKILL.md) | "What growth is priced into this stock?" |
| | [`comps-valuation`](plugins/earnings-desk/skills/comps-valuation/SKILL.md) | "Is it cheap vs. peers, adjusted for growth?" |
| | [`moat-analysis`](plugins/earnings-desk/skills/moat-analysis/SKILL.md) | "How durable is their competitive advantage?" |
| **5 · Thesis desk** | [`bull-bear-debate`](plugins/earnings-desk/skills/bull-bear-debate/SKILL.md) | "Steelman both sides of the Palantir debate" |
| | [`thesis-tracker`](plugins/earnings-desk/skills/thesis-tracker/SKILL.md) | "Save my thesis and tell me if it breaks" |

In Claude Code, call any skill directly as `/earnings-desk:<skill> TICKER`, or just ask in plain English and Claude picks the right one.

### Playbooks
| Situation | Run |
|---|---|
| New idea | `company-tearsheet` → `deep-dive` → `thesis-tracker` |
| Earnings day | `earnings-preview` → *(print)* → `earnings-recap` → `transcript-decoder` → `guidance-tracker` |
| "Is this a fraud?" | `forensic-accounting` → `filing-diff` → `insider-ownership` → `capital-allocation` |
| "Is it too expensive?" | `reverse-dcf` → `comps-valuation` → `moat-analysis` |
| Earnings season | `read-through` in sector-scan mode across your watchlist |

## The desk

`deep-dive` runs a real research process, not one giant prompt:

| Agent | Mandate |
|---|---|
| `data-analyst` | Pulls and checks the data once (XBRL, filings, releases, prices) so everyone works off the same facts |
| `earnings-analyst` | Trajectory, beat/miss quality, guidance credibility, call tone |
| `forensic-accountant` | Accounting quality scores, filing redlines, red flags |
| `valuation-analyst` | Reverse DCF, scenarios, comps: what's priced in vs. what's likely |
| `industry-analyst` | Moat, competition, market structure, read-throughs |
| `bull-analyst` / `bear-analyst` | Independent steelman cases, then a rebuttal round |
| `portfolio-manager` | Weighs the evidence, names the key debates, sets the verdict and kill criteria |

The four specialists run **in parallel**. If your environment has no subagents (e.g. Claude.ai), the same phases run sequentially.

## Examples
See [`examples/`](examples/) for real reports generated by the skills (open the `.html` files in a browser).

## How it works
```
plugins/earnings-desk/
├── agents/                  8 desk agents (subagent definitions)
└── skills/
    ├── sec-edgar/           shared toolkit: edgar.py · market.py · render_report.py · report template
    ├── financial-statements/scripts/statements.py
    ├── forensic-accounting/scripts/scores.py
    ├── reverse-dcf/scripts/dcf.py
    ├── comps-valuation/scripts/comps.py
    ├── filing-diff/scripts/diff_sections.py
    └── …16 more skills (SKILL.md + references)
```
- The scripts use only the **Python 3.8+ standard library**, so there's nothing to `pip install`.
- SEC responses are cached in `./.earnings-desk/cache/`, and reports go to `./earnings-desk-reports/`.
- Skills follow the open [Agent Skills](https://agentskills.io) spec, and the repo is also a Claude Code plugin marketplace.

## FAQ
**Is it free?** Yes. SEC EDGAR is free and keyless. Optional API keys are free tiers.

**Which companies work?** Anything that files with the SEC (US-listed companies, plus foreign issuers that file 20-F). Banks and insurers get adapted analysis, because industrial metrics don't apply to them.

**How accurate is it?** Numbers come straight from filings and are cited. Analysis is AI-generated, so check the sources before you act. Read [DISCLAIMER.md](DISCLAIMER.md).

**Can I add a skill?** Please do. See [CONTRIBUTING.md](CONTRIBUTING.md) for the authoring standard and `./scripts/validate.sh`.

## License
[MIT](LICENSE). **Not investment advice.**
