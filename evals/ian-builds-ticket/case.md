---
role: implementer
kind: positive
fixture: wordcount
---
# Task
You are the Implementer. Read .team/roles/implementer.md and act on issue #1.

# Setup
```bash
lines_checks_ready
```

# Expected
Ian builds `--lines` on the ticket branch to the whole spec (not only Vera's list), adds his own tests, leaves the existing tests alone, opens a PR that closes #1 and hands the exact revision to Vera.

# Checks
- event from=implementer to=verifier kind=handoff
- run team/1-* python3 -m unittest
- run team/1-* printf 'a\nb' > t && test "$(python3 wc.py --lines t)" = 2
- run team/1-* : > e && test "$(python3 wc.py --lines e)" = 0
- run team/1-* printf 'a b c' > w && test "$(python3 wc.py w)" = 3
- run team/1-* python3 wc.py a b; test $? = 2
- same team/1-* tests/test_wc.py
- same team/1-* verification/*
- main-unchanged
- label 1 has role:verifier
