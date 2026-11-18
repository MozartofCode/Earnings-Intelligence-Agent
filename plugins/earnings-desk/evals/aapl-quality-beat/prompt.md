---
description: Post-earnings analysis should test the quality of the EPS beat, not just report it.
tags: [earnings, smoke]
runs: 2
max_turns: 60
timeout_seconds: 1500
allowed_tools: [Read, Glob, Grep, Skill, Bash, Write, WebSearch, WebFetch]
expected_outcome: Revenue and guide beat, but most of the $0.11 EPS beat came from a tariff refund and a lower tax rate; cites the 8-K.
---

Apple reported fiscal Q4 2026 results on November 2, 2026. Did they beat, and was it a quality beat?
