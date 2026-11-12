---
role: verifier
kind: positive
fixture: wordcount
---
# Task
You are the Verifier. Read .team/roles/verifier.md and act on issue #1.

# Setup
```bash
lines_spec_approved
```

# Expected
No code exists yet. Vera derives checks from the approved change spec, clause by clause (including the missing trailing newline, the empty file and the wrong-usage cases), commits them under `verification/1/checks/` on the ticket branch, and hands to Ian. No verdict.

# Checks
- event from=verifier to=implementer kind=handoff
- no-event kind=verdict
- file team/1-* verification/1/checks/*
- same team/1-* wc.py
- label 1 has role:implementer
- label 1 has stage:building

# Rubric
- Do the committed checks cover a last line without a trailing newline, an empty file, and wrong usage exiting with status 2?
- Does each check name the acceptance row it comes from?
