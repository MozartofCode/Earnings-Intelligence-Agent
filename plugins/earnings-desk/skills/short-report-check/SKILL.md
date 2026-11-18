---
name: short-report-check
description: >-
  Fact-checks a short-seller report, activist letter or bearish article against the company's own SEC filings. Breaks the report into individual testable allegations, tests each one with primary evidence (XBRL financials, 10-K/10-Q text and notes, 8-K events such as auditor changes and restatements, Form 4 insider trades, filing redlines, earnings releases), and labels each Supported, Partly supported, Contradicted, Not verifiable from public filings, or Opinion, with short quotes and accession-numbered citations. Adds what has happened since the report (auditor resignations, late filings, restatements, company responses) and the stock reaction. Neutral by design, never accuses. Use when the user shares a short report, says "is this short report right", "fact-check these allegations", "Hindenburg / Muddy Waters / short seller says…", "is the short thesis true", "check this bear case against the filings", "activist letter claims", or pastes allegations about a company. Ends with an "Allegations" verdict.
license: MIT
compatibility: Requires Python 3.8+ and internet access to sec.gov. Web fetch for the report itself and for company responses.
metadata:
  category: "3-forensics-quality"
  version: "1.0.0"
  author: "earnings-desk"
---

# short-report-check · which allegations survive the filings?

A short report mixes three things: facts you can check, inferences from those facts, and opinions. This skill separates them and tests every checkable claim against what the company itself has filed with the SEC, so the user can see which parts hold up.

## When to use
- The user shares a short-seller report, activist letter, bearish article or list of allegations (a URL, PDF, pasted text or summary) about a US-listed company.
- **Not** for a general red-flag screen with no specific allegations (use `forensic-accounting`) or language changes alone (use `filing-diff`).

## Inputs
- `TICKER` (required) and **the report**: a URL (fetch it), a PDF or file (read it), or pasted text. If the user only names a report, search for it and confirm it's the right one (publisher, date) before testing.
- Optional: focus on specific allegations.
- SEC setup (user agent) is in `sec-edgar`.

> **Paths:** `${CLAUDE_SKILL_DIR}` is this skill's own folder. Claude Code fills it in automatically; in other tools, replace it with the folder that contains this `SKILL.md`. Sibling skills such as `${CLAUDE_SKILL_DIR}/../sec-edgar` are installed next to it.
>
> **Working files:** save intermediate JSON and the report JSON in `.earnings-desk/work/` inside the user's current folder (`mkdir -p .earnings-desk/work` first); finished reports go to `earnings-desk-reports/`.
>
> **Chat answer:** lead with the verdict, and put the source next to each key number in the chat reply itself (e.g. `8-K Ex.99.1, accn 0000320193-26-000024` or `web: nasdaq.com, 2026-11-03`). Don't leave citations only in the report.

## Workflow
1. **Get the report and its date.** Save the text to `.earnings-desk/work/TICKER-short-report.txt`. Record publisher, date, title, and the publisher's disclosed position (most short sellers disclose they are short; say so). If the source is anonymous or undated (a newsletter excerpt, a forum post, pasted claims), say so, use the date the user gives or "undated", and still test every claim; just skip the market-reaction step if there's no date.

2. **Extract allegations.** Write a numbered list of **atomic, testable claims**. Split compound sentences ("revenue is inflated through related parties and the auditor is conflicted" is two claims). For each claim note: the exact wording (short quote), the type (see [references/allegation-playbook.md](references/allegation-playbook.md)), severity (High = would change the financial statements or legality; Medium = governance/disclosure; Low = color), and whether it is a **fact**, an **inference** or an **opinion**. Opinions ("the stock is worth $0") are labeled Opinion and not tested.

