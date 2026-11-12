# Production: release, run and keep healthy

How merged work reaches users and stays healthy. Releases are for hobby, internal and production projects; prototypes stop at a preview link. Monitoring, incidents and support are for internal and production.

**Who:** Otto (releases, launch readiness, monitoring, incidents, health, housekeeping), Ian (previews, fixes, cleanup), Vera (preview, smoke and launch checks, health numbers), Quinn (threat list, abuse cases, store review), Max (AI safety and drift), Priya (support triage, the 30-day review), Bea (costs at scale), owner (approves every production deploy and every spend).

## Release

```text
PR ─▶ preview of the PR head ─▶ Vera checks it ─▶ PASS + green CI ─▶ owner merges
  ─▶ Otto prepares the release ─▶ owner approves ─▶ deploy ─▶ smoke ─▶ watch ─▶ released or rolled back
```

1. **Preview before merge.** Every PR that changes behaviour gets a preview of its exact head: per PR where the host offers it, otherwise one staging slot, one ticket at a time. Ian deploys it with the command in `TEAM.md`; Vera checks it as part of the verdict.
2. **A release is a list of merged PRs.** Otto cuts it from `main` with a semver version, plain release notes, its migrations and the exact rollback command, on a release issue labelled `needs-human` + `human:approve-release`.
3. **The owner approves every production deploy** through the environment's approval rule, until the autonomy stage covers releases. Migrations, sign-in, payments and data deletion always need the owner.
4. **Deploy, smoke, watch.** Otto deploys the approved version, runs the smoke checks from `TEAM.md` and watches errors and latency for the window (default 30 minutes). The tag comes after the window.
5. **Roll back first.** A failed smoke check or an error alert in the window means roll back, then open an incident. Rollback and restore are rehearsed at foundation and after any change to how the app deploys.
6. **Migrations are their own step.** A release says whether its migration is backward compatible. One that isn't gets its own release, after a verified backup.
7. **Agents never hold production credentials.** Deploys run from CI with the environment's secrets. An agent triggers the workflow and never sees the keys.

## Launch readiness

Green tests don't make a product safe to put in front of real users. Before the first production release, Otto opens a launch issue with this checklist, filtered by the product type in `TEAM.md`. Each item has an owner and a proof committed under `verification/launch/`. The owner approves the first production release only when every item is green or knowingly waived; Ella records each waiver and its risk in the decision log. Internal projects run the rows marked **all**; production projects run every row for their type. Later releases rerun a row when the change touches what it covers.

