---
name: earnings-recap
description: >-
  Post-earnings verdict for any US-listed stock, built from the 8-K press release and SEC XBRL. Scores the beat or miss line by line and by segment against consensus, compares new guidance with the prior guide and with the street, and judges the quality of the beat by stripping out one-offs, tax-rate help, below-the-line gains, buyback-driven EPS, pull-forward demand and working-capital games. Adds a margin bridge, the stock reaction in context and what changed in the thesis. Use it when the user asks "did they beat", "how was the quarter", "earnings recap", "break down the results", "why is the stock down after earnings", "was the beat real", "did they raise guidance", "quality of earnings this quarter", or pastes a ticker right after it reported. Ends with a "Print quality" verdict (Strong / Mixed / Weak). For the call itself, follow with transcript-decoder.
license: MIT
compatibility: Requires Python 3.8+ and internet access to sec.gov. Web search recommended for consensus and transcripts. Optional FMP_API_KEY or FINNHUB_API_KEY.
metadata:
  category: "2-earnings-season"
  version: "1.0.0"
  author: "earnings-desk"
---

# earnings-recap · was the beat real?

Headlines say "beat." Your job is to say whether it was a good quarter: how much came from the business versus the tax line, the share count and the calendar, what the guide implies, and whether anything in the thesis moved.

## When to use
- A company reported in the last few days (or the user names a specific past quarter).
- The stock moved hard after the print and the user wants to know why.
- **Not** for pre-print setup (use `earnings-preview`), multi-year guidance credibility (`guidance-tracker`), or a full accounting audit (`forensic-accounting`).

## Inputs
- `TICKER` (required).
- `quarter` (optional): defaults to the latest 8-K Item 2.02 (`--index 0`). Use `--index 1` for the prior quarter.
- `preview` (optional): a prior `earnings-preview` report to score against.
- Data setup (SEC user agent, keys) is in `sec-edgar`.

> **Paths:** `${CLAUDE_SKILL_DIR}` is this skill's own folder. Claude Code fills it in automatically; in other tools, replace it with the folder that contains this `SKILL.md`. Sibling skills such as `${CLAUDE_SKILL_DIR}/../sec-edgar` are installed next to it.
>
> **Working files:** save intermediate JSON and the report JSON in `.earnings-desk/work/` inside the user's current folder (`mkdir -p .earnings-desk/work` first); finished reports go to `earnings-desk-reports/`.
>
> **Chat answer:** lead with the verdict, and put the source next to each key number in the chat reply itself (e.g. `8-K Ex.99.1, accn 0000320193-26-000024` or `web: nasdaq.com, 2026-11-03`). Don't leave citations only in the report.

## Workflow
1. **Pull the release.**
   `python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/edgar.py earnings-release TICKER --max-chars 150000 > .earnings-desk/work/<TICKER>-er0.json`, then `grep`/`Read` that file instead of pulling it all into context. If `truncated` is true, raise `--max-chars`. The `exhibits` URLs are your citations. Extract: revenue, segment revenue, gross margin, operating income, GAAP and non-GAAP EPS, the GAAP→non-GAAP reconciliation, guidance (next quarter and full year), share count, cash flow, buybacks. Also pull the prior quarter's release (`--index 1`) for the **prior guide** and the year-ago one (`--index 4`) for comparisons.
   **Many companies (Apple, Microsoft and others) give guidance only on the call, not in the release.** If the release has no outlook section, take the new and prior guides from the call transcript or cited coverage (web search: "<company> <quarter> guidance"), and label them `web: site, date`.
2. **Cross-check with XBRL.**
   `python3 ${CLAUDE_SKILL_DIR}/../financial-statements/scripts/statements.py TICKER --quarters 8` for y/y growth, margins, tax rate, DSO/DIO/DPO, cash conversion, share count. If the 10-Q is already filed, `python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/edgar.py facts TICKER --periods 8`. Releases come before the 10-Q, so XBRL for the newest quarter may lag by days; say so and use the release figures.
