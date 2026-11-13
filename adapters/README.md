# Installing the team into a project

Role files are tool-neutral. These scripts copy the team into a project and map it to one tool.

Most people never run them by hand. They paste one line into their coding assistant, which follows [START.md](../START.md): as Ella, it installs Git and GitHub's tool with their OK, signs them in, gets or updates the team in `~/agentic-team`, runs the right installer, makes the first commit and the private repo, then starts intake. In Claude Code, the plugin does the same: `/plugin install agentic-team --marketplace vibhortayal/agentic-team-oss`, then `/agentic-team:start`. The plugin lives in [claude-code/plugin/](claude-code/plugin/) and is listed by the repo's `.claude-plugin/marketplace.json`; check both with `claude plugin validate .` after a change.

```bash
adapters/generic/install.sh ~/code/my-project       # any tool that reads AGENTS.md
adapters/claude-code/install.sh ~/code/my-project   # Claude Code (runs the generic install first)
adapters/github/labels.sh <owner/repo>              # once per repo, needs gh signed in
adapters/github/settings.py status|fill|ask NAME    # in the project folder: repo variables and secrets from team-settings.json
```

The generic install writes `.team/` (every role, the principles, playbooks, templates, docs, the label script and a `VERSION` file) and, if the project has none, an `AGENTS.md` from the template. It builds the copy in a temporary folder and swaps it in only when complete, so a failed run leaves the old install alone. Every role is always installed so links resolve; a project hires roles in its `TEAM.md`. Commit the result and record the version in `TEAM.md`.

To pick up a tuned role, pull this repo, run the script again and commit the diff. Never edit `.team/` or `.claude/agents/` by hand in a project: the next install overwrites it and no other project benefits. Tune here instead ([improve](../playbooks/improve.md)).

## How a session plays a role

The owner opens a session with Ella and talks only to her. She and Priya start the other roles as subagents or background sessions, each told its role and handed its issue: "You are the Verifier. Read `.team/roles/verifier.md` and act on issue #42." A role reads its file, the issue and its comments, does the work, posts a team comment and swaps the labels ([github-state](../docs/github-state.md)). Fish roles always get a fresh session. Elephants may keep one, but their memory of record is the repo. In a tool that can't start sessions itself, Ella hands the owner the one line to paste.

## Skills

A skill is a folder in `skills/` with a `SKILL.md`: a how-to a role loads for one task, sometimes with scripts. They follow the open [Agent Skills format](https://agentskills.io/specification), so they aren't tied to one tool. A role lists its skills under `skills:` and links each one at the step that uses it, so a tool without skills support still finds it by following the link.

The generic install copies them to `.team/skills/` and links each into `.agents/skills/`, where Codex and other tools that support the format look. The Claude Code install also links them into `.claude/skills/`. Links are relative, so they survive a clone; on Windows, turn on Git's symlink support. A project's own skill with the same name as a team skill is left alone. Skills a project adopts at intake are real folders in `.agents/skills/`; for Claude Code, Otto also links each one into `.claude/skills/` in the same gate PR.

Some skills are copied unchanged from other projects; each of those has an `UPSTREAM.md` saying where from, at which commit and under which licence. Everything else is the team's own. Skills installed on the machine outside the team can still load in a session; the principles say the role wins whenever one disagrees.

## Tools

How each tool finds its rules file, as of November 2026. Tools change this often; check their docs if something doesn't load.

| Tool | Reads `AGENTS.md`? | Notes |
|---|---|---|
| OpenAI Codex | Yes | Nothing extra |
| Cursor | Yes | Nothing extra |
| Gemini CLI | Reads `GEMINI.md` | Set its context file name to `AGENTS.md`, or add a one-line `GEMINI.md` pointing at it. Not tested here |
| Claude Code | Reads `CLAUDE.md` | Use the Claude Code installer below |
| Anything else | Unknown | Point the tool at `AGENTS.md` as its project instructions |

Role files say `tier: deep | standard | fast` and `capabilities: read, search, web, write, edit, shell` (or `all`). Map them to the tool's models and permissions: deep is your strongest reasoning model, standard a strong coding model, fast the cheap one. Record the mapping in `TEAM.md` if it isn't the default.

## Claude Code

The installer runs the generic install, then writes each role as a subagent in `.claude/agents/<role>.md`. It maps `tier` to `model` (deep to opus, standard to sonnet, fast to haiku) and `capabilities` to `tools` (`all` leaves tools out, so the agent inherits everything). It turns `skills:` into a list, so Claude Code loads those skills when the subagent starts. It drops `memory:`; Claude Code ignores the other extra fields. It writes a one-line `CLAUDE.md` (`@AGENTS.md`), or adds that line to an existing one, and removes the old `.claude/team/` copy if present.

The aliases follow the current model of each tier. To pin an exact model for one project, edit the installed subagent after each install and record why in that project's decision log. Never put a vendor model id in a role file here.

Claude Code sessions in the cloud may only push to a `claude/...` branch, which the gate doesn't know. Their PRs carry a `Team branch: <name>` line in the description so the gate applies that class ([PR classes](../templates/foundation/README.md#pull-request-classes)).

Subagents can't message each other, so the main session routes ([who runs the handoffs](../playbooks/build.md#who-runs-the-handoffs)). The main session is Ella. Subagents can't start subagents of their own, so Ella makes every call: `product-manager` to draft and run the spec review, then, following Priya's ticket flow, `verifier` to prepare, `implementer` with the full handoff, and `verifier` with the spec and revision only, asking for the check list before it reads the diff. For research it calls `researcher` twice in parallel, informed and independent, then `critic`. For internal and production projects Vera's approving run is a separate session holding the checker key, not a subagent.
