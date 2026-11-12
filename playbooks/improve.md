# Improve the team

How the team learns from its projects: which handoffs fail, which roles earn their cost, and when to tune, merge, retire or add a role. It runs in this repo, fed by evidence from projects. Tune roles here, never in a project's installed copy.

**Who:** a fresh Critic (retros), Max (quarterly review and comparisons), owner (approves every change to a role or rule).

```text
project evidence ─▶ retro by a fresh agent ─▶ team-finding issues here
  ─▶ quarterly scorecard ─▶ owner picks ─▶ tested on frozen cases ─▶ new team version
```

## 1. Retro

At every close-out, and after every SEV1 or SEV2, a Critic that didn't work on the project reads only the evidence: issues and team comments, `verification/`, the ledger, health reports, post-mortems and send-backs. It writes `reports/retro.md`, answering:

- Where did a handoff fail (missing input, wrong recipient, asked twice, waited on nobody)?
- Which checks caught real problems, and what reached the owner or production unseen?
- Where did the owner have to step in, and could a rule or check have saved that?
- Where did cost or time drift, and why?

Findings about the team, not the project, go to this repo as issues labelled `team-finding`, with links and no project vocabulary.

## 2. Quarterly review

Max gathers the `team-finding` issues and the ledgers of the quarter's projects into a role scorecard: sessions used, outputs actually used, rework caused, cost share, handoff failures, and a proposal for each role.

Every proposal links the findings and numbers behind it.

- **Tune** a role that misses the same kind of thing twice.
- **Merge** two roles when one is nearly always followed by the other with no hand-back, or both are thin.
- **Retire** a role, or make it optional, when nothing it produced was used for two quarters, or a CI check now does its job.
- **Add** a role only when the same gap shows up in two projects and no check, template or existing role covers it. Prefer a check to a persona.
- **Profiles:** if the same "other" kind of project came up twice, propose a new profile.

It also names the slowest step on the board, the most common blocker type, and questions agents asked that a document should have answered.

## 3. Change one thing and test it

1. Start from a dated finding with evidence (commit, verdict, log).
2. One hypothesis, one change to one role file. No change while a run that uses the role is in flight.
3. Run the old and new role on the same frozen cases, with the same model and task wording.
4. Check nothing else got worse: spec coverage, review strictness, security, autonomy.
5. Record the finding, the change, before and after, and the revert path in the pull request.
6. Bump the role's `version:` and tag the repo. Projects move their pin when they choose.

Before a team version is tagged, a fresh agent on a different model reviews the whole repo cold.

Keep quality and performance apart; never fold them into one score. Quality: independent PASS at an exact revision, negative control blocked, owner interventions during a dark run (target zero), evidence complete. Performance: time to first useful response, wall-clock per unit, rework rounds, token and API cost per unit.

## Testing the team

Three layers, cheapest first. Run the first two after any change to a role, playbook, template or tool.

| Layer | Command | Model? | Runs |
|---|---|---|---|
| Free checks: role files, vendor names, links and anchors, labels, the handoff table, case format, every installer, the gate self-test | `python3 tools/teamcheck.py` | No | Every pull request here (about a minute) |
| Tool self-test: planted mistakes the checks and the handoff replayer must catch, and a scripted fix loop through the harness | `python3 tools/sandbox/selftest.py` | No | Every pull request here |
| Role cases and end-to-end projects | `tools/sandbox/run.sh <adapter> --max-usd <cap> <case...>` | Yes | On demand, locally, in Docker |

The model layer never runs in CI. Each case gets a fresh copy of a tiny fixture project with the team installed, a local remote, and a stand-in `gh` that keeps issues, labels and comments in a file, so nothing touches GitHub. Agents run with full permissions, which is why it runs in Docker. In an end-to-end case the runner plays the main session (it starts each role from the next prompt in the latest team comment) and the owner (it answers and approves from the case, and merges only a head with a PASS). Afterwards the replayer checks every handoff (`python3 tools/teamcheck.py replay`).

**Spend** is capped and visible: `--max-usd` caps the whole run, each session gets what's left as its own cap, and no session starts once it's spent. Every session's tokens and cost go into the run's `ledger.csv`, in the budget ledger's format, next to `report.md`. An adapter that can't report cost needs `--allow-unpriced`, and then only turn and time caps apply. Start with one case and a small cap; check the real cost before running the whole set.

## Frozen cases

Each case is `evals/<case-id>/case.md`: frontmatter with `role` (a role, or `e2e` for a whole flow), `kind` (`negative` when the role must block, refuse or push back) and `fixture` (a starting project in `evals/fixtures/`), then these sections:

- **Task:** the prompt exactly as the agent gets it.
- **Setup:** a bash block that seeds issues, branches and earlier handoffs, using the helpers in `evals/fixtures/lib.sh`.
- **Expected:** what a correct result does, and the planted defect for a negative case.
- **Checks:** one per line, run against the result without a model: `event` and `no-event` (a new team comment whose event matches, e.g. `from=verifier verdict=BLOCK`), `label <n> has|lacks <label>`, `file` and `no-file <branch-glob> <path-glob> [contains <text>]`, `same <branch-glob> <path>` (unchanged since setup), `run <branch-glob> <shell command>`, `merged` and `not-merged <issue>`, `main-unchanged`.
- **Rubric:** yes/no questions for a judge model, only for what a check can't decide (did Ella explain the risk plainly). Every answer must be yes.
- **Owner:** what the simulated owner says when asked (end-to-end cases).

Prefer checks to rubric questions; judges cost money and disagree. A case never changes once used in a comparison; add a new one instead. Every set has at least one negative case, and no case carries project words. The seed set covers every role and two end-to-end flows on the word-count fixture; each project's retro adds at least one positive and one negative case from a real ticket.
