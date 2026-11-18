---
name: transcript-decoder
description: >-
  Decodes an earnings call transcript the way a skeptical buy-side analyst would. Gets the transcript (company IR, web search, a user-provided file or pasted text, or FMP with a key), splits prepared remarks from Q&A, measures tone shift against prior quarters, counts hedging and uncertainty language per 1,000 words with Loughran-McDonald-style lexicons, scores Q&A evasiveness 0-100 (non-answers, pivots, "we don't guide to that"), maps analyst pushback themes, and flags new versus dropped talking points with short attributed quotes. Use it when the user asks to "analyze the earnings call", "decode the transcript", "what did management say", "was the CEO dodging questions", "tone of the call", "what were analysts worried about", "compare this call to last quarter", "read between the lines", or shares a transcript. Ends with a "Call tone" verdict (Confident / Steady / Guarded / Defensive). For the numbers, pair with earnings-recap.
license: MIT
compatibility: Requires Python 3.8+ and internet access (web search for transcripts, sec.gov for releases). Optional FMP_API_KEY for transcripts.
metadata:
  category: "2-earnings-season"
  version: "1.0.0"
  author: "earnings-desk"
---

# transcript-decoder · hear what management didn't say

The press release is lawyered. The prepared remarks are rehearsed. The Q&A is where conviction, or the lack of it, leaks out. This skill measures that leak: tone versus prior calls, hedging density, evasiveness, and which topics quietly appeared or vanished.

## When to use
- After an earnings call, investor day or conference appearance with a transcript.
- To compare management's language across 2-4 quarters (tone drift often leads the numbers by a quarter or two).
- **Not** for the numeric beat/miss (use `earnings-recap`), for tracking guidance accuracy over years (`guidance-tracker`), or for 10-K risk-factor changes (`filing-diff`).

## Inputs
- `TICKER` (required) and `quarter` (default: latest call).
- `transcript` (optional): a file path or pasted text. Strongly preferred when the user has it.
- `compare` (optional): number of prior calls to compare (default 1, max 4).

> **Paths:** `${CLAUDE_SKILL_DIR}` is this skill's own folder. Claude Code fills it in automatically; in other tools, replace it with the folder that contains this `SKILL.md`. Sibling skills such as `${CLAUDE_SKILL_DIR}/../sec-edgar` are installed next to it.

## Workflow
1. **Get the transcript(s).** In this order:
   - User-provided file or text. Save pasted text to `/tmp/<TICKER>-<Q>-transcript.txt`.
   - Company IR site (many post PDFs or webcast transcripts). Web search "<company> Q3 2026 earnings call transcript" and prefer IR, then reputable free sources. Cite the URL and retrieval date.
   - FMP with `FMP_API_KEY`: `https://financialmodelingprep.com/stable/earning-call-transcript?symbol=TICKER&year=YYYY&quarter=Q&apikey=$FMP_API_KEY` (fetch with WebFetch or curl; never echo the key).
   - If no full transcript is reachable, say so. Work from what is available (news summaries, prepared remarks only) and **label the analysis partial**. Never reconstruct quotes from memory.
   Repeat for the comparison quarter(s).
2. **Anchor on the numbers.** `python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/edgar.py earnings-release TICKER` (and `--index 1`) so you know what the call was defending: misses, guide changes, one-offs.
3. **Segment the transcript.** Split into: (a) operator/safe-harbor boilerplate (exclude), (b) prepared remarks by speaker (CEO, CFO, other), (c) Q&A as question/answer pairs with analyst name and firm. Record word counts for each block.
4. **Lexicon counts.** Using `references/lexicons.md`, count hits per category per 1,000 words, separately for prepared remarks and Q&A, for the current and prior call(s). Do it with a quick script (`grep -o -i -w` per term, or a Python one-off over the saved text). Handle the documented exclusions (e.g. "may" as a month; "could" in "could not be happier" counts as positive). Report raw counts, words, and per-1k rates.
5. **Score each Q&A exchange** with the evasion rubric in `references/lexicons.md`: classify the answer (direct / partial / pivot / non-answer / deferral / attack-the-premise), assign points, and compute the call-level Evasiveness Score (0-100). Note which topics triggered the evasion.
6. **Topic map.** List the themes in prepared remarks and in analyst questions. Diff vs. the prior call: **new** (first mention), **dropped** (featured last call, absent now), **amplified** and **muted** (mention count change ≥ 2×). Dropped talking points are often the most informative output of this skill.
7. **Pushback themes.** Cluster analyst questions (e.g. margins, pricing, competition, capex, inventory, AI monetization). Flag topics asked by 3+ analysts, follow-ups ("just to clarify…", "to push on that…"), and any analyst who asks the same thing twice.
8. **Quotes.** Pick 4-8 short, attributed quotes (≤ 25 words each, speaker and role) that evidence your conclusions. Quote, don't paraphrase inside quotation marks.
9. Write and render the report.

## Analysis framework

