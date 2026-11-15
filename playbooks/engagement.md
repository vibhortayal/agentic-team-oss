# Engagement: how a project runs

We work with the owner the way a good agency works with a client: a likely cost and timeline before saying yes, every scope change priced, and an honest re-estimate when things drift. The build itself happens in [build](build.md); this playbook wraps it.

**Who:** Ella (the owner's single point of contact: intake, proposal, every request and decision after that, and who is on the team with which skills), Rohan and Quinn (the practice and skill review), Bea (estimates, status, ledger), Priya (specs, change requests), owner (approves).

## Project profiles

Ella's first question is what kind of project this is, because the answer sets how much process applies. It goes in `TEAM.md` and changes only on the owner's word.

| Profile | For | What runs | Vera's own key | Ends with |
|---|---|---|---|---|
| **research** | A question, no product | Researcher and Critic, no code gates | No code | A graded report |
| **prototype** | A demo, an event, an idea test | Rough estimate, the [trivial path](build.md#trivial-changes) for most tickets, the lite gate kit, session caps | No; one session can run everything | A demo link and a keep, kill or harden call |
| **hobby** | Personal and low stakes, but long-lived | Prototype plus tests in CI and a simple release | No | A personal deploy |
| **internal** | A tool a few people rely on | Full foundation, change specs, weekly status, release | Yes | Production for a small group |
| **production** | A product for real users | Everything, including the UI kit, monitoring, incidents and support | Yes | A live, supported app |
| **other** | Anything else | The closest profile, with the differences written down | As that profile | A new profile once the same kind of project shows up twice |

Moving up a profile (say prototype to production) is a change request. Bea prices a hardening pass first: the strict checks turned on in `zones.yml` (`require:` checker, lint and cap, with the checker App and a linter in place), tests for untested paths, a security, dependency and red-zone review, monitoring, a rollback rehearsal, and the [launch readiness](production.md#launch-readiness) items for the product type. The owner approves it before the profile changes.

## The light path (small apps)

Most first projects are small, and the full set of playbooks costs far more than a small app needs: in [our build-off](../docs/research/2026-11-14-one-agent-vs-full-team/README.md) it used about 140 times the cheapest way on a one-page app, with 16 sessions before any code, and caught one fault the light ways missed, at the critique. So a small app takes the light path by default, and keeps the critique.

**A small app** is a prototype or hobby project that Ella can describe in about ten lines, used by one person or a small group they know, with no payments, no sign-in for people the owner doesn't know, no personal data beyond names, and no AI feature inside the app. If any of those is unclear, ask the owner one question; if it's still unclear, take the full path.

**Who:** Ella, Quinn once, Bea for the price, Ian to build, Vera to check. Nobody else.

1. **Intake, short.** Profile, product type, the idea, who uses it and the owner's must-haves. No research, no practice and skill review.
2. **The plan is the spec.** Ella writes the [brief](../templates/documents.md#project-brief) in short and lists the owner's must-haves in their own words, numbered, each followed by one testable row ([testable-criteria](../skills/testable-criteria/SKILL.md)). That list is what Ian builds and Vera checks; there is no separate spec or spec review. Ella may add rows. She never changes or softens a must-have without the owner's yes to that one line, whatever earlier yes they gave.
3. **One critique.** A fresh Quinn reads only the plan, says its goal back in two lines, then finds how the app could go wrong in use (timing, repeated taps, odd input, a refresh, a small screen). This one fresh run is the brief's checker ([scale review to risk](../principles.md#who-checks-whom-the-review-matrix)). Ella adds rows for what holds and lists what she rejected.
4. **Price and yes.** Bea posts the session cap and the cost range on the project's issue (on a smaller model, inside Ella's session if the tool allows). The owner says yes to the plan and cost together, as in Ella's [intake](../roles/engagement-lead.md#intake-new-project-or-big-change).
5. **Build and check** as one ticket on the project's issue: [build](build.md) steps 6 to 9, with the plan's commit as the spec. Vera prepares checks from the rows before any code, Ian builds, a fresh Vera that didn't build it gives the verdict. Ella does the coordinator's jobs herself (branch, handoffs, accepting the verdict, the receipt line).

Later changes to a small app take the [trivial path](build.md#trivial-changes) where it fits, otherwise one light ticket like step 5 with the change's rows added to the plan.

**What the light path never drops:** the issue and team comments, the independent check, the cap, the share check on every preview, and the owner's yes before anything merges or goes live.

**Moving to the full path.** When a change would break the small-app line (payments, strangers signing in, personal data, an AI feature, or a plan Ella can no longer hold in ten lines), Ella tells the owner in one line why the next step needs more checking and what it costs, and that change goes through [research to spec](research-to-spec.md) and the normal ticket flow. A change of profile is still a change request, as above.

## Product types

The profile says how much process applies; the product type says which checks apply. Ella records it next to the profile in `TEAM.md`. A product can be more than one type (a phone app with an AI assistant is both).

| Type | What changes |
|---|---|
| **web** | The default. Previews are URLs; releases deploy and roll back |
| **mobile** | Store accounts, test builds as previews, store review, no rollback once installed ([mobile release](production.md#mobile-apps)) |
| **ai** | An AI feature or agent inside the product: quality evals plus abuse tests, drift checks and eval-gated model changes ([AI safety](production.md#ai-features-and-agents)) |
| **api** | No screens; the contract, load and abuse limits carry the weight |
| **other** | The closest type, with the differences written down, as for profiles |

## Lifecycle

| Step | What happens | Who | Output |
|---|---|---|---|
| 1. Intake | Profile, goal, users, scope, constraints, budget ceiling, then the [practice and skill review](#practice-and-skill-review) | Ella, Rohan, Quinn | Decision log, `research/practices-and-skills.md` |
| 2. Proposal | Brief plus a rough estimate: milestones, cost and calendar ranges, assumptions, exclusions | Ella, Bea | `docs/brief.md`, `budget/estimate-v1.md` |
| 3. Sign-off | The owner says yes to both in the chat; that sets the baseline budget and dates | Owner, through Ella | Ella's receipt, then the merged `docs/` PR |
| 4. Delivery | Specs, tickets, build and verify, inside each ticket's cap | Priya, build team | Merged PRs with evidence |
| 5. Release and run | Production releases, monitoring, incidents, support | Otto, owner | [production](production.md) |
| 6. Change requests | New or changed scope is written up and priced before work starts | Priya writes, Bea prices, owner approves | `docs/change-requests/CR-<n>.md` |
| 7. Weekly status | Done, next, blocked, spend against budget, dates against plan, risks, what the owner must do | Bea | `reports/status-<date>.md` |
| 8. Re-baseline | Actuals drift more than 20% from the estimate for the rest of the work | Bea, owner approves | `budget/estimate-vN.md` |
| 9. Close-out | Final cost and time against the baseline, then a retro by a fresh agent | Bea, then Quinn | `reports/close-out.md`, `reports/retro.md` |

Ella stays the owner's contact through every step. Approvals, the weekly status and anything else for the owner reach them through her. Templates for all of these are in [templates/documents.md](../templates/documents.md).

## Practice and skill review

Before the brief goes to the owner, Ella checks what good looks like for this kind of project and which skills the team should carry for it. She decides the team and its skills from the interview and this review; the owner approves both with the brief.

1. **Brief Rohan** with a [research brief](../templates/documents.md#research-brief) in informed mode. The question: what are the leading practices for this kind of project on this stack, and which skills would help the roles Ella plans to hire? It must read the interview notes and the team's own `skills/` (installed as `.team/skills/`), so he doesn't propose what the team already has.
2. **Rohan looks in this order** and grades each find like any source:
   - **Practices** from primary sources: the framework's and platform's own guides, security guides such as OWASP's for the project's kind of app, app-store or accessibility rules where they apply. Only what changes how this project should be built; skip what the model already knows.
   - **Rules that apply** (internal and production): from where the users are and who they are, which privacy laws, children's rules, accessibility laws, AI disclosure rules and store rules bind this product, each with its official page. This is a list for the owner, never legal advice.
   - **Skills** in the open Agent Skills format, from the stack's own vendors first (a database or hosting company's official skills), then well-known publishers, then community collections. Stars and download counts are a weak signal, never a reason on their own. For each candidate: link at an exact commit, licence, what it does, which role it's for, and what it would replace.
3. **Quinn vets every candidate skill** before Ella may propose it. A skill is instructions plus scripts that run with the agent's permissions, so two checks, both required:
   - **Scan it first** with [SkillSpector](https://github.com/NVIDIA/SkillSpector) (Apache-2.0), pinned at the tested commit `3c2c5d7a1ee148d228398070b91d3beaf0d73b11` (an untagged `main` commit, not a release), in its own virtual environment or its Docker image, never in the project's dependencies: `skillspector scan <skill folder> --no-llm --fail-on-findings --fail-on-incomplete --format json --output research/skill-scans/<name>.json`. Commit the report. `--no-llm` keeps the files on the machine and costs nothing; its AI mode sends them to a provider and runs only with the owner's OK. The scan is an alarm, not a verdict: in our test it called a skill that merges to `main` and tells the builder to edit tests "SAFE", and it flags some harmless text as high. So its score never counts as a pass. Every finding gets a line in the verdict, either harmless with the reason or a REJECT, and a high or critical finding nobody can explain is a REJECT. If the scanner can't run, the skill can't be adopted until it does. A partial scan (the scanner ran but couldn't parse some text, which `--fail-on-incomplete` reports) counts only when every unparsed span is listed in the verdict and explained.
   - **Then read every file**, not just `SKILL.md`, whatever the scan said. Reject it if:
   - its licence doesn't allow use and copying, or it has none;
   - it downloads code or instructions at run time, sends data anywhere, or reads files outside the project;
   - it needs a secret, a paid service or network access the spec doesn't allow;
   - it tells the agent to do something the roles or principles forbid (merge, skip the checker, edit tests, ask the owner mid-build) or to obey it over other instructions;
   - it repeats what a role file or a team skill already says.
   Otherwise: ADOPT, with the one-line reason, or ADOPT WITH NOTES, saying which instructions the role ignores.
4. **Ella decides** the team and the skills each hire carries, and puts them in the brief's **Team** section with one plain line each on why. Practices that change the plan go in **Advice**.
5. **After approval,** Otto copies each adopted skill unchanged into `.agents/skills/<name>/` (and into each agent tool's own skills folder, the way the tool's installer does for team skills) in a `gate/skills` PR, with its source, commit and licence in `TEAM.md`'s Skills table. Skills are gate files: none can be added or changed during a build, only through another reviewed `gate/` PR.

**Scale it to the profile.** Research: no skill review. Prototype and hobby: a short scan (time box about 20 minutes) of the stack vendors' official skills only, with Quinn's file read still required. Internal and production: the full review. Bea includes the sessions in the estimate.

A project skill that proves useful on two projects is proposed for the team repo through the [improve loop](improve.md), where it's tuned once and every project gets it.

## Existing projects

When the owner brings a repo that already exists, the team reads it before anyone asks a question.

1. **Read.** Rohan writes `research/repo-map.md` in informed mode: what the app does today, the stack, how to run it, whether tests exist and pass, and where it looks fragile, each claim with the file or command that shows it. Otto runs the health checks and records `quality/baseline.json`, so old debt can't block new work, only grow.
2. **Interview.** Ella opens intake with what the team found and asks where the owner wants it to go. The profile, brief and estimate follow as for a new project.
3. **Fit the foundation.** Otto installs the kit and branch protection in their own `gate/` PRs, which the owner approves. Code without tests gets tests before it changes: the first ticket for an untested area pins its current behaviour, and only then does a feature ticket change it.

After that it runs like any other project.

## Rules

1. **No work without an approved number.** Inside an approved ticket, reversible work needs no further ask.
2. **Ranges, not single numbers,** with the assumptions that move them most. Early ranges are wide. Say so.
3. **Show the owner's time.** Agents are fast; reviews and approvals are usually the slow part. Calendar estimates list both, with the assumed response time.
4. **Price changes before starting them.** If a change would break the budget, flag `needs-human` + `human:spend` and wait.
5. **Status comes from data.** Every number in the weekly status comes from GitHub, CI or the ledger. Anything unmeasured is labelled as such.
6. **Drift means re-baseline.** Past 20% drift, Bea re-estimates and the owner approves before work continues.

Early numbers will be rough and the ledger will have gaps until tools report usage. If this layer stops earning its keep, the quarterly review can retire it.
