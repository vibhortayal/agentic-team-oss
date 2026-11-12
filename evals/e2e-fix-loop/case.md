---
role: e2e
kind: negative
fixture: wordcount
max_sessions: 8
---
# Task
You are the Verifier. Read .team/roles/verifier.md and act on issue #1.

# Setup
```bash
lines_built bug
```

# Owner
Thanks. Go ahead with what you recommend.

# Expected
The fix loop works through handoffs alone: Vera blocks the planted bug (a last line without a newline isn't counted), Ian fixes it from her finding, Vera passes the new revision, the coordinator asks the owner to merge, and the owner merges. At most three rounds.

# Checks
- event from=verifier kind=verdict verdict=BLOCK
- event from=implementer to=verifier kind=handoff
- event from=verifier kind=verdict verdict=PASS
- merged 1
- run main python3 -m unittest
- run main printf 'a\nb' > t && test "$(python3 wc.py --lines t)" = 2
- run main : > e && test "$(python3 wc.py --lines e)" = 0
