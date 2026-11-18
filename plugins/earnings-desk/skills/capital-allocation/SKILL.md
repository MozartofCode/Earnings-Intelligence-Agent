---
name: capital-allocation
description: >-
  Grades how management spends shareholder cash (A to F) from 5 to 10 years of SEC filings, no API key. Builds a sources-and-uses table (operating cash flow, capex, M&A, buybacks, dividends, debt), tests buybacks against stock-based compensation (net dilution, average buyback price vs. today's price, i.e. buyback ROI), reviews the M&A record (goodwill, impairments, acquired growth), tracks ROIC vs. cost of capital, checks dividend sustainability (payout of FCF), and reads executive pay alignment from the proxy (DEF 14A: performance shares, TSR, EPS targets). Use it when the user asks "is management good with capital", "are buybacks creating value", "where does the cash go", "capital allocation", "do they overpay for acquisitions", "is the dividend safe", "are buybacks just offsetting SBC", "how is management paid", "ROIC vs WACC", or "shareholder returns".
license: MIT
compatibility: Requires Python 3.8+ (standard library only) and internet access to sec.gov. Optional FMP_API_KEY or FINNHUB_API_KEY for more reliable quotes.
metadata:
  category: "3-forensics-quality"
  version: "1.0.0"
  author: "earnings-desk"
---

# capital-allocation · follow the cash, grade the stewards

Over a decade, what management does with the cash matters as much as how much cash the business makes. This skill reconstructs every dollar in and out, prices the buybacks, audits the acquisitions, and checks whether pay rewards per-share value or just size, then assigns a letter grade.

## When to use
- "Is management good with capital?", "are buybacks working?", "where does the cash go?", "is the dividend safe?", "do they overpay for deals?", "how is the CEO paid?"
- Assessing a mature cash generator, a serial acquirer, or a heavy-SBC tech company.

**Not for:** general margin and growth analysis (`financial-statements`), accounting manipulation (`forensic-accounting`), insider buying and selling signals (`insider-ownership`), what the stock is worth (`reverse-dcf`).

## Inputs
- `TICKER` (required).
- `--years` 10 (default for this skill; use 5 for young companies).
- Optional: a cost-of-capital assumption (default 9% for a typical large cap, 10–11% for small caps or cyclicals; always label it as an assumption).

> **Paths:** `${CLAUDE_SKILL_DIR}` is this skill's own folder. Claude Code fills it in automatically; in other tools, replace it with the folder that contains this `SKILL.md`. Sibling skills such as `${CLAUDE_SKILL_DIR}/../sec-edgar` are installed next to it.
>
> **Working files:** save intermediate JSON and the report JSON in `.earnings-desk/work/` inside the user's current folder (`mkdir -p .earnings-desk/work` first); finished reports go to `earnings-desk-reports/`.
>
> **Chat answer:** lead with the verdict, and put the source next to each key number in the chat reply itself (e.g. `8-K Ex.99.1, accn 0000320193-26-000024` or `web: nasdaq.com, 2026-11-03`). Don't leave citations only in the report.

## Workflow
1. **Ten years of cash flows and returns**
   ```bash
   python3 ${CLAUDE_SKILL_DIR}/../financial-statements/scripts/statements.py TICKER --years 10 --quarters 8 > .earnings-desk/work/TICKER-st.json
   ```
   Per year use `operating_cash_flow`, `capex`, `fcf`, `acquisitions`, `buybacks`, `dividends_paid`, `sbc`, `total_debt`, `net_debt`, `cash`, `goodwill`, `shares_diluted`, `roic_pct`, `eps_diluted`. `acquisitions` is null for many companies that tag deals differently (MSFT is null even with Activision in FY24). When it's null, read the 10-K cash flow statement, and treat a goodwill jump as the tell (MSFT goodwill went from $67.9B to $119.2B in FY24).

2. **Shares repurchased, to price the buybacks**
   ```bash
   python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/edgar.py concept TICKER StockRepurchasedAndRetiredDuringPeriodShares | python3 -c "import json,sys; d=json.load(sys.stdin); rows=[r for u in d.get('units',{}).values() for r in u if r.get('form')=='10-K' and r.get('fp')=='FY' and r.get('frame') and 'start' in r]; print(d.get('error') or '\n'.join('%s %s %s' % (r['end'], r['val'], r['accn']) for r in rows[-10:]))"
   ```
   If the tag isn't reported, try `StockRepurchasedDuringPeriodShares`, then `TreasuryStockSharesAcquired` (AAPL reports the tag in the command above; MSFT reports `StockRepurchasedDuringPeriodShares`). As a last resort use the 10-K Item 5 "Issuer Purchases of Equity Securities" table or the equity note, which often states the average price paid. The same snippet works for any annual tag: `GoodwillImpairmentLoss`, `PaymentsToAcquireBusinessesNetOfCashAcquired`, `ProceedsFromIssuanceOfLongTermDebt`, `RepaymentsOfLongTermDebt`, `PaymentsForRepurchaseOfCommonStock`.

3. **Current price** for buyback ROI and dividend yield
   ```bash
   python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/market.py quote TICKER
   python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/market.py history TICKER --range 10y   # optional: price path vs. buyback years
   ```

4. **Management's stated framework and the deals**
   ```bash
   python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/edgar.py filing-text TICKER --form 10-K --section 7 --max-chars 40000
   ```
   Find the "Liquidity and Capital Resources" discussion: the stated priorities, authorization remaining, dividend policy, debt targets and acquisitions. Grep the saved 10-K for `"business combination|acquisition|purchase price|goodwill|impairment"` to list deals with prices, and check the goodwill note for impairments by reporting unit. `python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/edgar.py filings TICKER --forms 8-K --limit 100` shows Items 1.01 and 2.01 (deal announcements and closings) and 2.06 (impairments).

5. **Pay alignment from the proxy**
   ```bash
   python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/edgar.py filing-text TICKER --form "DEF 14A" --max-chars 2000    # prints saved_to
   ```
   Section extraction is **not reliable for proxies**: they have no "Item N." headings, so `--section "Compensation Discussion and Analysis"` usually matches the table of contents and runs to the end of the document (tested on MSFT's 2026 proxy). Grep the saved file instead (quote the path, because the filename contains a space):
   ```bash
   grep -n -i -E "performance (share|stock|unit)|PSU|PSA|relative TSR|total shareholder return|EPS|ROIC|return on invested|free cash flow|revenue growth|operating income|annual (cash )?incentive|pay versus performance|most important (financial )?(performance )?measures|clawback|stock ownership guideline" "<saved_to>" | head -60
   ```
   Read around the hits. The "Pay Versus Performance" tabular list of "most important financial performance measures" is the fastest summary of what really drives pay.

## Analysis framework

**1. Sources and uses (sum over the period, then show annually).**
- Sources: OCF, net debt raised, stock issued, asset sales.
- Uses: capex, acquisitions, buybacks, dividends, debt repaid, cash build.
- Express each as % of cumulative OCF. The mix tells the story: reinvestor (capex and M&A above 60%), returner (buybacks and dividends above 60% of FCF), or borrower (returns funded by net debt raised, a red flag if sustained).
- Check that buybacks plus dividends ≤ FCF over the period. If not, the gap was funded with debt or cash, so say which.

**2. Buybacks vs. SBC (are buybacks real?)**
- Net dilution = change in diluted share count over the period (CAGR). Gross reduction = shares repurchased / starting shares.
- Buyback offset ratio = buyback $ / SBC $. Near 1.0 or below means buybacks merely mop up dilution, and "capital return" is really employee compensation paid in cash.
- Shares retired vs. shares issued: if a company spent $X billion and the share count barely moved, that is the real cost of SBC.

**3. Buyback ROI (did they buy cheap or dear?)**
- Average buyback price per year = buyback $ / shares repurchased (check split adjustment: AAPL's FY2020 share count is post 4-for-1 split, so compare like with like).
- Weighted-average price over the period vs. today's price gives a simple ROI. Add dividends avoided on retired shares for a fuller IRR if you want precision.
- Timing skill: did buybacks rise when the stock was cheap (low P/E or after drawdowns) and fall when expensive? Pro-cyclical buying (most in peak years) is a common failure.
- Buybacks at a P/E above the company's earnings growth plus yield destroy value for remaining holders, even if the price later rose. Say whether the result was skill or market beta.

**4. M&A track record**
- Cumulative acquisition spend vs. goodwill and intangibles added. Goodwill / total assets trend (above 40% = acquisition-built).
- Impairments (`GoodwillImpairmentLoss`, 8-K 2.06): each write-down is an admission of overpayment, so tie it to the deal.
- Acquired growth: organic vs. total revenue growth from MD&A. Return on acquisition ≈ acquired NOPAT / price paid. Below WACC after 3 years means value-destructive.
- Pattern red flags: serial deals that mask organic decline, deals at peak valuations paid in cash, frequent "adjusted" add-backs for integration costs, segment recasts after deals.

**5. ROIC vs. WACC trend**
- `roic_pct` per year vs. your stated WACC assumption. The spread and its direction across the decade is the single best summary of allocation quality.
- Incremental ROIC = Δ NOPAT / Δ invested capital over 3–5 years, i.e. what the last dollars earned.
- Caveats: `roic_pct` uses NOPAT over average (equity + total debt) without subtracting cash, so treat it as a return on all capital; acquisitions add goodwill that depresses ROIC for years, so compare organic and reported returns.

**6. Dividend sustainability**
- FCF payout = dividends / FCF (below 60% comfortable, 60–80% fine for stable businesses, above 100% unsustainable without debt). Earnings payout = dividends / net income.
- Dividend growth vs. FCF-per-share growth over 5 years. Faster dividend growth can't last.
- Coverage through a downturn: payout on trough FCF, net debt / EBITDA headroom. Dividend cuts in the history are a data point, so look for them.

**7. Balance sheet use**
- Net debt trend vs. returns. Levering up to buy back stock at peak prices is the classic value trap.
- Debt maturities vs. FCF, and credit rating mentions in MD&A.
- Cash hoarding: net cash above 20% of market cap with no plan is also a misallocation (opportunity cost).

**8. Incentive alignment (DEF 14A)**
- Good: long-term PSUs on ROIC, per-share FCF or relative TSR over 3+ years; meaningful ownership guidelines; clawbacks beyond the legal minimum; caps on payout when absolute TSR is negative.
- Weak: annual bonuses on revenue or adjusted EPS (rewards empire building and buyback-driven EPS); metrics adjusted at the committee's discretion; one-off "retention" mega-grants; targets reset lower after a miss.
- Ask: would management get paid more for a value-destroying acquisition? If revenue or absolute EPS drive pay, yes.

**Grading rubric (judgment; show the sub-scores):**

| Grade | Profile |
|---|---|
| A | ROIC well above WACC and stable or rising; buybacks net-shrink the count at sensible prices; M&A disciplined with few impairments; dividends covered; pay tied to per-share value over 3+ years |
| B | Good returns with one weakness (for example buybacks mostly offset SBC, or one bad deal) |
| C | ROIC near WACC; returns funded partly by debt; mixed M&A; pay on adjusted EPS or revenue |
| D | ROIC below WACC for years; pro-cyclical buybacks; repeated impairments; dividend above FCF |
| F | Value destruction: big write-downs, levered buybacks at peaks, payouts funded by debt or dilution while the business shrinks, misaligned pay |

Score five pillars from 0–100 (reinvestment returns, buybacks, M&A, dividends and balance sheet, incentives), weight them by where the cash actually went, and map the result to the grade. Don't penalize a pillar the company doesn't use (no dividend is not a failure).

## Output
Write `.earnings-desk/work/TICKER-capital-allocation.json` per `../sec-edgar/references/report-schema.md`, `"skill": "capital-allocation"`.

- **title**: e.g. `"Buybacks that *actually shrink* the share count"` or `"Ten years of *buying high*"`.
- **verdict**: `{"label": "Capital allocation", "value": "A | B | C | D | F", "sub": "<one-line reason>", "tone": "pos (A/B) | neutral (C) | warn (D) | neg (F)"}`.
- **kpis** (4–6): cumulative FCF, % returned (buybacks plus dividends / FCF), net share count change (CAGR), average buyback price vs. current price, ROIC vs. WACC spread, FCF payout ratio.
- **sections**:
  1. *Where the cash went*: sources and uses table (cumulative $ and % of OCF) plus a stacked-looking bar chart by year (≤ 3 datasets: reinvestment, shareholder returns, net debt change).
  2. *Buybacks vs. SBC*: table by year (buyback $, shares retired, average price, SBC $, net share change), and a callout with the buyback ROI vs. today's price.
  3. *M&A record*: deal table (year, target, price, goodwill added, outcome or impairment), goodwill / assets trend.
  4. *Returns on capital*: ROIC line vs. a WACC line (labeled assumption), incremental ROIC.
  5. *Dividend sustainability*: payout table, coverage callout.
  6. *Incentives*: pay metrics table (metric, weight, horizon, alignment pill) with short cited quotes from the proxy.
  7. *Grade*: `scores` bars for the five pillars, then the letter with its rationale, labeled as judgment.
- **sources**: statements.py accessions, concept-tag accessions, 10-K and DEF 14A accession numbers, the quote source and timestamp.

```bash
python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/render_report.py .earnings-desk/work/TICKER-capital-allocation.json --out-dir earnings-desk-reports
```
**In chat** give the grade with a one-line reason, a compact sources-and-uses table, the buyback ROI line, the best and worst decision of the decade, the pay-alignment verdict, and the report paths.

## Quality bar & pitfalls
- **Per share, always.** Total FCF growth can hide per-share stagnation. Show FCF per share and the net share change.
- **Cash vs. accrual.** Use cash buybacks (cash flow statement), not authorizations. Announced programs mean nothing until executed.
- **Splits.** Share counts and average prices must be on the same split basis. Older filings aren't restated.
- **Tag gaps.** `acquisitions` and repurchased-share tags vary by company. A null is "not tagged", not "zero", so check the filing.
- **ASRs and excise tax.** Accelerated share repurchases and the 1% buyback excise tax (from 2023) create timing mismatches between cash paid and shares retired. Use multi-year totals.
- **WACC is an assumption.** State it, and show what changes if it is ±1 point.
- **Don't confuse luck with skill.** A buyback that "made money" in a bull market may still have been poor timing relative to the stock's own valuation range.

## Next skills
- `/earnings-desk:insider-ownership` to see whether insiders buy what the company buys
- `/earnings-desk:forensic-accounting` if goodwill, adjusted metrics or SBC look aggressive
- `/earnings-desk:reverse-dcf` to judge whether buying back stock at today's price makes sense
- `/earnings-desk:moat-analysis` to test whether high ROIC can persist
- `/earnings-desk:thesis-tracker` to log the grade against your thesis

_Not investment advice. Grades are analytical judgments based on public filings, which may contain errors; verify before acting._
