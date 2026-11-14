#!/usr/bin/env bash
# See whether a newer team is out, and install it into a project.
#
#   adapters/update.sh check <project-dir>   # prints "up to date" or "newer: <old> -> <new>" and what changed
#   adapters/update.sh apply <project-dir>   # updates this copy of the team, then reinstalls it into the project
#
# Run from the shared copy of the team (usually ~/agentic-team). "What changed" is
# one line per merged pull request since the project's installed version, for Ella
# to retell in plain words. apply picks the Claude Code installer when the project
# has .claude/agents/, else the generic one. It never commits: Ella does that on the
# owner's yes (the .team/ folder is a gate path).
set -euo pipefail

team_root="$(cd "$(dirname "$0")/.." && pwd)"
mode="${1:-}"
project="${2:-}"
case "$mode" in check|apply) ;; *) echo "usage: update.sh check|apply <project-dir>" >&2; exit 2 ;; esac
[ -d "$project" ] || { echo "no such directory: $project" >&2; exit 2; }

installed="$(cat "$project/.team/VERSION" 2>/dev/null || echo unknown)"
git -C "$team_root" fetch --quiet --tags origin main
latest="$(git -C "$team_root" describe --tags --always origin/main)"

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
