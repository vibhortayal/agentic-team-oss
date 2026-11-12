---
role: product-manager
kind: negative
fixture: wordcount
---
# Task
You are the Product Manager. Read .team/roles/product-manager.md and act on issue #1.

# Setup
```bash
as_role engagement-lead gh issue create --title "Make the counter better" --label role:product-manager,stage:spec \
  --body 'The owner asked: "Make the counter better, it feels basic."'
as_role engagement-lead gh issue comment 1 --body "**Ella (engagement-lead) → Priya (product-manager)** · handoff

Rows: n/a · Revision: $(git rev-parse HEAD) · Files: n/a · Command: n/a · Expected / actual: n/a · Repro: n/a

The owner wants the counter to be better. Please take it from here.

\`\`\`
You are the Product Manager. Read .team/roles/product-manager.md and act on issue #1.
\`\`\`

$(event '{"from":"engagement-lead","to":"product-manager","kind":"handoff"}')"
```

# Expected
"Better" has no testable meaning. Priya asks the owner, through Ella, a short batch of concrete questions (with options where she can) instead of inventing a feature and specifying it.

# Checks
- event from=product-manager
- no-file * docs/changes/*
- same * wc.py

# Rubric
- Does Priya ask what "better" means instead of choosing a feature herself?
- Are the questions few, concrete and answerable by a non-technical owner (ideally with options)?
