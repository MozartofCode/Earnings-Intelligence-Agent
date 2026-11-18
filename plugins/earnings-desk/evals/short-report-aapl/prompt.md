---
description: Allegation fact-check should label false claims Contradicted and true ones Supported, with filing citations and neutral language. The report is synthetic.
tags: [forensics, short-report]
runs: 2
max_turns: 60
timeout_seconds: 1500
allowed_tools: [Read, Glob, Grep, Skill, Bash, Write, WebSearch, WebFetch]
expected_outcome: Claims 1-3 Contradicted (AR up ~10% on ~15% revenue growth; no material weakness, the only mention is auditor boilerplate; no auditor change), claim 4 Supported (CEO change in 2026).
---

A newsletter I follow published this short thesis on Apple (AAPL) last week. Is it right? Check it against the filings.

"1) Apple's accounts receivable doubled in fiscal 2026 while revenue was flat, a classic sign of channel stuffing. 2) Apple's latest 10-K discloses a material weakness in internal controls. 3) Apple quietly replaced its auditor in 2026. 4) Apple changed CEOs in 2026, so leadership is in transition."
