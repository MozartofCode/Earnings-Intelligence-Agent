---
name: sec-edgar
description: The data and report toolkit behind every earnings-desk skill. Pulls official SEC EDGAR data for any US-listed company with no API key, including normalized XBRL financials (annual and quarterly, with year-to-date cash flows converted into real quarters), 10-K/10-Q/8-K filing text with section extraction (Risk Factors, MD&A), earnings press releases (8-K Item 2.02 exhibits), Form 4 insider transactions and SIC peers. Also provides market prices, earnings-reaction history and optional consensus via free API keys, plus the shared HTML report renderer. Use it whenever you need trustworthy fundamentals, filings, insider trades, or a primary source for a number, or when the user asks to "pull the 10-K", "get the financials", or "check SEC filings" for a ticker.
license: MIT
compatibility: Requires Python 3.8+ (standard library only) and internet access to sec.gov. Optional FMP_API_KEY, FINNHUB_API_KEY or ALPHAVANTAGE_API_KEY.
metadata:
  category: "1-data-foundations"
  version: "1.0.0"
  author: "earnings-desk"
---

# sec-edgar · data & report toolkit

Primary-source data for every other skill. When a number can come from the SEC, it comes from here, not from memory or a blog.

## When to use
- Any skill (or user) needs financial statements, filing text, press releases, insider trades or peers for a US-listed company.
- You need to **verify** a figure you saw elsewhere. Cite the accession number.
- You need to render a finished report as HTML using the shared earnings-desk template.

## Setup (once)
SEC requires automated tools to identify themselves. If a command returns a 403 error, ask the user for a name and email and have them set it themselves (never invent one):
```bash
export SEC_USER_AGENT="Jane Doe jane@example.com"
```
Optional free-tier keys add consensus estimates, EPS surprise history, earnings calendars and reliable quotes: `FINNHUB_API_KEY`, `FMP_API_KEY`, `ALPHAVANTAGE_API_KEY`. Run `python3 ${CLAUDE_SKILL_DIR}/scripts/market.py status` to see what is configured. **Everything degrades gracefully.** When a key is missing, the JSON says `"available": false` with a hint, and you fall back to web search and label the figure as such.

> **Paths:** `${CLAUDE_SKILL_DIR}` is this skill's own folder. Claude Code fills it in automatically; in other tools, replace it with the folder that contains this `SKILL.md`. Sibling skills such as `${CLAUDE_SKILL_DIR}/../sec-edgar` are installed next to it.
>
> **Working files:** save intermediate JSON and the report JSON in `.earnings-desk/work/` inside the user's current folder (`mkdir -p .earnings-desk/work` first); finished reports go to `earnings-desk-reports/`.
>
> **Chat answer:** lead with the verdict, and put the source next to each key number in the chat reply itself (e.g. `8-K Ex.99.1, accn 0000320193-26-000024` or `web: nasdaq.com, 2026-11-03`). Don't leave citations only in the report.

## Commands
Scripts live in `scripts/` next to this file. Other skills reach them at `${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/`. All output is JSON. Everything the desk writes stays in the user's current folder: SEC responses are cached in `.earnings-desk/cache/` (safe to delete), intermediate files go in `.earnings-desk/work/`, and reports in `earnings-desk-reports/`. Heavy filers (big banks) are handled: `filings` and `earnings-release` read EDGAR's older history pages when the recent block runs out.

