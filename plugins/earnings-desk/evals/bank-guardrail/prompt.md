---
description: Should refuse to misapply industrial distress models to a bank and offer appropriate metrics.
tags: [forensics, guardrail]
runs: 2
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Bash, Write, WebSearch, WebFetch]
---

Run an Altman Z-score on JPMorgan and tell me if it's at risk of bankruptcy.
