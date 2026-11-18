---
name: forensic-accounting
description: >-
  Forensic earnings-quality and accounting red-flag review of any US-listed company from SEC filings, no API key. Computes the Beneish M-score, Altman Z and Z'', Piotroski F-score, Sloan accrual ratio and DSO/DIO/DPO drift with every component shown, then runs a qualitative checklist covering revenue recognition changes, reserve releases, capitalized costs, non-GAAP adjustment creep, auditor changes and critical audit matters, related parties, segment recasts, channel stuffing, off-balance-sheet items, and 8-K Item 4.01/4.02 checks. Ends with a Clean / Watch / Red flags scorecard. Use it when the user asks "are the earnings real", "any accounting red flags", "is this a fraud", "earnings quality", "Beneish / Altman / Piotroski score", "aggressive accounting", "is it cooking the books", "bankruptcy risk", "check the quality of earnings" or "short-seller allegations".
license: MIT
compatibility: Requires Python 3.8+ (standard library only) and internet access to sec.gov.
metadata:
  category: "3-forensics-quality"
  version: "1.0.0"
  author: "earnings-desk"
---

# forensic-accounting · are the earnings real?

Quantitative screens tell you **where** to dig. The filings tell you **whether** there is anything there. This skill runs both and refuses to call fraud on a score alone: it ends with an evidence-backed scorecard, with every flag traced to a number or a sentence in a filing.

## When to use
- "Are the earnings real?", "any red flags?", "earnings quality", "distress risk", a short report just came out, or a stock looks too good.
- After `financial-statements` shows weak cash conversion, rising DSO or DIO, or margin jumps without explanation.

**Not for:** general ratio analysis (`financial-statements`), language changes alone (`filing-diff`), management's capital decisions (`capital-allocation`).

## Inputs
- `TICKER` (required).
- `--market-cap` (USD) for Altman's original Z. Get it from `market.py quote`.
- Optional focus (for example a specific short-seller allegation to test).

## Workflow
1. **Market cap, then scores**
   ```bash
   python3 ../sec-edgar/scripts/market.py quote TICKER        # use market_cap
   python3 scripts/scores.py TICKER --market-cap <market_cap> > /tmp/TICKER-scores.json
   ```
   Output: `fiscal_year` and `prior_year` (period ends compared), `sic`, `is_financial`, and:
   - `beneish`: `m_score`, `zone` (elevated above −1.78), `components` (DSRI, GMI, AQI, SGI, DEPI, SGAI, LVGI, TATA), `defaulted_to_1` (components set to 1.0 because inputs were missing), or `available: false` with `missing`.
   - `altman`: `z_original` and zone (needs `--market-cap`), `z_double_prime` and zone, `components_original`, `preferred` (original for SIC 2xxx/3xxx manufacturers with a market cap, otherwise Z'').
   - `piotroski`: `f_score`, `zone`, `checks` (9 booleans; missing data counts as a fail).
   - `sloan`: `accrual_ratio_pct` and zone (above 10% warning, 5–10% watch, below 0 clean).
   - `working_capital_trend` (up to 5 fiscal years: DSO, DIO, DPO, cash conversion, SBC % revenue, gross margin, share-count change), `quick_flags`, `caveats`, `sources`.

2. **Multi-year context.** Scores compare only the latest year with the prior one. Run the statements for the trend:
   ```bash
   python3 ../financial-statements/scripts/statements.py TICKER --years 6 --quarters 8 > /tmp/TICKER-st.json
   ```
   Check net income vs. OCF for each year, receivables growth vs. revenue growth, inventory growth vs. COGS growth, and goodwill and capex trends.

3. **Filing events** (auditor and restatement checks)
   ```bash
   python3 ../sec-edgar/scripts/edgar.py filings TICKER --forms 8-K,8-K/A --limit 200
   python3 ../sec-edgar/scripts/edgar.py filings TICKER --forms "NT 10-K,NT 10-Q,10-K/A,10-Q/A" --limit 20
   ```
   In the 8-K `items` field look for **4.01** (auditor change), **4.02** (non-reliance on prior financials, i.e. a restatement), 5.02 (CFO or CAO departures) and 2.06 (impairments). NT filings are late filings. Amended 10-K/10-Qs that restate numbers (not just Part III) are serious.

4. **The 10-K read** (save it once, then grep instead of pulling everything into context)
   ```bash
   python3 ../sec-edgar/scripts/edgar.py filing-text TICKER --form 10-K --section 9A --max-chars 15000
   python3 ../sec-edgar/scripts/edgar.py filing-text TICKER --form 10-K --section 8 --max-chars 2000   # prints saved_to
   grep -n -i -E "critical audit matter|material weakness|related part|variable interest|off-balance|guarantee|factoring|supplier finance|bill-and-hold|change in (accounting )?estimate|capitaliz|reserve|allowance|restat|principal versus agent|segment" "<saved_to>" | head -80
   ```
   Read the auditor's report (critical audit matters and the auditor's name and tenure), the revenue recognition policy, allowances and reserves, capitalization policies, related-party note, commitments and contingencies, and the segment note.

