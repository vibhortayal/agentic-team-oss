#!/usr/bin/env bash
# Refresh a project's safety checks (the foundation kit) from this copy of the team.
#
#   adapters/refresh-gates.sh <project-dir>
#
# update.sh apply runs this after the installer, so "update the team" also updates the
# checks. Only a project that already has the kit is touched, and only the kit's own
# files: zones.yml and CODEOWNERS hold the project's choices and are never replaced.
# It never commits: Ella does that on the owner's yes (these are gate files).
set -euo pipefail

team_root="$(cd "$(dirname "$0")/.." && pwd)"
project="${1:?usage: refresh-gates.sh <project-dir>}"
kit="$team_root/templates/foundation"

if [ ! -f "$project/.github/team/team_gates.py" ]; then
  echo "safety checks: not installed in this project, nothing to refresh"
  exit 0
fi

changed=0
while read -r src dst; do
  if ! cmp -s "$kit/$src" "$project/$dst"; then
    mkdir -p "$(dirname "$project/$dst")"
    cp "$kit/$src" "$project/$dst"
    echo "safety checks: updated $dst"
    changed=1
  fi
done <<'FILES'
scripts/team_gates.py .github/team/team_gates.py
scripts/run-checks.sh .github/team/run-checks.sh
verdict.schema.json .github/team/verdict.schema.json
workflows/team-gates.yml .github/workflows/team-gates.yml
workflows/team-checks.yml .github/workflows/team-checks.yml
pull_request_template.md .github/pull_request_template.md
ISSUE_TEMPLATE/ticket.md .github/ISSUE_TEMPLATE/ticket.md
FILES
[ "$changed" = 1 ] || echo "safety checks: already current"
