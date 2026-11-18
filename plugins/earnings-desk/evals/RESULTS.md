# Blind A/B results: Claude vs. Claude + earnings-desk

**Date:** November 2026. **Cases:** the five in this folder (AAPL beat quality, NVDA forensics, MSFT priced-in growth, TSLA risk-factor changes, JPM bank guardrail).

## Method
- **Two arms, same model, same tools.** Both arms got web search, web fetch and a shell. The *plain* arm was told not to use the earnings-desk files. The *desk* arm had the 20 skills available and chose one itself from the question (it picked the intended skill in 10 of 10 runs across both rounds).
- **Blind judging.** Each pair was shuffled into A/B with a random seed. Paths, skill names and script names were redacted. A separate judge model scored each answer without knowing which arm wrote it, and spot-checked at least two numbers per case against SEC filings and the web.
- **Scoring.** Case-specific pass/fail criteria (the same ones as the `llm` graders in this folder), plus 1–10 scores for sourcing, depth, accuracy and usefulness. Only the chat answer was judged, not the HTML report.
- **Limits.** One run per arm per case, an AI judge, and a small sample. Treat this as strong directional evidence, not a benchmark. Run `claude plugin eval` with the suite in this folder for repeatable numbers.

## Round 2 (current skills)

| Case | Winner | Plain: criteria | Desk: criteria |
|---|---|---|---|
| AAPL: was it a quality beat? | **earnings-desk** | 1 / 3 | 3 / 3 |
| NVDA: accounting red flags? | **earnings-desk** | 1 / 2 | 2 / 2 |
| MSFT: what's priced in at $500? | **earnings-desk** | 1 / 1 | 1 / 1 |
| TSLA: risk-factor changes | tie | 1 / 1 | 1 / 1 |
| JPM: Altman Z on a bank | **earnings-desk** | 1 / 1 | 1 / 1 |

**Wins: earnings-desk 4, plain 0, ties 1.** Criteria passed: **8/8 vs. 5/8.**

| Average score (1–10) | Plain Claude | earnings-desk |
|---|---|---|
| Sourcing | 5.4 | **8.6** |
| Depth | 6.6 | **8.8** |
| Accuracy | 7.2 | **7.6** |
| Usefulness | 6.8 | **8.8** |

Judge notes, in brief:
- **AAPL:** the desk put numbers on the tariff-refund and tax-rate help in the EPS beat and flagged the inventory build. The plain answer missed both.
- **NVDA:** the desk ran four screens with their drivers explained, found the Groq goodwill, and caught a later 8-K. The plain answer ran no screens.
- **MSFT:** the desk's implied growth was compared with history and backed by weighted scenarios and better sources.
- **JPM:** both arms correctly rejected Altman Z for a bank. The desk backed that with current, filing-sourced bank metrics; the plain answer used rough, unsourced numbers.
- **Errors the judge caught in desk answers:** one garbled figure (TSLA) and a CET1 ratio of 14.0% where the press release says 13.9% (JPM).

## Round 1 (before fixes), and what changed
In round 1 the desk won AAPL and JPM, tied TSLA and **lost MSFT narrowly**. The reason: its citations were in the HTML report but not in the chat answer, so sourcing scored 4/10. The NVDA case was excluded because a worked example inside the forensic skill contained NVDA's own scores. The runs also surfaced about 25 script and instruction issues. These were fixed before round 2:
- Every skill now cites key numbers inline in the chat answer.
- The NVDA example was removed from the forensic skill.
- A bank workflow was added.
- Fiscal-year labels, ROIC for net-cash companies, NVDA's net cash, page-break paragraph splits in filing diffs, and older EDGAR history for heavy filers are all fixed.
- The reverse DCF now reports the implied revenue CAGR.

The plain-arm answers were not re-run for round 2; the same answers were judged again against the updated desk answers.
