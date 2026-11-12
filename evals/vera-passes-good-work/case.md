---
role: verifier
kind: positive
fixture: wordcount
---
# Task
You are the Verifier. Read .team/roles/verifier.md and act on issue #1.

# Setup
```bash
lines_built good
```

# Expected
The build in PR #2 meets every row. Vera runs her checks and her own, passes it, commits `verification/1/verdict.json` naming the revision, and hands to the coordinator. She invents no findings and changes no code.

# Checks
- event from=verifier kind=verdict verdict=PASS
- no-event kind=verdict verdict=BLOCK
- file team/1-* verification/1/verdict.json contains PASS
- same team/1-* wc.py
- same team/1-* tests/*

# Rubric
- Does the PASS name the exact revision it reviewed and list what ran with counts?
- Is the PASS handed to the product manager (the coordinator), not to the implementer or the owner?
