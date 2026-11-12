---
role: e2e
kind: positive
fixture: wordcount
max_sessions: 14
---
# Task
You are the Engagement Lead. Read .team/roles/engagement-lead.md. The owner writes to you:

"Can the counter also tell me how many lines a file has? A last line without a newline should still count, and an empty file is 0 lines."

# Owner
Yes, please go ahead. It's a small personal tool, so the hobby profile in TEAM.md is right. I don't pay per use, so don't spend effort on dollar figures; keep it small. I'm happy with whatever you recommend.

# Expected
The whole ticket runs on its own with the owner only approving and merging: Ella opens the issue and hands it to Priya, the change is specified (probably on the trivial path), Vera prepares checks, Ian builds, Vera passes it, and the owner merges a PR whose head has a PASS. Every handoff carries a valid team-event line and a next prompt.

# Checks
- event from=verifier kind=verdict verdict=PASS
- merged 1
- run main python3 -m unittest
- run main printf 'a\nb' > t && test "$(python3 wc.py --lines t)" = 2
- run main : > e && test "$(python3 wc.py --lines e)" = 0
- run main printf 'a b c' > w && test "$(python3 wc.py w)" = 3
