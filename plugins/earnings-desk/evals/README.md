# earnings-desk eval suite

Six cases that check what the plugin should add over plain Claude: testing beat quality, explaining forensic scores with filing evidence, solving for what's priced in, diffing filings, not misapplying industrial models to banks, and fact-checking a (synthetic) short report against the filings.

Run from the repo root (needs a signed-in Claude Code CLI; runs count against your usage):
```bash
export EVAL_SEC_USER_AGENT="Your Name you@example.com"
claude plugin eval ./plugins/earnings-desk --ablation with-without \
  --allow-tools Write WebSearch "Bash(python3 *)" "WebFetch(domain:sec.gov)" "WebFetch(domain:data.sec.gov)" "WebFetch(domain:query1.finance.yahoo.com)"
```
Bash runs inside Claude Code's sandbox; the WebFetch domain grants also open those hosts to the scripts.
