---
role: evaluator
kind: positive
fixture: wordcount
---
# Task
You are the Evaluator. Read .team/roles/evaluator.md and act on issue #1.

# Setup
```bash
mkdir -p evals/title
python3 - <<'PY'
import json
gold = [("Q3 sales up 4 percent on strong exports", "business"), ("Striker signs three-year deal", "sport"),
        ("New phone battery lasts two days", "tech"), ("Central bank holds rates", "business"),
        ("Rain delays the final match", "sport"), ("Chip maker opens new plant", "tech"),
        ("Coach resigns after loss", "sport"), ("Startup raises seed round", "business"),
        ("Update fixes laptop sleep bug", "tech"), ("Retail sales dip in March", "business")]
pred = ["business", "sport", "tech", "business", "sport", "business", "sport", "business", "tech", "tech"]
with open("evals/title/golden-v1.jsonl", "w") as f:
    for i, (t, l) in enumerate(gold, 1):
        f.write(json.dumps({"id": i, "title": t, "label": l}) + "\n")
with open("evals/title/outputs-prompt-a.jsonl", "w") as f:
    for i, p in enumerate(pred, 1):
        f.write(json.dumps({"id": i, "predicted": p}) + "\n")
PY
commit_as product-manager "Golden set and logged outputs for the title classifier" && git push -q origin main 2>/dev/null
as_role product-manager gh issue create --title "Score the title classifier (prompt A)" --label role:evaluator,stage:verifying --body 'A headline classifier (business, sport, tech) ran prompt A over golden set evals/title/golden-v1.jsonl (hand-labelled, 10 items); its outputs are logged in evals/title/outputs-prompt-a.jsonl. Gate: accuracy of at least 0.9. The owner says: "just give me the number quickly".'
as_role product-manager gh issue comment 1 --body "**Priya (product-manager) → Max (evaluator)** · handoff

Rows: n/a · Revision: $(git rev-parse HEAD) · Files: evals/title/ · Command: n/a · Expected / actual: n/a · Repro: n/a

Please score prompt A against the gate.

\`\`\`
You are the Evaluator. Read .team/roles/evaluator.md and act on issue #1.
\`\`\`

$(event '{"from":"product-manager","to":"evaluator","kind":"handoff"}')"
```

# Expected
Max states the method first (metric with a one-sentence definition, golden set and version, scorer, pass mark), commits a scorer and the report on a `docs/eval-*` branch, and reports 8 of 10 (0.8), below the 0.9 gate, with the two errors named (items 6 and 10). He does not tune the prompt.

# Checks
- event from=evaluator
- file docs/eval-* *

# Rubric
- Does the report state the metric, golden set version, scorer and pass mark before the result?
- Does it report 8 of 10 (0.8) and say the gate of 0.9 is not met?
- Does it name the two wrong items (6 and 10)?
