# Vision and roadmap

## Vision

Anyone with an idea, technical or not, can build it with a team of AI agents without learning how agentic coding works first. The person we design for uses phone apps, websites and a chat assistant every day but has never heard of GitHub, a repository or a deploy. An engineer shipping a production app uses the same team; only the amount of process and explanation changes.

It is a **portal**: the person signs in and sees all their projects, how far along each one is, and a button to start a new one. Inside a project they can chat with it, and it does the work.

**The product leads; the person decides.** Most people do not know what a good software process looks like, so the product does not wait to be told. From the team's playbooks and the project's profile it always knows the next sensible step, and it shows that step with what it is, why it matters now, and what happens if it is skipped. The person approves, changes or asks about it. Phases are shown in everyday words: idea, plan, build, test, launch, keep it running.

**A plan the person can read before anything starts.** From the intake interview the platform works out which playbooks the project needs, the steps the person will take themselves, and how much technical skill each step needs. Steps beyond the person's comfort can be handed to a **helper**: a more technical friend, family member or colleague they invite, who gets just those steps. Building a website was once a job for specialists, until site builders let everyday users make one step by step. This aims to do the same for software built by AI agents: we borrow the step-by-step, guided ideas of beginner app builders and one-click installers (we do not use them), keep a real engineering process underneath, and let the person learn how software is made as they go.

The person meets the Engagement Lead in a friendly chat, gets a recommended team they can accept or change, can talk to any agent to learn what it does or adjust it for their project, and then watches the work happen. They are asked only for the decisions that are truly theirs. Repos, issues, gates, model keys and costs stay underneath, visible to anyone who wants to look.

When the person does have to do something technical (create a GitHub account, approve a deploy, add a payment method for a model), a **guide** walks them through it one step at a time: what it is in everyday words, why it is needed, exactly what to click, and a short beginner resource if they want to learn more. Along the way they come to understand how software goes from idea to release, without being buried in detail.

## Positioning

**Guided, verified building that you own and learn from.** The agent team is the friendly face, not the pitch.

1. **Proof it works.** An independent checker, safety gates the builder cannot change, and evidence the person can understand. Speed alone is not the promise.
2. **The product leads.** It always shows the next sensible step, why it matters and what skipping it risks, so the person learns the process instead of guessing it.
3. **The whole lifecycle.** Not just the first build: release, monitoring, incidents, support and keeping the code healthy.
4. **Ownership.** The code and all project state live in the person's own repository; the team is open source and works with any agent tool.

What we will not try to win: the fastest first build or the most polished editor. Funded products do that well.

## Landscape (as of November 2026)

| Kind of product | What it does well | Where it stops |
|---|---|---|
| Multi-agent app builders with a named agent team for non-technical founders | Describe an app in plain words; a team of named agents (product manager, architect, engineer, researcher) builds it; login, database, payments and hosting included | Hosted on the vendor's platform; speed first; the team is the pitch rather than proof of quality |
| Prompt-to-app builders | Very fast first versions, good-looking interfaces, one-click deploy, code export | The person must lead; testing and security are largely up to them |
| Browser coding workspaces with an agent | Flexible, many languages, good for people who code | Built for developers |
| No-code agent builders | Building agents that automate tasks, not software | Not for building and running an app |

What the evidence says about beginners building with AI: practitioner accounts describe the code as mostly "fast but flawed", testing often skipped, and apps shipped without proper access control or with secrets in the code, by builders who cannot debug or secure what they made ([grey-literature review of 101 sources, 2025](https://arxiv.org/html/2510.00328v1)). That gap is where this team is aimed.

## Roadmap

| Phase | What it delivers | Status |
|---|---|---|
| **1. Plumbing** | The team itself: roles, principles, playbooks and templates; any-tool installers; state on GitHub; the foundation gate kit; project profiles; release, operate and improvement loops | In progress |
| **2. Prove it** | Run real projects with the plumbing as it is. The first is a non-coder's own small app, started from the one-line setup and published as a case study with their OK: the plan, check reports, cost against estimate and what went wrong. Retros, the first frozen eval cases, and the first quarterly role review tune the team from evidence | Next |
| **3. Front door** | The portal, built by the team as its own project in a separate private repo, installed like any user's project: a home page of projects and their progress, Ella's intake chat, team picker with agent introductions, per-project adjustments, the next-step card that leads the person through the lifecycle, the readable plan with a skill level per step, inviting a helper for chosen steps, the guide, and a "you're needed" list | Started: a progress board on your own computer that shows what's waiting on you, with a Settings page for keys. The rest follows once phase 2 produces evidence |
| **4. Package** | One-step setup for non-technical users (accounts, keys and hosting handled or guided) and the guide's step-by-step help for every human task | Later |

Each phase is entered on the owner's word, and the plumbing keeps improving through the [improvement loop](playbooks/improve.md) in every phase.
