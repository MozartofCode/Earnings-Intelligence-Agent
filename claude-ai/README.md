# earnings-desk for Claude.ai and Claude Desktop

Every skill here is a **ready-to-upload zip**. Each one is self-contained: skills that need the SEC data tools carry their own copy inside a `vendor/` folder.

## Install (about 30 seconds per skill)

1. **Download** the zip(s) you want from this folder. Open a file on GitHub, then click the download button (↓).
2. In [claude.ai](https://claude.ai) or the Claude Desktop app, go to **Customize → Skills** ([claude.ai/customize/skills](https://claude.ai/customize/skills)).
3. Click **Upload skill** and choose the zip. Repeat for each skill.
4. Make sure each skill is **turned on**.
5. Start a new chat and ask a question, e.g. *"Did Apple beat last quarter? Was it a quality beat?"* Claude picks the matching skill automatically.

**You'll need:**
- A paid plan that supports skills (Pro, Max, Team or Enterprise).
- **Code execution turned on** (Settings → Capabilities). The skills run small Python scripts.
- For live SEC data, the code sandbox must be allowed to reach `sec.gov` (check your network/egress setting under code execution). If it can't, the skills fall back to web search and say so in the report.

**Tell Claude who you are, for the SEC.** The SEC asks automated tools for a name and email. Start your first chat with:
> My SEC user agent is "Jane Doe jane@example.com". Use it for SEC requests.

## Which zips to upload

**Starter pack (recommended):**

| Zip | Use it for |
|---|---|
| `help.zip` | "What can you do?", picking the right skill |
| `company-tearsheet.zip` | One-page snapshot of any company |
| `earnings-recap.zip` | "Did they beat? Was it real?" |
| `forensic-accounting.zip` | "Any accounting red flags?" |
| `reverse-dcf.zip` | "What growth is priced in?" |
| `bull-bear-debate.zip` | Strongest bull and bear case, judged |

**Everything else:** `sec-edgar`, `financial-statements`, `filing-diff`, `earnings-preview`, `transcript-decoder`, `guidance-tracker`, `kpi-tracker`, `read-through`, `capital-allocation`, `insider-ownership`, `comps-valuation`, `moat-analysis`, `thesis-tracker`, `deep-dive`, `short-report-check` (fact-checks a short-seller report against the filings).

## Good to know on Claude.ai
- **`deep-dive`** uses 8 parallel agents in Claude Code. On Claude.ai it runs the same phases one after another (data → four analyst passes → bull vs bear → portfolio manager). It takes longer but follows the same process.
- **Reports:** Claude creates the HTML report as a file you can download and open in your browser. Ask for *"the HTML report"* if it only answers in chat.
- **`thesis-tracker`** saves your thesis as a file. Claude.ai chats don't keep files between conversations, so download it and re-upload it next time, or use Claude Code, which keeps it on disk.

These zips are built from `plugins/earnings-desk/skills/`. If you change a skill there, rebuild its zip by zipping the skill folder itself (not its contents).
