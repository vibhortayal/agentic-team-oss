# AGENTS.md (for working on agentic-team itself)

This repo defines a company of AI agents: roles, principles, playbooks and templates. The team itself is plain Markdown and shell (plus the standard-library Python gate scripts in `templates/foundation/`), and must stay usable by any agent tool. The dashboard is built by the team in its own repo, as a project like any other; no app code lives here.

- Read `README.md` and `principles.md` before changing anything. The evidence behind the design is in `docs/research/`.
- Role files use neutral frontmatter (`tier`, `capabilities`). Never put one vendor's model names or tool names in a role, playbook or template. Vendor-specific mapping belongs only in `adapters/<tool>/`.
- Keep the repo generic: no names of specific users, companies or projects in any file.
- Tune roles here, never in a project's installed copy ([playbooks/improve.md](playbooks/improve.md)). Explain each change to a rule or role in its pull request.
- After changing the gate kit, run `bash templates/foundation/tests/selftest.sh`; every planted violation must be caught.
- Check an installer after changing it: run it into a scratch directory and confirm every role installs and its links resolve.
