#!/usr/bin/env bash
# Write the team's Claude Code subagents from the roles installed in a project.
#
#   adapters/claude-code/agents.sh <project-dir>
#
# Reads <project-dir>/.team/roles/ (so the team version doesn't change) and the
# working style in <project-dir>/TEAM.md (thrifty, balanced or fast; balanced if
# it isn't set), and writes <project-dir>/.claude/agents/<role>.md, mapping the
# neutral frontmatter: the style's tier -> model, capabilities -> tools,
# skills -> a skills list (Claude Code preloads them). A role's tier is its
# balanced tier; thrifty-tier and fast-tier override it for those styles. The
# neutral memory: field is dropped (a team convention, not a Claude Code setting).
# It also sets "model" in <project-dir>/.claude/settings.json to the Engagement
# Lead's model for the style, so the next main session (Ella) starts on it; other
# settings there are kept. install.sh runs this; run it alone after the owner changes the working style.
set -euo pipefail

project="${1:?usage: agents.sh <project-dir>}"
[ -d "$project/.team/roles" ] || { echo "no team installed in $project" >&2; exit 1; }

style=balanced
if [ -f "$project/TEAM.md" ]; then
  picked="$(sed -n 's/.*\*\*Working style:\*\* *`\([a-z]*\)`.*/\1/p' "$project/TEAM.md" | head -1)"
  case "$picked" in thrifty|balanced|fast) style="$picked" ;; esac
fi

mkdir -p "$project/.claude/agents"
for src in "$project"/.team/roles/*.md; do
  role="$(basename "$src" .md)"
  # Role links are relative to .team/roles/; from .claude/agents/ that is ../../.team/
  awk -v style="$style" '
    function model(t) { return (t == "deep") ? "opus" : (t == "fast") ? "haiku" : "sonnet" }
    BEGIN { fm = 0 }
    /^---$/ {
      fm++
      if (fm == 2) {
        t = tier
        if (style == "thrifty" && thrifty != "") t = thrifty
        if (style == "fast" && fast != "") t = fast
        print "model: " model(t)
      }
      print; next
    }
    fm == 1 && /^memory:/ { next }
    fm == 1 && /^tier:/ { tier = $2; next }
    fm == 1 && /^thrifty-tier:/ { thrifty = $2; next }
    fm == 1 && /^fast-tier:/ { fast = $2; next }
    fm == 1 && /^skills:/ {
      line = $0; sub(/^skills:[ ]*/, "", line)
      n = split(line, s, /[ ,]+/); print "skills:"
      for (i = 1; i <= n; i++) if (s[i] != "") print "  - " s[i]
      next
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
# Ella is the main session, not a subagent: her model is the project's default model.
lead="$(sed -n 's/^model: //p' "$project/.claude/agents/engagement-lead.md" | head -1)"
python3 - "$project/.claude/settings.json" "$lead" <<'PY'
import json, os, sys
path, model = sys.argv[1], sys.argv[2]
data = {}
if os.path.exists(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
data["model"] = model
with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
    f.write("\n")
PY
echo "Claude Code subagents ($style working style) -> $project/.claude/agents; new chats start on $lead"
