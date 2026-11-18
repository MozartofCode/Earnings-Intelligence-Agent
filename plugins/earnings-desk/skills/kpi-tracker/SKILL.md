---
name: kpi-tracker
description: >-
  Tracks the company-specific operating KPIs that actually drive a stock, beyond revenue and EPS. Pulls metrics such as net revenue retention, RPO and cRPO, ARR, ARPU, subscribers and churn, same-store sales, GMV and take rate, backlog and book-to-bill, units, utilization, NIM, RevPAR or load factor from earnings press releases, 10-Q and 10-K MD&A text and custom XBRL tags, then builds a clean, chart-ready quarterly time series with q/q and y/y change, acceleration or deceleration, and definition changes flagged. Ships an industry KPI library for 18 sectors. Use it when the user asks "track the KPIs", "what metrics matter for this company", "is growth accelerating", "show subscriber trends", "how is NRR trending", "what's the backlog doing", "same-store sales history", "operating metrics", or "build a KPI dashboard". Ends with a "KPI momentum" verdict (Accelerating / Stable / Decelerating / Deteriorating).
license: MIT
compatibility: Requires Python 3.8+ and internet access to sec.gov.
metadata:
  category: "2-earnings-season"
  version: "1.0.0"
  author: "earnings-desk"
---

# kpi-tracker · the numbers behind the numbers

Revenue is an output. KPIs are the engine: retention, pricing, volume, capacity, mix. They turn first, and they are often buried in a press-release table or one MD&A sentence. This skill digs them out, lines them up quarter by quarter, and tells you which way the second derivative is pointing.

## When to use
- Building or refreshing a model; checking whether a story ("re-acceleration", "pricing power", "churn is stabilizing") shows up in the operating data.
- Before a print (`earnings-preview` needs the swing KPI trend) or after one (`earnings-recap` needs the KPI scorecard).
- **Not** for standard financial statements and ratios (use `financial-statements`) or valuation (use `comps-valuation`, `reverse-dcf`).

## Inputs
- `TICKER` (required).
- `kpis` (optional): a list to track. Default: pick 4-8 from `references/kpi-library.md` for the company's industry, plus anything the company itself headlines.
- `quarters` (optional): default 8, up to 12.

> **Paths:** `${CLAUDE_SKILL_DIR}` is this skill's own folder. Claude Code fills it in automatically; in other tools, replace it with the folder that contains this `SKILL.md`. Sibling skills such as `${CLAUDE_SKILL_DIR}/../sec-edgar` are installed next to it.
>
> **Working files:** save intermediate JSON and the report JSON in `.earnings-desk/work/` inside the user's current folder (`mkdir -p .earnings-desk/work` first); finished reports go to `earnings-desk-reports/`.
>
> **Chat answer:** lead with the verdict, and put the source next to each key number in the chat reply itself (e.g. `8-K Ex.99.1, accn 0000320193-26-000024` or `web: nasdaq.com, 2026-11-03`). Don't leave citations only in the report.

## Workflow
1. **Identify the industry and the KPI set.**
   `python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/edgar.py profile TICKER` (SIC code and description). Map to an industry in `references/kpi-library.md`. Then read the latest release (`python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/edgar.py earnings-release TICKER --max-chars 150000 > .earnings-desk/work/TICKER-er0.json`) and note every operating metric the company headlines or tables. The company's own headline KPIs override the library.
2. **Look for XBRL first (cleanest series).** Some KPIs are tagged:
   - Standard: `python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/edgar.py concept TICKER RevenueRemainingPerformanceObligation` (RPO), `ContractWithCustomerLiabilityCurrent` (deferred revenue), `RevenueRemainingPerformanceObligationPercentage` (share recognized within the next period, which gives cRPO), `InventoryNet`, `NumberOfStores`, `NumberOfRealEstateProperties`, `AreaOfRealEstateProperty`.
   - Other standard taxonomies: `--taxonomy srt` or `--taxonomy dei` for a few count-type facts.
   - Custom, company-prefixed tags (e.g. `nflx:PaidMemberships`) are generally **not** served by SEC's XBRL API, so `concept` returns "not reported" for them. That is expected: go to text extraction (step 3). If you know the filing, the tagged value is still visible in the filing's own document, so cite that accession.
   `concept` returns raw, undimensioned facts: dedupe by `end` date and keep the latest-filed value (restated figures supersede). Sanity-check scale and scope against the filing text. A fact can cover only a subset (e.g. one store class) or carry an obvious scaling error in an old filing.
