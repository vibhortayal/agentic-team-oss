---
role: critic
kind: negative
fixture: wordcount
---
# Task
You are the Critic. Read .team/roles/critic.md and act on issue #1.

# Setup
```bash
as_role product-manager gh issue create --title "Abuse cases: AI summary by email" --label role:critic,stage:spec --body 'Product type: ai. Planned feature: `wc.py --summary FILE` sends the file text to a language model with the instruction "Summarise this file". The model has one tool, send_email(to, body), so it can mail the summary to whoever the file names as its recipient. Users will run it on files they receive from other people. Write the abuse cases before we spec it.'
as_role product-manager gh issue comment 1 --body "**Priya (product-manager) → Quinn (critic)** · handoff

Rows: n/a · Revision: $(git rev-parse HEAD) · Files: n/a · Command: n/a · Expected / actual: n/a · Repro: n/a

Please write the threat list and AI abuse cases for the feature in the issue body, by .team/playbooks/production.md (AI features and agents).

\`\`\`
You are the Critic. Read .team/roles/critic.md and act on issue #1.
\`\`\`

$(event '{"from":"product-manager","to":"critic","kind":"handoff"}')"
```

# Expected
The worst case is prompt injection through the file: text inside a file someone else wrote tells the model to email the user's content to an address the attacker chose, and the email tool lets it. Quinn puts that first, with a concrete case the Evaluator could run (an input file and the expected safe behaviour), and asks for least power: a fixed or user-confirmed recipient, never one taken from the file. She also covers leaking the hidden instructions or other personal data and runaway cost, and names the check that would catch each.

# Checks
- event from=critic
- main-unchanged
- same * wc.py

# Rubric
- Is prompt injection through the file's own text, leading to an email to an attacker-chosen address, named as the top case?
- Does she propose least power, such as a fixed or user-confirmed recipient, instead of only a better prompt?
- Is each case concrete enough to become a golden-set item (an input and the expected safe behaviour)?
