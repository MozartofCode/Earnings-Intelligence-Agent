---
name: insider-ownership
description: >-
  Reads insider trading and ownership for any US-listed stock from SEC Form 4, Form 144, Schedule 13D/13G and proxy filings, no API key. Finds cluster buying (several insiders buying on the open market within weeks, the strongest signal), separates discretionary sales from 10b5-1 plan sales, sizes sales as a % of holdings, focuses on CEO and CFO behavior and on timing around earnings, and maps the ownership structure (dual-class shares, founder control, activists, big holders). Institutional and 13F shifts and short interest come from cited web sources or optional keys. Ends with a Bullish / Neutral / Caution signal. Use it when the user asks "are insiders buying or selling", "insider trading", "Form 4", "is the CEO selling", "who owns this stock", "institutional ownership", "13F", "short interest", "activist stake", "dual-class / founder control", or "insider cluster buy".
license: MIT
compatibility: Requires Python 3.8+ (standard library only) and internet access to sec.gov. Web search is used for 13F aggregates and short interest.
metadata:
  category: "3-forensics-quality"
  version: "1.0.0"
  author: "earnings-desk"
---

# insider-ownership · what the people who know are doing with their own money

Insiders sell for many reasons but buy for one. This skill filters the noise of grants, tax withholding and pre-planned sales down to the trades that carry information, then sets them against who controls the company and how the big holders and short sellers are positioned.

## When to use
- "Are insiders buying?", "is the CEO dumping stock?", "who owns this?", "any activist?", "how much is shorted?"
- As corroboration in `forensic-accounting` (selling into aggressive numbers) or `capital-allocation` (do insiders buy what the company buys back?).

**Not for:** executive pay design (`capital-allocation`), general company overview (`company-tearsheet`).

## Inputs
- `TICKER` (required).
- `--days` window (default 365 for this skill; 180 for a quick read). `--limit` is the number of Form 4 **filings** scanned (default 40). Raise it to 100–200 for mega-caps, where 40 filings may cover only a few months.

> **Paths:** `${CLAUDE_SKILL_DIR}` is this skill's own folder. Claude Code fills it in automatically; in other tools, replace it with the folder that contains this `SKILL.md`. Sibling skills such as `${CLAUDE_SKILL_DIR}/../sec-edgar` are installed next to it.

## Workflow
1. **Form 4 transactions**
   ```bash
   python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/edgar.py insiders TICKER --days 365 --limit 150 > /tmp/TICKER-insiders.json
   ```
   Output: `window_days`, `filings_scanned`, `parse_errors`, `summary` (`open_market_buys`, `buy_value`, `open_market_sales`, `sale_value`, `unique_buyers`, `sales_under_10b5_1`), and `transactions[]` with `filed`, `date`, `insider`, `role`, `code`, `type`, `acquired_disposed`, `shares`, `price`, `value`, `shares_after`, `10b5_1_plan` and `url`.
   Codes: **P** open-market buy, **S** open-market sale, A grant or award, M or X option exercise, F tax withholding, G gift, D disposition to issuer, C conversion, J other. **Only P and S carry signal.** F and A are mechanical, and G is estate planning.
   If `filings_scanned` equals `--limit`, the window was cut short, so raise `--limit` or say so.

2. **Planned sales and 13D/13G filings**
   ```bash
   python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/edgar.py filings TICKER --forms "144,SCHEDULE 13D,SCHEDULE 13D/A,SC 13D,SC 13D/A,SCHEDULE 13G,SCHEDULE 13G/A,SC 13G,SC 13G/A" --limit 40
   ```
   Form 144 means notice of a proposed sale by an affiliate: sales coming in the next 90 days. Schedule 13D means an active holder above 5% (activist intent). 13G means a passive holder above 5%. EDGAR renamed the forms from "SC 13D/G" to "SCHEDULE 13D/G" in late 2024, so query both names. Open a 13D's text (`index_url`) to read Item 4, "Purpose of Transaction".

