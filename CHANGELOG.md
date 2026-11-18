# Changelog

## 1.1.0 — 2026-11-18
Hardened by real end-to-end runs: a blind A/B against plain Claude (earnings-desk won 4 of 5, tied 1, lost 0) and a full 8-agent deep dive on MSFT. Over 40 issues found and fixed.
- **Proof:** eval suite for `claude plugin eval` plus blind A/B results (`plugins/earnings-desk/evals/`).
- **New example:** MSFT deep dive with its complete audit trail.
- **Data accuracy:**
  - fiscal labels (`FY27 Q1`) for every fiscal calendar
  - 16-week retail quarters (Costco-style)
  - lease-aware FCF (`fcf_incl_finance_leases`)
  - finance-lease debt in the DCF
  - Oracle-style debt tags; NVDA's switch to the `DebtSecuritiesCurrent` tag
  - SG&A fallback
  - ROIC on equity + debt
  - EDGAR history pages for heavy filers
  - insider window reporting
- **Analysis:**
  - implied revenue CAGR in the reverse DCF
  - a bank/insurer workflow
  - comps distortion flags
  - filing diffs that rejoin page-split paragraphs and return saved filing paths
  - `--accession` for releases
- **Skills:**
  - `${CLAUDE_SKILL_DIR}` paths
  - inline citations in every chat answer
  - project-local work folder
  - zsh-safe commands
  - no hard-coded answers in examples
- **Desk:** role-prefixed data files for parallel agents, one valuation convention, clearer conviction and kill-criteria rules.

## 1.0.1 — 2026-11-18
- Repository is now skills-only: removed the landing-page site, CI workflows and repo helper scripts.
- Install commands and plugin metadata point at MozartofCode/Earnings-Intelligence-Agent.

## 1.0.0 — 2026-11-16
First public release.
- 20 skills across six desks: orchestration, data & foundations, earnings season, forensics & quality, valuation & competition, thesis desk.
- 8 specialist subagents (data, earnings, forensics, valuation, industry, bull, bear, portfolio manager) orchestrated by `/earnings-desk:deep-dive`.
- Keyless SEC EDGAR toolkit: normalized XBRL financials with true quarterly cash flows, section-level filing text, 8-K earnings releases, Form 4 insiders.
- Tested analysis scripts: statements, forensic scores, reverse DCF, filing redlines, comps.
- Shared editorial HTML report template (light/dark, print-ready, charts, sources).
