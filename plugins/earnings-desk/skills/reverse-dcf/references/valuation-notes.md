# Valuation notes: the plumbing behind a credible DCF

Reference for `reverse-dcf` (and `comps-valuation`). The aim isn't precision. It's to avoid the handful of errors that make a valuation wrong by 30–50%.

## 1. WACC build (simple CAPM)

```
Cost of equity  Ke = Rf + β × ERP  (+ size/specific premium only with a stated reason)
After-tax Kd       = pre-tax yield on the company's debt × (1 − marginal tax rate)
WACC               = E/(D+E) × Ke + D/(D+E) × Kd        (market-value weights)
```

| Input | Where to get it (free) | Notes |
|---|---|---|
| Rf | 10-yr US Treasury yield (treasury.gov, FRED `DGS10`), cite the date | Match currency and duration to the cash flows. Use the 10-yr, not T-bills. |
| ERP | Damodaran's implied ERP (pages.stern.nyu.edu/~adamodar), updated monthly | Historically often ~4–6%. Cite the month you use. |
| β | Regression vs. index (2–5y weekly) or an industry unlevered beta relevered: βL = βU × (1 + (1−t) D/E) | Raw betas for single names are noisy, so prefer industry betas. |
| Kd | YTM on the company's bonds, or interest expense / average debt from statements.py | The second is a book proxy and lags rate moves. |
| Weights | Market cap and debt from market.py / statements.py | Exclude excess cash from D. Leases: see §6. |

**Typical all-in ranges (USD, normal rate regime).** Mega-cap staples and utilities 6.5–8%, mega-cap tech and quality compounders 8–9.5%, average large-cap 8.5–10%, small or high-beta 10–12%, pre-profit or binary 12–15%.
- If your WACC falls below Rf + ~3 pts, recheck the beta or ERP.
- WACC precision beyond ±0.5 pt is false precision. Show the grid.
- Don't raise WACC to "price in risk" you can model explicitly (a bear-case scenario is more honest).

## 2. Terminal value sanity checks

The Gordon terminal value is TV = FCF(N+1) / (WACC − g).

1. **Terminal share of value.** In a 10-year DCF it's commonly 55–80%. Above 85% means the valuation is almost entirely a bet on durability past year 10, so lengthen the explicit period or justify the moat.
2. **Implied exit multiple.** TV / FCF(N) = (1 + g) / (WACC − g).

   | WACC \ g | 2% | 3% | 4% |
   |---|---|---|---|
   | 8% | 17.0x | 20.6x | 26.0x |
   | 9% | 14.6x | 17.2x | 20.8x |
   | 10% | 12.8x | 14.7x | 17.3x |

   Compare with the FCF multiples that mature, low-growth companies trade on today. A 26x exit for a company that will be ex-growth in ten years is a red flag.
3. **Growth must be paid for.** In steady state, g = reinvestment rate × ROIC on new capital. Terminal g of 3% with ROIC of 15% needs ~20% of NOPAT reinvested. dcf.py holds the FCF margin flat into the terminal year, which implicitly assumes this reinvestment is already in FCF. For a capital-intensive company, lower the terminal FCF margin.
4. **g ≤ long-run nominal GDP** (about 2–4% in USD). A firm can't outgrow the economy forever.
5. **Steady-state year.** The final explicit year should look normal: margins at a sustainable level, capex ≈ maintenance + growth, no one-offs.

## 3. When DCF breaks, and what to use instead

