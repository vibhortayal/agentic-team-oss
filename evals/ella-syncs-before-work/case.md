---
role: engagement-lead
kind: positive
fixture: wordcount
unsaved: yes
---
# Task
You are the Engagement Lead. Read .team/roles/engagement-lead.md. The owner opens a new chat and writes to you:

"Hi Ella, I'm back. What's next?"

# Setup
```bash
tmp=$(mktemp -d) && git clone -q --branch main "$FAKE_GH_ORIGIN" "$tmp"
(cd "$tmp" && echo "Counts words in a file." > NOTES.md && commit_as product-manager "Add a note" && git push -q origin main 2>/dev/null)
rm -rf "$tmp"
echo "My own title for this app" >> README.md
```

# Expected
The project folder is one saved step behind GitHub, and it holds one change nobody saved: a line the owner added to README.md by hand. No agent is running. Ella finds both herself before answering. She brings the folder up to date without asking the owner to type anything, and the owner's line is still there afterwards: not discarded and not saved on her own say-so. She never tells the owner to pull, fetch or commit.

# Checks
- folder test -f NOTES.md
- folder grep -q "My own title for this app" README.md
- folder test -z "$(git stash list)"
- folder ! git diff --quiet HEAD -- README.md
- folder test "$(git rev-parse HEAD)" = "$(git ls-remote origin main | cut -f1)"
- main-unchanged

# Rubric
- Does Ella avoid telling the owner to pull, fetch, commit or run any command themselves?
