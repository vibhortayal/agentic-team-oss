# Thanks for contributions

This team is built on other people's work. These are the projects we took ideas or files from, and the ones we learned from by comparing them with ours. If you like the team, give them a look and a star.

## Ideas we adopted

- **[AI Hero skills](https://github.com/mattpocock/skills)** by Matt Pocock. His grill-me skill asks one question at a time. Ella now does the same in her first interview, with her own suggested answer for each.
- **[The Home Repo pattern](https://www.aihero.dev/the-home-repo-pattern)**, also by Matt Pocock. One repo holds the shared rules and skills for all your projects. This repo works that way, and your copy of the team keeps a list of your projects so one update reaches them all.
- **[Superpowers](https://github.com/obra/superpowers)** by Jesse Vincent. Our debug-a-failure skill draws on its systematic-debugging skill.
- **[agent-ops-patterns](https://github.com/u00dxk2/agent-ops-patterns).** We used its "who decides what" map on our own team. It showed that the spending cap and the three-strikes stop were only instructions. Now a check on GitHub enforces both.
- **[Orbi](https://orbi.build).** It runs agent work as labels on GitHub, like we do. Reading it, together with that map, led to a receipt on each change and a watch mode for new checks.
- **[no-ai-slop](https://github.com/petergyang/no-ai-slop)**. Our site and README follow its writing rules: no slogans, no catchphrases, plain words.
- **[Atoms](https://atoms.dev).** A paid product, not open source. It showed us how to make the team feel friendly: an idea picker in the demo, and updates that say who is working.

## Projects we learned from

We read these closely and compared them with our team. We didn't take code or rules from them, but they changed how we think about it.

- **[Quarterdeck](https://github.com/shannonbay/Quarterdeck).** Text from outside, like an issue or a web page, should never count as instructions. Trust can be earned one kind of action at a time. And when the owner says no, the reason should become a rule.
- **[Everything Claude Code](https://github.com/affaan-m/ECC).** Comparing our team with it showed our full team was too heavy for a small app. That's why small apps now take a light path: Ella, one builder and one independent check.
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
