# Final investment memo: template, verdict rubric and report JSON

The deep dive ends in **one report JSON** (`pm/report.json`) rendered by the shared renderer:
```bash
python3 <S>/sec-edgar/scripts/render_report.py <RUN>/pm/report.json --out-dir earnings-desk-reports
```
→ `earnings-desk-reports/<TICKER>-deep-dive-<date>.html` plus a `.md` twin. The schema is in `../../sec-edgar/references/report-schema.md`. This file says what goes *in* it.

## 1. Memo structure (in this order)
| # | Part | Where in JSON | What it must answer |
|---|---|---|---|
| 0 | **Verdict** | `verdict` + `title` | Research view, conviction and the one-line why |
| 1 | **Executive summary** | `summary` | View, the 2 variables that decide it, probability-weighted value vs. price, and the strongest argument *against* the view. 4–6 sentences. |
| 2 | Business & moat | section | How it makes money, the moat (7 Powers) and its trend, industry structure |
| 3 | Financial quality | section | Growth, margins, returns, cash conversion, balance sheet: a 5-year table plus a chart |
| 4 | Earnings trajectory | section | Acceleration or deceleration, beat quality, guidance credibility, next-print setup |
| 5 | Forensic check | section | Scores (as `scores` bars), red flags ranked by severity, the clean findings |
| 6 | Valuation | section | What's priced in (reverse DCF) vs. the desk's view: scenario table, comps, the hinge input |
| 7 | Bull vs. bear | section | Each side's thesis and pillars, and what survived the rebuttal (the PM's debate scorecard) |
| 8 | Key debates | section | 2–4 deciding variables: bull view · bear view · desk call · resolving evidence · date |
| 9 | Catalysts & risks | section | Dated catalysts (both directions) and the risk register |
| 10 | Kill criteria & monitoring | section | 3–5 measurable, dated triggers, ready for `thesis-tracker` |
| 11 | Sources | `sources` | Every citation from every memo, de-duplicated |

That is 9 sections, above the schema's usual 4–8, on purpose: this is the flagship long-form memo. Quick mode uses 5 (see §5).

## 2. Verdict rubric
Compute the **probability-weighted value (PWV)** = Σ p_i × value_i over the bear/base/bull cases (probabilities sum to 100%), then the **upside/downside ratio** = (bull − price) / (price − bear). If the bear value is at or above the price, the ratio is "n/a (no modeled downside)".

| Research view | Rule (before overrides) | Tone |
|---|---|---|
| **Attractive** | PWV ≥ price + 15% **and** upside/downside ≥ 1.5 | `pos` |
| **Fairly valued** | everything in between | `neutral` |
| **Unattractive** | PWV ≤ price − 15%, **or** upside/downside < 0.7 | `neg` |

