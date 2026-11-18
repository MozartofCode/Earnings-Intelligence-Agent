---
name: filing-diff
description: >-
  Redlines a company's latest 10-K or 10-Q against a prior filing to surface what management quietly changed in risk factors, MD&A, legal proceedings, controls and accounting policies. Triages added, removed and reworded paragraphs, flags priority terms (material weakness, going concern, restatement, investigation, covenant, customer concentration, export controls, tariffs) and measures shifts in hedging, litigation, liquidity, supply-chain, AI and cyber vocabulary. Uses SEC EDGAR, no API key. Use it when the user asks "what changed in the 10-K", "compare this year's risk factors to last year's", "redline the filing", "any new risks", "did they soften the language", "what did they remove", "diff the 10-Q", "same quarter last year MD&A", or wants to catch new risks, removed assurances, going-concern or material-weakness language before the market does.
license: MIT
compatibility: Requires Python 3.8+ (standard library only) and internet access to sec.gov.
metadata:
  category: "1-data-foundations"
  version: "1.0.0"
  author: "earnings-desk"
---

# filing-diff · what management changed when they hoped no one was reading

Companies reuse most of their filing text year after year, so the **edits** are the signal. A new risk factor, a deleted "we believe our liquidity is sufficient", or a customer-concentration sentence that appeared overnight often shows up in the filing before it shows up in the numbers. This skill finds those edits and interprets them.

## When to use
- After a new 10-K or 10-Q drops: "what changed?", "any new risks?".
- Before earnings, to check whether risk language has been building.
- As part of a forensic review (new legal, control or accounting-policy language).

**Not for:** summarizing a single filing (`sec-edgar` filing-text), changes in the numbers (`financial-statements`), call-transcript tone (`transcript-decoder`).

## Inputs
- `TICKER` (required).
- `--form` 10-K (default) or 10-Q.
- `--section`: `1A` risk factors (default), `7` or `mdna`, `3` legal proceedings, `9a` controls, `1` business, `7a` market risk, or any heading text (for example `"Critical Accounting"`).
- `--new` (default 0 = latest) and `--old` (default 1 = the one before) **filing indexes**, plus `--max-items` (default 40).

### Getting the index right (read this)
Indexes count **only filings of the chosen form, plus its `/A` amendments**, newest first.
- **10-K:** `--old 1` is last year's 10-K, `--old 2` is two years back.
- **10-Q:** a fiscal year has **three** 10-Qs (Q4 is reported in the 10-K). So `--old 1` is the **prior quarter** and **`--old 3` is the same quarter last year** (the right comparison for seasonal MD&A language). Verified on MSFT: index 0 = quarter ended 2026-09-30, index 3 = quarter ended 2025-09-30.
- **Amendments shift the count.** A 10-K/A (often just Part III) takes an index slot and usually has no Item 1A, which makes the script fail with "Section not found". Always list filings first and pick the indexes:
  ```bash
  python3 ../sec-edgar/scripts/edgar.py filings TICKER --forms 10-K,10-K/A,10-Q,10-Q/A --limit 12
  ```

## Workflow
1. **Pick the filings** with the `filings` command above. Note filed dates and period ends for both sides of the comparison.

2. **Run the core diffs** (10-K example, then 10-Q year-on-year):
   ```bash
   python3 scripts/diff_sections.py TICKER --section 1A > /tmp/TICKER-diff-1a.json
   python3 scripts/diff_sections.py TICKER --section 7 > /tmp/TICKER-diff-mdna.json
   python3 scripts/diff_sections.py TICKER --section 3 > /tmp/TICKER-diff-legal.json
   python3 scripts/diff_sections.py TICKER --section 9a > /tmp/TICKER-diff-9a.json
   python3 scripts/diff_sections.py TICKER --section "Critical Accounting" > /tmp/TICKER-diff-cap.json
   python3 scripts/diff_sections.py TICKER --form 10-Q --section mdna --old 3 > /tmp/TICKER-diff-q-mdna.json
   ```
   Output JSON: `new_filing`, `old_filing` (form, filed, period, accession, url), `stats` (paragraph counts, added, removed, changed, unchanged, word counts, `word_delta_pct`), `added[]` and `removed[]` (each `text` up to 1,500 chars plus `priority_terms`, sorted with priority hits first and then by length), `changed[]` (`similarity`, inline `redline` with `[-deleted-]` and `{+inserted+}`, `new`, `priority_terms`), `lexicon_per_10k_words` (old, new, delta per category), `truncated` (more items than `--max-items`).

