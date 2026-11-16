#!/usr/bin/env bash
# Install the team into a project for Claude Code.
#
#   adapters/claude-code/install.sh <project-dir>
#
# Runs the generic installer (.team/ and AGENTS.md), then writes each role as a
# Claude Code subagent in <project-dir>/.claude/agents/ (agents.sh: models
# follow the working style in TEAM.md), and links every skill into
# .claude/skills/. Writes a one-line CLAUDE.md that imports AGENTS.md, or adds
# the import to an existing CLAUDE.md that lacks it. Adds the team's guard rails
# (guard-rails.json: never read secret files, force-push, delete a repo or throw
# away unsaved work) to permissions.deny in .claude/settings.json, keeping the rest.
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
team_root="$(cd "$here/../.." && pwd)"
project="${1:?usage: install.sh <project-dir>}"

bash "$team_root/adapters/generic/install.sh" "$@"

rm -rf "$project/.claude/team"   # older installs kept a copy here; .team/ replaces it
bash "$here/agents.sh" "$project"

bash "$team_root/adapters/generic/link-skills.sh" "$project" .claude/skills

# Guard rails: things no agent may do, whatever it reads (guard-rails.json). Added to
# permissions.deny in .claude/settings.json; everything else there is kept.
python3 - "$project/.claude/settings.json" "$here/guard-rails.json" <<'PY'
import json, os, sys
path, rails = sys.argv[1], sys.argv[2]
data = {}
if os.path.exists(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
with open(rails, encoding="utf-8") as f:
    want = json.load(f)["deny"]
deny = data.setdefault("permissions", {}).setdefault("deny", [])
added = [r for r in want if r not in deny]
deny += added
with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
    f.write("\n")
print("guard rails: %d added to .claude/settings.json" % len(added) if added else "guard rails: already in place")
PY

if [ ! -f "$project/CLAUDE.md" ]; then
  echo "@AGENTS.md" > "$project/CLAUDE.md"
  echo "wrote CLAUDE.md (imports AGENTS.md)"
elif ! grep -qx "@AGENTS.md" "$project/CLAUDE.md"; then
  printf '\n@AGENTS.md\n' >> "$project/CLAUDE.md"
  echo "added @AGENTS.md to the existing CLAUDE.md"
fi
