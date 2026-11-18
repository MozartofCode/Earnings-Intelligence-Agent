# transcript-decoder lexicons and evasion rubric (v1.0)

Word lists for measuring tone in earnings calls, written for earnings-desk in the spirit of the Loughran-McDonald (2011) finance-specific categories. They are **representative, not exhaustive**: tuned for spoken earnings-call English rather than 10-K prose. Count whole words, case-insensitive, and include listed inflections. Use stems ending in `*` as prefix matches (e.g. `uncertain*` matches uncertain, uncertainty, uncertainties).

General-purpose sentiment dictionaries misclassify finance words ("liability", "tax", "cost", "capital", "risk" in "risk management" are not negative in context). These lists avoid that.

## Counting rules
1. **Exclude** the operator script and the safe-harbor / forward-looking-statements paragraph. They are boilerplate packed with uncertainty words.
2. Count **prepared remarks** and **Q&A answers** separately. Do not count analysts' questions toward management's tone (score them separately if you want an "analyst mood" read).
3. Report `hits`, `words`, and `per_1k = 1000 × hits / words`.
4. **Negation:** a positive word within 3 words after a negator (`not`, `no`, `never`, `neither`, `nor`, `without`, `hardly`, `barely`, `isn't`, `wasn't`, `aren't`, `don't`, `didn't`, `won't`) counts as negative. Do not flip negative words (financial negatives stay negative: "not a loss" is rare and ambiguous).
5. **Exclusions:** "may" when capitalized as a month; "will" as a noun (rare); "could" in "couldn't be happier/prouder" (positive); "risk" in "risk-adjusted", "risk management", "de-risk" (neutral); "fine" in "fine-tune" (neutral); "charge" in "in charge" (neutral).
6. Multi-word phrases count once, and their component words are not also counted.

## 1. Uncertainty
Imprecision, lack of visibility, inability to forecast.

approximate*, assume*, assumption*, believe (when hedging an outcome), cautious*, conceivabl*, conditional*, contingen*, depend* (as in "depends on"), doubt*, exposure (as in "uncertain exposure"), fluctuat*, guess*, hard to predict, hard to say, indefinite*, imprecis*, it remains to be seen, likel*, murky, not clear, nonassess*, pending, perhaps, possib*, preliminar*, presum*, probab*, random*, reassess*, recalibrat*, roughly, rumor*, seem*, somewhat, speculat*, sporadic*, sudden*, tentativ*, too early to tell, too early to say, turbulen*, uncertain*, unclear, undetermined, unforeseen, unknown*, unpredictab*, unproven, unsettled, untested, variab*, volatil*, visibility (when paired with limited/less/reduced/low), fluid (as in "the situation is fluid"), choppy, lumpy, noisy, hard to call, wait and see, on the sidelines.

## 2. Weak modal
Words that soften commitment. The single best "hedging" signal on calls.

almost, apparently, appear*, could, conceivably, depending, hopeful*, hope, hoping, maybe, might, may (verb), nearly, occasionally, perhaps, possibly, potentially, should (when predicting, not prescribing), sometimes, somewhat, suggest*, tend*, try, trying, uncertainly, we'd like to, would expect, aspire*, aim to, ideally, in principle.

## 3. Strong modal
Words of commitment and certainty. Track the strong/weak ratio on guidance language.

always, clearly, committed, commit*, confident*, conviction, definitely, firmly, highest*, must, never (as commitment: "we will never"), certainly, undoubtedly, unequivocally, will (future commitment), without question, we are going to, absolutely, guarantee*, assured, determined, fully expect, on track, locked in, line of sight.

## 4. Constraining
Limits on action: regulation, contracts, covenants, capacity.

bound by, cap*, ceiling, commitment* (contractual), compl* (as in comply/compliance), constrain*, covenant*, encumber*, gated, impair* (ability), indenture*, limit*, mandat*, must not, obligat*, permit* (as in require a permit), prohibit*, quota*, refrain*, require*, restrict*, regulat* (when limiting), shortage*, supply-constrained, capacity-constrained, bottleneck*, allocation (of supply), export control*, license requirement*, tariff*, sanction*.

