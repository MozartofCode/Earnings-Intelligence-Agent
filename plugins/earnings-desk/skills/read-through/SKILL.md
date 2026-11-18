---
name: read-through
description: >-
  Cross-company read-across for earnings season. Takes one company's print and works out what it means for peers, competitors, suppliers and customers. It reads demand, pricing, inventory, capex and guidance signals and grades each one by strength (direct, indirect or weak) and by direction. The value-chain map comes from SEC peers, 10-K customer and supplier concentration disclosures and segment data, and the skill checks whether related stocks have already moved. A sector-scan mode puts a group of tickers' recent prints into one beat, miss and guide table and pulls out the common themes. Use it when the user asks "what does this mean for peers", "read-through", "read-across", "who else is affected by these earnings", "implications for suppliers", "what does NVDA's print say about TSMC", "how did the sector report", "earnings season scorecard", "sector scan" or "which stocks move in sympathy". Ends with a "Read-through" verdict (Positive / Mixed / Negative).
license: MIT
compatibility: Requires Python 3.8+ and internet access to sec.gov. Web search recommended for consensus and transcripts. Optional FMP_API_KEY or FINNHUB_API_KEY.
metadata:
  category: "2-earnings-season"
  version: "1.0.0"
  author: "earnings-desk"
---

# read-through · one print, many stocks

Every earnings report also tells you something about other companies. A hyperscaler's capex guide works as a demand forecast for semiconductors. A retailer's inventory comment tells its suppliers what next quarter looks like. This skill turns one print into a graded map of signals across the value chain. It can also turn a whole sector's prints into one scoreboard.

## When to use
- **Single-print mode:** a bellwether just reported, and the user owns or watches a related stock.
- **Sector-scan mode:** partway through the season, the user wants a beat/miss/guide table and the common themes for a group of tickers.
- Before a print: peers that have already reported are the best leading indicator. Feed them into `earnings-preview`.
- **Not** for one company's own results in depth (use `earnings-recap`) or for relative valuation (use `comps-valuation`).

## Inputs
- `SOURCE_TICKER` for single-print mode, or a list of tickers or a sector name for sector-scan mode.
- `targets` (optional): specific related tickers to assess. By default the skill builds the map itself (step 2).
- `quarter` (optional): defaults to the latest print.
- Data setup (SEC user agent, optional keys) is covered in `sec-edgar`.

## Workflow: single-print mode
1. **Digest the source print.**
   `python3 ../sec-edgar/scripts/edgar.py earnings-release SOURCE --max-chars 150000 > /tmp/SOURCE-er0.json`, then `grep`/`Read` the file. If an `earnings-recap` already exists for this print, reuse it. Pull out the facts that matter for other companies:
   - demand commentary by end market and region
   - pricing actions
   - inventory, both the company's own and in the channel
   - capex guide and order trends
   - customer behavior (budget scrutiny, longer sales cycles, pull-ins)
   - supply constraints and guidance changes

   Then get the transcript by web search (company IR first) and look for comments about suppliers, customers and competitors. Cite the URL and date.
2. **Build the value-chain map.**
   - **Peers and competitors.** `python3 ../sec-edgar/scripts/edgar.py peers SOURCE --limit 30` gives a raw list only. SIC codes are coarse, so filter it by business model. Add competitors the source names in its own 10-K: `python3 ../sec-edgar/scripts/edgar.py filing-text SOURCE --form 10-K --section 1`, then grep `saved_to` for "compet".
   - **Customers and suppliers.** Grep the source's 10-K Items 1 and 1A and its revenue/concentration note for "customer", "% of revenue", "% of net revenue", "sole source", "single source" and "supplier".
   - **Reverse lookup.** For each candidate target, grep *its* 10-K (`filing-text TARGET --form 10-K`, plus `--section 1A`) for the source's name. A supplier that discloses "Customer A accounted for 19% of revenue" has a direct link even if the customer is unnamed. Match the customer by segment, geography and size, and label the match **inferred**.
   - **Exposure sizing.** Use `python3 ../sec-edgar/scripts/edgar.py facts TARGET --periods 4` and the target's segment and geographic notes to estimate how much of the target's revenue the signal touches.
