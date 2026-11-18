---
name: earnings-preview
description: >-
  Pre-earnings setup for any US-listed stock, built before the print. Finds what consensus expects for revenue, EPS and guidance, estimates the buy-side whisper and how high the bar really is, names the 3-5 KPIs that will actually move the stock, compares the options-implied move with the stock's historical post-earnings moves, and lays out a bull/base/bear scenario table with the likely reaction plus the five sharpest questions for the call. Use it when the user asks "what to expect from earnings", "earnings preview", "what's the bar", "what's priced in going into the print", "implied move", "what will move the stock on earnings", "should I worry about earnings next week", "what questions should I ask on the call", or names a ticker reporting soon. Ends with a "Setup" verdict (bar is low / balanced / high / priced for perfection). For results already out, use earnings-recap.
license: MIT
compatibility: Requires Python 3.8+ and internet access to sec.gov. Web search recommended for consensus and implied move. Optional FMP_API_KEY or FINNHUB_API_KEY.
metadata:
  category: "2-earnings-season"
  version: "1.0.0"
  author: "earnings-desk"
---

# earnings-preview · know the bar before the print

Stocks don't trade on beats. They trade on the gap between the print and what the marginal holder already believed. This skill measures that gap before the number lands: published consensus, the real (whisper) bar, the KPIs that decide it, and how much move the options market is paying for.

## When to use
- A company reports in the next few days or weeks and the user wants to know what matters.
- The user holds (or wants to hold) through the print and needs a risk/reward frame.
- **Not** for results already released. Use `earnings-recap`. For long-run guidance credibility, use `guidance-tracker`. For the full thesis, use `deep-dive`.

## Inputs
- `TICKER` (required).
- `quarter` (optional): defaults to the next unreported fiscal quarter.
- `key KPIs` (optional): if the user already knows what the street watches (e.g. "Azure growth"), start there.
- Data setup (SEC user agent, optional keys) lives in `sec-edgar`. Run `python3 ../sec-edgar/scripts/market.py status` once.

## Workflow
1. **Calendar and context.**
   `python3 ../sec-edgar/scripts/market.py calendar TICKER` gives the date and timing (pre-market vs. after close). No key? Web search "TICKER earnings date" on the company IR site and cite it. Then `python3 ../sec-edgar/scripts/market.py quote TICKER` and `python3 ../sec-edgar/scripts/market.py history TICKER --range 1y`: compute the run-up into the print (1-month and 3-month return, and vs. a sector ETF via web search if useful). A stock up 25% in the month before the print carries a higher bar than the published numbers say.
