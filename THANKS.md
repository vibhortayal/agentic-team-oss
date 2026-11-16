# Thanks for contributions

This team is built on other people's work. These are the projects we took ideas or files from, and the ones we learned from by comparing them with ours. If you like the team, give them a look and a star.

## Ideas we adopted

Each row says which idea we borrowed, where it lives in this repo, and the pull request that added it.

| Project | Idea we borrowed | Where it lives here |
|---|---|---|
| [AI Hero skills](https://github.com/mattpocock/skills) by Matt Pocock | His grill-me skill asks one question at a time, each with a suggested answer. Ella's first interview now works the same way. | [Ella's role](roles/engagement-lead.md), intake step 7 ([#60](https://github.com/vibhortayal/agentic-team-oss/pull/60)) |
| [The Home Repo pattern](https://www.aihero.dev/the-home-repo-pattern) by Matt Pocock | One repo holds the shared rules and skills, with a list of your other projects. Your copy of the team keeps that list, so one update reaches every project. | [adapters/update.sh](adapters/update.sh) (`add` and `all`), README ([#60](https://github.com/vibhortayal/agentic-team-oss/pull/60)) |
| [Superpowers](https://github.com/obra/superpowers) by Jesse Vincent | Its systematic-debugging skill: find the cause before changing code. | [skills/debug-a-failure](skills/debug-a-failure/SKILL.md) ([#12](https://github.com/vibhortayal/agentic-team-oss/pull/12)) |
| [agent-ops-patterns](https://github.com/u00dxk2/agent-ops-patterns) | Its "who decides what" map. Run on our team, it showed the spending cap and the three-strikes stop were only instructions. Now a GitHub check enforces both. | The `limits` gate in [team_gates.py](templates/foundation/scripts/team_gates.py), and the `spend-approved` and `rounds-approved` labels ([#29](https://github.com/vibhortayal/agentic-team-oss/pull/29)) |
| [Orbi](https://orbi.build) | It runs agent work as GitHub labels with a separate reviewer. Reading it, together with that map, led to a receipt on each change, a watch mode for new checks, and counting only comments from trusted people. | `watch:` in [zones.yml](templates/foundation/zones.yml), the receipt line in [Priya's role](roles/product-manager.md) ([#30](https://github.com/vibhortayal/agentic-team-oss/pull/30)) |
| [Quarterdeck](https://github.com/shannonbay/Quarterdeck) | The team takes work only from the owner and collaborators, and work shaped by outside text (an issue, a web page, a pasted file) never merges without the owner's yes. | `principles.md` rule 3, `docs/github-state.md` (Outside input) |
| [no-ai-slop](https://github.com/petergyang/no-ai-slop) | Its writing rules: no slogans, no catchphrases, plain words. | The site and this README ([#9](https://github.com/vibhortayal/agentic-team-oss/pull/9)) |
| [Atoms](https://atoms.dev) (a paid product, not open source) | A friendlier feel: pick an idea and see who joins, and updates that say who is working. | The picker in the [demo lesson](learn/demo.html), Ella's status updates ([#23](https://github.com/vibhortayal/agentic-team-oss/pull/23)) |

## Projects we learned from

We read these closely and compared them with our team. We didn't take code or rules from them, but they changed how we think about it.

- **[Quarterdeck](https://github.com/shannonbay/Quarterdeck).** Besides the rule above, two ideas we may try after our first pilot: trust earned one kind of action at a time, and turning the owner's "no" into a rule.
- **[Everything Claude Code](https://github.com/affaan-m/ECC).** Comparing our team with it showed our full team was too heavy for a small app. That's one reason small apps now take a light path: Ella, one builder and one independent check ([#59](https://github.com/vibhortayal/agentic-team-oss/pull/59)).
- **[MetaGPT](https://github.com/FoundationAgents/MetaGPT).** One of the first projects to run AI agents as a software company with named roles.
- **[CCPM](https://github.com/automazeio/ccpm).** It keeps agent work in GitHub issues, as we do. Seeing it work gave us confidence in that choice.
- **[cc-sdd](https://github.com/gotalab/cc-sdd).** A fresh builder and a separate reviewer for each task, close to our builder and checker split.
- **[Archon](https://github.com/coleam00/Archon).** It shows what needs the person's attention and the cost of each run, two things we want on our board.

## Files we copied

Some skills in [skills/](skills/) are copied unchanged from these projects. Each folder has an `UPSTREAM.md` with the exact source and keeps its own licence.

- [anthropics/skills](https://github.com/anthropics/skills): frontend-design, webapp-testing
- [openai/skills](https://github.com/openai/skills): security-threat-model
- [trailofbits/skills](https://github.com/trailofbits/skills): differential-review, property-based-testing, sharp-edges
- [addyosmani/web-quality-skills](https://github.com/addyosmani/web-quality-skills): accessibility, core-web-vitals, performance
- [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills): security-and-hardening
- [ai-evals-course/evals-skills](https://github.com/ai-evals-course/evals-skills): eval-audit, generate-synthetic-data, validate-evaluator, write-code-eval, write-judge-prompt
- [grafana/skills](https://github.com/grafana/skills): k6
- [product-on-purpose/pm-skills](https://github.com/product-on-purpose/pm-skills): measure-instrumentation-spec
- [microsoft/hve-core](https://github.com/microsoft/hve-core): owasp-agentic, owasp-llm, built on the OWASP Foundation's Top 10 lists

## Tools we use

- **[SkillSpector](https://github.com/NVIDIA/SkillSpector)** by NVIDIA. Quinn scans every outside skill with it before the team adopts one.

The research behind the team's design, with every paper and article we read, is in [docs/research](docs/research/agentic-software-company-practices.md).

When we adopt something new from another project, we add it here in the same change.