3. **If a section isn't found.** The error includes `new_saved_to` and `old_saved_to` (full plain-text filings). Try the exact heading text (`--section "Legal Proceedings"`), or grep the saved files. Item 3 is often one line pointing to a note ("see Note 14 — Commitments and Contingencies"). In that case diff the note by heading text, for example `--section "Contingencies"`. To compare arbitrary text (two notes, or a 10-K/A you pulled by hand), save each to a file and run `python3 scripts/diff_sections.py --files old.txt new.txt`.

4. **Triage in this order:** priority-term hits in `added` → `removed` paragraphs (deletions are under-read and often the most telling) → `changed` paragraphs with low similarity (0.55–0.75 means substantive rewording) → lexicon deltas. Ignore pure date or fiscal-year rolls and renumbering.

5. **Read the context.** For each finding that matters, open the paragraph in `saved_to` (grep a distinctive phrase) and read the surrounding text. Then check it against the numbers (`statements.py`) and the latest press release. A new risk factor about a customer is far more important if that customer's receivable also jumped.

## Analysis framework

**The edits that matter, and what they usually mean**

| Change | Typical meaning | Severity |
|---|---|---|
| New "material weakness" in Item 9A, or "not effective" controls | Financial reporting can't be relied on yet; restatement and auditor-change risk | High |
| "Substantial doubt … going concern" added | Auditor or management doubts 12-month survival | High |
| "Restate", "non-reliance", "investigation", "subpoena", "Wells notice" added | Regulatory or accounting problem in progress | High |
| A specific risk turned from hypothetical to actual ("could" → "has", "may experience" → "experienced") | The risk materialized | High |
| New named customer, or a "% of revenue" concentration sentence | Concentration rising; pricing power shifting to the customer | Medium–high |
| Assurance removed ("we believe existing cash … sufficient for at least 12 months" deleted or shortened) | Liquidity confidence falling | High |
| Covenant language added or a waiver or amendment mentioned | Lender pressure | Medium–high |
| Brand-new risk factor (new paragraph with a new bolded heading) | Management or counsel sees a new exposure: regulation, export controls, tariffs, AI, a product, a geography | Medium |
| Risk factor deleted | Risk resolved, or deemphasized to look cleaner. Check which | Medium |
| Revenue-recognition, reserve or capitalization policy rewording in critical accounting estimates | Judgment changed; can move earnings without changing the business | Medium–high |
| Hedging-word density up sharply in MD&A | Less confidence in the outlook | Low–medium |
| Specific numbers replaced with vague language ("approximately 40%" → "a significant portion") | Less transparency, often because the number got worse | Medium |
| Legal matter moved from "remote" to "reasonably possible", or an accrual is added | Loss now estimable or likely | Medium–high |
| Segment descriptions or KPI definitions changed | Possible re-cast that hides a weak unit | Medium |

**Reading the lexicon.** `lexicon_per_10k_words` counts occurrences per 10,000 words for hedging, negative, litigation, liquidity, supply_chain, ai and cyber terms. Treat a delta as a **pointer**, not a finding. A delta of more than ±20% of the old rate in litigation, liquidity or negative words is worth chasing to the paragraphs that caused it. Counting is crude substring matching: "may" also matches words that contain it, and `" ai "` needs spaces on both sides, so "AI," or "AI." is missed. Confirm with the actual text before you write anything.

