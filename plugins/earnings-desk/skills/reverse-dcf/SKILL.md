---
name: reverse-dcf
description: >-
  Reverse DCF and expectations investing - works out what growth and margins today's stock price implies, then tests whether that is plausible. Solves for market-implied revenue growth and FCF margin from SEC XBRL TTM cash flows (no API key), compares them with the company's own history, guidance, consensus and base rates for sustained growth, builds bull/base/bear scenarios with explicit drivers, a WACC build and sensitivity tables, and names the one variable that matters most. Use when the user asks "what's priced in", "is it overvalued", "is it undervalued", "is the stock expensive", "what growth does the price imply", "run a DCF", "intrinsic value", "fair value", "price target math", "market expectations", or "how much upside". Not for banks or insurers (use P/B vs ROE via comps-valuation).
license: MIT
compatibility: Requires Python 3.8+ (standard library only) and internet access to sec.gov. Prices via market.py (keyless, best-effort) or --price; optional FMP_API_KEY / FINNHUB_API_KEY.
metadata:
  category: "4-valuation-competition"
  version: "1.0.0"
  author: "earnings-desk"
---

# reverse-dcf · what's priced in, and is it believable?

Don't guess fair value first. Start from the price, back out the future it implies, then ask whether that future is likely. This is the expectations-investing discipline (Rappaport & Mauboussin): the market has already made a forecast, and your job is to decide whether it's too high or too low.

## When to use
- "Is NVDA overvalued?", "what's priced into TSLA?", "what growth does $X justify?", "build me a DCF".
- Before buying a stock after a big run (or a big drawdown), to see what the price now demands.
- **Not** for banks, insurers or brokers, because FCF isn't meaningful when debt is raw material. Use `comps-valuation` (P/B vs ROE). For deeply cyclical or pre-profit companies, read the "When DCF breaks" section of [references/valuation-notes.md](references/valuation-notes.md) first.
- For relative value against peers, use `comps-valuation`. For the qualitative case behind a growth rate, use `moat-analysis`.

