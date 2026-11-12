#!/usr/bin/env bash
# Link every skill in <project-dir>/.team/skills/ into a tool's skills folder.
#
#   adapters/generic/link-skills.sh <project-dir> <folder relative to the project>
#
# Each link is relative (../../.team/skills/<name>), so it survives a clone.
# Links that point into .team/skills/ but whose skill is gone are removed;
# anything else in the folder (the project's own skills) is left alone.
set -euo pipefail

project="${1:?usage: link-skills.sh <project-dir> <skills-folder>}"
folder="${2:?usage: link-skills.sh <project-dir> <skills-folder>}"
dir="$project/$folder"
up="$(echo "$folder" | sed -E 's#[^/]+#..#g')"
mkdir -p "$dir"

for link in "$dir"/*; do
  [ -L "$link" ] || continue
  case "$(readlink "$link")" in
    "$up/.team/skills/"*) [ -e "$link" ] || rm "$link" ;;
  esac
done

for skill in "$project"/.team/skills/*/; do
  name="$(basename "$skill")"
  target="$up/.team/skills/$name"
  if [ -L "$dir/$name" ] || [ ! -e "$dir/$name" ]; then
    ln -sfn "$target" "$dir/$name"
  else
    echo "left $folder/$name alone: the project has its own skill by that name" >&2
  fi
done
echo "skills -> $dir"