2. **What management guided.**
   `python3 ../sec-edgar/scripts/edgar.py earnings-release TICKER` (last quarter's 8-K Ex.99). Extract the guide for this quarter and the full year: revenue range, margin, EPS, segment color, capex. If guidance was only given on the call, find it in the transcript (web search, cite). Note where the midpoint sits vs. consensus.
3. **What consensus expects.**
   `python3 ../sec-edgar/scripts/market.py estimates TICKER` (FMP/Finnhub). Without a key, web search for consensus revenue and EPS (e.g. Nasdaq, Zacks, MarketBeat, company-provided consensus) and cite site + date. Capture: revenue, EPS, the low-high range and analyst count, plus street numbers for the swing KPIs if published. A wide high-low range means the market is not anchored and the reaction depends on the KPI, not the headline.
4. **History of beats and reactions.**
   `python3 ../sec-edgar/scripts/market.py surprises TICKER` (EPS surprise history, key needed) and `python3 ../sec-edgar/scripts/market.py reactions TICKER --n 8`. Build a table: quarter, EPS surprise %, revenue surprise % (web if needed), guide raised/held/cut, next-day move. Look for the pattern: does this stock fall on beats? That is the clearest sign the whisper sits above consensus.
   The `reactions` window is event-day close to next close, which is right for after-close reporters. For **pre-market** reporters, re-run each date with `python3 ../sec-edgar/scripts/market.py reaction TICKER --date <prior trading day>` so the move includes the print day.
5. **Options-implied move.** Web search "TICKER implied move earnings" (sources: Barchart, Market Chameleon, OptionCharts, broker notes) and cite. If only the straddle is available: implied move ≈ ATM straddle price for the first expiry after the print / stock price. That approximates the expected *absolute* move, so it compares directly with `avg_abs_move_pct` from step 4. If the expiry is more than a few days out, trim it (a common shortcut is ~85% of the straddle) to strip non-event time value.
6. **The KPIs that move the stock.** Read the last two releases and the latest 10-Q MD&A (`python3 ../sec-edgar/scripts/edgar.py filing-text TICKER --form 10-Q --section mdna`). Pick the 3-5 metrics the market actually prices (see framework). If the company has a KPI history, run `kpi-tracker` logic for the trend, or pull the series quickly with `python3 ../financial-statements/scripts/statements.py TICKER --quarters 8` (growth, margins, DSO, DIO).
7. **Recent news flow.** Web search the last 90 days: pre-announcements, analyst days, peer prints (see `read-through`), estimate revisions, management changes, sell-side upgrades/downgrades. Peer read-across is often the best leading indicator.
8. **Build scenarios, questions, verdict.** Then write and render the report.

## Analysis framework

### Reading the bar
| Signal | Bar lower | Bar higher |
|---|---|---|
| Guide midpoint vs. consensus | Consensus below guide midpoint | Consensus above the top of the guide |
| Estimate revisions (last 90d) | Cut into the print | Raised into the print, especially after a peer beat |
| Run-up vs. sector (1-3m) | Lagged | Outperformed by > 10 pts |
| Past reactions | Rallies on in-line prints | Falls on beats (≥ 2 of last 4 beats sold off) |
| Valuation vs. own 5y range | Bottom third | Top third, or `reverse-dcf` implies heroic growth |
| Positioning (web: short interest, "crowded" commentary) | High short interest | Consensus long / hedge-fund VIP lists |
| Beat cadence | Beats shrinking | Consistent beats of a set size (the "usual beat" is priced) |

**Whisper estimate (label it as an estimate).** Start with consensus. Add the company's median beat over the last 8 quarters (the "usual beat"). Adjust up for a strong run-up, positive peer read-through and upward revisions; down for the reverse. Example: consensus revenue $10.0B, usual beat +2.0%, strong peer data → whisper ≈ $10.25B. If a credible published whisper exists (buy-side surveys, Estimize), cite it and use it.

**Verdict scale (Setup):** `Bar is low` (3+ signals lower, stock de-rated), `Balanced`, `Bar is high` (3+ signals higher), `Priced for perfection` (bar high **and** implied move below historical average or valuation at range top: asymmetric downside).

### Picking the KPIs that matter
Ask: which number did the stock react to last time? Which line does the bull case depend on? Defaults by model (see `../kpi-tracker/references/kpi-library.md` for 15 industries):
- **Software/SaaS:** cRPO growth, net new ARR, NRR, FCF margin, next-quarter revenue guide. Headline revenue rarely matters.
- **Semis:** next-quarter revenue guide, gross margin guide, inventory days (own and channel), data-center or segment mix.
- **Consumer/retail:** comps (traffic vs. ticket), gross margin, inventory growth vs. sales growth, FY guide.
- **Internet/ads:** ad revenue growth, paid clicks/impressions vs. price, engagement, capex guide.
- **Banks:** NII and NIM guide, deposit costs/beta, credit provisions and NCOs, CET1.
- **Industrials:** orders and book-to-bill, backlog, price vs. volume, incremental margins.
- **Pharma/biotech:** key-drug scripts and revenue, pipeline readouts, gross-to-net.

Cap it at 5. For each: last value, trend over 4-8 quarters, street expectation if published (cite), and the threshold that would change the narrative ("cRPO below 15% breaks the re-acceleration story").

### Implied vs. historical move
- **Implied / historical avg abs move < 0.8:** options are cheap relative to history; the market expects a quiet print. Surprises in either direction hit harder.
- **0.8-1.2:** fairly priced.
- **> 1.2:** event premium is rich; a "fine" print often sees the stock move less than implied (vol crush).
- Note skew if available: an expensive downside put skew signals the street is hedged for disappointment.
- Remember: the implied move is an expected absolute move (roughly 0.8 standard deviations), not a ceiling. Count how many of the last 8 actual moves exceeded the current implied move.

### Scenario table (required)
Build three scenarios on the metrics that matter, not just EPS:
| Scenario | Headline vs. cons. | Swing KPI | Guide | Likely reaction | Probability |
|---|---|---|---|---|---|
| Bull | Beat > usual beat | Accelerates | Raise above consensus | +1.0-1.5× implied move | your estimate |
| Base | Usual beat | In line with trend | Maintain / raise by the beat | ±0.5× implied | |
| Bear | In line or miss | Decelerates | Guide below consensus | −1.0-2.0× implied (misses hurt more than beats help) | |
Anchor reaction sizes in the stock's own history (best and worst of the last 8 moves). Probabilities are judgment; label them. Expected move = Σ(p × reaction) should be sanity-checked against the bar: if the bar is high, the base case should carry a slightly negative reaction.

### The five sharpest questions
Good questions force a number or expose a contradiction. Avoid questions management will happily answer in the prepared remarks. Templates:
- "Your guide implies H2 margins of X% vs. Y% in H1. What specifically bridges that gap?"
- "Receivables grew 25% vs. revenue 12%. Were there any changes to payment terms or end-of-quarter deals?"
- "You stopped disclosing [metric] last quarter. What would it have shown?"
- "Peer [X] cited [inventory digestion / pricing pressure]. Why would you be immune?"
- "How much of the guide raise is FX / pricing / M&A vs. organic volume?"
Tie each question to a KPI or risk named earlier.

## Output
Write `/tmp/<TICKER>-earnings-preview.json` per `../sec-edgar/references/report-schema.md`.
- `skill`: `"earnings-preview"`; `title` e.g. `"The bar is *higher* than consensus"`; `subtitle`: "Q3 FY26 preview · reports Nov 19 after close".
- `verdict`: `{label: "Setup", value: "Bar is low | Balanced | Bar is high | Priced for perfection", sub: "<one-phrase reason>", tone: pos | neutral | warn | neg}`.
- `kpis` (4-6): Consensus revenue (with guide-midpoint delta), Consensus EPS, Whisper estimate (labeled "est."), Implied move vs. hist. avg, 1-month run-up, Usual beat (median 8Q).
- `sections`:
  1. **The bar** — table: guide (low/mid/high) vs. consensus vs. whisper for revenue, EPS, margin; callouts for the top 2 bar signals.
  2. **KPIs that will move the stock** — table: KPI, last 4 values, street expects, break-point; a line chart for the #1 KPI trend.
  3. **Reaction history** — table of last 8 prints (EPS surprise, guide action, move); bar chart of moves; `scores` bar comparing implied vs. historical move.
  4. **Scenarios** — the bull/base/bear table, probabilities labeled as judgment.
  5. **Questions for the call** — numbered list of 5, each tagged to the KPI or risk it tests.
  6. **Risks and catalysts beyond the print** — callouts (peer prints, analyst day, macro data).
- `sources`: last 8-K accession, 10-Q accession, consensus site + date, implied-move site + date, price source.

Render:
```bash
python3 ../sec-edgar/scripts/render_report.py /tmp/<TICKER>-earnings-preview.json --out-dir earnings-desk-reports
```
Fix any warnings. In chat, print: the verdict, consensus vs. whisper in one line, implied vs. historical move, the swing KPI, and the HTML + Markdown paths.

## Quality bar & pitfalls
- **Stale consensus is the #1 error.** Always state the retrieval date; estimates move in the final two weeks.
- Do not equate "beat" with "up." Quantify the usual beat and show what happened after past beats.
- Fiscal labels: say "Q3 FY26 (quarter ending Oct 2026)", never just "Q3".
- Don't invent an implied move. If you cannot find one, say "not found" and use the historical average alone.
- Segment-level consensus is often unavailable for free; say so rather than guessing.
- Separate facts (guide, consensus, past moves) from judgment (whisper, probabilities, reactions) with explicit labels.
- Mention binary non-earnings risks in the window (FDA dates, court rulings, index events).

After the print, run `/earnings-desk:earnings-recap` to score the result against this preview, then `/earnings-desk:transcript-decoder` on the call. For context on management's guidance habits, run `/earnings-desk:guidance-tracker`.

_Not investment advice. Data is from public filings and cited third-party sources and may contain errors; verify before acting._
