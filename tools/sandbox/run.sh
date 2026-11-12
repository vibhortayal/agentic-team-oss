#!/usr/bin/env bash
# Run eval cases inside Docker, so agents with full permissions only touch a throwaway container.
#   tools/sandbox/run.sh <adapter> --max-usd <cap> [other run_evals.py options] <case...|--all>
# Results land in evals/runs/<timestamp>/ (report.md, ledger.csv, each session's prompt and log).
set -euo pipefail
root="$(cd "$(dirname "$0")/../.." && pwd)"
adapter="${1:?usage: run.sh <adapter> --max-usd <cap> <case...|--all>}"; shift
agent="$root/adapters/$adapter/eval-agent.sh"
[ -f "$agent" ] || { echo "no $agent" >&2; exit 1; }
tag="agentic-team-sandbox:$adapter"
docker build -q -t "$tag" --build-arg AGENT_INSTALL="$(bash "$agent" --install)" "$root/tools/sandbox" >/dev/null
envs=()
for v in $(bash "$agent" --env) HTTPS_PROXY HTTP_PROXY NO_PROXY; do [ -n "${!v:-}" ] && envs+=(-e "$v"); done
mkdir -p "$root/evals/runs"
exec docker run --rm --user "$(id -u):$(id -g)" "${envs[@]}" \
  -v "$root:/team:ro" -v "$root/evals/runs:/runs" "$tag" \
  --adapter "$adapter" --out "/runs/$(date +%Y%m%d-%H%M%S)" "$@"