3. **Check what happened since.** This is often the most decisive evidence.
   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/evidence.py events TICKER --since <report date minus 1 year> > .earnings-desk/work/TICKER-events.json
   ```
   Auditor changes (4.01), non-reliance/restatement (4.02), listing notices (3.01), late filings (NT 10-K/10-Q) and executive departures (5.02) after the report date are strong signals, but they are not proof of a specific allegation. Read each filing for the stated reason: 8-Ks with `python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/edgar.py earnings-release TICKER --accession <accn> --max-chars 60000` (main document plus exhibits, e.g. the auditor's Ex.16 letter), and any other form, including NT 10-K/10-Q late-filing notices, with `edgar.py filing-text TICKER --accession <accn>`. If `window_complete` is false in the events output, raise `--limit`. Also look for the company's direct response (8-K, press release, IR page) and any regulator or special-committee findings (web search, cited).

4. **Test each claim with the right evidence** (the playbook maps claim types to sources):
   ```bash
   # disclosures and wording across filings (counts per filing show whether disclosure grew)
   python3 ${CLAUDE_SKILL_DIR}/scripts/evidence.py search TICKER --terms "related party|related parties,<named entity>,<named person>" --forms 10-K,10-Q --n 4 > .earnings-desk/work/TICKER-ev-1.json
   # terms are literal phrases; use --term "phrase, with comma" for phrases containing commas
   # numbers behind accounting claims
   python3 ${CLAUDE_SKILL_DIR}/../financial-statements/scripts/statements.py TICKER --years 6 --quarters 8 > .earnings-desk/work/TICKER-st.json
   python3 ${CLAUDE_SKILL_DIR}/../forensic-accounting/scripts/scores.py TICKER > .earnings-desk/work/TICKER-scores.json
   # insider selling claims
   python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/edgar.py insiders TICKER --days 365 --limit 150 > .earnings-desk/work/TICKER-insiders.json
   # language the company added or removed around the report
   python3 ${CLAUDE_SKILL_DIR}/../filing-diff/scripts/diff_sections.py TICKER --section 1A > .earnings-desk/work/TICKER-diff-1a.json
   ```
   Read the full filing text at `saved_to` for context around every snippet you rely on. One snippet out of context is not evidence.

5. **Label every claim** using the rubric below. Record the evidence for and against, each with a citation, and one sentence explaining the label.

6. **Market context.** `python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/market.py reaction TICKER --date <report date>` for the day-one move, plus a cited web source for the longer-run move if relevant.

7. Write and render the report.

## Labeling rubric
| Label | Use when |
|---|---|
| **Supported** | The company's own filings or later events confirm the factual core (e.g. the related party, the transaction, the number) |
| **Partly supported** | The facts are confirmed but the report's inference or magnitude isn't, or only some of a claim's parts check out |
| **Contradicted** | Filings directly show something incompatible with the claim (e.g. the claimed revenue decline didn't happen) |
| **Not verifiable** | Public filings can't confirm or refute it (channel checks, interviews, private records). Say what evidence would settle it |
| **Opinion** | A judgment, forecast or valuation claim; record it, don't test it |

Rules:
- **Disclosure is not wrongdoing.** A related party that is disclosed confirms the relationship, not the alleged abuse. Say exactly which part is supported.
- **Later events count, with care.** An auditor resignation after the report supports concerns about controls; it does not by itself prove each specific allegation.
- **Absence of evidence:** "not found in the last 4 10-Ks" is evidence only for things companies are required to disclose there.
- **The company's own word is not a contradiction.** If the only contrary evidence is the company's denial, its own special committee or a clean audit opinion, label the claim **Not verifiable** (and say what the review covered), not Contradicted. Contradicted needs filed facts that are incompatible with the claim, or an independent finding (regulator, court, restatement).
- **Report timing for market reaction:** reports usually come out before the open, so use `event_day_move_pct`; later moves may reflect other news (say which).
- **Never accuse.** Write "the filings confirm…", "consistent with the allegation…", "the report alleges…". Allegations stay allegations unless a filing, regulator or court establishes them.

## Verdict (Allegations)
Weight claims by severity (High 3, Medium 2, Low 1) and count only testable claims:
- **Largely supported:** most High-severity claims Supported or Partly supported, or a serious later event (4.02 restatement, auditor resignation citing the issues, regulator action) matches the core thesis.
- **Mixed:** some High-severity claims hold and others are Contradicted or Not verifiable.
- **Largely unsupported:** High-severity claims are mostly Contradicted or Not verifiable, and no serious later events.
Always report the counts (e.g. "High-severity: 3 supported, 1 partly, 2 not verifiable, 1 contradicted").

## Output
Write `.earnings-desk/work/TICKER-short-report-check.json` per `${CLAUDE_SKILL_DIR}/../sec-edgar/references/report-schema.md`, `"skill": "short-report-check"`.
- **title**: e.g. `"The filings back the *governance* claims, not the fraud claims"`; **subtitle**: publisher, report title, date, disclosed position.
- **verdict**: `{"label": "Allegations", "value": "Largely supported | Mixed | Largely unsupported", "sub": "High-severity: 3 of 5 supported", "tone": "neg | warn | pos"}` (tone from the company's point of view: supported allegations are `neg`).
- **kpis** (4–6): claims tested, Supported, Partly, Contradicted, Not verifiable, serious events since report.
- **sections**:
  1. *Allegation scorecard*: table with #, allegation (short), type, severity, label (pill with tone), key evidence, source.
  2. *What happened since the report*: dated events table (8-K items, NT filings, restatements, company responses, regulator actions).
  3. *The claims that matter most*: callouts for each High-severity claim with evidence for and against.
  4. *Opinions and untestable claims*: what can't be settled from filings and what would settle it.
  5. *Market reaction*: day-one move and context.
  6. *What to watch*: filings or events that would confirm or refute the open claims.
- **sources**: the short report (URL and date), every filing accession used, and cited web sources.

```bash
python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/render_report.py .earnings-desk/work/TICKER-short-report-check.json --out-dir earnings-desk-reports
```
**In chat:** the verdict with the counts, the 2–3 most important findings each with a citation, the serious events since the report, and the report paths.

## Quality bar & pitfalls
- Test the **specific** claim, not a nearby one. If the report says "$983M of sales to a related party in FY23", find that number or say you couldn't.
- Quote filings briefly (one sentence) and cite the accession. Don't paraphrase a filing into something stronger than it says.
- Separate the publisher's facts from its inferences; the same report can be right on facts and wrong on conclusions.
- Note the publisher's position and incentives once, neutrally. Don't dismiss claims because of it, and don't accept them because the stock fell.
- Check dates: evidence from filings made **before** the report shows what was already public; evidence from **after** shows how events developed.

## Next skills
- `/earnings-desk:forensic-accounting` for a full accounting-quality screen
- `/earnings-desk:filing-diff` to redline the sections the report targets
- `/earnings-desk:insider-ownership` for insider-selling claims in depth
- `/earnings-desk:bull-bear-debate` to weigh the short thesis against the long case

_Not investment advice. This skill tests allegations against public filings; it does not establish wrongdoing. Data may contain errors; verify before acting._
