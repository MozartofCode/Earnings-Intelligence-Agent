# earnings-desk report schema

Every skill's final deliverable is one JSON object rendered by
`scripts/render_report.py` into the shared HTML template (plus a Markdown twin).
Keep it factual, sourced and skimmable. The template handles all styling.

```jsonc
{
  "skill": "earnings-recap",                 // required: skill name (shown in the masthead)
  "ticker": "NVDA",
  "company": "NVIDIA Corp",
  "exchange": "Nasdaq",
  "date": "2026-11-16",                      // defaults to today
  "title": "Another *beat-and-raise*",       // required; wrap 1–3 words in *asterisks* for the accent color
  "subtitle": "Q2 FY27 results · reported Aug 26, 2026",
  "meta": ["Price $182.40 (Finnhub, Nov 14 close)", "Mkt cap $4.44T", "FY ends late Jan"],

  "verdict": {                               // optional stamp in the header
    "label": "Print quality", "value": "Strong", "sub": "Beat + raise", "tone": "pos"
  },

  "kpis": [                                  // 3–6 headline numbers
    { "label": "Revenue", "value": "$96.2B", "delta": "+106% y/y · +3.1% vs cons.", "tone": "pos" }
  ],

  "summary": "Markdown. 2–4 sentences: what happened, why it matters, what to watch.",

  "sections": [
    {
      "heading": "Beat / miss scorecard",    // required per section
      "kicker": "The numbers",               // small label above the heading
      "callouts": [                          // cards: key takeaways, risks, red flags
        { "title": "Data Center +117% y/y", "body": "Markdown allowed.", "tone": "pos" }
      ],
      "body": "Markdown paragraphs, lists, blockquotes, small tables.",
      "scores": [                            // horizontal bars: 0–100 pct + a display value
        { "name": "Beneish M-score", "pct": 60, "value": "-1.62", "tone": "warn" }
      ],
      "tables": [
        {
          "caption": "Reported vs. consensus",
          "columns": ["Metric", "Actual", "Consensus", "Surprise"],
          "rows": [
            ["Revenue", "$96.2B", "$93.3B", { "text": "+3.1%", "tone": "pos", "pill": true }]
          ]
        }
      ],
      "charts": [                            // Chart.js: bar | line | doughnut; mixed via dataset.type
        {
          "type": "bar", "title": "Quarterly revenue ($B)", "yFormat": "usd",   // yFormat: usd | pct | x
          "labels": ["Q3 FY26", "Q4 FY26", "Q1 FY27", "Q2 FY27"],
          "datasets": [
            { "label": "Revenue", "data": [57.0, 68.1, 81.6, 96.2] },
            { "label": "Op. margin %", "data": [62, 64, 65, 66], "type": "line" }
          ]
        }
      ],
      "after": "Markdown shown after tables/charts."
    }
  ],

  "sources": [                               // required: every number must trace here
    { "label": "10-Q for quarter ended 2026-07-26 (accn 0001045810-26-000082)", "url": "https://www.sec.gov/..." },
    "Consensus: web search, Nasdaq.com, retrieved 2026-11-16"
  ]
}
```

## Tones
`pos` (green) · `neg` (red) · `warn` (amber) · `accent` (brand orange) · `neutral` (grey).
Use color to carry meaning: good, bad, caution. Don't use it for decoration.

## Conventions
- Numbers for humans: `$96.2B`, `$2.46`, `+106% y/y`, `+40 bps`, `24.5x`. Numeric columns right-align automatically.
- Label every estimate, consensus and opinion clearly. Facts come from filings.
- 4–8 sections is the sweet spot. Lead with the answer and put the detail after it.
- Charts: ≤ 3 datasets, ≤ 12 labels. One idea per chart.
- Write the JSON to a temp file, render it, fix any `warnings`, then share the HTML and Markdown paths.