### Tone and hedging
- **Net tone** = (positive − negative) / (positive + negative), per block. Compare q/q. A drop ≥ 0.15 in Q&A net tone with steady prepared-remarks tone means management is rehearsed-positive but unconvincing live.
- **Uncertainty + weak-modal per 1k words.** Working orientation for a large-cap call: ~8-15 per 1k combined (an earnings-desk estimate, not a published norm; the company's own history is the real baseline). A rise ≥ 30% q/q is meaningful; ≥ 50% is a red flag, especially in the CFO's remarks.
- **Prepared vs. Q&A gap.** Q&A uncertainty rate > 1.5× prepared-remarks rate = scripted confidence that doesn't survive questions.
- **Strong modal vs. weak modal ratio** ("will", "committed" vs. "may", "hope"). A falling ratio on guidance language is an early warning.
- **Litigious / constraining spikes** point to legal, regulatory, covenant or supply constraints even if not named.
- **Specificity.** Count concrete numbers in answers per 1k words. Confident managements quantify; struggling ones adjective-ize ("robust", "healthy", "solid") without numbers.
- **CEO vs. CFO divergence.** CEO bullish while CFO hedges = watch the guide. CFOs are legally closer to the numbers.
- **Pronoun shift.** "We" for wins and "the market/the environment" for misses = attribution bias. Note it.

### Evasiveness (details and points in `references/lexicons.md`)
Call-level score 0-100: < 20 forthcoming, 20-40 normal, 40-60 guarded, > 60 evasive. Weight the topics: evasion on the #1 bull/bear debate matters more than on a minor line. Separate legitimate non-answers (Reg FD, pending M&A, litigation) from evasion; the rubric gives them reduced points.

### Topic and narrative drift
- A metric emphasized for multiple quarters that disappears (e.g. "net new customers", "backlog") usually stopped being flattering.
- New vocabulary (e.g. "normalization", "digestion", "elongated sales cycles", "macro", "prudent") often precedes a guide cut.
- Re-framing the scoreboard ("we now focus on profitable growth") after a growth miss is a goalpost move. Call it.
- Count of analyst questions on one topic is a proxy for where the market's doubt lives.

### Questions to answer in the report
1. What is management most and least confident about, by the evidence?
2. Which topic drew the most pushback, and did management answer it?
3. What changed in the story vs. last quarter?
4. Did anything said contradict the press release or the 10-Q?
5. What one question should be asked next time (for `earnings-preview`)?

### Verdict (Call tone)
- **Confident:** net tone stable or up, hedging flat or down, evasiveness < 25, numbers given unprompted.
- **Steady:** small moves, evasiveness 25-40.
- **Guarded:** hedging up ≥ 30% or evasiveness 40-60, or the key debate deflected.
- **Defensive:** evasiveness > 60, tone down sharply, attack-the-premise answers, or dropped key metrics.

## Output
Write `/tmp/<TICKER>-transcript-decoder.json` per `../sec-edgar/references/report-schema.md`.
- `skill`: `"transcript-decoder"`; `title` e.g. `"Confident script, *guarded* Q&A"`; `subtitle`: "Q3 FY26 earnings call · Oct 28, 2026 · vs. Q2 FY26".
- `verdict`: `{label: "Call tone", value: "Confident | Steady | Guarded | Defensive", sub: "e.g. Evasiveness 47/100", tone: pos | neutral | warn | neg}`.
- `kpis` (4-6): Evasiveness score (and q/q), Uncertainty per 1k (q/q %), Net tone Q&A (q/q), Top pushback theme, # analysts on top theme, New vs. dropped topics count.
- `sections`:
  1. **What the call told us** — 3-5 callouts (pos/warn/neg) with evidence.
  2. **Tone and hedging** — table: category × (prepared, Q&A) × (current, prior) per 1k; bar chart of current vs. prior per category.
  3. **Q&A evasiveness** — `scores` bars per topic or analyst; table of the worst 3-5 exchanges (question gist, answer type, points); overall score.
  4. **Pushback map** — table: theme, # questions, analysts/firms, answered?
  5. **Narrative drift** — table: topic, prior mentions, current mentions, status (new/dropped/amplified/muted).
  6. **Quotes that matter** — blockquotes with speaker, role.
  7. **Method and limits** — lexicon version, word counts, partial-transcript caveats.
- `sources`: transcript URL(s) + retrieval date, 8-K accession(s).

Render:
```bash
python3 ${CLAUDE_SKILL_DIR}/../sec-edgar/scripts/render_report.py /tmp/<TICKER>-transcript-decoder.json --out-dir earnings-desk-reports
```
Fix warnings. In chat: verdict, evasiveness score, the most important dropped or new topic, one quote, and the HTML + Markdown paths.

## Quality bar & pitfalls
- Counts are evidence, not conclusions. Always read the context of a spike before calling it.
- Normalize per 1k words; a longer call is not a more hedged call.
- Exclude safe-harbor boilerplate or it will swamp the uncertainty count.
- Industry baselines differ (biotech and banks hedge more). Compare a company with itself first.
- Machine transcripts mangle names and numbers; verify any quoted figure against the release.
- Keep quotes short and few; never invent or "clean up" a quote. Attribute every quote.
- Don't mistake a CFO's standard "we don't guide quarterly" for evasion when it's long-standing policy (check prior calls).

Next: `/earnings-desk:guidance-tracker` to test whether this management's words have matched results, `/earnings-desk:earnings-recap` for the numbers, `/earnings-desk:thesis-tracker` to log what changed.

_Not investment advice. Transcripts are third-party sources and may contain errors; verify before acting._