**Reading the stats.**
- `word_delta_pct` above +10% for risk factors in one year is a lot. Find where the words went.
- Many `changed` items with high similarity (above 0.9) are usually copy edits.
- Risk factors are long (NVDA's 1A is about 17,000 words). Expect 20–60 changes in a normal year; a near-zero change count after a turbulent year is itself notable (boilerplate inertia).

**10-Q specifics.** 10-Q Part II Item 1A often says only "no material changes from the 10-K". Any substantive 10-Q risk-factor update is unusual and important. For MD&A, compare with the same quarter last year (`--old 3`) to see how management's explanation of the same seasonal period changed, and with the prior quarter (`--old 1`) to catch fresh developments.

**Questions to ask of every finding:** Is it new information or new disclosure of old information? Does it connect to a number (receivables, inventory, segment margin, debt)? Is the language more or less specific than before? Who is the audience: is this lawyers protecting against a lawsuit, or a business change? Did peers add the same language (industry-wide, like tariffs or export controls) or is it company-specific (more important)?

## Output
Write `/tmp/TICKER-filing-diff.json` per `../sec-edgar/references/report-schema.md`, `"skill": "filing-diff"`.

- **title**: the single most important change, e.g. `"A new *customer concentration* risk appears"` or `"Mostly *boilerplate*, one real change"`.
- **subtitle**: "10-K filed <date> vs. 10-K filed <date> · Items 1A, 7, 3, 9A".
- **verdict**: `{"label": "Disclosure change", "value": "Benign | Notable | Concerning | Red flag", "tone": "pos|neutral|warn|neg"}`.
- **kpis** (3–5): new risk paragraphs, removed paragraphs, % of text changed, risk-factor word count change, priority-term hits, largest lexicon move.
- **sections**:
  1. *What changed that matters*: 3–6 callouts ranked by severity. Each one has a short quote from the new (or deleted) text, the section, and our interpretation, labeled as judgment.
  2. *Risk factors (1A)*: stats table, top added and removed paragraphs (shortened), key redlines.
  3. *MD&A*: changed explanations, numbers replaced with vague language, the 10-Q y/y compare if run.
  4. *Legal, controls and accounting policies*: Items 3 and 9A and critical accounting estimates findings ("no change" is a valid result).
  5. *Language shifts*: lexicon table (category, old, new, delta) and a bar chart of deltas.
  6. *What to watch*: how each change could show up in the next print or filing.
- **sources**: both filings' accession numbers and URLs for every section compared.

```bash
python3 ../sec-edgar/scripts/render_report.py /tmp/TICKER-filing-diff.json --out-dir earnings-desk-reports
```
**In chat** give the verdict, the top 3 changes (each with a short quote and its meaning), a one-line stats summary, and the report paths.

## Quality bar & pitfalls
- **Quote, don't paraphrase,** the key changed sentence (briefly), so the user can verify. Cite the filing.
- **Ignore churn.** Date rolls, renumbered notes, and "fiscal 2025" → "fiscal 2026" edits are noise. The paragraph matcher treats reflowed text as changed, so read the redline before calling it substantive.
- **Section extraction can grab the wrong block.** It takes the longest match between "Item" headings. Check that both sides cover the same section by comparing the first lines and `stats.old_words` vs. `new_words`. A 90% word drop usually means a bad extraction, not a rewrite.
- **Moved is not new.** Paragraphs that moved between sections show up as added in one diff and removed in another. Check before calling a risk "new".
- **Deletions need a reason.** A removed risk could mean it was resolved (good), folded into another paragraph (neutral) or hidden (bad). Find out which.
- **Don't overstate.** Most risk-factor additions are defensive legal drafting. Reserve "red flag" for control failures, going concern, restatement, investigations and materialized risks.

## Next skills
- `/earnings-desk:forensic-accounting` if controls, policies or legal language changed
- `/earnings-desk:transcript-decoder` to see whether management's spoken tone matches the written edits
- `/earnings-desk:earnings-preview` to turn new risks into questions for the next call
- `/earnings-desk:thesis-tracker` to log the change against your thesis
- `/earnings-desk:read-through` if the new risk names a customer, supplier or competitor

_Not investment advice. Data is from public filings and may contain errors; verify before acting._
