#!/usr/bin/env bash
# Install the team into a project for Claude Code.
#
#   adapters/claude-code/install.sh <project-dir>
#
# Runs the generic installer (.team/ and AGENTS.md), then writes each role as a
# Claude Code subagent in <project-dir>/.claude/agents/ (agents.sh: models
# follow the working style in TEAM.md), and links every skill into
# .claude/skills/. Writes a one-line CLAUDE.md that imports AGENTS.md, or adds
# the import to an existing CLAUDE.md that lacks it.
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
team_root="$(cd "$here/../.." && pwd)"
project="${1:?usage: install.sh <project-dir>}"

bash "$team_root/adapters/generic/install.sh" "$@"

rm -rf "$project/.claude/team"   # older installs kept a copy here; .team/ replaces it
bash "$here/agents.sh" "$project"

bash "$team_root/adapters/generic/link-skills.sh" "$project" .claude/skills

if [ ! -f "$project/CLAUDE.md" ]; then
  echo "@AGENTS.md" > "$project/CLAUDE.md"
  echo "wrote CLAUDE.md (imports AGENTS.md)"
elif ! grep -qx "@AGENTS.md" "$project/CLAUDE.md"; then
  printf '\n@AGENTS.md\n' >> "$project/CLAUDE.md"
  echo "added @AGENTS.md to the existing CLAUDE.md"
fi
