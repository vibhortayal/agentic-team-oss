# AGENTS.md (for working on agentic-team itself)

This repo is an open-source multi-agent development framework: a company of AI agents defined as roles, principles, playbooks and templates. To beginners we call it "an AI team that helps you build your app"; use those two names, not "tool", "product" or "skill". The team itself is plain Markdown and shell (plus standard-library Python: the gate scripts in `templates/foundation/`, the test tools in `tools/` and the skill scripts in `skills/`; a skill that drives a browser also needs Playwright, installed in the project, not here), and must stay usable by any agent tool. The dashboard is built by the team in its own repo, as a project like any other; no app code lives here.

- Read `README.md` and `principles.md` before changing anything. The evidence behind the design is in `docs/research/`.
- Role files use neutral frontmatter (`tier`, `capabilities`). Never put one vendor's model names or tool names in a role, playbook or template. Vendor-specific mapping belongs only in `adapters/<tool>/`.
- Keep the repo generic: no names of specific users, companies or projects in any file.
- Tune roles here, never in a project's installed copy ([playbooks/improve.md](playbooks/improve.md)). Explain each change to a rule or role in its pull request.
- After changing the gate kit, run `bash templates/foundation/tests/selftest.sh`; every planted violation must be caught.
- After changing a role, skill, playbook, template, adapter or tool, run `python3 tools/teamcheck.py` (it also runs every installer into a scratch folder and checks the links) and `python3 tools/sandbox/selftest.py`. Both are free and CI runs them too. Run model cases only on demand, in Docker, with a spend cap ([testing the team](playbooks/improve.md#testing-the-team)).