3. **Consensus.** `python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/market.py estimates TICKER` and `python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/market.py surprises TICKER` (keys optional). Otherwise web search for the pre-print consensus (revenue, EPS, segment and KPI estimates if published) and cite site + date. Use the consensus **as of the print**, not revised post-print numbers.
4. **Reaction.** `python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/market.py reactions TICKER --n 8`. `move_pct` spans the prior close to the next close (covers pre-market and after-close releases); report `after_close_move_pct` or `pre_market_move_pct` once you know the release time. Compare with the stock's average absolute move and the implied move (web search, cite).
5. **Transcript (if available).** Web search the company IR page or a transcript source and cite it. Pull guidance color, one-off explanations and analyst pushback. For a full linguistic read, hand off to `transcript-decoder`.
6. **Quality-of-beat checks** (framework below), then the margin bridge, then the thesis delta. If anything smells, run `python3 ${CLAUDE_SKILL_DIR}/../forensic-accounting/scripts/scores.py TICKER` for accruals and working-capital drift.
7. Write and render the report.

## Analysis framework

### 1. Scorecard
For each line: actual, consensus, surprise % = (actual − consensus) / |consensus|, and y/y growth. Rows: revenue, each segment, gross margin (in bps vs. cons.), operating income/margin, EPS (GAAP and the company's adjusted EPS, compared with the matching consensus basis), FCF, and the 1-3 swing KPIs. Classify:
- **Clean beat:** revenue and EPS both > 1% above, swing KPI above.
- **Low-quality beat:** EPS beat with revenue in line or below, or EPS beat explained by non-operating lines.
- **Miss:** revenue or swing KPI below by > 1%.
A 0.5% revenue beat on a company that beats by 3% every quarter is effectively a miss. Compare with the usual beat (median of last 8 surprises).

### 2. Guidance
| Compare | Read |
|---|---|
| New guide midpoint vs. prior guide midpoint | Raise / maintain / cut |
| New FY raise vs. the Q beat size | Raise > beat = underlying raise; raise < beat = implied H2 cut ("beat and lower the rest") |
| New guide midpoint vs. consensus | What the stock trades on |
| Range width vs. prior | Widening = less visibility |
| Metrics added or dropped | Dropping a metric is a signal (see `guidance-tracker`) |
Implied next-period guide: FY guide − YTD actual. Many "raises" imply a weaker Q4 than consensus once you do this subtraction.

### 3. Quality of the beat (the core of this skill)
Quantify each item as EPS cents and as % of the beat. Beat attribution = operating beat + tax + below-the-line + share count + other.
- **Tax rate.** EPS effect = pretax income × (benchmark rate − actual rate) / diluted shares. Benchmark, in order of preference: the company's guided rate, the consensus model's rate, then the average effective rate of the prior 3–4 quarters (`tax_rate_pct` in statements.py). Say which you used, because it can move the verdict. A rate 3+ pts below the benchmark that provides > 25% of the beat is a low-quality beat.
- **Below-the-line items.** Interest income on cash piles, equity-method gains, mark-to-market on investments, FX gains, gains on sale. Non-operating income growing faster than operating income flags it.
- **Share count.** EPS growth − net income growth ≈ buyback contribution. Fine, but it is capital allocation, not operations.
- **Non-GAAP adjustments.** Track the GAAP-to-adjusted gap over 4-8 quarters. Red flags: new add-back categories, "restructuring" every year, SBC above 15% of revenue excluded, acquisition costs on serial acquirers. Gap growing > 5 pts of EPS = weakening quality.
- **Pull-forward / one-offs.** Price increases announced for next quarter (customers pre-buy), large single deals, license revenue timing, extra week (53-week years), channel fill, catch-up billing, reserve releases, insurance recoveries, one-time government or customer payments.
- **Working capital.** DSO up > 10% q/q or receivables growth > revenue growth + 10 pts = possible end-of-quarter push or loosened terms. Inventory growth > COGS growth + 10 pts = demand risk or a coming gross-margin hit. DPO stretch inflating OCF is not durable.
- **Reserves and accruals.** Lower allowance for doubtful accounts, warranty reserve, or returns reserve as % of revenue. Capitalized software or contract costs rising faster than revenue.
- **Cash conversion.** `ocf_to_ni` (operating cash flow / net income) < 0.8 for two quarters while EPS beats = earnings ahead of cash. statements.py's `cash_conversion` is FCF / net income, a stricter measure that also absorbs capex.
- **Deferred revenue / RPO.** For subscription models: billings (revenue + Δdeferred revenue) slowing while revenue beats means future revenue is being pulled forward.
- **Organic vs. reported.** Strip M&A and FX (constant-currency figures from the release).

### 4. Margin bridge
Gross margin and operating margin change y/y in bps, decomposed: price/mix, volume leverage, input costs, FX, opex lines (R&D, S&M, G&A as % of revenue), one-offs. Incremental operating margin = Δoperating income / Δrevenue (y/y). Above the current margin = operating leverage; negative while revenue grows = cost problem or investment cycle (say which, with management's stated reason).

### 5. Reaction context
Size the move against the stock's average absolute move and the implied move. Explain divergences: beat but down = guide, swing KPI, quality, or a bar above consensus (check the run-up). Do not over-read day-one moves; note day 2-3 drift if available.

### 6. What changed in the thesis
List each pillar of the bull and bear case and mark it strengthened / unchanged / weakened with the specific datapoint. Note new risks (customer loss, pricing, regulatory, capex step-up) and new disclosures.

### Verdict (Print quality)
- **Strong:** clean beat on revenue and the swing KPI, guide raised by more than the beat, ≥ 80% of EPS beat operational, no working-capital red flags.
- **Mixed:** beat with offsetting issues (guide in line, low-quality components 25-50% of beat, one deteriorating KPI).
- **Weak:** miss on revenue or swing KPI, guide cut or below consensus, or > 50% of the beat from non-operating/one-off items.

## Output
Write `.earnings-desk/work/<TICKER>-earnings-recap.json` per `../sec-edgar/references/report-schema.md`.
- `skill`: `"earnings-recap"`; `title` e.g. `"A *low-quality* beat"` or `"Beat, raise, and *the cash agrees*"`; `subtitle`: "Q3 FY26 results · reported Oct 28, 2026".
- `verdict`: `{label: "Print quality", value: "Strong | Mixed | Weak", sub: "e.g. Beat + raise, 90% operational", tone: pos | warn | neg}`.
- `kpis` (4-6): Revenue (y/y and vs. cons.), EPS (vs. cons.), Swing KPI, Guide midpoint vs. cons., Operational share of beat, Stock reaction vs. avg move.
- `sections`:
  1. **Scorecard** — table: metric, actual, consensus, surprise (pill toned), y/y; segment table.
  2. **Guidance** — table: metric, prior guide, new guide, consensus, read; callout for implied next-quarter math.
  3. **Quality of the beat** — table: component, EPS impact, % of beat; `scores` bars (operational share, cash conversion, DSO change); red-flag callouts.
  4. **Margin bridge** — bar chart of bps contributions or a table; incremental margin.
  5. **Reaction** — move vs. average and implied; short "why" paragraph.
  6. **Thesis delta** — callouts per pillar (pos/neutral/neg) and new questions.
- `sources`: 8-K accession(s) and Ex.99 URL, 10-Q accession if filed, consensus site + date, transcript URL, price source.

Render:
```bash
python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/render_report.py .earnings-desk/work/<TICKER>-earnings-recap.json --out-dir earnings-desk-reports
```
Fix warnings. In chat, print: verdict, the three-line scorecard (revenue, EPS, guide vs. cons.), the biggest quality flag, and the HTML + Markdown paths.

## Quality bar & pitfalls
- Match bases: adjusted EPS vs. adjusted consensus, GAAP vs. GAAP. Say which.
- Use pre-print consensus. Post-print revisions make every quarter look in line.
- 53-week years, calendar shifts and M&A distort y/y; adjust or flag.
- Derived quarterly XBRL (`derived_quarter: true`) for Q4 is FY minus 9M; EPS is approximate.
- Never attribute the reaction to one cause without evidence. Offer the 2-3 most likely drivers.
- "Not disclosed" beats a guess. Segment consensus is often not free.
- Banks/insurers: replace gross margin and DSO with NIM, provisions, combined ratio; say why.

Next: `/earnings-desk:transcript-decoder` for tone and evasiveness on the call, `/earnings-desk:guidance-tracker` to see whether this guide is credible, `/earnings-desk:read-through` for peer implications, and `/earnings-desk:thesis-tracker` to log the thesis changes.

_Not investment advice. Data is from public filings and cited third-party sources and may contain errors; verify before acting._
