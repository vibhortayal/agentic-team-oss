#!/usr/bin/env bash
# One sandbox eval session with Claude Code, for tools/sandbox/run_evals.py:
#   eval-agent.sh <workdir> <prompt-file> <tier> <max-usd> <max-turns> <result-json>
#   eval-agent.sh --install   the command that installs the tool in the sandbox image
#   eval-agent.sh --env       the environment variables the tool needs (passed into Docker)
# Writes {"cost_usd", "input_tokens", "cached_input_tokens", "output_tokens", "turns", "output", "exit"}.
# The session gets full permissions, so run it only in a sandbox (tools/sandbox/run.sh).
set -uo pipefail
case "${1:-}" in
  --install) echo "npm install -g @anthropic-ai/claude-code"; exit 0 ;;
  --env) echo "ANTHROPIC_API_KEY CLAUDE_CODE_OAUTH_TOKEN"; exit 0 ;;
esac
work=$1 prompt=$2 tier=$3 budget=$4 turns=$5 out=$6
case "$tier" in deep) model=opus ;; fast) model=haiku ;; *) model=sonnet ;; esac
args=(-p --output-format json --model "$model" --max-turns "$turns" --max-budget-usd "$budget")
if [ "${EVAL_JUDGE:-}" = 1 ]; then args+=(--tools ""); else args+=(--dangerously-skip-permissions); fi
[ "${TEAM_SANDBOX:-}" = 1 ] && export IS_SANDBOX=1   # lets the container's user skip permission prompts
(cd "$work" && claude "${args[@]}" < "$prompt" > "$out.raw" 2> "$out.err")
code=$?
python3 - "$out.raw" "$out.err" "$out" "$code" <<'PY'
import json, sys
raw, err, out, code = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
try:
    d = json.load(open(raw))
except Exception:
    d = {}
u = d.get("usage") or {}
json.dump({"cost_usd": d.get("total_cost_usd"),
           "input_tokens": (u.get("input_tokens") or 0) + (u.get("cache_creation_input_tokens") or 0) if u else None,
           "cached_input_tokens": u.get("cache_read_input_tokens"), "output_tokens": u.get("output_tokens"),
           "turns": d.get("num_turns"), "output": d.get("result", ""), "exit": code,
           "error": open(err).read()[-500:] if code else ""}, open(out, "w"))
PY
