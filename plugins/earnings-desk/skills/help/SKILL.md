---
name: help
description: >-
  Concierge and router for the earnings-desk plugin. Shows what the 20 research skills and 8 analyst agents can do as a categorized menu with example prompts, recommends ready-made workflows (earnings day playbook, new idea, is this a fraud, what's priced in), checks setup (SEC_USER_AGENT and optional free FMP, Finnhub and Alpha Vantage keys, with signup links), and routes a vague question to the single best skill. Use when the user asks "what can you do", "help", "how do I research a stock", "where do I start", "which skill should I use", "how do I set this up", "do I need an API key", "what is earnings-desk", or asks an investing research question without naming a skill.
license: MIT
compatibility: Setup check requires Python 3.8+. Everything else is plain guidance.
metadata:
  category: "0-orchestration"
  version: "1.0.0"
  author: "earnings-desk"
---

# help · your concierge to the research desk

earnings-desk is a free, open-source equity research desk: **20 skills and 8 specialist analysts** running on SEC EDGAR, with no paid data required. This skill helps the user find the right tool fast, get set up, and follow a proven workflow.

## When to use
- "What can you do?", "help", "where do I start?", "which skill for X?"
- Setup questions: keys, SEC 403 errors, "is anything configured?"
- A research question that doesn't name a skill. Route it (see **Routing**) and offer to run it.
- **Not** when the user has already named a skill or the intent is unambiguous ("recap NVDA's earnings"). Just run that skill.

## Inputs
- Optional: the user's question or goal, a ticker, or `setup`. With no input, show the menu.

> **Paths:** `${CLAUDE_SKILL_DIR}` is this skill's own folder. Claude Code fills it in automatically; in other tools, replace it with the folder that contains this `SKILL.md`. Sibling skills such as `${CLAUDE_SKILL_DIR}/../sec-edgar` are installed next to it.
>
> **Working files:** save intermediate JSON and the report JSON in `.earnings-desk/work/` inside the user's current folder (`mkdir -p .earnings-desk/work` first); finished reports go to `earnings-desk-reports/`.
>
> **Chat answer:** lead with the verdict, and put the source next to each key number in the chat reply itself (e.g. `8-K Ex.99.1, accn 0000320193-26-000024` or `web: nasdaq.com, 2026-11-03`). Don't leave citations only in the report.

## Workflow
1. **Read the intent.** Is it a menu request, a setup question, or a research question in disguise?
2. **Menu request:** show the menu (below) in full, then the workflows, then ask "What are you researching?". Keep your own words short. The tables are the content.
3. **Setup question** (or the first time anyone asks for help): run the setup check and explain the results (see **Setup**).
4. **Research question:** pick the single best skill from **Routing**, say why in one line, show the exact command, and offer to run it now. If two skills fit, recommend one and name the other as the follow-up.
5. Always end with one concrete next step the user can type.

## The menu
Invoke any skill as `/earnings-desk:<skill> TICKER`, or just ask in plain English.

**0 · Orchestration**
| Skill | What it answers | Try |
|---|---|---|
| `deep-dive` | The full desk: 8 analysts, debate, PM verdict, investment memo | `/earnings-desk:deep-dive NVDA` (add `--quick` or `--focus valuation`) |
| `help` | What can I do, where do I start, am I set up? | "help me research a stock" |

**1 · Data foundations**
| Skill | What it answers | Try |
|---|---|---|
| `company-tearsheet` | **Start here:** a one-page snapshot of any company | "give me a tearsheet on COST" |
| `financial-statements` | 3 statements, margins, returns, ratio trends | "show MSFT's financials for 5 years" |
| `filing-diff` | What changed in the 10-K/10-Q (risk factors, MD&A) | "what changed in TSLA's risk factors?" |
| `sec-edgar` | Raw SEC data: filings, XBRL, insiders, press releases | "pull AAPL's latest 10-K" |

**2 · Earnings season**
| Skill | What it answers | Try |
|---|---|---|
| `earnings-preview` | What to expect, what's priced in, what to watch | "preview AMD's earnings" |
| `earnings-recap` | Beat or miss? Guide? Quality of the quarter | "did NVDA beat?" |
| `transcript-decoder` | Call tone, hedging, evasive answers in Q&A | "decode META's earnings call" |
| `guidance-tracker` | Does management hit its own guidance? | "is AMZN's guidance credible?" |
| `kpi-tracker` | Company-specific KPIs over time | "track NFLX's subscriber and ARPU trends" |
| `read-through` | What one company's print means for others | "what does TSMC's quarter mean for NVDA and AMD?" |

**3 · Forensics & quality**
| Skill | What it answers | Try |
|---|---|---|
| `forensic-accounting` | Beneish, Altman, Piotroski, accruals, red flags | "any accounting red flags at SMCI?" |
| `capital-allocation` | Buybacks vs. SBC, M&A, ROIC: a management grade | "how well does GOOGL allocate capital?" |
| `insider-ownership` | Insider buying/selling clusters, 13F, short interest | "are insiders selling PLTR?" |

**4 · Valuation & competition**
| Skill | What it answers | Try |
|---|---|---|
| `reverse-dcf` | What growth is priced into today's price? | "what's priced into TSLA?" |
| `comps-valuation` | Peer multiples, growth-adjusted cheap vs. rich | "comps for CRWD vs. peers" |
| `moat-analysis` | 7 Powers and Porter: how durable is the moat? | "does V have a moat?" |

**5 · Thesis desk**
| Skill | What it answers | Try |
|---|---|---|
| `bull-bear-debate` | Steelmanned bull vs. bear, rebuttal, judged | "bull vs bear on INTC" |
| `thesis-tracker` | A living thesis file with kill criteria, checked each quarter | "save my thesis on ASML" |

**The desk's 8 analysts** (used by `deep-dive`, and callable directly in Claude Code): data-analyst · earnings-analyst · forensic-accountant · valuation-analyst · industry-analyst · bull-analyst · bear-analyst · portfolio-manager.

## Workflows (recommend the one that matches the goal)
| Goal | Playbook |
|---|---|
| **New idea:** "is this worth my time?" | `company-tearsheet` → `deep-dive` (or `deep-dive --quick` first) → `thesis-tracker` |
| **Earnings day playbook** | before the print: `earnings-preview` · after: `earnings-recap` → `transcript-decoder` → `guidance-tracker` → `thesis-tracker` (check the kill criteria) |
| **"Is this a fraud?"** | `forensic-accounting` → `filing-diff` → `insider-ownership` → `capital-allocation` |
| **"What's priced in?"** | `reverse-dcf` → `comps-valuation` → `moat-analysis` (is the premium earned?) |
| **Sector earnings season** | `earnings-recap` on the bellwether → `read-through` → `kpi-tracker` on the names that matter |
| **"I already own it"** | `thesis-tracker` (create or review) → `guidance-tracker` → `insider-ownership` each quarter |
| **Stress-test my view** | `bull-bear-debate` → `forensic-accounting` → `thesis-tracker` |

## Routing (ambiguous question → best skill)
| If the user says… | Route to | Then offer |
|---|---|---|
| "tell me about X", "what does X do", "quick look" | `company-tearsheet` | `deep-dive` |
| "should I buy X?", "is X a good investment?", "full analysis" | `deep-dive` (frame it as a research view, not advice) | `thesis-tracker` |
| "is X overvalued / cheap?" | `reverse-dcf` | `comps-valuation` |
| "how did earnings go?", "did they beat?" | `earnings-recap` | `transcript-decoder` |
| "earnings next week", "what to expect" | `earnings-preview` | `read-through` |
| "can I trust management?" | `guidance-tracker` | `capital-allocation` |
| "is this a scam / too good to be true?", "short report" | `forensic-accounting` | `filing-diff` |
| "who are the competitors?", "is it defensible?" | `moat-analysis` | `comps-valuation` |
| "why did the stock drop?" | `earnings-recap` if near a print, else `filing-diff` and `insider-ownership` | `bull-bear-debate` |
| "compare X and Y" | `comps-valuation` | `company-tearsheet` on each |
Requests for personal advice (what to buy, how much, when to sell) get a short note: earnings-desk produces research views, not personalized investment advice. Then offer the research skill that informs the decision.

## Setup
Run the check (scripts live in the sibling skill):
```bash
python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/market.py status
```
If the relative path fails, Glob `**/earnings-desk/**/skills/sec-edgar/scripts/market.py` and use that path. Present the result as a table: **Key · Status · What it unlocks**. Then explain:

**Required: nothing.** SEC EDGAR data (financials, filings, insiders) needs no key.

**Strongly recommended: `SEC_USER_AGENT`.** The SEC asks automated tools to identify themselves, and a 403 error means you need it. The user sets it themselves with their own name and email (never invent one):
```bash
export SEC_USER_AGENT="Jane Doe jane@example.com"     # add to ~/.zshrc or ~/.bashrc to persist
```

**Optional free-tier keys** (each one only enhances results; everything degrades gracefully to web search, labeled as such):
| Key | Free signup | Unlocks |
|---|---|---|
| `FMP_API_KEY` | https://site.financialmodelingprep.com/developer/docs | Reliable quotes, consensus estimates, earnings calendar |
| `FINNHUB_API_KEY` | https://finnhub.io/register | Quotes, EPS surprise history, earnings calendar |
| `ALPHAVANTAGE_API_KEY` | https://www.alphavantage.co/support/#api-key | Quotes, earnings history |
Set them the same way (`export FINNHUB_API_KEY=...`), then restart the session. **Never ask the user to paste a key into chat.** They set it in their own shell. If only one key is wanted, recommend Finnhub (surprises plus calendar) or FMP (estimates).

Other setup notes: Python 3.8+ with the standard library only. Caches and run files live in `./.earnings-desk/`. Reports are written to `./earnings-desk-reports/`. On Claude.ai, skills run without subagents, so `deep-dive` uses its sequential fallback automatically.

## Output
A compact, scannable answer: the menu tables (when asked for), one recommended workflow or skill with its exact command, the setup table (when relevant), and a single "type this next" line. No report rendering is needed for help.

## Quality bar & pitfalls
- **Route, don't lecture.** If the intent is clear, recommend one skill and offer to run it. Don't dump the whole menu on someone who asked a specific question.
- Show the full menu only when asked "what can you do" or similar.
- Never imply a paid key is required. Never handle key values in chat.
- Use the user's ticker in example commands when they gave one.
- Keep the advice boundary. Research views and frameworks are fine. Personal buy/sell/sizing advice is not.

_Not investment advice. earnings-desk produces research from public filings and may contain errors; verify before acting._
