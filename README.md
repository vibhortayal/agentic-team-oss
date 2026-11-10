# Agentic Team

A company of AI agents for building software the way a disciplined engineering team would. Each agent has a name, a role and a mandate. It works with any agent tool (Claude Code, Codex, Gemini CLI, Cursor and others): roles are plain Markdown, all state lives in the project's GitHub repo, and each tool gets a thin adapter. A project hires the agents it needs from here instead of writing its own prompts. This repository is the source of truth: roles are tuned here once, and every project picks up the improvement by moving its pin.

**What this is.** Not a new agent, and not a multi-agent framework. The agents come from the tool you already use; this repo is the company they work in: job descriptions (roles), a process (playbooks), guardrails they can't switch off (the CI gate kit), and one shared record (GitHub). Think of it as a franchise manual plus quality control for AI agents.

**When is something done?** A ticket is done when Vera passes the exact version against its written criteria, every gate is green, and you merge it. A project is done when it reaches the result its [profile](playbooks/engagement.md#project-profiles) promises, and a fresh agent has written the retro.

Where this is going, and what is being built now: [ROADMAP.md](ROADMAP.md).

The mandates say how an agent works, never what to build. Everything about a project travels in that project's own spec and its `TEAM.md` pointer file.

## The roster

| Name | Role | Department | Tier | Job in one line | Mandate |
|---|---|---|---|---|---|
| **Ella** | Engagement Lead | Advisory | deep | The only agent you talk to, on every project: guides you through the process, runs intake, coordinates everyone else, brings you decisions | [roles/engagement-lead.md](roles/engagement-lead.md) |
| **Priya** | Product Manager | Product | deep | Turns the brief or a request into an approved, testable spec and runs each ticket through build and verify | [roles/product-manager.md](roles/product-manager.md) |
| **Rohan** | Researcher | Research | deep | Answers a question from primary sources, grades the evidence, labels what it did not check | [roles/researcher.md](roles/researcher.md) |
| **Quinn** | Critic | Research | deep | Attacks a plan, idea or spec before money or code is spent on it, and adjudicates outside critique | [roles/critic.md](roles/critic.md) |
| **Arjun** | Architect | Engineering | deep | For multi-unit full specs only: acceptance map, unit order, release notes; writes no code | [roles/architect.md](roles/architect.md) |
| **Ian** | Implementer | Engineering | standard | Builds one bounded unit, writes its own tests, self-checks every acceptance row | [roles/implementer.md](roles/implementer.md) |
| **Vera** | Verifier | Engineering | deep | Writes checks from the spec before reading code, gives one verdict per revision, can block | [roles/verifier.md](roles/verifier.md) |
| **Max** | Evaluator | Engineering | deep | Measures prompt and model quality against a golden set, one variable at a time, and reports the whole score path | [roles/evaluator.md](roles/evaluator.md) |
| **Bea** | Budget Analyst | Finance | standard | Estimates cost and time as ranges, prices every new requirement, sets per-ticket caps, keeps the ledger of actual spend | [roles/budget-analyst.md](roles/budget-analyst.md) |
| **Otto** | Ops | Operations | standard | Sets up the gates, keeps repositories tidy, runs production releases with the owner's approval, monitoring and incidents | [roles/ops.md](roles/ops.md) |

Names are for easy reference: "ask Quinn to critique this", "send it to Vera". Each starts with a different letter, and most match the role's first letter. The role (the file name) stays the stable id that tools and commits use; a name can change without breaking anything.

Each role is one agent definition that can run as many copies as the work needs. Elephants (Ella, Priya, Arjun, Bea, Otto) remember a project through files in the repo; fish (Ian, Vera, Rohan, Quinn, Max) start every task fresh, which keeps them independent. See [principles.md](principles.md#memory-elephants-and-fish). The split follows Google's [Elephant-Goldfish Model](https://opensource.googleblog.com/2026/10/introducing-elephant-goldfish-model-plugin.html).

**You only talk to Ella.** She's on every project and can't be removed; every other agent is optional. She interviews you, writes the proposal with Bea's estimate, and after you sign off she runs the rest: Priya specs and runs each ticket with Ian and Vera (or Arjun for a large multi-unit build), Otto releases, Bea reports. Ella comes back to you only for decisions, each with one recommendation, and she'll tell you when a shortcut puts the project at risk. You can always overrule her.

## Playbooks

| Playbook | Use it when |
|---|---|
| [engagement](playbooks/engagement.md) | Every project: profile, proposal with cost and time, change requests, weekly status |
| [research-to-spec](playbooks/research-to-spec.md) | An idea isn't a spec yet, or a spec needs its fresh-eyes review |
| [foundation](playbooks/foundation.md) | A new project repo, before any feature work |
| [build](playbooks/build.md) | An approved spec needs code, including trivial changes and prompt or model quality |
| [production](playbooks/production.md) | Releases, monitoring, incidents, support, code health, housekeeping |
| [improve](playbooks/improve.md) | The team's own loop: retros, the quarterly role review, tuning a role |

**How we work.** The team follows *spec-driven flow*: small written specs, tickets that flow through build, independent verification and gates, and no sprints. [docs/how-we-work.md](docs/how-we-work.md) compares it with waterfall, Scrum, SAFe and Kanban, with the evidence.

## Words you'll see

| Word | Meaning |
|---|---|
| Spec, change spec | A short written description of a change with checkable acceptance criteria, approved before any code |
| Ticket | One unit of work: a GitHub issue, a branch and a pull request |
| PASS, BLOCK | Vera's verdict on an exact version of the work. BLOCK lists what's wrong |
| Typed blocker | An agent's honest "I can't do this": unclear request, missing access, too big, or impossible |
| Gate | A CI check the agents can't change, such as "existing tests weren't edited" |
| Red zone | Risky paths (sign-in, payments, migrations, infrastructure) that always need your approval |
| Autonomy stage | How much merges without you, widened one area at a time on evidence |
| Elephant, fish | Elephants remember a project through files; fish start fresh each time so they stay independent |
| Dark run | A build that runs without questions to you, except the decisions only you can make |
| Profile | The kind of project (prototype, production and so on), which sets how much process applies |

The rules every agent follows are in [principles.md](principles.md), and the evidence behind the design is in [the research report](docs/research/agentic-software-company-practices.md).

## Getting started

The team works the same way in every agent tool. Only three things differ by tool: the install command, which file the tool reads first, and how you open a fresh session. Roles, rules, playbooks and prompts are identical everywhere.

### 1. Put the team in your project (once per project)

```bash
git clone <this repo's URL> ~/agentic-team

# any tool: copies the team into .team/ and writes AGENTS.md
~/agentic-team/adapters/generic/install.sh ~/code/my-project

# Claude Code: run this instead (does the above, plus subagents and CLAUDE.md)
~/agentic-team/adapters/claude-code/install.sh ~/code/my-project

# GitHub labels the agents use to show who holds what (needs the gh CLI, signed in)
~/agentic-team/adapters/github/labels.sh <owner>/<repo>
```

Then copy [templates/TEAM.md](templates/TEAM.md) into the project and fill it in, fill in the project lines at the top of `AGENTS.md`, and commit `.team/`, `AGENTS.md` and `TEAM.md`. For a brand-new repo, run the [foundation](playbooks/foundation.md) playbook before any feature work.

### 2. Your tool

Codex and Cursor read `AGENTS.md` as is. Claude Code uses its own installer above. Other tools need a pointer to `AGENTS.md`; [adapters/README.md](adapters/README.md) has the details and how to pick a model for each role's `tier`.

### 3. Talk to Ella

Open a session in the project and paste:

```text
You are Ella, the Engagement Lead. Read AGENTS.md and .team/roles/engagement-lead.md. <what you want, in your own words>
```

That's the only prompt you need. Start a new idea, ask for a change, ask how things are going, approve something: it all goes to Ella, and she starts the other agents. In a tool that can't start sessions on its own, she gives you the one line to paste into a new session.

Agents hand off on GitHub issues and keep the `role:`, `stage:` and `needs-human` labels current ([docs/github-state.md](docs/github-state.md)); Ella answers from there, and the dashboard will read the same data.

The team's own maintenance (the quarterly role review, tuning a role) runs in this repo: `You are Max, the Evaluator. Read roles/evaluator.md and playbooks/improve.md. Run the quarterly team review.` To pick up a tuned role in a project, re-run the installer and commit the diff. Never edit `.team/` inside a project by hand.

## Layout

```text
roles/        one page per agent: neutral frontmatter (tier, capabilities) and its mandate
playbooks/    the six ways agents work together
templates/    what a project copies: TEAM.md, AGENTS.md, DESIGN.md, spec.md, documents.md, budget/, the foundation kit
adapters/     install scripts (generic, Claude Code) and the GitHub label script
docs/         how we work, the GitHub state contract, the research behind the design
evals/        frozen cases for tuning roles (see improve)
```

## License

Apache-2.0. See [LICENSE](LICENSE).