3. **Grade each link** using the framework below: relationship, evidence, exposure %, signal, direction, strength, lag.
4. **Check what is priced in.** Run `python3 ../sec-edgar/scripts/market.py reaction TARGET --date <source release date>` for each target and for the source. If the source reported before the market opened, use the prior trading day as the date. If a target has already made the sympathy move, the read-through is already consensus. If a strong direct signal produced no move, it is either the opportunity or the trap, and the report must explain which. Before you credit the source print, check headlines for target-specific news that day. Get each target's next report date with `python3 ../sec-edgar/scripts/market.py calendar TARGET` or a cited web search.
5. **Cross-check against the target's own words.** Pull the target's latest guidance with `python3 ../sec-edgar/scripts/edgar.py earnings-release TARGET` and its KPI trend (`kpi-tracker` logic). Does the source's signal confirm or contradict what the target said last quarter? A contradiction is the most valuable finding this skill can produce.
6. Write and render the report.

## Workflow: sector-scan mode
1. **Define the set.** Use the user's list, or run `peers` and filter to 6-15 names by business model. Say why each name is included.
2. **Collect each print.** For each ticker:
   - Run `python3 ../sec-edgar/scripts/edgar.py earnings-release TICKER > /tmp/TICKER-er0.json`. Check `filing.filed` to confirm the print is from this season.
   - Extract revenue, EPS (state the basis), the guide, and the guide change against the prior guide.
   - Get consensus from `python3 ../sec-edgar/scripts/market.py estimates TICKER` / `surprises TICKER`, or from a cited web search. Use pre-print figures.
   - Get the reaction from `python3 ../sec-edgar/scripts/market.py reactions TICKER --n 1`. `move_pct` covers both pre-market and after-close releases; use `pre_market_move_pct` / `after_close_move_pct` to isolate the session once you know the release time.
3. **Build the scoreboard.** Tally beats, misses, raises and cuts. Extract 3-5 common themes (pricing, volumes, inventory, FX, tariffs, AI demand, consumer health) and record which companies said what, with citations.
4. **Flag outliers and preview the rest.** An outlier is, for example, the one company that missed when everyone else beat. Decide whether it is company-specific or an early warning, and give the evidence. Then list the names still to report and what the season so far implies for each.

## Analysis framework

### Signal types and what to extract
| Signal | What to pull from the source | Who it reads through to |
|---|---|---|
| Demand / volume | End-market growth, orders, backlog, traffic | Competitors (share vs. market), suppliers (volume) |
| Pricing | Price increases or cuts, promotional intensity, ASP trend | Competitors (pricing power or a price war), customers (cost pressure) |
| Inventory | Own DIO, channel weeks, "digestion", "destocking" | Suppliers (orders fall before end demand does), distributors |
| Capex | Capex guide, capacity adds, build plans | Equipment and component suppliers, construction, power |
| Guidance | Raise or cut, macro language, visibility | Peers with the same end market and customers |
| Customer behavior | Budget scrutiny, longer cycles, pull-ins ahead of price hikes | Peers selling to the same buyer |
| Supply | Shortages, lead times, allocation | Competitors (gain share if they have supply), suppliers (pricing) |
| Cost inputs | Freight, wages, commodities, FX | Peers with the same cost structure |

### Strength grading
- **Direct (strong):** there is a documented commercial relationship, meaning a named customer or supplier or disclosed concentration of at least 10% of revenue. The signal is also specific: a capex figure, an order trend or an inventory number.
- **Indirect (moderate):** the companies share an end market and customer set, or the relationship is inferred, or the signal is general (macro tone, sector-wide pricing).
- **Weak:** the companies share only a SIC code or a theme, have a different business mix, or the signal touches less than 10% of the target's revenue.

**Scale by exposure.** Effective strength = strength × the share of the target's revenue the signal touches. A direct signal on 5% of revenue matters less than an indirect one on 60%. Show the exposure figure and its source.

### Direction and second-order logic
- **Market or share?** A competitor's weak print can be good for the target (it gains share) or bad (the whole market is weak). Decide from the evidence. Did the source blame the market, or its own execution? Do other peers confirm?
- **Bullwhip effect.** Inventory corrections get bigger as they move upstream. A 5% slowdown in end demand can mean a 20%+ order cut for component suppliers. Upstream companies react earlier and harder.
- **One company's capex is another's revenue.** Supplier revenue impact ≈ change in the customer's capex × the supplier's share of that spend. Show the math with sourced inputs and label the result an estimate.
- **Price moves cut both ways.** A price increase helps the seller and squeezes the buyer's margins unless the buyer can pass it on.
- **Lag.** Suppliers usually see demand change 1-2 quarters before the end customer reports it. Distributors sit in between. Put the expected lag on every link.
- **Reflexivity.** If the target already moved more than its own average earnings-day move in sympathy, the bar for its next print just went up. Flag this for `earnings-preview`.