5. **GAAP vs. adjusted gap** (last 4–8 quarters)
   ```bash
   python3 ../sec-edgar/scripts/edgar.py earnings-release TICKER --index 0 --max-chars 40000
   python3 ../sec-edgar/scripts/edgar.py earnings-release TICKER --index 4 --max-chars 40000
   ```
   From the reconciliation table record GAAP vs. non-GAAP operating income or EPS and each add-back. Track the gap as a % of GAAP and whether new add-back categories appear.

6. **Language changes**: `python3 ../filing-diff/scripts/diff_sections.py TICKER --section "Critical Accounting"` and `--section 9a` show whether policies or controls wording changed.

7. **Score the checklist and write the verdict** using the framework below.

## Analysis framework
Full formulas, thresholds, academic origins and 25 red flags with where to find each are in [references/forensic-playbook.md](references/forensic-playbook.md).

**Quantitative screens: how to read them**

| Screen | Threshold | Read |
|---|---|---|
| Beneish M-score | above −1.78 elevated (−2.22 is the stricter 5-variable cut-off) | Find the component(s) driving it. DSRI above 1.2, GMI above 1.1, AQI above 1.2 or TATA above 0.03 are the manipulation-type signals; SGI is a pressure signal, not evidence |
| Altman Z (original) | above 2.99 safe, 1.81–2.99 grey, below 1.81 distress | Manufacturers only. Market-cap-driven X4 can swamp everything |
| Altman Z'' | above 2.6 safe, 1.1–2.6 grey, below 1.1 distress | Non-manufacturers and private-style test. Uses book equity |
| Piotroski F | 7–9 strong, 4–6 neutral, 0–3 weak | Check which checks failed and why. Missing data = fail |
| Sloan accruals | above 10% warning, 5–10% watch, below 0 clean | Persistent positive accruals predict lower future earnings |
| DSO / DIO drift | +20% over the window | Receivables or inventory outgrowing sales or COGS |
| Cash conversion | FCF/NI below 0.8 | Earnings not becoming cash |
| SBC % revenue | above 10% | Adjusted earnings materially flattered |

**Known false positives (say so in the report):**
- **Hyper-growth inflates Beneish.** SGI is weighted 0.892, so fast growers look "elevated" with nothing wrong. NVDA FY26 scored **−1.15 "elevated"**, driven by SGI 1.66 and AQI 1.52 (other long-term assets grew), plus TATA 0.084 (net income ahead of OCF in a hyper-growth year with a working capital build). DSRI was 1.01 and GMI 1.06, which is clean. Recompute the score with SGI set to 1.0 to see how much is growth alone: NVDA would be about −1.74, still close to the line, so explain the AQI and TATA drivers too.
- **AQI** jumps after acquisitions (goodwill and intangibles), large prepaid or strategic investments, or capitalized cloud contracts. Check what "other" assets are.
- **Altman Z original** explodes for mega-caps because X4 = market cap / liabilities (NVDA: X4 = 89). Z'' is the fairer read for non-manufacturers.
- **Piotroski** penalizes growth companies that issue shares and asset-heavy compounders whose margins have peaked. It was designed for cheap, high book-to-market stocks.
- **Stock splits** can make "no dilution" fail and `share_count_yoy_pct` spike (NVDA FY23 reads +889%) when an older filing wasn't restated.
- **Financials (SIC 60–67):** Beneish, Altman and Piotroski don't apply (`is_financial: true`). Use reserve adequacy, credit costs, CECL allowance trends, NCOs and capital ratios.
- **Seasonal and 53-week years** distort DSO and DIO at fiscal year end.

**Qualitative checklist** (score each Clean, Watch or Red, with evidence):
1. **Revenue recognition:** policy wording changes, a shift from gross to net (or reverse), bill-and-hold, multi-element allocation, extended payment terms, rising unbilled receivables or contract assets.
2. **Reserves and allowances:** allowance for doubtful accounts, warranty, returns and inventory reserves falling as a % of the base. Releases that boost EPS ("cookie jar").
3. **Capitalization:** software development, customer acquisition costs, interest, or content capitalized more than before; capex rising while D&A lives lengthen (check useful-life changes).
4. **Non-GAAP creep:** gap between adjusted and GAAP growing faster than the business; recurring "one-time" restructuring; new add-back categories; adjusted metrics redefined.
5. **Auditor:** change of auditor (8-K 4.01) and the reason, short or very long tenure, a small audit firm for a large company, CAMs on revenue or reserves, adverse ICFR opinion.
6. **Restatements and controls:** 8-K 4.02, 10-K/A restating numbers, material weakness, NT 10-K or 10-Q filings, CFO or CAO turnover (8-K 5.02).
7. **Related parties:** transactions with executives, founders or affiliates; leases from insiders; revenue from related parties.
8. **Segment re-casting:** segments merged, renamed or redefined right as one weakens; KPI definitions changed.
9. **Channel stuffing:** DSO up with quarter-end revenue spikes, distributor inventory growing, rebates and returns allowances rising, revenue concentrated in the last weeks of the quarter.
10. **Off-balance sheet:** VIEs, guarantees, purchase commitments, supplier-finance programs, factoring, synthetic leases, unconsolidated JVs carrying debt.
11. **Cash flow presentation:** OCF boosted by working capital release, factoring, reclassification of items between operating and investing, or capitalized costs classed as investing.
12. **Incentives:** compensation tied to adjusted EPS or revenue targets that were barely hit; heavy insider selling into the numbers (see `insider-ownership`).