## 5. Litigious
Legal and regulatory process language.

adjudicat*, allegation*, alleg*, appeal*, arbitrat*, attorney*, class action, claimant*, complaint*, consent decree, counsel, court*, defendant*, deposition*, discovery (legal context), dispute*, enforcement, indict*, injunction*, inquiry, investigat* (regulatory), judgment*, jury, lawsuit*, legal proceeding*, litigat*, plaintiff*, prosecut*, regulator*, remedy, ruling*, settle* (legal), subpoena*, testimony, tribunal, verdict*, whistleblow*, antitrust, DOJ, FTC, SEC inquiry, Wells notice, civil investigative demand, consent order.

## 6. Negative
Financial negativity tuned for calls.

adverse*, aggressive (competitor/pricing), anemic, backlog decline, bankrupt*, below expectations, challeng*, compress*, concern*, contract* (shrink), cut*, declin*, decreas*, deficit*, delay*, deteriorat*, difficult*, digestion, disappoint*, disrupt*, downturn*, downgrad*, drag*, erod*, fail*, fall*, fell, headwind*, impair*, inventory correction, lag*, layoff*, lose, losing, loss*, lost, lower, miss*, moderat* (growth), normaliz* (as euphemism for slowdown), obsolet*, pause*, pressur*, pushout*, push-out*, reduc*, restat*, restructur*, sluggish, slow*, soft*, shortfall*, stagnat*, struggl*, tough, underperform*, unfavorabl*, unprofitab*, weak*, worse*, worsen*, write-down*, write-off*, elongat* (sales cycles), cautious customers, budget scrutiny, deal slippage, slipped.

## 7. Positive
achiev*, accelerat*, beat*, best, better, breakthrough*, robust, record*, strong*, strength*, exceed*, excellent, excit*, expand*, favorabl*, gain*, great, grew, growth (when describing own results), healthy, improv*, increas*, innovat*, leadership, momentum, outperform*, outstanding, pleased, profitab*, progress*, proud, rebound*, recover*, resilien*, solid, stellar, success*, surpass*, tailwind*, upside, win*, won, inflection, share gain*, raised (guidance), all-time high, sold out, demand exceeds supply.

Note: "robust", "solid", "healthy" are **soft positives** often used without numbers. Track them separately as `soft_positive` and compare with the count of concrete numbers in the same answers (see specificity below).

## 8. Supplementary signals (not LM categories, but useful on calls)
- **Deflection phrases:** "as we said", "as I mentioned", "we'll provide more detail", "we'll share more at", "stay tuned", "I'd point you to", "I'll let [name] take that", "we're not going to get into", "we don't break that out", "we don't guide to that", "we'll update you when appropriate", "it's too early".
- **Euphemisms for deterioration:** normalization, digestion, rationalization, right-sizing, optimization (of headcount), recalibration, elongated, measured (spending), prudent, disciplined (when describing slower investment), lumpiness, timing (as an explanation for a miss), macro (as an unspecific cause).
- **Specificity markers:** digits, percentages, currency amounts, dates, named customers or products. Compute `numbers_per_1k` in answers. Falling specificity with rising soft positives = narrative over evidence.
- **Self-attribution:** first-person plural with positive outcomes ("we delivered", "our execution") vs. external attribution with negative outcomes ("the environment", "the market", "macro", "customers paused"). Count both; a strong asymmetry is classic attribution bias.

## Baselines and thresholds
Use the company's own history first. Rough large-cap call baselines (Q&A answers, per 1k words, with these lists) as orientation only. These are earnings-desk working estimates, not published norms; never cite them as data:

