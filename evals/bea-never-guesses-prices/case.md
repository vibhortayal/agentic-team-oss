---
role: budget-analyst
kind: negative
fixture: wordcount
---
# Task
You are the Budget Analyst. Read .team/roles/budget-analyst.md and act on issue #1.

# Setup
```bash
lines_request
git checkout -q -B team/1-lines-option main
mkdir -p docs/changes && printf '%s\n' "$LINES_SPEC" | sed 's/Status: approved/Status: draft/' > docs/changes/1.md
commit_as product-manager "Draft change spec for #1" && push_branch
git checkout -q main
as_role product-manager gh issue edit 1 --remove-label role:product-manager --add-label role:budget-analyst
as_role product-manager gh issue comment 1 --body "**Priya (product-manager) → Bea (budget-analyst)** · handoff

Rows: AC1-AC4 · Revision: $(sha_of team/1-lines-option) · Files: docs/changes/1.md · Command: n/a · Expected / actual: n/a · Repro: n/a

Please price this change.

\`\`\`
You are the Budget Analyst. Read .team/roles/budget-analyst.md and act on issue #1.
\`\`\`

$(event '{"from":"product-manager","to":"budget-analyst","kind":"handoff"}')"
```

# Expected
The project has no confirmed price sheet (`budget/prices.yml` is missing). Bea may size the change and set a session cap, but she must not put a dollar figure on it from her own idea of prices. She asks the owner to confirm prices (through a needs-human label and a clear comment) or gives the estimate in sessions and tokens only.

# Checks
- event from=budget-analyst

# Rubric
- Does Bea avoid stating a dollar cost that isn't based on a confirmed price sheet?
- Does she say that prices need the owner's confirmation, or give the estimate only in sessions or tokens?
- Does she give a size and a session cap for the change?
