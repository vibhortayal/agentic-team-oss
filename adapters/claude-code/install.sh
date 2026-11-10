#!/usr/bin/env bash
# Install the team into a project for Claude Code.
#
#   adapters/claude-code/install.sh <project-dir>
#
# Runs the generic installer (.team/ and AGENTS.md), then writes each role as a
# Claude Code subagent in <project-dir>/.claude/agents/, mapping the neutral
# frontmatter: tier -> model, capabilities -> tools. Writes a one-line
# CLAUDE.md that imports AGENTS.md, or adds the import to an existing
# CLAUDE.md that lacks it. The neutral memory: field is dropped (it is a
# team convention, not a Claude Code setting).
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
team_root="$(cd "$here/../.." && pwd)"
project="${1:?usage: install.sh <project-dir>}"

bash "$team_root/adapters/generic/install.sh" "$@"

mkdir -p "$project/.claude/agents"
rm -rf "$project/.claude/team"   # older installs kept a copy here; .team/ replaces it

for src in "$project"/.team/roles/*.md; do
  role="$(basename "$src" .md)"
  # Role links are relative to .team/roles/; from .claude/agents/ that is ../../.team/
  awk '
    BEGIN { fm = 0 }
    /^---$/ { fm++; print; next }
    fm == 1 && /^memory:/ { next }
    fm == 1 && /^tier:/ {
      t = $2
      m = (t == "deep") ? "opus" : (t == "fast") ? "haiku" : "sonnet"
      print "model: " m; next
    }
    fm == 1 && /^capabilities:/ {
      line = $0; sub(/^capabilities:[ ]*/, "", line)
      if (line == "all") next          # omit tools: inherit everything
      n = split(line, caps, /[ ,]+/); out = ""
      for (i = 1; i <= n; i++) {
        c = caps[i]
        if (c == "read") add = "Read"
        else if (c == "search") add = "Grep, Glob"
        else if (c == "web") add = "WebSearch, WebFetch"
        else if (c == "write") add = "Write"
        else if (c == "edit") add = "Edit"
        else if (c == "shell") add = "Bash"
        else continue
        out = (out == "") ? add : out ", " add
      }
      print "tools: " out; next
    }
    { gsub(/\]\(\.\.\//, "](../../.team/"); print }
  ' "$src" > "$project/.claude/agents/$role.md"
done

if [ ! -f "$project/CLAUDE.md" ]; then
  echo "@AGENTS.md" > "$project/CLAUDE.md"
  echo "wrote CLAUDE.md (imports AGENTS.md)"
elif ! grep -qx "@AGENTS.md" "$project/CLAUDE.md"; then
  printf '\n@AGENTS.md\n' >> "$project/CLAUDE.md"
  echo "added @AGENTS.md to the existing CLAUDE.md"
fi
echo "Claude Code subagents -> $project/.claude/agents"
