---
role: architect
kind: positive
fixture: wordcount
---
# Task
You are the Architect. Read .team/roles/architect.md and act on issue #1.

# Setup
```bash
mkdir -p docs/specs && cat > docs/specs/v1.md <<'MD'
# Spec v1: richer counts

Status: approved

## Requirements
- R1: `wc.py --lines FILE` prints the number of lines. A last line without a trailing newline counts. An empty file has 0.
- R2: `wc.py --chars FILE` prints the number of characters, counting a newline as one character.
- R3: `wc.py FILE` keeps printing the word count.
- R4: `--lines` and `--chars` together are rejected with the usage line on stderr and exit status 2.

## Units
1. Lines (R1, R3)
2. Characters and the combined-flag rule (R2, R4); depends on unit 1.
MD
commit_as product-manager "Spec v1" && git push -q origin main 2>/dev/null
as_role product-manager gh issue create --title "Build spec v1 (multi-unit)" --label role:architect,stage:ready,mode:multi-unit --body "Approved full spec: docs/specs/v1.md at $(git rev-parse HEAD). Two units."
as_role product-manager gh issue comment 1 --body "**Priya (product-manager) → Arjun (architect)** · handoff

Rows: R1-R4 · Revision: $(git rev-parse HEAD) · Files: docs/specs/v1.md · Command: python3 -m unittest · Expected / actual: n/a · Repro: n/a

The owner approved spec v1. Please map and dispatch the units.

\`\`\`
You are the Architect. Read .team/roles/architect.md and act on issue #1.
\`\`\`

$(event '{"from":"product-manager","to":"architect","kind":"handoff"}')"
```

# Expected
Arjun creates an issue and a `team/<issue>-<slug>` branch per unit, commits an acceptance map in `work/<issue>/` covering every requirement, rejection and boundary (no trailing newline, empty file, both flags), orders unit 2 after unit 1, and hands the first unit on. He writes no implementation code.

# Checks
- event from=architect
- file team/* work/*
- same * wc.py
- main-unchanged

# Rubric
- Does the acceptance map cover R4 (both flags rejected) and the empty-file and no-trailing-newline boundaries?
- Is unit 2 ordered after unit 1?
