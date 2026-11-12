---
role: product-manager
kind: positive
fixture: wordcount
---
# Task
You are the Product Manager. Read .team/roles/product-manager.md and act on issue #1.

# Setup
```bash
lines_request
```

# Expected
Priya creates `team/1-<slug>` with a one-page change spec `docs/changes/1.md` as its first commit: testable acceptance rows (including a file whose last line has no newline, and an empty file), scope and out of scope. She hands on for pricing or approval, and writes no code.

# Checks
- event from=product-manager
- file team/1-* docs/changes/1.md
- same * wc.py
- main-unchanged

# Rubric
- Is every acceptance row a statement someone could check with a command and an expected output?
- Does the spec settle what happens with a last line that has no trailing newline, or flag it as a question?
- Does it state what is out of scope?