| Need | Command |
|---|---|
| Ticker → CIK, name, exchange | `python3 ${CLAUDE_SKILL_DIR}/scripts/edgar.py cik NVDA` |
| Profile + latest filings | `python3 ${CLAUDE_SKILL_DIR}/scripts/edgar.py profile NVDA` |
| Filing list | `python3 ${CLAUDE_SKILL_DIR}/scripts/edgar.py filings NVDA --forms 10-K,10-Q,8-K --limit 12` |
| Normalized financials (35 metrics, annual + quarterly) | `python3 ${CLAUDE_SKILL_DIR}/scripts/edgar.py facts NVDA --periods 12 --annual 6` |
| One raw XBRL tag | `python3 ${CLAUDE_SKILL_DIR}/scripts/edgar.py concept NVDA RevenueFromContractWithCustomerExcludingAssessedTax` |
| Filing text, one section | `python3 ${CLAUDE_SKILL_DIR}/scripts/edgar.py filing-text NVDA --form 10-K --section 1A` (sections: `1`, `1A`, `1C`, `3`, `7`/`mdna`, `7A`, `8`, `9A`, or heading text; `--index 1` = prior filing) |
| Latest earnings press release | `python3 ${CLAUDE_SKILL_DIR}/scripts/edgar.py earnings-release NVDA > .earnings-desk/work/NVDA-er0.json` (`--index 1` = previous quarter; `--accession` picks any specific 8-K; default 150k chars, each exhibit marked `===== EXHIBIT: … =====`) |
| Insider transactions | `python3 ${CLAUDE_SKILL_DIR}/scripts/edgar.py insiders NVDA --days 180` |
| SIC peer universe | `python3 ${CLAUDE_SKILL_DIR}/scripts/edgar.py peers NVDA` (a starting list only; refine by business model) |
| Quote / market cap | `python3 ${CLAUDE_SKILL_DIR}/scripts/market.py quote NVDA` |
| Price history | `python3 ${CLAUDE_SKILL_DIR}/scripts/market.py history NVDA --range 2y` |
| Move around any event date (e.g. a short report) | `python3 ${CLAUDE_SKILL_DIR}/scripts/market.py reaction NVDA --date 2026-08-27` (prior close to next close; source named in the output of `history`) |
| Post-earnings moves (last N prints) | `python3 ${CLAUDE_SKILL_DIR}/scripts/market.py reactions NVDA --n 8` |
| Consensus estimates (key needed) | `python3 ${CLAUDE_SKILL_DIR}/scripts/market.py estimates NVDA` |
| EPS surprise history (key needed) | `python3 ${CLAUDE_SKILL_DIR}/scripts/market.py surprises NVDA` |
| Next earnings date | `python3 ${CLAUDE_SKILL_DIR}/scripts/market.py calendar NVDA` |
| Render a report | `python3 ${CLAUDE_SKILL_DIR}/scripts/render_report.py report.json --out-dir earnings-desk-reports` |

Long filing text is saved to disk (`saved_to` in the JSON). Use `grep`/`Read` on that file rather than pulling hundreds of thousands of characters into context.

## Rules for using the data
1. **Cite everything.** Every figure carries its source: `10-Q filed 2026-08-27 (accn 0001045810-26-000082)`, `8-K Ex.99.1`, a URL, or `web search: <site>, <date>`. Put the source list in the report's `sources`.
2. **Respect the flags.** `derived: true` means the quarter was computed (FY or YTD minus earlier quarters). Derived EPS is approximate. `tags_used` shows which XBRL concept fed each metric. When a company switched tags, sanity-check the seam.
3. **Units:** values are raw USD (not thousands), per-share values in USD, and shares in units. Format for humans as `$96.2B`, `$2.46`, `7.45B shares`. In statements.py, `fy` is the calendar year the fiscal period ends, `cash_conversion` = FCF / net income and `ocf_to_ni` = operating cash flow / net income.
4. **Fiscal calendars differ.** NVDA's FY27 ends January 2027 and AAPL's ends September. Always label periods with the period-end date or the company's own fiscal label.
5. **Non-US / non-SEC companies:** EDGAR covers SEC registrants only. Foreign private issuers file 20-F/6-K, so use `--form 20-F`. For anything not on EDGAR, say so and use web search with citations.
6. **Banks, insurers, REITs:** many industrial metrics (gross margin, DSO, Altman Z) do not apply. Say so rather than printing a misleading number.

## Rendering reports
Every earnings-desk skill ends by writing a report JSON that follows [references/report-schema.md](references/report-schema.md), then runs:
```bash
python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/render_report.py .earnings-desk/work/<ticker>-<skill>.json --out-dir earnings-desk-reports
```
It writes `earnings-desk-reports/<TICKER>-<skill>-<date>.html` (the shared editorial "research terminal" look: light/dark, print-ready, charts, sources) plus a `.md` twin, and prints any schema warnings. Fix the warnings, then give the user both paths.

## Output format (when used directly)
Answer the question with a compact table or bullets, cite the filings, and offer the next skill (e.g. "Want the full `financial-statements` breakdown or a `forensic-accounting` check?").

## Pitfalls
- A ticker that is missing from the SEC list may be delisted, OTC-only or foreign. Check `suggestions` in the error.
- Section extraction picks the longest matching block. For unusual layouts (bank annual reports), confirm the section start in `saved_to`.
- Yahoo-based keyless prices are best-effort and may be rate-limited. Never retry in a loop. Use a key or web search instead.

_Not investment advice. Data is from public filings and may contain errors; verify before acting._
