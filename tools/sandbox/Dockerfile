# The sandbox image for eval runs: the agent works with full permissions, but only
# inside this throwaway container. Built by tools/sandbox/run.sh; the team repo is
# mounted read-only at /team and results are written to /runs.
FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends git jq ca-certificates nodejs npm \
 && rm -rf /var/lib/apt/lists/* && git config --system --add safe.directory '*'
ARG AGENT_INSTALL=""
RUN if [ -n "$AGENT_INSTALL" ]; then sh -c "$AGENT_INSTALL"; fi
ENV TEAM_SANDBOX=1 PYTHONDONTWRITEBYTECODE=1 HOME=/tmp
ENTRYPOINT ["python3", "/team/tools/sandbox/run_evals.py"]
