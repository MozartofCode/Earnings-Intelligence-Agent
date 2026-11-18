<p align="center">
  <img src="docs/banner.svg" alt="earnings-desk: an AI research desk for stocks and earnings" width="100%">
</p>

<p align="center">
  <b>20 Claude skills · 8 specialist agents · zero paid data</b><br>
  Turn Claude into a skeptical buy-side research desk that reads the SEC filings and checks the math for you.
</p>

<p align="center">
  <a href="#watch-the-1-minute-demo">Demo</a> ·
  <a href="#quick-start">Quick start</a> ·
  <a href="#use-it-in-claudeai-no-coding">Claude.ai</a> ·
  <a href="#what-you-can-do">What you can do</a> ·
  <a href="#the-20-skills">Skills</a> ·
  <a href="#the-desk-deep-dive">Agents</a> ·
  <a href="#example-reports">Example reports</a> ·
  <a href="#troubleshooting">Troubleshooting</a>
</p>

---

## What is this?

**earnings-desk** is a collection of [Claude skills](https://agentskills.io): instruction packs that teach Claude how to do professional stock and earnings research. Install it once, then ask things like *"did Apple beat?"*, *"any accounting red flags at NVIDIA?"* or *"what growth is priced into Microsoft?"*. Claude follows the matching skill step by step:

- **Primary sources.** It pulls official SEC EDGAR filings and financial data for free, with no API key.
- **Real analysis.** It runs the checks a professional analyst would: beat quality, guidance credibility, forensic scores, reverse DCF and more.
- **Shareable reports.** It writes a polished HTML report (light/dark mode, charts) plus Markdown, and every number links back to its source.

There's no app to run, no server and no `pip install`. It's just skills: Markdown instructions, plus a few small standard-library Python helpers inside the skill folders that fetch SEC data.

```text
> /earnings-desk:deep-dive NVDA

  ▸ data-analyst        pulled 6y XBRL, 10-K risk factors, latest release, Form 4s
  ▸ earnings-analyst    ┐
  ▸ forensic-accountant │ working in parallel…
  ▸ valuation-analyst   │
  ▸ industry-analyst    ┘
  ▸ bull-analyst  vs  bear-analyst   rebuttal round
  ▸ portfolio-manager   verdict + kill criteria

  ✔ earnings-desk-reports/NVDA-deep-dive-2026-11-16.html
```

---

## Watch the 1-minute demo

<p align="center">
  <a href="docs/demo.mp4"><img src="docs/demo.gif" alt="earnings-desk 1-minute demo: installing on Claude.ai, asking about Apple's earnings, the 8-agent deep dive and the finished reports" width="100%"></a>
</p>
<p align="center"><a href="docs/demo.mp4"><b>▶ Watch in full HD (MP4)</b></a></p>

---

## Why not just ask Claude?

Claude is a brilliant generalist. Ask it about a stock without a process, though, and you get a fluent summary of what's commonly said. earnings-desk gives Claude the **data, the methods and the skepticism** of a professional research desk:

| | Claude on its own | Claude + earnings-desk |
|---|---|---|
| **Where numbers come from** | Training data or a quick web search | Official SEC filings (10-K, 10-Q, 8-K, XBRL), downloaded fresh, with each number cited to its filing |
| **"Did they beat?"** | "Yes, revenue and EPS beat estimates" | Beat by line, guidance vs. consensus, and **how much of the beat was real** (tax rate, one-offs, buybacks, working capital) |
| **Accounting quality** | Rarely checked | Beneish, Altman, Piotroski and Sloan scores, plus filing evidence: auditor notes, restatements, odd goodwill |
| **Valuation** | A generic P/E comparison | A reverse DCF that shows **what growth the price already assumes**, with scenarios and peer regressions |
| **Point of view** | One balanced paragraph | Bull and bear agents argue, rebut each other, and a portfolio-manager agent names the deciding variables and kill criteria |
| **Output** | A chat reply | A shareable HTML report with charts, tables and a sources list, plus Markdown |
| **Repeatability** | Different every time | The same rigorous checklist every time, for every ticker |

In the [AAPL example](examples/AAPL-earnings-recap-2026-11-17.md), the headline was "beat on revenue and EPS". earnings-desk found that the **whole $0.11 EPS beat was roughly a tariff refund plus a lower tax rate**, and that inventory was 2.5× last year's level. That's the difference.

### Tested blind, not just claimed

We ran the same five research questions through Claude twice: once on its own (with web search) and once with earnings-desk. The answers were shuffled and anonymized, and a separate judge model scored them without knowing which was which, spot-checking numbers against SEC filings.

| | Claude alone | Claude + earnings-desk |
|---|---|---|
| Head-to-head (5 cases) | 0 wins | **4 wins**, 1 tie |
| Case criteria passed | 5 / 8 | **8 / 8** |
| Sourcing (1–10) | 5.4 | **8.6** |
| Depth (1–10) | 6.6 | **8.8** |
| Usefulness (1–10) | 6.8 | **8.8** |
| Accuracy (1–10) | 7.2 | **7.6** |

The method, its limits (one run per case, an AI judge), the first round where earnings-desk lost one case, and what we fixed afterwards are all in [evals/RESULTS.md](plugins/earnings-desk/evals/RESULTS.md). The eval suite is included, so you can re-run it yourself with `claude plugin eval`.

---

## Quick start

**1. Install** (in your terminal, with [Claude Code](https://claude.com/claude-code) installed):
```bash
claude plugin marketplace add MozartofCode/Earnings-Intelligence-Agent
```
```bash
claude plugin install earnings-desk@earnings-desk
```

**2. Identify yourself to the SEC.** It's free, but the SEC requires automated tools to send a name and email. Add this line to your shell profile (`~/.zshrc` or `~/.bashrc`), then open a new terminal:
```bash
export SEC_USER_AGENT="Your Name you@example.com"
```

**3. Start Claude Code and ask:**
```text
/earnings-desk:help
```
or just type a question in plain English: *"Did Apple beat last quarter? Was it a quality beat?"*

Your reports appear in an `earnings-desk-reports/` folder in whatever directory you started Claude in. Open the `.html` file in your browser.

---

## Installation options

### Claude Code (recommended)
This gets everything: all 20 skills, the 8-agent desk and slash commands.

From your terminal:
```bash
claude plugin marketplace add MozartofCode/Earnings-Intelligence-Agent
```
```bash
claude plugin install earnings-desk@earnings-desk
```
Or from inside a Claude Code session: type `/plugin marketplace add MozartofCode/Earnings-Intelligence-Agent`, then `/plugin install earnings-desk@earnings-desk`.

Check it worked:
```bash
claude plugin details earnings-desk
```

### Other AI coding agents (Cursor, Codex, Gemini CLI, …)
The skills follow the open Agent Skills format, so the `skills` CLI can install them into most agents:
```bash
npx skills add MozartofCode/Earnings-Intelligence-Agent
```
It shows a picker. Choose all skills, or just the ones you want. **Always include `sec-edgar`**, because the other skills use its data tools. The multi-agent `deep-dive` works best in Claude Code; other agents run its phases one after another.

### Claude.ai / Claude Desktop
See [Use it in Claude.ai](#use-it-in-claudeai-no-coding) below. Ready-made zips are in [`claude-ai/`](claude-ai/).

---

## Use it in Claude.ai (no coding)

No terminal needed. Each skill comes as a **ready-to-upload zip** in the [`claude-ai/`](claude-ai/) folder.

**1. Download the skills you want**
- Open the [`claude-ai/`](claude-ai/) folder on GitHub, click a zip, then click the download button (↓).
- **Starter pack:** `help.zip`, `company-tearsheet.zip`, `earnings-recap.zip`, `forensic-accounting.zip`, `reverse-dcf.zip`, `bull-bear-debate.zip`.
- To get all 20 at once: **Code → Download ZIP** on the repo page, then look inside `claude-ai/`.

**2. Upload them to Claude**
- Go to **Customize → Skills** in [claude.ai](https://claude.ai/customize/skills) or the Claude Desktop app.
- Click **Upload skill**, pick a zip, and repeat for each skill.
- Make sure each skill's toggle is **on**.

**3. Check two settings**
- **Code execution must be on** (Settings → Capabilities). The skills run small Python scripts.
- For live SEC data, the code sandbox must be allowed to reach `sec.gov` (the network setting for code execution). If it can't, the skills fall back to cited web search and say so.
- Skills need a paid plan that supports them (Pro, Max, Team or Enterprise).

**4. Ask your question**

Start a new chat. The first time, tell Claude your SEC contact (the SEC requires a name and email; it's free):
```text
My SEC user agent is "Jane Doe jane@example.com".
Did Apple beat last quarter? Was it a quality beat?
```
Claude picks the right skill automatically. You'll see it load the skill, run its scripts, and reply with the verdict plus a downloadable **HTML report**.

**Good to know on Claude.ai**
- `deep-dive` runs its phases one after another rather than with 8 parallel agents, so it's slower, but the process is the same.
- Downloaded reports open in any browser. Ask for *"the HTML report"* if Claude only answers in chat.
- Chats don't keep files between conversations. To keep a `thesis-tracker` thesis, download it and re-upload it next time.

More detail is in [`claude-ai/README.md`](claude-ai/README.md).

---

## What you can do

Ask in plain English. These all work as written (swap in any ticker):

### Before and after earnings
| Ask | You get |
|---|---|
| *"What's the setup into Nvidia's earnings next week?"* | Consensus vs. the real bar, the 3–5 KPIs that will move the stock, the options-implied move vs. history, bull/base/bear scenarios, and the 5 sharpest questions for the call |
| *"Did Amazon beat? Was it a quality beat?"* | A beat/miss scorecard, guidance vs. consensus, a breakdown of where the EPS beat came from, a margin bridge, and a **Print quality** verdict |
| *"Was management dodging questions on the Tesla call?"* | Tone shift vs. last quarter, hedging-word counts, a 0–100 evasiveness score per answer, and analyst pushback themes |
| *"Does Meta's management sandbag its guidance?"* | Every guided metric vs. actual over 3 years: hit rate, average beat, and a sandbagger / straight shooter / over-promiser label |
| *"Chart Netflix's subscribers and ARPU for the last 3 years"* | A clean KPI time series with acceleration and deceleration flagged, plus definition changes |
| *"What does TSMC's quarter mean for AMD, Apple and Nvidia?"* | Read-through signals (demand, pricing, inventory, capex) graded direct or indirect, and whether those stocks already moved |

### Is something off?
| Ask | You get |
|---|---|
| *"Any accounting red flags at Super Micro?"* | Beneish, Altman, Piotroski and Sloan with every component explained, filing evidence (auditor, restatements, controls), and a **Clean / Watch / Red flags** verdict |
| *"What changed in Boeing's risk factors this year?"* | A redline of new, removed and softened language, ranked by importance (investigations, covenants, customer concentration…) |
| *"Are insiders buying or selling Palantir?"* | Form 4 cluster buying, 10b5-1 vs. discretionary sales, CEO/CFO behavior, ownership structure |
| *"Are Apple's buybacks actually creating value?"* | Buybacks vs. stock-based compensation, the average buyback price vs. today's, M&A track record, ROIC vs. cost of capital, and an A–F grade |

### Is it worth the price?
| Ask | You get |
|---|---|
| *"What growth is priced into Microsoft?"* | Reverse DCF: the growth and margins today's price implies, compared with history and base rates, plus scenarios and a sensitivity table |
| *"Is Salesforce cheap vs. its peers, adjusted for growth?"* | A peer multiples table, an EV/Sales-vs-growth regression, and whether the premium or discount is justified |
| *"Does Visa have a real moat? Is it widening?"* | A 7 Powers + Porter scorecard with filing evidence and a moat trend |

### Build and track a view
| Ask | You get |
|---|---|
| *"Give me a one-pager on Costco"* | A tearsheet: business model, 5-year financials, valuation, balance sheet, catalysts, and 3 bull and 3 bear points |
| *"Do a full deep dive on Nvidia"* | The 8-agent desk: shared data, 4 parallel specialist memos, bull vs. bear with rebuttals, and a PM verdict with kill criteria |
| *"Steelman both sides of the Tesla debate"* | Independent bull and bear cases, a rebuttal round, the 2–3 variables that decide it, and a pre-mortem |
| *"Save my thesis on Costco and check it after each earnings report"* | A living thesis file with measurable pillars and kill criteria, re-scored as **Intact / Under pressure / Broken** |
| *"How did the semiconductor group report this earnings season?"* | A sector scan: a beat/miss/guide table across the group, common themes and outliers |

---

## Setup details

| Setting | Required? | What it does | How to get it |
|---|---|---|---|
| `SEC_USER_AGENT` | **Yes** | Lets the tools download SEC filings (the SEC blocks anonymous scripts) | Just your name and email: `"Jane Doe jane@example.com"` |
| `FINNHUB_API_KEY` | Optional | Consensus EPS estimates, earnings surprise history, earnings dates, reliable quotes | Free at [finnhub.io/register](https://finnhub.io/register) |
| `FMP_API_KEY` | Optional | Consensus revenue/EPS estimates, earnings calendar, quotes | Free tier at [financialmodelingprep.com](https://site.financialmodelingprep.com/developer/docs) |
| `ALPHAVANTAGE_API_KEY` | Optional | Earnings surprise history | Free at [alphavantage.co](https://www.alphavantage.co/support/#api-key) |

Put them in your shell profile as `export NAME="value"`. A template is in [`.env.example`](.env.example).

**Without any keys everything still works:**
- SEC data never needs a key.
- Prices come from a public endpoint on a best-effort basis (it can rate-limit).
- Consensus estimates come from web search, and the report labels them that way.

Ask `/earnings-desk:help` and it will tell you which keys are set.

Requirements: Python 3.8 or newer (preinstalled on macOS and most Linux). Nothing else.

---

## How to use it

### Two ways to run a skill
1. **Slash command**, the most direct: `/earnings-desk:<skill> TICKER [options]`
   ```text
   /earnings-desk:earnings-recap AAPL
   /earnings-desk:reverse-dcf MSFT
   /earnings-desk:deep-dive NVDA --quick
   ```
2. **Plain English.** Claude picks the right skill from your wording:
   ```text
   Was Amazon's last quarter a real beat or just a tax-rate beat?
   Are insiders at Palantir buying or selling?
   What changed in Tesla's risk factors since last year?
   ```

### What you get back
- **A short answer in chat:** the verdict, the key numbers and the biggest risk.
- **A full report** at `earnings-desk-reports/<TICKER>-<skill>-<date>.html` (open it in a browser; it has charts, tables, a theme toggle and is printable), plus a `.md` copy for your notes.
- **Sources for every number:** SEC accession numbers, filing links, or "web search: site, date" for anything that didn't come from a filing.

### Files it creates (in the folder you run Claude from)
| Path | What |
|---|---|
| `earnings-desk-reports/` | Finished HTML and Markdown reports |
| `.earnings-desk/cache/` | Cached SEC downloads, so repeat runs are fast (safe to delete) |
| `.earnings-desk/runs/<TICKER>-<date>/` | A deep dive's working files: data pack, analyst memos, debate, PM decision |
| `.earnings-desk/theses/<TICKER>.md` | Your saved thesis and kill criteria from `thesis-tracker` |

Tip: keep a dedicated folder for research (e.g. `~/research`) and start Claude there.

### A typical session (illustrative, not real output)
```text
you    > /earnings-desk:company-tearsheet COST
claude > one-page snapshot: business, 5-year financials, valuation, bull/bear points
you    > looks interesting, do the full workup
claude > (runs /earnings-desk:deep-dive COST: 8 analysts, about 15–40 min)
         Research view: Fairly valued · Medium conviction · kill criteria listed
you    > save the thesis
claude > (runs thesis-tracker, writes .earnings-desk/theses/COST.md)
...three months later, after earnings...
you    > /earnings-desk:thesis-tracker COST
claude > Thesis: Intact. Membership renewals 90.4% vs your 89% floor ✔
```

---

## The 20 skills

| Group | Skill | What it answers | Try |
|---|---|---|---|
| **Start here** | [`help`](plugins/earnings-desk/skills/help/SKILL.md) | What can this do? Which skill fits my question? Is my setup OK? | `/earnings-desk:help` |
| | [`deep-dive`](plugins/earnings-desk/skills/deep-dive/SKILL.md) | The full research process with all 8 agents, ending in an investment memo | `/earnings-desk:deep-dive NVDA` |
| **Data & foundations** | [`sec-edgar`](plugins/earnings-desk/skills/sec-edgar/SKILL.md) | Raw SEC data: financials, filings, press releases, insider trades | "Pull Apple's last 12 quarters" |
| | [`company-tearsheet`](plugins/earnings-desk/skills/company-tearsheet/SKILL.md) | One-page snapshot of any company | `/earnings-desk:company-tearsheet COST` |
| | [`financial-statements`](plugins/earnings-desk/skills/financial-statements/SKILL.md) | Margins, growth, returns on capital, cash conversion, balance sheet | `/earnings-desk:financial-statements MSFT` |
| | [`filing-diff`](plugins/earnings-desk/skills/filing-diff/SKILL.md) | What changed in the 10-K/10-Q vs. last year (risk factors, MD&A) | `/earnings-desk:filing-diff TSLA` |
| **Earnings season** | [`earnings-preview`](plugins/earnings-desk/skills/earnings-preview/SKILL.md) | Before the print: expectations, the real bar, implied move, scenarios | `/earnings-desk:earnings-preview NVDA` |
| | [`earnings-recap`](plugins/earnings-desk/skills/earnings-recap/SKILL.md) | After the print: beat/miss, guidance, *quality* of the beat | `/earnings-desk:earnings-recap AAPL` |
| | [`transcript-decoder`](plugins/earnings-desk/skills/transcript-decoder/SKILL.md) | Call tone, hedging language, evasive answers | `/earnings-desk:transcript-decoder AMZN` |
| | [`guidance-tracker`](plugins/earnings-desk/skills/guidance-tracker/SKILL.md) | Does management sandbag or over-promise? | `/earnings-desk:guidance-tracker META` |
| | [`kpi-tracker`](plugins/earnings-desk/skills/kpi-tracker/SKILL.md) | Company-specific metrics over time (subscribers, NRR, same-store sales…) | `/earnings-desk:kpi-tracker NFLX` |
| | [`read-through`](plugins/earnings-desk/skills/read-through/SKILL.md) | What one company's results mean for peers, suppliers and customers | "What does TSMC's print mean for AMD?" |
| **Forensics & quality** | [`forensic-accounting`](plugins/earnings-desk/skills/forensic-accounting/SKILL.md) | Accounting red flags: Beneish, Altman, Piotroski, accruals, filing evidence | `/earnings-desk:forensic-accounting NVDA` |
| | [`capital-allocation`](plugins/earnings-desk/skills/capital-allocation/SKILL.md) | Are buybacks, M&A and dividends creating value? (A–F grade) | `/earnings-desk:capital-allocation AAPL` |
| | [`insider-ownership`](plugins/earnings-desk/skills/insider-ownership/SKILL.md) | Insider buying and selling, ownership structure | `/earnings-desk:insider-ownership PLTR` |
| **Valuation & competition** | [`reverse-dcf`](plugins/earnings-desk/skills/reverse-dcf/SKILL.md) | What growth is priced in, and is it realistic? | `/earnings-desk:reverse-dcf MSFT` |
| | [`comps-valuation`](plugins/earnings-desk/skills/comps-valuation/SKILL.md) | Cheap or expensive vs. peers, adjusted for growth | `/earnings-desk:comps-valuation CRM` |
| | [`moat-analysis`](plugins/earnings-desk/skills/moat-analysis/SKILL.md) | How durable is the competitive advantage? | `/earnings-desk:moat-analysis V` |
| **Thesis desk** | [`bull-bear-debate`](plugins/earnings-desk/skills/bull-bear-debate/SKILL.md) | Strongest bull and bear cases, rebuttals and a judged verdict | `/earnings-desk:bull-bear-debate TSLA` |
| | [`thesis-tracker`](plugins/earnings-desk/skills/thesis-tracker/SKILL.md) | Save your thesis and kill criteria; re-check them after news | `/earnings-desk:thesis-tracker COST` |

### Playbooks
| Situation | Run, in order |
|---|---|
| New idea | `company-tearsheet` → `deep-dive` → `thesis-tracker` |
| Earnings day | `earnings-preview` (before) → `earnings-recap` → `transcript-decoder` → `guidance-tracker` |
| "Is something off here?" | `forensic-accounting` → `filing-diff` → `insider-ownership` → `capital-allocation` |
| "Is it too expensive?" | `reverse-dcf` → `comps-valuation` → `moat-analysis` |
| Earnings season | `read-through` in sector-scan mode across your watchlist |

---

## The desk (`deep-dive`)

`deep-dive` runs a real research process rather than one giant prompt:

| Phase | Who | What happens |
|---|---|---|
| 1 · Data | `data-analyst` | Pulls and checks the data **once** (financials, filings, releases, prices) so everyone works from the same facts |
| 2 · Analysis | `earnings-analyst`, `forensic-accountant`, `valuation-analyst`, `industry-analyst` | Four specialists work **in parallel**, independently, each writing a sourced memo |
| 3 · Debate | `bull-analyst` vs `bear-analyst` | Each writes the strongest possible case, then rebuts the other's best points |
| 4 · Verdict | `portfolio-manager` | Weighs the evidence, names the 2–4 variables that decide the outcome, sets the view and kill criteria, writes the report |

Options:
- `--quick`: a single-agent take in about 5 minutes.
- `--focus earnings|valuation|forensics`: one lens goes deep and the others are trimmed.
- `--peers A,B,C`: sets the comparison group yourself.

Every intermediate memo is saved in `.earnings-desk/runs/` so you can audit how the verdict was reached.

---

## Example reports

Real reports, produced by following the skills on live SEC data. Read the Markdown here, or download the HTML and open it in a browser. The deep dive's [audit trail](examples/MSFT-deep-dive-run/) has every intermediate file: the data brief, four specialist memos, the bull and bear cases with rebuttals, and the portfolio manager's decision.

| Report | Verdict | The finding |
|---|---|---|
| [MSFT · deep-dive (full 8-agent desk)](examples/MSFT-deep-dive-2026-11-18.md) ([HTML](examples/MSFT-deep-dive-2026-11-18.html) · [audit trail](examples/MSFT-deep-dive-run/)) | Research view: **Unattractive**, medium conviction | Great franchise, demanding price. The 10-year break-even FCF margin (31.1%) is above Microsoft's best ever (29.1%), and reported FCF of $67.0B is about $42.4B once finance-lease assets count. OpenAI is now 10.8% of revenue and non-exclusive |
| [AAPL · earnings-recap, Q4 FY26](examples/AAPL-earnings-recap-2026-11-17.md) ([HTML](examples/AAPL-earnings-recap-2026-11-17.html)) | Print quality: **Mixed** | Revenue and guidance beat, but the $0.11 EPS beat is about equal to a tariff refund plus a lower tax rate; inventory is 2.5× last year's level |
| [NVDA · forensic-accounting, FY26](examples/NVDA-forensic-accounting-2026-11-17.md) ([HTML](examples/NVDA-forensic-accounting-2026-11-17.html)) | Forensic verdict: **Watch** | The "elevated" Beneish score is mostly growth, but $14.4B of goodwill came from a non-exclusive license-and-hire deal |

---

## Updating and removing

```bash
claude plugin marketplace update earnings-desk    # fetch the latest catalog
```
```bash
claude plugin update earnings-desk@earnings-desk  # update the plugin
```
```bash
claude plugin uninstall earnings-desk@earnings-desk
```
```bash
claude plugin marketplace remove earnings-desk
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `SEC returned 403 Forbidden` | Set `SEC_USER_AGENT` (name and email) and open a new terminal so it takes effect |
| Skills don't show up after installing | Restart Claude Code or run `/reload-plugins`, then check `claude plugin details earnings-desk` |
| "No quote source reachable" / missing prices | The free public price endpoint is rate-limited. Wait a bit, or add a free `FINNHUB_API_KEY` |
| Consensus estimates missing | Expected without a key. Claude uses web search and labels the source. Add `FINNHUB_API_KEY` or `FMP_API_KEY` for direct data |
| `Unknown ticker` | EDGAR only covers companies that file with the SEC (US-listed, plus foreign issuers filing 20-F) |
| Odd metrics for banks or insurers | Expected. Industrial ratios (gross margin, Altman Z, DCF) don't apply, and the skills switch to bank-appropriate checks |
| `python3: command not found` | Install Python 3.8+ from [python.org](https://www.python.org/downloads/) |

---

## What's in this repo

```
.claude-plugin/marketplace.json     the catalog Claude Code reads (one plugin: earnings-desk)
plugins/earnings-desk/
├── .claude-plugin/plugin.json      plugin name, version, description
├── agents/                         the 8 desk agents (one Markdown file each)
└── skills/                         the 20 skills, one folder each:
    └── <skill>/
        ├── SKILL.md                the instructions Claude follows
        ├── references/             deeper playbooks loaded only when needed
        ├── assets/                 templates (e.g. the HTML report template)
        └── scripts/                small stdlib-Python helpers (SEC data, scores, DCF)
claude-ai/                          ready-to-upload skill zips for Claude.ai / Desktop
examples/                           sample reports
docs/                               demo video, banner and icon
```

The data helpers all live in the `sec-edgar` skill (`edgar.py`, `market.py`, `render_report.py`). The other skills call them as a sibling folder (`../sec-edgar/scripts/`).

---

## FAQ

**Is it free?** Yes. SEC EDGAR is free and keyless, and the optional API keys are free tiers.

**Which companies work?** Anything that files with the SEC: US-listed companies, plus foreign issuers that file 20-F.

**How accurate is it?** Numbers come straight from filings and are cited, but the analysis is AI-generated, so check the sources before acting. See [DISCLAIMER.md](DISCLAIMER.md).

**Does it give buy/sell advice?** No. It produces research views ("Attractive / Fairly valued / Unattractive") with the evidence and what would change the view. It never gives price targets or trade instructions.

**Can I add or improve a skill?** Yes. See [CONTRIBUTING.md](CONTRIBUTING.md) for the authoring standard.

## License

[MIT](LICENSE). **Not investment advice.**