3. **Extract from text (most KPIs live here).** Loop over releases (`--index 0..N`, saved to `.earnings-desk/work/TICKER-er$i.json`) and the 10-Q MD&A:
   ```bash
   python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/edgar.py filing-text TICKER --form 10-Q --section mdna --index 0
   python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/edgar.py filing-text TICKER --form 10-K --section mdna --index 0
   ```
   Long text is written to `saved_to`; `grep -n -i` it for the metric name and its synonyms (e.g. "net dollar retention", "dollar-based net expansion"). Q4 values usually appear only in the 10-K or the Q4 release. Record for every data point: period end, value, unit, exact definition wording, source accession, and whether it was restated.
4. **Pull revenue and the core financials** for ratio KPIs and sanity checks: `python3 ${CLAUDE_SKILL_DIR}/../financial-statements/scripts/statements.py TICKER --quarters 12`. Derive KPIs the company implies but doesn't print (see framework), and label them **derived**.
5. **Check definitions.** Compare the KPI definition text across filings. Any change (cohort basis, inclusion of acquisitions, "paid" vs. "active" users, trailing-12-month vs. point-in-time) creates a seam. Flag it and do not splice series across a definition change without saying so.
6. **Compute trends** (framework), build the series table, pick the chart(s), assign the verdict.
7. Write and render the report.

## Analysis framework

### Series math
- **q/q % and y/y %** for every KPI. For ratios (margins, NRR, take rate, NIM), use bps/pts change, not %.
- **Acceleration** = y/y growth this quarter − y/y growth last quarter (pts). Two consecutive same-sign changes = a trend; one is noise.
- **Two-year stack** = (1 + y/y_t) × (1 + y/y_t−4) − 1. Use for comps and any seasonal or base-effect-distorted KPI (same-store sales, travel).
- **TTM / 4-quarter average** for lumpy KPIs (bookings, backlog adds, large deals).
- **Seasonality:** compare with the same quarter last year, never sequentially, for retail, travel, ads, semis.

### Derived KPIs (label as derived, show the formula)
- **cRPO** = RPO × % recognized in next 12 months (from the RPO footnote).
- **Billings** = revenue + Δ deferred revenue (current, or total). Calculated billings growth vs. revenue growth: billings slower for 2+ quarters = forward revenue slowdown.
- **Net new ARR** = ARR_t − ARR_t−1. Its y/y growth leads revenue growth.
- **Book-to-bill** = orders / revenue. > 1.0 backlog builds; trend matters more than level.
- **Implied backlog conversion** = revenue / beginning backlog.
- **ARPU** = segment revenue / average subscribers (average of beginning and end).
- **Take rate** = revenue / GMV (or TPV). Rising take rate with slowing GMV = monetizing a maturing base.
- **Revenue per unit / per store / per employee** for productivity.
- **Inventory weeks or days** = inventory / (COGS / 13 or / 91).
- **Implied churn** (if gross adds disclosed) = (beginning subs + gross adds − ending subs) / average subs.

### Reading the KPI
- **Leading vs. lagging:** cRPO, billings, net new ARR, orders, book-to-bill, pipeline and bookings lead revenue by 1-4 quarters. Subscribers and units are coincident; NRR is lagging (often trailing-twelve-month).
- **Price × volume decomposition:** growth = volume growth + price/mix growth (approximately). Price-led growth without volume is fragile when inflation fades.
- **Cohort masking:** a blended metric can hide a deteriorating newer cohort. If the company discloses cohorts or customer tiers ($100K+ customers), track them separately.
- **NRR in context:** NRR > 120% best-in-class software, 105-115% healthy, < 100% means the installed base is shrinking. Watch the direction: NRR falling 2+ pts per quarter for 3 quarters usually precedes a growth reset.
- **Same-store sales:** split traffic vs. ticket. Ticket-led comps with negative traffic = price-driven, vulnerable.
- **Utilization and load factor:** above ~85-90% supports pricing; capacity additions dilute it before demand catches up.

