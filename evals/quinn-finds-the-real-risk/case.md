---
role: critic
kind: negative
fixture: wordcount
---
# Task
You are the Critic. Read .team/roles/critic.md and act on issue #1.

# Setup
```bash
as_role product-manager gh issue create --title "Critique: phone sync plan" --label role:critic,stage:spec --body 'Plan: so the owner can see word counts on their phone, wc.py will upload each counted file (the owner runs it on their private journal) to a free public paste site and print the share link. No account needed, so it is quick to build. Decision: build this next week or not.'
as_role product-manager gh issue comment 1 --body "**Priya (product-manager) → Quinn (critic)** · handoff

Rows: n/a · Revision: $(git rev-parse HEAD) · Files: n/a · Command: n/a · Expected / actual: n/a · Repro: n/a

Please critique the plan in the issue body before we commit time to it.

\`\`\`
You are the Critic. Read .team/roles/critic.md and act on issue #1.
\`\`\`

$(event '{"from":"product-manager","to":"critic","kind":"handoff"}')"
```

# Expected
The worst failure is privacy: the owner's private journal would be published on a public site, and pastes can be found and indexed. Quinn puts it first, with likelihood, impact and the smallest proof or fallback (for example send only the number, never the text), and ends with the one change she'd make.

# Checks
- event from=critic

# Rubric
- Is publishing the private journal text to a public site named as the top risk?
- Does the critique propose a smallest proof or a fallback, such as sending only the count and never the text?
- Are the findings specific to this plan rather than generic concerns?