### Questions a great analyst asks
1. Did the source say *why*: the market, share shifts or execution? The answer reverses the read for peers.
2. How much of the target's revenue does this signal actually touch?
3. Is this new information, or did the target already say it last quarter?
4. Has the target already moved in sympathy (priced in) or not?
5. Which target reports next, and what datapoint would confirm or refute the read?

### Verdict (Read-through)
- **Single-print mode:** `Positive`, `Mixed` or `Negative` for the group. The sub-label names the strongest single link, e.g. "Strong direct positive for suppliers; negative for memory pricing".
- **Sector-scan mode:** the label is "Sector tone".
- **Positive:** the majority of direct links point up and there are no strong negative direct links.
- **Mixed:** direct links point in different directions, or the read depends on market-vs-share.
- **Negative:** the majority of direct links point down, or a strong demand/inventory warning hits upstream names.

## Output
Write `/tmp/<SOURCE>-read-through.json`, or `/tmp/<SECTOR>-read-through.json` in scan mode with `ticker` set to a short sector label. Follow `../sec-edgar/references/report-schema.md`.
- `skill`: `"read-through"`.
- `title`: e.g. `"Capex guide is a *green light* for suppliers"` or `"Software season: *beats, cautious guides*"`.
- `subtitle`: "Read-through from Q3 FY26 print · Oct 29, 2026" or "Sector scan · 11 of 14 reported".
- `verdict`: `{label: "Read-through" | "Sector tone", value: "Positive | Mixed | Negative", sub: "<strongest link>", tone: pos | warn | neg}`.
- `kpis` (3-6):
  - **Single-print mode:** the source's headline signal (e.g. "Capex guide +35% y/y"), # targets assessed, # direct links, strongest positive link, strongest negative link.
  - **Scan mode:** % that beat on revenue, % that raised guidance, median reaction, # still to report.
- `sections` (single-print mode):
  1. **What the source said:** one callout per signal type, with cited figures or short attributed quotes.
  2. **Value-chain map:** table with columns target, relationship (peer/competitor/supplier/customer), evidence (filing + %), exposure %, signal, direction (pill), strength, lag.
  3. **Already priced?:** table with target, move on the source date vs. its average earnings move, and next report date. Add a bar chart of the sympathy moves.
  4. **Second-order effects:** a body section with the bullwhip and capex math, estimates labeled.
  5. **Contradictions and confirmations:** callouts where the source's signal conflicts with or supports the target's own guidance.
  6. **What to watch:** upcoming target prints and the datapoint that would confirm or refute each read.
- `sections` (sector-scan mode):
  1. **Scoreboard:** table with ticker, revenue vs. consensus, EPS vs. consensus, guide (raise/maintain/cut), reaction, all as pills.
  2. **Tally:** `scores` bars for % beat, % raised and % cut.
  3. **Common themes:** callouts recording who said what, with citations.
  4. **Outliers.**
  5. **Read-through for names yet to report.**
- `sources`: every accession used (the source's 8-K and 10-K, and the targets' 10-K and 8-K filings), transcript URLs, consensus site + date, price source.

Render:
```bash
python3 ../sec-edgar/scripts/render_report.py /tmp/<SOURCE>-read-through.json --out-dir earnings-desk-reports
```
Fix any warnings. In chat, print:
- the verdict
- the 2-3 strongest links, each with direction and strength
- which of those are already priced in
- the HTML and Markdown paths

## Quality bar & pitfalls
- SIC peers are not competitors. Say why each target is on the map.
- Label unnamed customers ("Customer A") as inferred matches and give the reasoning.
- Don't double-count: a target's move on the source date may reflect its own news.
- One company's miss is not a sector signal without a second data point.
- Fiscal calendars differ. Align on calendar quarters and say so (e.g. a January FY-end against a December one).
- In scan mode, use pre-print consensus and state the basis (adjusted vs. GAAP). If consensus can't be found, write "n/a".
- Keep facts (disclosed relationships, reported numbers) visibly separate from judgment (direction, strength, second-order estimates).
- Every link has a source. "Everyone knows" is not a source.

Next: `/earnings-desk:earnings-preview` for the next related company to report, `/earnings-desk:kpi-tracker` to confirm the read in that company's operating data, and `/earnings-desk:comps-valuation` to see which exposed name is cheapest for the signal.

_Not investment advice. Data is from public filings and cited third-party sources and may contain errors; verify before acting._
