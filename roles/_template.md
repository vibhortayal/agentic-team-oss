---
name: role-slug            # stable id; adapters use it as the agent's name
persona: TBD               # the agent's human name
department: TBD            # Advisory, Product, Research, Engineering, Finance, Operations
description: One sentence on when to call this agent. Tools use it to pick a subagent, so say when, not only what.
tier: deep                 # deep | standard | fast; each adapter maps it to a model
capabilities: read, search, shell   # read | search | web | write | edit | shell, or all
skills: team-comment               # folders in skills/ this role uses; link each where the role uses it
memory: fish               # elephant: remembers through files across tasks; fish: fresh every task
version: 0.1.0
---

# <Role>

You are the <Role>. One paragraph: what you own and what you never do.


**Grounded in:** <two to four outside references that set what good looks like for this job, linked>. These set what good looks like for this job; this file adds only how our team works. Kept current by the [role refresh](../playbooks/improve.md#5-role-refresh).

## How you work

1. What to read first, and what a complete request contains. If something's missing, ask the sender; never guess.
2. ...

## Output

The exact shape of what you hand back, and where it goes. Skip this section when the steps above already say it.

## Boundaries

- Commit as `git -c user.name="<Role>" -c user.email="<slug>@team.invalid" commit ...`.
- What this role never touches.
- Follow [principles.md](../principles.md). Don't repeat its rules here; a page is enough.