| Situation | Why FCF DCF fails | Use instead |
|---|---|---|
| **Banks, insurers, brokers** | Debt is inventory and FCF is meaningless; regulatory capital limits payouts | Justified P/B = (ROE − g) / (Ke − g); P/E vs. ROE; excess-return model; dividend discount. Check CET1, NIM, credit costs, and combined ratio for insurers. |
| **Cyclicals** (semis, autos, chemicals, energy, homebuilders) | TTM FCF can be peak or trough; extrapolating it misleads | Normalize to mid-cycle margins (5–10-yr average from statements.py), value on through-cycle EPS/FCF. Watch the P/E paradox: it looks cheapest at the peak. |
| **Commodity producers** | Value is set by the commodity curve | NAV at strip prices, cost-curve position, EV/reserves. |
| **Pre-profit / high-growth** | Negative FCF, so the reverse solve fails and value sits in the terminal | Reverse DCF with `--manual` using a mature-peer target margin; EV/Sales vs. growth; unit economics (LTV/CAC, contribution margin, payback); dilution runway (cash / burn). |
| **REITs** | Depreciation isn't economic; capital is recycled | P/AFFO, NAV / implied cap rate, dividend coverage. |
| **Conglomerates / holdcos** | Mixed businesses with different risk | Sum-of-the-parts with segment-specific multiples, less holdco discount. |
| **Distressed** | Equity is an option on the assets | Recovery analysis, debt-stack waterfall. |

## 4. Stock-based compensation

SBC is a real economic cost: shareholders give up ownership instead of cash. Pick one treatment and use it consistently:
- **Treatment A (dcf.py default):** subtract SBC from FCF and use today's diluted share count.
- **Treatment B:** don't subtract SBC, but forecast the share count rising by net dilution each year (gross grants less buybacks used only to offset dilution).

Never do neither. Adding back SBC and using a static share count overstates value by roughly SBC/FCF.
- Flag it when SBC is above 5% of revenue or above 20% of FCF (common in software and internet).
- Buybacks that only offset SBC are not shareholder returns. Check `share_count_yoy_pct` in statements.py.

## 5. Net debt and the EV bridge

Equity value = EV − debt − leases (if treated as debt) − pension deficit − minority interest − preferred + cash + non-operating investments.
- dcf.py's `net_debt` = long-term + short-term debt − cash − short-term investments. It **excludes** operating leases, pensions, minority interests, preferred stock, convertibles (as debt) and equity-method stakes. Add them by hand when they exceed ~5% of market cap. Take the figures from the 10-K balance sheet and notes (`edgar.py filing-text TICKER --section 8`).
- Cash held abroad or trapped (China JVs, regulated subsidiaries) may deserve a haircut.
- Convertibles: treat as debt if out of the money, as equity (in diluted shares) if in the money. Don't count them twice.

## 6. Leases (ASC 842 / IFRS 16)

- **US GAAP operating leases:** lease cost runs through operating expenses and operating cash flow, so FCF (OCF − capex) is already after rent. In that case **don't** add operating lease liabilities to net debt, or you double-count.
- **If you use EBITDA / EV multiples or IFRS reporters** (where lease principal sits in financing cash flow): add lease liabilities to EV and subtract lease payments from FCF, consistently on both sides.
- Finance leases are debt. Include them.
- Lease-heavy sectors (retail, airlines, restaurants) can show very different EV/EBITDA depending on this choice. State which one you used.

## 7. Expectations investing checklist (Rappaport & Mauboussin)

1. Estimate price-implied expectations (reverse DCF): growth, margin, forecast horizon.
2. Find the **value trigger** (sales is usually the biggest) and the **value factors** it drives (volume, price/mix, operating leverage, cost efficiencies, investment efficiency).
3. Pick the **turbo trigger**, the driver with the most leverage on value and the most uncertainty.
4. Decide whether expectations are likely to be revised up or down. That's the buy/sell decision, not "intrinsic value vs. price" by itself.
5. Ask whether the market's forecast horizon (years of excess returns) is consistent with the competitive position (see `moat-analysis`).

## 8. Common errors (checklist)

- Mixing nominal cash flows with a real discount rate, or the reverse.
- Margin expansion and high growth in the same scenario with no reinvestment cost.
- Using peak-cycle TTM as the base year.
- Terminal growth above WACC − 3 pts, which produces huge multiples.
- Ignoring dilution, leases or minority interests when they're material.
- Treating consensus as truth instead of as one expectation to test.