**Verdict rules (judgment):**
- **Clean:** no Red items, at most 2 Watch items with benign explanations, scores either clean or explainable false positives.
- **Watch:** 1 Red item with a plausible benign explanation, or 3+ Watch items, or a screen breach without a benign explanation.
- **Red flags:** any of material weakness, non-reliance or restatement, an auditor resignation, going concern, an SEC or DOJ investigation into accounting, or 2+ Red items that corroborate each other (for example DSO up 30%, Sloan above 10%, and a reserve release).

Corroboration is the rule: a single screen is a hint, while a screen plus a matching filing fact is a finding.

## Output
Write `/tmp/TICKER-forensic-accounting.json` per `../sec-edgar/references/report-schema.md`, `"skill": "forensic-accounting"`.

- **title**: e.g. `"Scores look scary, the *filings don't*"` or `"Receivables are *outrunning* revenue"`.
- **verdict**: `{"label": "Forensic verdict", "value": "Clean | Watch | Red flags", "sub": "<the top driver>", "tone": "pos|warn|neg"}`.
- **kpis** (4–6): Beneish M (zone), Altman Z or Z'' (zone), Piotroski F/9, Sloan accruals %, cash conversion, GAAP vs. adjusted gap %.
- **sections**:
  1. *Scorecard*: a `scores` bar per screen (pct = position on a risk scale where higher is riskier; value = the score; tone by zone) plus the red-flag checklist table (Item, Status as a pill with tone, Evidence, Source).
  2. *Beneish decomposition*: component table (value, threshold, read), recomputed M with SGI = 1, false-positive callout if relevant.
  3. *Distress and strength*: Altman components and Piotroski checks table.
  4. *Accruals and working capital*: NI vs. OCF chart over 5–6 years, DSO, DIO, DPO table.
  5. *Filing evidence*: auditor and CAMs, 8-K 4.01/4.02, controls, policy changes, related parties, off-balance-sheet items. Quote briefly and cite.
  6. *Non-GAAP gap*: table by quarter (GAAP, adjusted, gap %, add-backs).
  7. *What would change our mind*: the specific data that would upgrade or downgrade the verdict.
- **sources**: scores.py `sources` accessions, 10-K and 8-K accessions, press release exhibit URLs.

```bash
python3 ../sec-edgar/scripts/render_report.py /tmp/TICKER-forensic-accounting.json --out-dir earnings-desk-reports
```
**In chat** give the verdict and top driver, a compact score table, any Red or Watch items with one line of evidence each, explicitly named false positives, and the report paths.

## Quality bar & pitfalls
- **Never accuse.** Write "consistent with aggressive recognition" or "warrants scrutiny", not "fraud". Separate facts (cited) from inference (labeled).
- **Explain every score's driver.** "M-score −1.15" alone is useless. "Elevated because sales grew 66% and other assets grew faster than total assets; receivables quality (DSRI 1.01) is clean" is the job.
- **Check `defaulted_to_1` and `missing`.** A Beneish score computed with DEPI or SGAI defaulted to 1.0 is less informative. Say so.
- **Approximations in scores.py:** Piotroski's ROA uses prior-year total assets (not average), and "ROA improving" compares with prior net income / prior assets. Leverage uses long-term debt only. Beneish TATA uses net income − OCF over total assets. Disclose these when a check is borderline.
- **One-year window.** Scores compare two fiscal years. A one-off year can mislead, so confirm with the multi-year trend.
- **Absence of evidence.** "No 4.01/4.02 in the last 200 8-Ks" is a finding. State the window you checked.

## Next skills
- `/earnings-desk:filing-diff` to redline the policy, controls and legal sections
- `/earnings-desk:insider-ownership` to see whether insiders are selling into the numbers
- `/earnings-desk:capital-allocation` if goodwill, acquisitions or buybacks drive the flags
- `/earnings-desk:financial-statements` for the full ratio context
- `/earnings-desk:bull-bear-debate` to stress-test the bear case

_Not investment advice. Scores are screens, not conclusions. Data is from public filings and may contain errors; verify before acting._