3. **Ownership structure from the proxy**
   ```bash
   python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/edgar.py filing-text TICKER --form "DEF 14A" --max-chars 2000      # prints saved_to
   grep -n -i -E "security ownership of certain beneficial owners|beneficial owner|class b|class c|votes per share|voting power|controlled company|sunset|pledg|hedging policy|stock ownership guideline" "<saved_to>" | head -50
   ```
   Proxies have no "Item N." headings, so section extraction is unreliable. Grep the saved file (quote the path; it contains a space). Extract: insiders' and directors' combined % of shares and of **votes**, dual-class terms (votes per share, sunset clauses), founder control, "controlled company" exemptions, pledged shares, hedging and ownership-guideline policies.

4. **Earnings dates for timing analysis**
   ```bash
   python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/market.py reactions TICKER --n 8
   python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/market.py history TICKER --range 1y
   ```
   Use the 8-K Item 2.02 dates to place each P and S trade relative to earnings (most companies' trading windows open about 2 days after the release and close 2–4 weeks before quarter end). Use the price history to see whether buys came after drawdowns.

5. **Institutions, 13F changes and short interest** (no SEC aggregate in this toolkit)
   Use web search, for example "TICKER institutional ownership 13F" or "TICKER short interest days to cover", on sources such as Nasdaq.com, exchange short-interest reports, fintel, WhaleWisdom or the company IR site. Cite site and date. 13F data lags 45 days after quarter end, and short interest is published twice a month. If the user has `FMP_API_KEY`, its institutional and short-interest endpoints can help, but they are not built into `market.py`, so label the source clearly. Never state a short-interest number without a citation.

## Analysis framework

**Signal hierarchy (strongest first)**
1. **Cluster buying:** 3+ distinct insiders making open-market purchases (code P) within ~30 days, especially after a drawdown or right after earnings. Academic and practitioner evidence consistently finds this the most predictive insider signal.
2. **CEO or CFO open-market buy** that is large relative to salary or to existing holdings (above 10% added, or above $250k for a mid-cap).
3. **Director buys** (smaller signal; directors buy partly for optics).
4. **Discretionary CEO or CFO sales of large stakes** (above 20–25% of holdings in a window), not under a 10b5-1 plan, especially just before bad news. Caution signal.
5. **Routine 10b5-1 sales and tax withholding (F)**: mostly noise.

**Sizing sales.** Sale % of holdings = shares sold / (shares sold + `shares_after`) for that line. Caveat: `shares_after` is the holding **in that ownership form** (direct, or a specific trust), so an insider with large indirect holdings looks like they sold a bigger fraction than they did. Check the Form 4 (`url`) for other holdings lines before writing "sold 58% of their stake". Also note that the script reads only the **non-derivative** table: options and RSUs held, and derivative exercises, are not counted.

**The 10b5-1 flag is heuristic.** `10b5_1_plan` is set to true when the Form 4 XML contains the text "10b5-1" anywhere (usually a footnote) **or** the `aff10b5One` checkbox (added to Form 4 in 2023) is set. It applies to **every** transaction in that filing, including grants, gifts and withholding. It can therefore be wrong both ways: a footnote saying a sale was "not made pursuant to a Rule 10b5-1 plan" sets it to true, and an older filing without the footnote reads false even for a planned sale. For any sale you cite as meaningful, open the filing and read the footnote. Also note that plan sales still carry *some* information. Rules effective in 2023 require a cooling-off period (90–120 days for officers), so plan adoption timing (disclosed quarterly in 10-K/10-Q Item 9B or Part II Item 5) can be informative. Grep for "trading arrangement" to find adoptions and terminations.

**Timing tests.**
- Buys in the open window right after a weak print or a big drawdown suggest insiders see the selloff as overdone.
- Sales clustered right before a disappointing release, or a large discretionary sale followed by guidance cuts, are a Caution signal. Note it factually and don't allege wrongdoing.
- Purchases by multiple insiders on the same day the window opens are typical of a coordinated vote of confidence. Purchases spread over weeks at rising prices are stronger.

**Base rates.** Most insiders at most large caps are net sellers almost all the time because pay is in stock. Selling alone is weak information. Compare this year's selling with the insider's own history and with the company's grant pattern. The absence of any open-market buying at a stock down 50% is mildly informative.

**Ownership structure.**
- Founder or insider stake above 10% aligns interests but can entrench management. Dual-class with super-voting shares (for example 10 votes per share) means outside holders can't force change. Check for sunset clauses.
- Pledged shares are a margin-call risk and a governance red flag.
- A 13D from an activist means a catalyst: read the purpose and the asks (buybacks, a sale, board seats).
- Rising institutional ownership with falling short interest is supportive. Short interest above 10% of float or above 5 days to cover means a crowded short (squeeze risk, but also informed skepticism), so find out the bear thesis.

**Verdict rules (judgment):**
- **Bullish:** a cluster buy, or a meaningful CEO or CFO open-market buy, in the window with no offsetting discretionary selling. Or an activist 13D with credible value asks.
- **Neutral:** routine plan sales, withholding and grants; no open-market buying; sales small relative to holdings.
- **Caution:** large discretionary sales by the CEO, CFO or multiple officers (especially above 25% of holdings or ahead of bad news), new Form 144s stacking up, pledging, or a rising short interest with a credible bear case.

## Output
Write `/tmp/TICKER-insider-ownership.json` per `../sec-edgar/references/report-schema.md`, `"skill": "insider-ownership"`.

- **title**: e.g. `"Three insiders *bought the dip*"` or `"Steady selling, *nothing unusual*"`.
- **subtitle**: "Form 4 activity, last <N> days · ownership as of <proxy date>".
- **verdict**: `{"label": "Insider signal", "value": "Bullish | Neutral | Caution", "sub": "<the key trade or pattern>", "tone": "pos|neutral|warn"}`.
- **kpis** (4–6): open-market buys (count and $), open-market sales (count and $), unique buyers, % of sales flagged 10b5-1 (labeled heuristic), insider ownership % (votes % if dual class), short interest % of float (cited).
- **sections**:
  1. *The signal*: 2–4 callouts on the trades that matter (who, role, date, $, % of holdings, timing vs. earnings), each linked to its Form 4.
  2. *Transactions*: a table of P and S trades only (date, insider, role, code, shares, price, value, % of holdings, 10b5-1 flag), plus a one-line count of excluded A, F, G and M rows.
  3. *Timing*: a monthly bar chart of buy $ vs. sell $ over the window (≤ 3 datasets), with earnings dates noted in the body.
  4. *Ownership structure*: table of top holders and insiders from the proxy, class and voting terms, pledging.
  5. *Institutions and short interest*: cited figures with dates, 13D/13G filings, Form 144 notices.
  6. *What would change the signal*: specific triggers (a cluster buy, a CEO plan termination, a new 13D).
- **sources**: Form 4 index URLs for every cited trade, DEF 14A and 13D/G accession numbers, and every web source with site and date.

```bash
python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/render_report.py /tmp/TICKER-insider-ownership.json --out-dir earnings-desk-reports
```
**In chat** give the verdict and the key trade, a compact table of meaningful P and S trades, the ownership and control structure in one line, short interest (cited) if found, and the report paths.

## Quality bar & pitfalls
- **Filter before counting.** A headline total without separating plan sales, gifts and withholding is misleading. NVDA's 120-day window (tested Nov 2026) showed $968M of code-S sales, with 9 of 25 flagged 10b5-1, alongside 500,000-share gifts (G) and tax withholding (F) that are not sales at all.
- **Read the footnote** behind any trade you call meaningful: plan status, weighted-average price ranges and indirect holdings all live there.
- **Window coverage.** State `filings_scanned` and the date range. The script scans EDGAR's "recent" filings list (up to 400 Form 4s), so very active filers may be truncated.
- **One owner per filing.** The parser reads the first reporting owner. Joint filings (a fund plus its GP, for example) show one name.
- **Derivatives not parsed.** Option grants and exercises in the derivative table are missing. Read the Form 4 if an exercise-and-sell pattern matters.
- **10% owners and funds** (VCs distributing shares after an IPO, for example) are not management. Treat their sales separately.
- **No fabrication.** Institutional and short-interest numbers must come from a dated, cited source or be marked "not found".

## Next skills
- `/earnings-desk:capital-allocation` to compare insider behavior with company buybacks and pay
- `/earnings-desk:forensic-accounting` if selling coincides with aggressive accounting
- `/earnings-desk:earnings-preview` to see whether insider timing hints at the next print
- `/earnings-desk:bull-bear-debate` if short interest is high and the bear thesis needs testing
- `/earnings-desk:company-tearsheet` for the full one-page context

_Not investment advice. Insider filings show what was traded, not why; data is from public filings and cited sources and may contain errors; verify before acting._