## Inputs
- `TICKER` (required). Optional: `--price` (pass a cited price whenever you have one), `--wacc` (default 9), `--terminal-growth` (default 3), `--years` (default 10), `--growth` (your base-case year-1 revenue growth, %), `--target-margin` (FCF margin reached by year 5, %; default is today's TTM margin), `--sbc-ignore` (default deducts SBC from FCF).

## Workflow
Scripts live in `scripts/`. Shared data tools live at `../sec-edgar/scripts/`.

1. **Price and context.** `python3 ../sec-edgar/scripts/market.py quote TICKER`. If it returns `"available": false`, web-search a price and cite the site and timestamp. Write down the price, the source and the time. Every implied number depends on it.
2. **History, the reality check.** `python3 ../financial-statements/scripts/statements.py TICKER --years 10 --quarters 8`. Pull revenue CAGR over 3, 5 and 10 years (as far as data goes), the FCF margin range (min, max, median), SBC % of revenue, ROIC trend and share-count drift. Ask whether this is a steady compounder, a cyclical, or a company that has just inflected.
3. **Reverse DCF.** Hold margins at today's level first:
   `python3 scripts/dcf.py TICKER --price P --wacc W`
   Read `reverse.implied_year1_growth_pct`, which is the year-1 growth that, fading linearly to terminal growth over `--years`, justifies the price. **It is not a CAGR.** Compute the implied 10-year revenue CAGR from the base projection: `(revenue_y10 / revenue_ttm)^(1/10) - 1`. That CAGR is the number to compare with history and base rates.
   Then read `reverse.implied_target_fcf_margin_pct`, the year-5 FCF margin needed if growth runs at `--growth` (or 10% when `--growth` is omitted). Also note `implied_fcf_yield_pct` (TTM FCF / market cap).
4. **Gather the expectation benchmarks.** Get guidance from `python3 ../sec-edgar/scripts/edgar.py earnings-release TICKER` (outlook section) and consensus from `python3 ../sec-edgar/scripts/market.py estimates TICKER` (needs a key; otherwise web search, cited). Put implied vs. history vs. guidance vs. consensus vs. base rate in one table.
5. **Your own scenarios.** Run dcf.py once per scenario with **explicit drivers**, so each case says exactly what you believe:
   ```bash
   python3 scripts/dcf.py TICKER --price P --wacc 9 --growth 12 --target-margin 28   # base
   python3 scripts/dcf.py TICKER --price P --wacc 9 --growth 20 --target-margin 33   # bull
   python3 scripts/dcf.py TICKER --price P --wacc 9 --growth 5  --target-margin 22   # bear
   ```
   ⚠ **If `--growth` is omitted, dcf.py sets the base case to the market-implied growth, so base value equals price by construction**, and its bull/bear are mechanical (growth ×1.5 / ×0.5, margin ×1.2 / ×0.75). That's fine for a first look but it is not a forecast. Always pass `--growth` and `--target-margin` from your own reasoning for the scenarios you publish.
6. **Sensitivity.** The JSON has `sensitivity_value_per_share` (WACC ± 2 pts × terminal growth ± 1 pt). Add a growth × margin grid, because that's usually where the debate lives:
   ```bash
   for g in 5 10 15 20 25; do for m in 20 25 30 35; do
     python3 scripts/dcf.py TICKER --price P --growth $g --target-margin $m \
       | python3 -c "import json,sys; d=json.load(sys.stdin); print($g, $m, d['scenarios']['base']['value_per_share'])"
   done; done
   ```
7. **Sanity-check the terminal value.** Check `terminal_share_of_value_pct` and the implied exit multiple (see the framework below). If either looks absurd, fix the inputs before writing anything.
8. **Weigh it and write it up.** Assign probabilities to bear/base/bull (they must sum to 100%), compute the probability-weighted value, and render the report.

## Analysis framework

**Read the implied numbers like a buy-side PM**
- Compare the implied 10-yr revenue CAGR with the trailing 5- and 10-yr CAGR. An implied rate **above the company's best-ever 5-year stretch** means the market is pricing in an acceleration. It needs a named reason (new product, TAM unlock, pricing).
- Compare the implied margin with the company's best-ever FCF margin and the best-in-class peer. If the price needs margins nobody in the industry has sustained, it's priced for perfection.
- **Implied FCF yield vs. growth** (dcf.py defaults: 9% WACC, 3% terminal growth, flat margin, 10 years): a ~6% FCF yield implies about a 3% 10-yr revenue CAGR, roughly nominal GDP. A ~3% yield implies about 11% (year-1 growth ~19%, fading). A ~1.5% yield implies about 20%, and ~1% implies about 25%. Use these to calibrate quickly, then run the model.
- **Market-implied forecast period:** if the price only works with 15+ years of excess returns (try `--years 15`), the market is extrapolating a durable moat. Ask `moat-analysis` whether that's earned.

**Base rates (outside view).** Michael Mauboussin and Dan Callahan's *The Base Rate Book* (Credit Suisse, 2016) and their later updates show that sales growth regresses toward the mean quickly, and that very high growth sustained for a decade is rare. Roughly, only a low-single-digit share of companies compound sales at ~20%+ for ten years, and the share falls further as starting revenue rises. Quote these figures as approximate and attribute them; check the current edition before citing a precise number. Practical heuristics:
- The bigger the revenue base, the harder high growth gets. A $100B+ company compounding 20% for a decade would be close to unprecedented.
- ROIC also mean-reverts. High returns attract competition unless a moat (see `moat-analysis`) blocks it.
- Blend inside and outside views: start from the base-rate distribution for the company's size and sector, then adjust for company-specific evidence. Don't start from management's plan.

**Scenario construction.** Each case needs 2–4 explicit drivers with numbers and a one-line *why*, for example: "Bull: data-center share holds at ~80%, so year-1 growth is 25%; software attach lifts FCF margin to 40%". Bear is not "base minus 20%". It's a coherent story (share loss, price war, cycle turn). Give probabilities, and show what the weighted value implies vs. price.

**WACC (keep it simple and honest).** CAPM cost of equity = risk-free (10-yr US Treasury, cite date) + beta × equity risk premium (Damodaran's implied ERP, often around 4–5%; cite his site and month). Typical all-in ranges: mega-cap stable 7–8.5%, average large-cap 8.5–10%, small or high-beta 10–12%, pre-profit or single-product 12%+. Debt barely moves WACC for cash-rich companies. Don't tune WACC to 0.1%. Show the sensitivity instead. Full build: [references/valuation-notes.md](references/valuation-notes.md).

**Terminal value sanity**
- Implied exit multiple of terminal FCF = (1 + g) / (WACC − g). At 9% and 3% that's ~17x FCF. Compare it with what mature, low-growth peers trade at today.
- `terminal_share_of_value_pct` above ~80% means most of the value sits past year 10, so the call is really about durability.
- Terminal growth must not exceed long-run nominal GDP (about 2–4%). Values ≥ 4% need extraordinary justification.

**Expectations-investing lens: find the lever.** Of the three value drivers (sales growth, FCF margin, discount rate), which one moves value most per reasonable unit of uncertainty? Compare the growth × margin grid with the WACC grid. That variable is the thesis. State it plainly: "This is a margin call, not a growth call: ±5 pts of margin moves value ±30%, while ±5 pts of growth moves it ±12%."

**SBC.** dcf.py deducts SBC from FCF by default. Keep it that way for any company with SBC above ~3% of revenue. If you use `--sbc-ignore`, model the dilution through a rising share count instead. Never ignore both.

**Analyst questions to answer in the report**
1. What must be true for today's price to be right, and has the company ever done it?
2. Does the implied path beat guidance and consensus? Where does it fall in the base-rate distribution?
3. Which single variable decides the outcome, and what evidence over the next 2–4 quarters would move it?
4. What's the asymmetry: downside to the bear value vs. upside to the bull value?

## Output
Write the report JSON per [../sec-edgar/references/report-schema.md](../sec-edgar/references/report-schema.md), with `"skill": "reverse-dcf"`.
- **Title idea:** `"Pricing in a *decade of 20%*"` or `"Expectations look *too low*"`.
- **Verdict stamp:** `{"label": "Expectations", "value": "Demanding" | "Reasonable" | "Undemanding", "sub": "implied 10y CAGR 17% vs 5y hist 11%", "tone": "neg" | "neutral" | "pos"}`.
- **KPIs (3–6):** Price (source), implied 10-yr revenue CAGR, implied FCF margin, FCF yield, probability-weighted value vs. price (%), terminal % of value.
- **Sections:**
  1. *What's priced in*: a callout with the one-sentence answer, plus a table of implied vs. 3/5/10-yr history vs. guidance vs. consensus vs. base rate.
  2. *History check*: a bar chart of annual revenue ($B) with an FCF-margin % line.
  3. *Scenarios*: a table (case, growth, margin, value/share, upside, probability, key drivers) and a callout per case with its story.
  4. *Sensitivity*: a WACC × terminal-growth table and a growth × margin table. Highlight the cell nearest today's price with a pill.
  5. *The lever*: which variable matters most, with `scores` bars showing value swing per driver.
  6. *Model hygiene*: WACC build, terminal checks, SBC/lease treatment and caveats.
- **Sources:** XBRL accessions (from statements.py `sources`), price source and time, guidance 8-K, consensus source and date, base-rate reference.

Render:
```bash
python3 ../sec-edgar/scripts/render_report.py /tmp/TICKER-reverse-dcf.json --out-dir earnings-desk-reports
```
**In chat:** two or three sentences, for example: "At $P the market is pricing in about X% revenue CAGR for 10 years at Y% FCF margins, above the company's 5-yr record of Z%. Probability-weighted value is $V (±N%). The decisive variable is margin." Then give the report paths and next steps.

## Quality bar & pitfalls
- **Never present the default base case as a valuation.** Without `--growth`, base equals price by construction.
- Report the implied **CAGR**, not just year-1 growth. Year-1 growth on a linear fade overstates the growth level people picture.
- TTM FCF can be distorted (working-capital swings, capex cycles, one-off tax payments). Compare it with 3-year average FCF margin from statements.py and use `--target-margin` to normalize.
- Net debt in dcf.py excludes leases, pensions and minority interests. Adjust by hand when they're material (see the references file).
- Negative FCF today: the reverse solve may fail (returns `null`). Use `--manual` with a normalized margin, or switch to EV/Sales vs. growth (`comps-valuation`).
- Label facts (filings), market data (cited), and your judgment (scenarios, probabilities) as separate things.
- Don't anchor on consensus. It's one benchmark, not the truth.

## Next skills
`/earnings-desk:comps-valuation` (relative value check) · `/earnings-desk:moat-analysis` (can the implied returns last?) · `/earnings-desk:guidance-tracker` (is guidance credible enough to underwrite?) · `/earnings-desk:bull-bear-debate` (stress-test the scenarios) · `/earnings-desk:thesis-tracker` (record the decisive variable as a KPI).

_Not investment advice. Valuation models are only as good as their assumptions; verify data and do your own research._