### Red flags
- A KPI disclosed for years that disappears, or switches from quarterly to annual disclosure (cross-check with `guidance-tracker` for guided metrics).
- Definition changes in the quarter growth slowed.
- "Users" redefined (monthly active → daily active, paid → total) or a threshold changed (e.g. "customers > $50K" → "> $100K").
- KPI strong while the related financial line weakens (subscribers up, ARPU down more; GMV up, take rate down; backlog up, but book-to-bill < 1 for 3 quarters).
- Backlog growth driven by multi-year deals with cancellation clauses (read the definition).

### Verdict (KPI momentum)
- **Accelerating:** the leading KPI(s) accelerated for 2+ quarters and no core KPI deteriorated.
- **Stable:** growth within ±2 pts of the trailing average, no adverse definition changes.
- **Decelerating:** leading KPI decelerated for 2+ quarters, still growing.
- **Deteriorating:** a core KPI turned negative y/y, or a KPI was dropped/redefined amid weakness.

## Output
Write `.earnings-desk/work/<TICKER>-kpi-tracker.json` per `../sec-edgar/references/report-schema.md`.
- `skill`: `"kpi-tracker"`; `title` e.g. `"cRPO is *re-accelerating*"`; `subtitle`: "8 quarters of operating KPIs, Q4 FY24 - Q3 FY26".
- `verdict`: `{label: "KPI momentum", value: "Accelerating | Stable | Decelerating | Deteriorating", sub: "Leading KPI + latest change", tone: pos | neutral | warn | neg}`.
- `kpis` (4-6): the latest value of each headline KPI with `delta` = y/y and acceleration (e.g. "cRPO $41.2B", "+18% y/y · +2 pts accel.").
- `sections`:
  1. **The KPI set** — table: KPI, why it matters, leading/coincident/lagging, source type (XBRL / release / MD&A / derived).
  2. **Time series** — the chart-ready table: rows = KPIs, columns = quarters (≤ 12), plus y/y and acceleration columns.
  3. **Trend charts** — 1-3 charts, one idea each (e.g. bar = KPI level, line = y/y %). Use `yFormat` usd/pct appropriately.
  4. **What's driving it** — price × volume, cohorts, mix; derived KPIs with formulas.
  5. **Definitions and seams** — callouts for definition changes, dropped metrics, restatements.
  6. **What to watch next quarter** — thresholds per KPI that would change the verdict.
- `sources`: every accession per data point family (release 8-Ks, 10-Qs, 10-Ks), XBRL tag names used.

Render:
```bash
python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/render_report.py .earnings-desk/work/<TICKER>-kpi-tracker.json --out-dir earnings-desk-reports
```
Fix warnings. In chat: verdict, the leading KPI's last value with y/y and acceleration, any definition change, and the HTML + Markdown paths.

## Quality bar & pitfalls
- Prefer the company's definition and label. Don't rename "net dollar retention" to NRR without noting it.
- Q4 data often lives only in the 10-K/Q4 release. Don't leave Q4 as "derived" when it was disclosed.
- Point-in-time vs. average vs. trailing-12-month metrics are not comparable. Label each.
- When a value can't be found for a quarter, leave the cell as "n/d" and keep the column. Never interpolate.
- Watch units: thousands vs. millions in press-release tables, and per-share vs. total.
- Raw `concept` output can include duplicate facts (same period reported in later filings). Keep the latest filed value and note restatements.
- Banks, insurers, REITs have their own KPI families (library covers them). Don't force SaaS metrics on them.

Next: `/earnings-desk:earnings-preview` to set the bar on the swing KPI, `/earnings-desk:read-through` to compare the KPI trend with peers, `/earnings-desk:moat-analysis` if retention or pricing KPIs are the question.

_Not investment advice. Data is from public filings and may contain errors; verify before acting._
