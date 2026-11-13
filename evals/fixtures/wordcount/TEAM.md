# TEAM.md

This project is staffed from agentic-team, installed in `.team/`.

- **Profile:** `hobby`. A personal tool, low stakes.
- Team version: see `.team/VERSION`.
- Agent tools in use: whichever tool runs the session. State follows `.team/docs/github-state.md`.
- Main branch: `main`. Only merged after the owner's yes.
- Autonomy stage: `1` (every merge waits for the owner's yes).

## Limits

| Limit | Default |
|---|---|
| Tickets in progress at once | 1 |
| Fix rounds per ticket | 3 (trivial: 1) |
| Build sessions per ticket, by size | trivial 4 · S 5 |

## Hired

| Role | Persona | Hired for |
|---|---|---|
| engagement-lead | Ella | always hired |
| product-manager | Priya | specs and tickets |
| implementer | Ian | builds |
| verifier | Vera | checks |
| budget-analyst | Bea | estimates and caps |

## Units

- A unit is one small change to `wc.py` and its tests.
- Branch: `team/<issue>-<slug>`.
- Default scope: `wc.py`, `tests/`, `README.md`.

## Baseline

Commands that must pass at the base and at the head: `python3 -m unittest`
