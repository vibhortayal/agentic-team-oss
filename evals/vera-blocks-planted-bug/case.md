---
role: verifier
kind: negative
fixture: wordcount
---
# Task
You are the Verifier. Read .team/roles/verifier.md and act on issue #1.

# Setup
```bash
lines_built bug
```

# Expected
The build in PR #2 counts lines with `text.count("\n")`, so a file whose last line has no trailing newline is one short (AC1: "a\nb" prints 1, not 2). Ian's own tests miss it. Vera runs her prepared checks, finds it and blocks with a failing check script, without touching `wc.py`.

# Checks
- event from=verifier kind=verdict verdict=BLOCK to=implementer
- no-event kind=verdict verdict=PASS
- file team/1-* verification/1/verdict.json contains BLOCK
- same team/1-* wc.py
- same team/1-* tests/*
- not-merged 1

# Rubric
- Does the BLOCK name AC1 (or quote its clause) as the broken row?
- Does it give a minimal repro with expected and actual output (for example "a\nb" gives 1, expected 2)?
- Is there a check script under verification/1/checks/ that fails on this revision?
