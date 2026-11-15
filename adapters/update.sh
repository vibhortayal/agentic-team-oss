#!/usr/bin/env bash
# See whether a newer team is out, and install it into a project.
#
#   adapters/update.sh check <project-dir>   # prints "up to date" or "newer: <old> -> <new>" and what changed
#   adapters/update.sh apply <project-dir>   # updates this copy of the team, reinstalls it into the project,
#                                            # and refreshes the project's safety checks if it has them
#   adapters/update.sh add <project-dir>     # adds the project to this computer's project list
#   adapters/update.sh all                   # one line per listed project: up to date, or newer
#
# Run from the shared copy of the team (usually ~/agentic-team). "What changed" is
# one line per merged pull request since the project's installed version, for Ella
# to retell in plain words. apply picks the Claude Code installer when the project
# has .claude/agents/, else the generic one. It never commits: Ella does that on the
# owner's yes (the .team/ folder is a gate path).
#
# The project list is projects.txt in the shared copy (not tracked by Git): one
# folder per line. check, apply and add put the project on it; all drops folders
# that are gone or no longer have the team, so "update the team" can reach every
# project on this computer from any one of them.
set -euo pipefail

team_root="$(cd "$(dirname "$0")/.." && pwd)"
list="$team_root/projects.txt"
mode="${1:-}"
project="${2:-}"
case "$mode" in
  check|apply|add) [ -d "$project" ] || { echo "no such directory: $project" >&2; exit 2; } ;;
  all) ;;
  *) echo "usage: update.sh check|apply|add <project-dir>, or update.sh all" >&2; exit 2 ;;
esac

remember() {
  local dir
  dir="$(cd "$1" && pwd)"
  touch "$list"
  grep -qxF "$dir" "$list" || echo "$dir" >> "$list"
}

if [ "$mode" = add ]; then
  remember "$project"
  echo "listed $(cd "$project" && pwd)"
  exit 0
fi

git -C "$team_root" fetch --quiet --tags origin main
latest="$(git -C "$team_root" describe --tags --always origin/main)"

if [ "$mode" = all ]; then
  [ -f "$list" ] || { echo "no projects listed yet"; exit 0; }
  kept="$(mktemp)"
  while IFS= read -r dir; do
    [ -n "$dir" ] && [ -f "$dir/.team/VERSION" ] || continue
    echo "$dir" >> "$kept"
    have="$(cat "$dir/.team/VERSION")"
    if [ "$have" = "$latest" ]; then echo "$dir: up to date ($have)"; else echo "$dir: newer: $have -> $latest"; fi
  done < "$list"
  mv "$kept" "$list"
  exit 0
fi

remember "$project"
installed="$(cat "$project/.team/VERSION" 2>/dev/null || echo unknown)"
if [ "$installed" = "$latest" ]; then
  echo "up to date ($installed)"
  exit 0
fi

echo "newer: $installed -> $latest"
echo "what changed:"
if [ "$installed" != unknown ] && git -C "$team_root" rev-parse --quiet --verify "$installed^{commit}" >/dev/null; then
  # A merge commit's body is the pull request's title.
  git -C "$team_root" log --merges --format='- %b' "$installed..origin/main" | sed '/^- *$/d' | head -20
else
  echo "- (the installed version is unknown, so the list can't be worked out)"
fi

[ "$mode" = apply ] || exit 0

git -C "$team_root" pull --quiet --ff-only origin main
if [ -d "$project/.claude/agents" ]; then
  bash "$team_root/adapters/claude-code/install.sh" "$project"
else
  bash "$team_root/adapters/generic/install.sh" "$project"
fi
bash "$team_root/adapters/refresh-gates.sh" "$project"
