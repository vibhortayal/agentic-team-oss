#!/usr/bin/env bash
# Install the team into a project for any agent tool.
#
#   adapters/generic/install.sh <project-dir>
#
# Copies every role, the principles, playbooks, templates, docs and the GitHub
# label script into <project-dir>/.team/, and writes <project-dir>/AGENTS.md
# from the template if the project has none. Every agent tool that reads
# AGENTS.md (or can be told to read a file) can then play any role by reading
# .team/roles/<role>.md. All roles are always installed so every link resolves;
# a project hires roles in its TEAM.md, not by installing a subset.
# The new copy is built in a temporary folder and swapped in only when complete,
# so a failed run leaves the previous install untouched.
set -euo pipefail

team_root="$(cd "$(dirname "$0")/../.." && pwd)"
project="${1:?usage: install.sh <project-dir>}"
[ "$#" -le 1 ] || { echo "install.sh takes only the project folder; hire roles in TEAM.md" >&2; exit 1; }
[ -d "$project" ] || { echo "no such directory: $project" >&2; exit 1; }

dest="$project/.team"
tmp="$(mktemp -d "$project/.team.new.XXXXXX")"
trap 'rm -rf "$tmp"' EXIT

mkdir -p "$tmp/roles" "$tmp/adapters"
cp "$team_root/principles.md" "$tmp/"
cp -R "$team_root/playbooks" "$team_root/templates" "$team_root/docs" "$tmp/"
cp -R "$team_root/adapters/github" "$tmp/adapters/"
for f in "$team_root"/roles/*.md; do
  [ "$(basename "$f")" = "_template.md" ] && continue
  cp "$f" "$tmp/roles/"
  echo "installed $(basename "$f" .md)"
done

version="$(git -C "$team_root" describe --tags --always 2>/dev/null || echo unknown)"
echo "$version" > "$tmp/VERSION"

rm -rf "$dest"
mv "$tmp" "$dest"
trap - EXIT

if [ ! -f "$project/AGENTS.md" ]; then
  cp "$team_root/templates/AGENTS.md" "$project/AGENTS.md"
  echo "wrote AGENTS.md (fill in the project lines)"
else
  echo "AGENTS.md exists; left as is (check it points at .team/)"
fi

echo "team version $version -> $dest (record it in TEAM.md)"
