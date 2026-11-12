#!/usr/bin/env bash
# One sandbox eval session with any agent CLI that reads a prompt on stdin, for tools/sandbox/run_evals.py:
#   AGENT_CMD='<your tool and its non-interactive flags>' eval-agent.sh <workdir> <prompt-file> <tier> <max-usd> <max-turns> <result-json>
# Optional: AGENT_INSTALL (command that installs the tool in the sandbox image), AGENT_ENV (variable names to pass in).
# This adapter can't see tokens or cost, so the runner needs --allow-unpriced and only the
# turn and time caps apply. Write a tool adapter (see adapters/claude-code/eval-agent.sh) to get cost.
set -uo pipefail
case "${1:-}" in
  --install) echo "${AGENT_INSTALL:-}"; exit 0 ;;
  --env) echo "AGENT_CMD ${AGENT_ENV:-}"; exit 0 ;;
esac
work=$1 prompt=$2 out=$6
: "${AGENT_CMD:?set AGENT_CMD to your agent tool's non-interactive command}"
(cd "$work" && $AGENT_CMD < "$prompt" > "$out.txt" 2> "$out.err")
code=$?
python3 - "$out.txt" "$out" "$code" <<'PY'
import json, sys
json.dump({"cost_usd": None, "output": open(sys.argv[1]).read()[-20000:], "exit": int(sys.argv[3])}, open(sys.argv[2], "w"))
PY