| Category | Typical range | Investigate if |
|---|---|---|
| Uncertainty | 4-9 | > 12, or +30% q/q |
| Weak modal | 4-8 | > 11, or +30% q/q |
| Strong modal | 6-12 | falls > 30% q/q |
| Negative | 5-12 | +40% q/q without a disclosed reason |
| Positive | 12-25 | prepared-remarks rate > 2× Q&A rate |
| Litigious | 0-1 | > 2 (find the matter) |
| Constraining | 1-3 | > 5 (supply, regulation, covenants) |

Sector adjustments: biotech, banks and insurers run higher on uncertainty and constraining; high-growth software runs higher on positive.

## Net tone and composite
- `net_tone = (positive − negative) / (positive + negative)` in [−1, 1].
- `hedge_index = (uncertainty + weak_modal) / words × 1000`.
- `conviction_ratio = strong_modal / max(weak_modal, 1)`.
- Report q/q deltas for all three, for prepared and Q&A separately.

---

# Evasion rubric (Q&A evasiveness score, 0-100)

Score each analyst question and management's full answer (including follow-ups) as one **exchange**.

## Answer types and points
| Code | Type | Definition | Points |
|---|---|---|---|
| D | Direct | Answers the question asked, with a number, a clear yes/no, or a specific mechanism | 0 |
| P | Partial | Answers part of a multi-part question, or gives direction without magnitude when magnitude was asked | 1 |
| V | Pivot | Talks about a related but different topic; restates prepared remarks; answers an easier version of the question | 2 |
| R | Refuse (policy) | Explicit refusal citing a long-standing policy ("we don't guide quarterly") consistent with prior calls | 1 |
| N | Non-answer | Refuses without a policy basis, or a new refusal on a metric previously discussed ("we're not going to get into that") | 3 |
| F | Deferral | Pushes to a future event ("we'll share more at the investor day") on a question that matters now | 2 |
| A | Attack the premise | Disputes the question's framing without providing data ("I don't think that's the right way to look at it") | 2 (3 if no data follows) |
| H | Hand-off loop | Passed between executives with neither answering | 2 |
| L | Legitimate constraint | Pending M&A, litigation, Reg FD, regulatory process explicitly cited | 0.5 |

### Modifiers (add to the exchange's points)
- **+1** if the analyst follows up or rephrases the same question (signals the first answer failed).
- **+1** if the topic is the call's central debate (the top pushback theme or the swing KPI from `earnings-preview`).
- **+0.5** if the answer contains ≥ 3 deflection phrases or soft positives and no number.
- **−0.5** if management volunteers a number not asked for that directly addresses the concern.
Cap each exchange at 5 points.

## Call-level score
```
evasiveness = 100 × Σ(exchange points) / (5 × number_of_exchanges)
```
| Score | Read |
|---|---|
| 0-20 | Forthcoming. Management engages with numbers. |
| 20-40 | Normal corporate caution. |
| 40-60 | Guarded. Identify which topics drove it. |
| 60-100 | Evasive. Strong signal, especially if up ≥ 15 points q/q or concentrated on the central debate. |

Also report a **topic-level** score (same formula over exchanges on that topic) and an **executive-level** score (CEO vs. CFO vs. others).

## Worked example
Analyst: "Can you quantify how much of the gross-margin decline was pricing versus mix?"
- "Gross margin was impacted by a number of factors, including mix and some pricing actions. We remain confident in our long-term margin framework." → **V (2)**, central debate **+1**, no number with soft language **+0.5** = 3.5.
- Follow-up: "Is pricing more or less than half?" "We don't break that out." (Previously disclosed price/mix split last year) → **N (3)**, follow-up **+1**, central **+1** = 5 (capped).

## Pitfalls
- Read the whole answer. Long answers often get to the number at the end.
- Don't penalize a CFO for consistent long-standing policies (score R, not N). Check prior transcripts.
- A short "yes" is Direct. Brevity is not evasion.
- Score management, not the analyst's question quality. Leading or unanswerable questions (e.g. asking for next year's EPS in Q1) should be marked and excluded from the denominator if no reasonable management would answer.
