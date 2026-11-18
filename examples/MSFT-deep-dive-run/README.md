# Deep dive · MSFT · 2026-11-17
- Company: Microsoft Corp (CIK 0000789019, Nasdaq) · FY ends June 30
- Mode: full · Focus: none
- Run dir (absolute): <project>/.earnings-desk/runs/MSFT-2026-11-17
- Keys: FMP no · Finnhub no · Alpha Vantage no · SEC_USER_AGENT set (export SEC_USER_AGENT="earnings-desk-dev test@example.com" before every script call)
- Project cwd for all commands: <project>

## Tools (absolute paths: agents' cwd is the user's project, not the plugin)
S=<plugin>/skills
RUN=<project>/.earnings-desk/runs/MSFT-2026-11-17
python3 $S/sec-edgar/scripts/edgar.py · market.py · render_report.py
python3 $S/financial-statements/scripts/statements.py
python3 $S/forensic-accounting/scripts/scores.py
python3 $S/reverse-dcf/scripts/dcf.py
python3 $S/comps-valuation/scripts/comps.py
python3 $S/filing-diff/scripts/diff_sections.py
Contracts: $S/deep-dive/references/agent-contracts.md · Memo template: $S/deep-dive/references/memo-template.md
Agent definitions (system prompts): <plugin>/skills/../agents/<role>.md

## File index
| File | Owner | Status |
|---|---|---|
| README.md | orchestrator | done (Phase 0) |