**Overrides (apply in order and state them in the memo):**
1. Forensics `Red flags` with any **Critical** item unresolved → the view is at best *Fairly valued*, conviction Low. Say "numbers not reliable enough to underwrite".
2. Forensics `Watch` → conviction at most Medium.
3. A data-quality issue that touches a key debate variable → conviction at most Medium.
4. Quick mode → conviction at most Medium, and the verdict label gets the suffix "(quick take)".
5. The PM may deviate from the arithmetic only with a written reason (e.g. a binary regulatory event the DCF can't capture).

**Conviction:** **High** = the lenses broadly agree, each key variable has strong evidence, data quality is good, and the bear–bull range is under ~60% of price. **Low** = a key variable is close to a coin flip, the lenses conflict, or the data has gaps. **Medium** = everything else.

**Framing (mandatory):** the verdict is a *research view on risk/reward at today's price*. Never "buy", "sell", "short", "target price" or position sizing. The stamp's `sub` always ends in "· not advice".

## 3. KPIs (4–6)
Price (source, date) · Probability-weighted value (Δ vs. price) · Implied growth from the reverse DCF (vs. 3-yr history) · TTM revenue growth · TTM FCF margin post-SBC · Forensic quality (Clean / Watch / Red flags). Tone each one by meaning, not decoration.

## 4. Report JSON skeleton (full mode)
**Every value below is a placeholder that shows format only. Never copy a number from it.** Each figure in the real report comes from the run's memos and data, with a source. Remove the `//` comments, because the renderer expects plain JSON.
```jsonc
{
  "skill": "deep-dive",
  "ticker": "NVDA", "company": "NVIDIA Corp", "exchange": "Nasdaq", "date": "2026-11-16",
  "title": "Priced for *perfection*, built for it?",   // the view in ≤ 8 words; 1–3 words in *accent*
  "subtitle": "Deep dive · earnings-desk research desk · 8 analysts",
  "meta": ["Price $182.40 (Finnhub, 2026-11-14 close)", "Mkt cap $4.44T", "FY ends late Jan", "Run: .earnings-desk/runs/NVDA-2026-11-16"],
  "verdict": { "label": "Research view", "value": "Fairly valued", "sub": "Conviction: Medium · not advice", "tone": "neutral" },
  "kpis": [
    { "label": "Price", "value": "$182.40", "delta": "Finnhub · Nov 14", "tone": "neutral" },
    { "label": "Prob.-weighted value", "value": "$191", "delta": "+5% vs price", "tone": "neutral" },
    { "label": "Implied growth (rev DCF)", "value": "24%/yr", "delta": "vs 3-yr avg 71%", "tone": "pos" },
    { "label": "Revenue TTM", "value": "$187B", "delta": "+68% y/y", "tone": "pos" },
    { "label": "FCF margin (post-SBC)", "value": "41%", "delta": "+3 pts y/y", "tone": "pos" },
    { "label": "Forensic quality", "value": "Clean", "delta": "Beneish −2.6 · F-score 8", "tone": "pos" }
  ],
  "summary": "**Research view: Fairly valued, medium conviction.** … The view hinges on (1) … and (2) …. Probability-weighted value $191 (+5%). **Strongest argument against:** ….",
  "sections": [
    { "kicker": "1 · The business", "heading": "Business & moat",
      "callouts": [{ "title": "Moat: Wide · Strengthening", "body": "Primary power: … [I2]", "tone": "pos" }],
      "body": "…", "tables": [{ "caption": "Five forces", "columns": ["Force", "Rating", "Why"], "rows": [] }] },
    { "kicker": "2 · The numbers", "heading": "Financial quality",
      "tables": [{ "caption": "Five-year summary", "columns": ["FY", "Revenue", "Growth", "Op. margin", "FCF margin", "ROIC"], "rows": [] }],
      "charts": [{ "type": "bar", "title": "Revenue ($B) and operating margin", "yFormat": "usd", "labels": [], "datasets": [] }] },
    { "kicker": "3 · The trajectory", "heading": "Earnings trajectory",
      "callouts": [{ "title": "Guidance credibility: High", "body": "Beat the guided midpoint 6 of 6 quarters [E4]", "tone": "pos" }],
      "body": "…", "charts": [] },
    { "kicker": "4 · Can we trust it?", "heading": "Forensic check",
      "scores": [{ "name": "Beneish M-score", "pct": 25, "value": "−2.61", "tone": "pos" }],
      "callouts": [{ "title": "Material: …", "body": "… [F3]", "tone": "warn" }] },
    { "kicker": "5 · What's priced in", "heading": "Valuation",
      "body": "The price implies …; the desk's base case assumes … because ….",
      "tables": [
        { "caption": "Scenarios (value if assumptions hold, not a target)", "columns": ["Case", "Prob.", "Growth y1", "FCF margin y5", "WACC", "Value/sh", "vs price"], "rows": [] },
        { "caption": "Comps", "columns": ["Ticker", "EV/Sales", "EV/EBIT", "P/E", "FCF yield", "Growth"], "rows": [] }
      ] },
    { "kicker": "6 · The debate", "heading": "Bull vs. bear",
      "callouts": [
        { "title": "Bull: …", "body": "Thesis … · survived: … · weakened: …", "tone": "pos" },
        { "title": "Bear: …", "body": "Thesis … · survived: … · refuted: …", "tone": "neg" }
      ],
      "tables": [{ "caption": "PM debate scorecard", "columns": ["Pillar", "Side", "Outcome", "Why"], "rows": [] }] },
    { "kicker": "7 · What decides it", "heading": "Key debates",
      "tables": [{ "columns": ["Variable", "Bull view", "Bear view", "Desk call", "Resolves with", "When"], "rows": [] }] },
    { "kicker": "8 · Calendar & risks", "heading": "Catalysts & risks",
      "tables": [{ "caption": "Catalysts", "columns": ["Date", "Event", "Watch for", "Direction"], "rows": [] }],
      "callouts": [{ "title": "Risk: …", "body": "…", "tone": "warn" }] },
    { "kicker": "9 · When we're wrong", "heading": "Kill criteria & monitoring",
      "tables": [{ "columns": ["#", "Kill criterion", "Threshold", "Check by", "Source"], "rows": [] }],
      "after": "Save these with `/earnings-desk:thesis-tracker NVDA` to track them every quarter." }
  ],
  "sources": [
    { "label": "10-K FY2026, filed 2026-02-25, accn 0001045810-26-000012", "url": "https://www.sec.gov/…" },
    "Transcript Q3 FY27: web search, <site>, retrieved 2026-11-16"
  ]
}
```

## 5. Quick-mode skeleton
Same header. Use `"subtitle": "Deep dive · quick take"` and append "(quick take)" to the verdict value. KPIs: Price, Implied growth, Revenue TTM growth, FCF margin, Forensic quality. **Five sections:** Snapshot (business in 3 sentences plus a 5-year table) · Quality & forensics (scores bars) · What's priced in (reverse DCF plus one base scenario) · Bull vs. bear (3 bullets each, steelmanned) · Kill criteria & next steps (suggest the full deep dive and the skills that would resolve the open questions).

## 6. Writing standards for the memo
- Lead every section with its conclusion in the first sentence, then the evidence.
- Each callout title states the finding ("Receivables +38% vs revenue +12%"), not the topic ("Receivables").
- Label judgment: "Desk view:", "Judgment:", "(est.)".
- Keep tables to 8 rows or fewer, charts to 3 datasets and 12 labels or fewer.
- Kill criteria must be checkable by a stranger: metric, threshold, window, source. Bad: "if growth slows". Good: "Data Center revenue growth < 40% y/y in two consecutive 10-Qs (FY27 Q4–FY28 Q1)".
