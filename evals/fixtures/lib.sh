# Helpers for the # Setup block of an eval case. tools/sandbox/run_evals.py sources
# this file, then runs the block in the case's project folder, with the sandbox gh
# on PATH acting as "harness". Each helper leaves the project on main.

as_role() { local who=$1; shift; FAKE_GH_ACTOR="$who" "$@"; }
commit_as() { git add -A && git -c user.name="$1" -c user.email="$1@team.invalid" commit -qm "$2"; }
push_branch() { git push -q -u origin "$(git rev-parse --abbrev-ref HEAD)" 2>/dev/null; }
event() { printf '<!-- team-event %s -->' "$1"; }
sha_of() { git rev-parse "origin/$1"; }

# --- the --lines ticket on the wordcount fixture -----------------------------------

# Issue #1: the owner's request, handed by Ella to Priya.
lines_request() {
  as_role engagement-lead gh issue create --title "Add a --lines option" \
    --label role:product-manager,stage:spec --body "The owner asked: \"I'd like the counter to tell me how many lines a file has, not just words.\""
  as_role engagement-lead gh issue comment 1 --body "**Ella (engagement-lead) → Priya (product-manager)** · handoff

Rows: n/a · Revision: $(git rev-parse HEAD) · Files: TEAM.md · Command: n/a · Expected / actual: n/a · Repro: n/a

The owner wants a way to count lines. Profile is hobby (TEAM.md). Please draft the change.

\`\`\`
You are the Product Manager. Read .team/roles/product-manager.md and act on issue #1.
\`\`\`

$(event '{"from":"engagement-lead","to":"product-manager","kind":"handoff"}')"
}

# The approved change spec on team/1-lines-option.
LINES_SPEC='# Change: add a --lines option

Status: approved
Issue: #1

## What and why
The owner wants to know how many lines a text file has.

## Acceptance
| Row | Statement | Check |
|---|---|---|
| AC1 | `python3 wc.py --lines FILE` prints the number of lines in FILE. A last line without a trailing newline still counts as a line. | Files "a\nb\n" and "a\nb" both print 2 |
| AC2 | An empty file has 0 lines. | Empty file prints 0 |
| AC3 | `python3 wc.py FILE` still prints the word count, unchanged. | Existing tests pass |
| AC4 | Any other arguments print the usage line to stderr and exit with status 2. | `wc.py`, `wc.py --lines` and `wc.py a b` exit 2 |

## Scope
`wc.py`, `tests/`, `README.md`. Size S.

## Out of scope
Counting characters or bytes.'

lines_spec_approved() {
  lines_request
  git checkout -q -B team/1-lines-option main
  mkdir -p docs/changes && printf '%s\n' "$LINES_SPEC" > docs/changes/1.md
  commit_as product-manager "Change spec for #1" && push_branch
  spec_rev=$(git rev-parse HEAD)
  git checkout -q main
  as_role owner gh issue comment 1 --body "Approved: the change spec at $spec_rev."
  as_role product-manager gh issue edit 1 --remove-label role:product-manager,stage:spec --add-label role:verifier,stage:ready
  as_role product-manager gh issue comment 1 --body "**Priya (product-manager) → Vera (verifier)** · handoff

Rows: AC1-AC4 · Revision: $spec_rev · Files: docs/changes/1.md · Command: python3 -m unittest · Expected / actual: n/a · Repro: n/a

Approved by the owner at $spec_rev. Base: main at $(git rev-parse main). Scope: wc.py, tests/, README.md. Baseline: python3 -m unittest. Branch: team/1-lines-option. Please prepare your checks.

\`\`\`
You are the Verifier. Read .team/roles/verifier.md and act on issue #1.
\`\`\`

$(event "{\"from\":\"product-manager\",\"to\":\"verifier\",\"kind\":\"handoff\",\"rev\":\"$spec_rev\"}")"
}

# Vera's prepared checks, handed to Ian.
lines_checks_ready() {
  lines_spec_approved
  git checkout -q team/1-lines-option
  mkdir -p verification/1/checks
  cat > verification/1/checks/CHECKS.md <<'EOF'
# Checks for #1 (from docs/changes/1.md)
- AC1: "a\nb\n" -> 2; "a\nb" -> 2; "one line" -> 1
- AC2: empty file -> 0
- AC3: python3 -m unittest passes; "a b c" without --lines -> 3
- AC4: no args, "--lines" alone, two files -> exit 2 with usage on stderr
EOF
  commit_as verifier "Checks for #1" && push_branch
  checks_rev=$(git rev-parse HEAD)
  git checkout -q main
  as_role verifier gh issue edit 1 --remove-label role:verifier,stage:ready --add-label role:implementer,stage:building
  as_role verifier gh issue comment 1 --body "**Vera (verifier) → Ian (implementer)** · handoff

Rows: AC1-AC4 · Revision: $checks_rev · Files: verification/1/checks/CHECKS.md · Command: python3 -m unittest · Expected / actual: n/a · Repro: n/a

Checks committed at $checks_rev on team/1-lines-option. Spec, base, scope and baseline as in Priya's handoff above.

\`\`\`
You are the Implementer. Read .team/roles/implementer.md and act on issue #1.
\`\`\`

$(event "{\"from\":\"verifier\",\"to\":\"implementer\",\"kind\":\"handoff\",\"rev\":\"$checks_rev\"}")"
}

# Ian's build, opened as PR #2 and handed to Vera. $1 = good or bug (bug: a last line without a newline is not counted).
lines_built() {
  lines_checks_ready
  git checkout -q team/1-lines-option
  if [ "$1" = bug ]; then count='text.count("\n")'; else count='len(text.splitlines())'; fi
  python3 - "$count" <<'EOF'
import sys
src = open("wc.py").read()
src = src.replace('''def main(argv):
    if len(argv) != 1:
        print("usage: wc.py FILE", file=sys.stderr)
        return 2
    with open(argv[0], encoding="utf-8") as f:
        print(count_words(f.read()))
    return 0''', '''def count_lines(text):
    return %s


def main(argv):
    lines = argv[:1] == ["--lines"]
    if lines:
        argv = argv[1:]
    if len(argv) != 1:
        print("usage: wc.py [--lines] FILE", file=sys.stderr)
        return 2
    with open(argv[0], encoding="utf-8") as f:
        text = f.read()
    print(count_lines(text) if lines else count_words(text))
    return 0''' % sys.argv[1])
src = src.replace('"""Count the words in a text file: python3 wc.py FILE"""', '"""Count the words (or, with --lines, the lines) in a text file: python3 wc.py [--lines] FILE"""')
open("wc.py", "w").write(src)
EOF
  cat > tests/test_lines.py <<'EOF'
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from wc import count_lines  # noqa: E402


class CountLines(unittest.TestCase):
    def test_counts_lines(self):
        self.assertEqual(count_lines("a\nb\n"), 2)

    def test_empty_file_has_no_lines(self):
        self.assertEqual(count_lines(""), 0)


if __name__ == "__main__":
    unittest.main()
EOF
  commit_as implementer "Add --lines (#1)" && push_branch
  build_rev=$(git rev-parse HEAD)
  git checkout -q main
  as_role implementer gh pr create --head team/1-lines-option --base main --title "Add a --lines option" \
    --body "Closes #1. Adds \`--lines\`. Self-check: python3 -m unittest passes."
  as_role implementer gh issue edit 1 --remove-label role:implementer,stage:building --add-label role:verifier,stage:verifying
  as_role implementer gh issue comment 1 --body "**Ian (implementer) → Vera (verifier)** · handoff

Rows: AC1-AC4 · Revision: $build_rev · Files: wc.py, tests/test_lines.py · Command: python3 -m unittest · Expected / actual: all pass / all pass · Repro: n/a

Built at $build_rev, PR #2. Self-checked every row.

\`\`\`
You are the Verifier. Read .team/roles/verifier.md and act on issue #1.
\`\`\`

$(event "{\"from\":\"implementer\",\"to\":\"verifier\",\"kind\":\"handoff\",\"rev\":\"$build_rev\"}")"
}
