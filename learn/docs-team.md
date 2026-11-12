---
title: Meet the team
nav_order: 3
has_children: true
permalink: /roles/
nav_exclude: false
search_exclude: false
has_toc: true
---

# Meet the team

**You only talk to Ella.** She's on every project and can't be removed; every other agent is optional. She interviews you, writes the proposal with Bea's estimate, and after you sign off she runs the rest: Priya specs and runs each ticket with Ian and Vera (or Arjun for a large multi-unit build), Otto releases, Bea reports. Ella comes back to you only for decisions, each with one recommendation, and she'll tell you when a shortcut puts the project at risk. You can always overrule her.

**Do I need all ten?** No. The ten roles are the jobs a small software company has, from first idea to keeping the app running. Most projects need only a few. Ella picks the smallest team that does the job and writes down who and why in the brief; a small test app might use three or four. She's the only fixed member, and you can ask her to add or drop anyone.

| Name | Role | Department | Tier | Job in one line | Mandate |
|---|---|---|---|---|---|
| **Ella** | Engagement Lead | Advisory | deep | The only agent you talk to, on every project: guides you through the process, runs intake, coordinates everyone else, brings you decisions | [roles/engagement-lead.md](../roles/engagement-lead.md) |
| **Priya** | Product Manager | Product | deep | Turns the brief or a request into an approved, testable spec and runs each ticket through build and verify | [roles/product-manager.md](../roles/product-manager.md) |
| **Rohan** | Researcher | Research | deep | Answers a question from primary sources, grades the evidence, labels what it did not check | [roles/researcher.md](../roles/researcher.md) |
| **Quinn** | Critic | Research | deep | Attacks a plan, idea or spec before money or code is spent on it, and adjudicates outside critique | [roles/critic.md](../roles/critic.md) |
| **Arjun** | Architect | Engineering | deep | For multi-unit full specs only: acceptance map, unit order, release notes; writes no code | [roles/architect.md](../roles/architect.md) |
| **Ian** | Implementer | Engineering | standard | Builds one bounded unit, writes its own tests, self-checks every acceptance row | [roles/implementer.md](../roles/implementer.md) |
| **Vera** | Verifier | Engineering | deep | Writes tests from the spec before reading code, gives one verdict per revision, can block | [roles/verifier.md](../roles/verifier.md) |
| **Max** | Evaluator | Engineering | deep | Measures prompt and model quality against a golden set, one variable at a time, and reports the whole score path | [roles/evaluator.md](../roles/evaluator.md) |
| **Bea** | Budget Analyst | Finance | standard | Estimates cost and time as ranges, prices every new requirement, sets per-ticket caps, keeps the ledger of actual spend | [roles/budget-analyst.md](../roles/budget-analyst.md) |
| **Otto** | Ops | Operations | standard | Sets up the gates, keeps repositories tidy, runs production releases with the owner's approval, monitoring and incidents | [roles/ops.md](../roles/ops.md) |

Names are for easy reference: "ask Quinn to critique this", "send it to Vera". Each starts with a different letter, and most match the role's first letter. The role (the file name) stays the stable id that tools and commits use; a name can change without breaking anything.

Each role is one agent definition that can run as many copies as the work needs. Elephants (Ella, Priya, Arjun, Bea, Otto) remember a project through files in the repo; fish (Ian, Vera, Rohan, Quinn, Max) start every task fresh, which keeps them independent. See [principles.md](../principles.md#memory-elephants-and-fish). The split follows Google's [Elephant-Goldfish Model](https://opensource.googleblog.com/2026/10/introducing-elephant-goldfish-model-plugin.html).
