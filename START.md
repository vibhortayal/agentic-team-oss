# Start here (for the coding assistant)

The person asked you to set up Agentic Team in this folder and then hand over to Ella. They may be new to all of this: they know web search and a chat assistant, and maybe nothing else. Do the work yourself; ask them only for what needs their hands. Write to them in short, everyday sentences, one idea at a time.

Before the first step, tell them in two sentences what you're about to do and that the team itself is free. Say it takes a few minutes.

## Steps

1. **Check the folder.** Run your commands in the folder the person opened you in. If it's their home folder, or it holds files that look unrelated (photos, documents), don't install there. Suggest a new folder named after their idea, such as `~/code/grocery-list`, create it with their OK, and work there.
2. **Install Git if it's missing.** Run `git --version`. If Git is missing, explain it in one sentence ("a free program that keeps a history of your project's files"), ask for their OK, then install it yourself:
   - **Mac:** running `git --version` makes the Mac offer its developer tools, which include Git. Tell them to click Install in the box that pops up and wait a few minutes.
   - **Windows:** run `winget install --id Git.Git -e --source winget`. Tell them to click Yes when Windows asks. Git Bash comes with it; run the installers below with it. If your shell can't find Git afterwards, ask them to close and reopen you.
   - **Linux:** use the system's package manager, such as `sudo apt install git`. They type their computer password when asked.
   - If an install fails, give the download link https://git-scm.com/downloads and wait for them to say it's done.
3. **Get the team.** The team lives in `~/agentic-team`, shared by all their projects.
   - If that folder exists and is a Git copy of this repository, update it: `git -C ~/agentic-team pull --ff-only`.
   - If it doesn't exist, run `git clone https://github.com/vibhortayal/agentic-team-oss ~/agentic-team`.
   - If it exists but is something else, stop and ask.
4. **Install it into this folder.** If you are Claude Code, run `bash ~/agentic-team/adapters/claude-code/install.sh "$PWD"`. Otherwise run `bash ~/agentic-team/adapters/generic/install.sh "$PWD"`.
5. **Save a first snapshot.** If the folder isn't a Git project yet, run `git init`. Then run `git add -A` and `git commit -m "Add the agent team"`. If Git asks who they are, explain that it labels each snapshot with a name. Help them set `user.name` and `user.email`, and suggest the private email GitHub gives them so their own stays hidden.
6. **Connect to GitHub.** Ask if they have a GitHub account. If not, give them https://github.com/signup and wait: only a person can make one, because GitHub checks the email and asks a robot test. Then check for GitHub's command line tool with `gh --version`. If it's missing, ask for their OK and install it: on Windows `winget install --id GitHub.cli -e --source winget`; on a Mac `brew install gh` if Homebrew is there, otherwise send them the installer from https://cli.github.com; on Linux follow https://github.com/cli/cli#installation. Then run `gh auth login --hostname github.com --git-protocol https --web`. It shows a one-time code and opens their browser: tell them the code, and ask them to sign in and click Authorize. If your tool can't wait for it, ask them to run that line in their own terminal. Never ask for their GitHub password.
7. **Hand over to Ella.** Read `AGENTS.md` and `.team/roles/engagement-lead.md`, and from now on you are Ella. If the person already told you their idea, start her intake with it. If not, say hello as Ella and ask what they'd like to build.

## Rules while setting up

- Don't create accounts, online projects or anything that costs money. Ella does those later, with the person's OK.
- Install only Git and GitHub's command line tool here, each with their OK. Anything else the app needs, Ella sets up later.
- Never ask for a password, key or token, and never accept one pasted into the chat.
- If a step fails, say what happened in plain words and try one fix. If it fails again, stop and tell them what you'd try next.
- Don't explain more than the step needs. They can always ask "tell me more".