| Item | Type | Who | Proof |
|---|---|---|---|
| **Threat list** for each red-zone area (sign-in, data separation, payments, uploads, admin): how it could be attacked and the check that stops it | all | Quinn at planning; checks join the spec | `docs/specs/vN-review/threats.md` |
| **Security scan** of the running preview with OWASP ZAP's baseline scan, and the OWASP ASVS Level 1 checklist marked pass, fail or not relevant | web, api | Vera | Scan report, checklist |
| **Data list** in the spec: what personal data, why, where it's kept, which outside services see it, how long | all | Priya | Spec section |
| **Privacy policy and terms** from a managed generator (buy, don't build), matching the data list; legal pages are red zone | all | Priya drafts, owner approves | Links |
| **Users can download and delete their own data;** tracking waits for consent where the rules require it | all | Vera | Check scripts |
| **Load test** with k6 at 10 times the expected load in the spec, against a production-sized preview; costs shown at today's load and at 10 times | web, api, ai | Otto runs, Arjun sets the load, Bea prices | k6 summary, cost table |
| **Speed budgets** from the spec met: page speed via Lighthouse CI on the preview, start time and crash-free rate on mobile, response time and cost per call for AI | all | Vera | Report |
| **Accessibility** to WCAG 2.2 AA: the automated check plus a keyboard and screen-reader pass of the main flows; platform scanners on mobile | web, mobile | Vera | Notes, screenshots |
| **Backup restore** rehearsed within the last 90 days, inside the spec's data-loss and recovery targets | all | Otto | Drill log |
| **Monitoring** live (below) and **analytics** sending the spec's events | all | Otto | Dashboard links |
| **Email** that reaches inboxes: SPF, DKIM and DMARC set on the sending domain | if it sends email | Otto, owner edits DNS | Record check |
| **Support channel** feeding `support` issues, and the help pages live | all | Priya | Links |
| **Store must-haves** (below) | mobile | Priya, Quinn, owner | Store checklist |
| **AI abuse cases** pass (below) | ai | Max, Vera | Eval report |

Agents never say a product is "compliant" with a law. Where a project touches health, money, children or sensitive personal data, Ella tells the owner plainly that an hour with a lawyer is worth it before launch, and records the answer.

## Mobile apps

A store app can't be rolled back once it's on people's phones, and the store can reject it. So:

1. **Accounts.** The owner creates the store developer accounts; Ella walks them through it and Bea lists the fees. New store accounts can have waiting periods (a new personal Google Play account needs a closed test with a minimum number of testers for a minimum time); Rohan checks today's rules at intake and Bea puts them and review time in the calendar.
2. **Previews are test builds** (TestFlight on iOS, an internal test track on Android) of the PR head, or of `main` where per-PR builds cost too much. Vera checks them on simulators or emulators at the phone sizes the spec names.
3. **Build and sign in CI or a managed build service.** Signing keys live with the store or the service, never with agents. macOS build minutes cost far more than Linux, so Bea prices a managed build service against the CI plan.
4. **Version 1 ships a remote off switch** for risky features and a minimum-version check that asks users to update. Releases roll out in stages (a small share of users first), and Otto watches crash rate before widening.
5. **Store must-haves**, drafted by Priya and approved by the owner: listing text and screenshots, the privacy label or data safety form matching the data list, the privacy policy link, account deletion inside the app if users can sign up, and age rating. Before each submission Quinn checks the build against the store's published review guidelines and common rejection reasons.
6. **A rejection is a ticket,** with the store's message quoted, not an incident.

## AI features and agents

Max's evals measure whether AI output is good. These rules cover whether it can be tricked, leak, or do harm.

1. **Abuse cases.** Quinn writes them from the OWASP Top 10 for LLM applications and the spec: prompt injection (including through documents, web pages or emails the AI reads), leaking personal data or its own instructions, harmful or off-topic output, an agent acting beyond its job, and runaway cost. Max adds them to the golden set as a red-team slice with its own pass mark, run before every prompt or model change.
2. **Least power.** An agent inside the product gets only the tools its job needs, and asks the user before it spends money, sends a message, deletes anything or acts outside the app. Its tool permissions are red zone.
3. **Tell users** when they're talking to an AI, and where its answers can be wrong.
4. **Drift.** Each month Max scores a small sample of real AI calls against the golden set's metric, only where users agreed and only through a mode that doesn't train on the data. A drop below the pass mark is a SEV3.
5. **Model changes are eval-gated.** Providers retire models. A new model or version goes through the full eval, red-team slice included, before release; retirement dates go on the coming-due list.

## Monitoring (buy, don't build)

Set up at the first release with managed services, on free tiers where they fit. Otto proposes each with its monthly cost; the owner approves any spend. Cover: an uptime check on the main page and a health endpoint, error tracking tagged with the release, searchable logs with an approved retention, automatic backups in an account no agent can delete (restored in a drill every quarter, not just once), product analytics for the spec's events from a privacy-friendly service, and spend alerts on every paid service and model provider. Every alert opens or updates a GitHub issue labelled `incident`, so the board is the one place to look.

## After launch

Thirty days after the first production release, then each quarter, Priya and Bea write a short review on `team/records`: each "How we'll know" signal from the brief against its target, cost per active user, the top support issues and incidents. Ella brings the owner one recommendation: keep going, change course (a change request) or stop.

## Incidents

| Severity | Meaning | Response |
|---|---|---|
| SEV1 | Down, data loss or a security problem | Roll back or switch off first; tell the owner at once (`needs-human` + `human:blocker`) |
| SEV2 | A main feature broken for many users | Fix or roll back the same day |
| SEV3 | A minor bug or degraded path | A normal ticket |

Stabilise before diagnosing: roll back, turn the feature off or scale down. Never hot-fix production. The fix is a ticket with a failing check that reproduces the incident ([trivial path](build.md#trivial-changes) if it qualifies). SEV1 and SEV2 get a blameless post-mortem by a fresh agent: what happened, why the gates missed it, and one change to a gate, check or role, which goes to [improve](improve.md).

## Support

User reports from email, a form or app feedback become GitHub issues labelled `support`. Priya triages them weekly: a bug becomes a ticket with a severity, a request becomes a change request, and a question gets an answer the owner approves before it's sent. Agents never reply to users directly.

## Code health

The quality gate stops new mess. This part measures what's left and pays it down, in every project with merged code.

**Monthly report.** Otto writes `reports/health-<YYYY-MM>.md` ([template](../templates/documents.md#health-report)) from numbers it can recompute, and commits the script. A fresh Vera re-runs it before the owner sees the report. It covers change failure rate (merged PRs followed within 14 days by a revert, hotfix or bug ticket naming them), rework (lines changed again within 30 days), warnings, complexity and duplication against the baseline and last month, copying versus refactoring, BLOCK rounds per ticket, typed blockers by type, owner send-backs with reasons, and the least healthy modules. Never report "% of code written by AI"; nobody measures it with a disclosed method. It also shows headroom (load and spend against their limits) and a coming-due list for the next 90 days: renewals, store and platform deadlines, model retirements, runtime end-of-life, free-tier limits, the next restore drill. Each item past due or within 30 days becomes a ticket. It ends with at most three recommendations, each with one line of evidence.

**Cleanup.** Every cycle (default two weeks), Otto files one cleanup ticket from the latest report, a normal change spec with owned paths and a proof command and a fixed budget (default one Ian and one Vera session). What doesn't fit waits for the next cycle. Ian refactors in small steps with existing tests green; Vera checks behaviour didn't change and the numbers moved the right way. A module flagged unhealthy is cleaned before a new feature lands in it, and Priya adds that cleanup to the feature's plan. When a count drops, the same PR lowers `quality/baseline.json`.

## Housekeeping

Weekly, before the owner resets or merges anything, and whenever the owner asks, Otto checks this repo and every project repo with a `TEAM.md`. Repos the owner put on hold are left alone.

1. `git fetch --prune origin`.
2. `git status` in every checkout from `git worktree list`. Name the agent that owns each dirty tree; never commit, stash or discard another agent's work.
3. Unpushed commits per branch (`git log --oneline origin/<branch>..<branch>`). A local `main` ahead of `origin/main` is always reported.
4. Delete branches whose tip is in `origin/main` and whose PR merged. Never delete `main`, an active branch, one with an open PR, or one with unmerged commits; ask its owner.
5. `git worktree prune`, and remove only your own clean, merged worktrees.
6. Post one short summary: what was deleted, what's dirty or unpushed and whose, what's left for the owner.

Merging to or resetting `main`, tags, force-pushes, deploys and deleting a repo stay with the owner.
