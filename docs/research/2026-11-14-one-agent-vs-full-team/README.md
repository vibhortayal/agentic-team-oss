# Build-off: one agent, the full team, and two cheaper ways

14 November 2026. One small app, built four ways from the same brief, scored against a checklist written before any build. We ran it to answer two questions: does a very strong single agent make the full team unnecessary, and what do the different ways of building cost?

Short answer: on a small app, all four ways passed every check. The full team used far more than the others and caught one thing the others missed. This is one app, run once, so treat it as a first reading and not a law.

## Method

- **The job.** A one-page scorekeeper for a singing game, written as an owner would ask for it: [brief.md](brief.md), 13 plain lines, "don't ask me questions".
- **The score.** [scoring-checklist.md](scoring-checklist.md): 18 pass or fail checks, written before any build and never shown to a builder. [score.js](score.js) drives each finished app in a browser and runs them.
- **The four ways.** Each started in an empty folder with only the brief.
  1. *One agent:* one session on the strongest model builds, then a fresh session on the same model checks.
  2. *Full team:* the Engagement Lead runs the team's playbooks at the smallest profile, every role on the strongest model, without GitHub or CI.
  3. *Thrifty:* the smallest model builds, a mid model checks.
  4. *Balanced:* a strong model plans and checks, a mid model builds.
- **The measures.** Sessions, working time and tokens were read from the session transcripts with [tally.py](tally.py). "Working time" is time the agents were active, not time on the clock.
- **Extra probes.** After scoring we tried five things the checklist didn't cover ([extra.js](extra.js), [extra2.js](extra2.js)). They were chosen after the builds, so they are reported separately.

The four finished apps are in [apps/](apps/). Each is one file; open it in a browser.

## Results

| Way | Checks passed | Sessions | Working time | Usage, cheapest = 1 |
|---|---|---|---|---|
| Thrifty | 18 of 18 | 2 | 6 min | 1 |
| Balanced | 18 of 18 | 3 | 6 min | about 4 |
| One agent | 18 of 18 | 2 | 11 min | about 10 |
| Full team | 18 of 18 | 23 (16 before any code) | 134 min | about 140 |

### What "usage" means here

A token is a small piece of text, roughly three quarters of a word. Everything an agent reads and writes is counted in tokens, and both a subscription's allowance and a pay-per-use bill are worked out from them. Two things matter more than the raw count:

- **Which model.** A token on the strongest model counts for many times a token on the smallest one.
- **What kind.** Text the agent writes counts the most. New text it reads counts less. Text it re-reads from a few minutes ago (its own conversation so far) counts very little, but there is a lot of it.

So raw token counts alone mislead. The first three ways used almost the same number of tokens; they differ by up to ten times only because of which model did the work. The "usage" column weights each token by its model and kind, using one provider's public prices as the weights[^1]. That is the closest neutral measure we have. A subscription's allowance is weighted in a similar way, but providers don't publish the exact rule, so read the column as "roughly", not as a promise.

Tokens by model tier (thousands):

| Way | Tier | New text read | Text written | Re-read |
|---|---|---|---|---|
| Thrifty | smallest (builds) | 246 | 68 | 1,488 |
| | mid (checks) | 225 | 8 | 648 |
| Balanced | strong (plans, checks) | 334 | 20 | 1,218 |
| | mid (builds) | 124 | 32 | 1,206 |
| One agent | strongest | 441 | 78 | 3,475 |
| Full team | strongest | 5,635 | 1,141 | 60,056 |

Counted raw, the full team used about 13 times the tokens of any other way. Weighted, about 140 times the cheapest.

## What differed in the apps

On the 18 checks, nothing. On the extra probes:

| Probe | Thrifty | Balanced | One agent | Full team |
|---|---|---|---|---|
| A tap just after the buzzer doesn't score for the next team | no | no | no | **yes** |
| Accepts a letter outside A to Z | yes | no | yes | yes |
| Accepts such a letter with a vowel sign attached | yes | no | no | yes |
| A double tap on "Passed" doesn't skip a team | no | no | no | no |

The full team's one clear win, the late tap, came from its critic at the spec stage, before any code. Its independent check also blocked the first build once, for a real fault (a refresh lost the game after certain unusual letters), and passed the fix.

## What the full team spent its sessions on

- 16 of 23 sessions ran before any code was written.
- The smallest profile still produced 119 acceptance criteria and about 74,700 words across 58 files, for an app the others described in 3,000 to 7,600 words.
- The team's brief turned "must be easy to read on a phone" into "may work on a phone", under a standing yes from an owner who had said "don't ask me". The app still passed the phone check, but an owner requirement was weakened without a real yes.
- The retro step didn't run.

## Limits

- One small app, each way run once. Model output varies from run to run.
- No owner was present, so intake, teaching and approvals, a large part of what the team is for, were not tested.
- The full team ran without GitHub, CI or the gates, and with every role on the strongest model. Its usual mix of tiers would cost less.
- Running four ways at once hit a plan's short-term limit and paused the work for 20 minutes; that pause is not in the working times.
- The extra probes were chosen after the fact.

## What we'd change because of it

1. For a small app, default to one builder plus the independent check. The full roster earns its cost on bigger or riskier work.
2. Keep one "how will this go wrong" critique before the build. It found the only fault the others missed.
3. Give the Engagement Lead a size rule, so the amount of process follows the size and risk of the job.
4. Let the playbooks scale down. The smallest profile is still far too heavy for a one-page app.
5. Never weaken an owner requirement without a real yes, even under a standing one.

The first product of this test is already in the Engagement Lead's role: at intake she suggests one of three ways of building and the owner confirms.

## One strong agent or a team?

Before the build-off we compared the two on paper. What a current top-tier model does well alone: holds a whole small project in one context, plans and re-plans without a written handoff, runs and reads its own tests, drives a browser to look at its own work, and can start a helper session when it wants a second look. Detailed step-by-step role instructions written for weaker models can make such a model slower, not better.

What it doesn't replace:

- **A check by someone who didn't build it.** A fresh session with only the spec finds what the builder argued itself out of. Every way above kept this.
- **Rules the builder can't switch off.** Required checks and protected paths in GitHub hold whatever the agent decides.
- **A spending cap.**
- **One plain voice** for a person who has never built software, on their first day and after.
- **Something to look at:** a board that shows progress without reading code.
- **Cheaper models.** On small and mid models the split into roles still helps; this test's cheapest way was a two-model team.

The conclusion we drew: most of the ten roles can become skills of one agent for small work. The Engagement Lead and the independent check stay as they are.

## Product review, same week

A separate end-to-end review of the product reached a matching view. For developers, existing plugins already cover plan, build and review. For people who don't code, what is ours is the single plain voice, first-day setup, checks the builder can't switch off, the cost cap and the board. Its advice was to narrow, stop adding features, and learn from a first pilot user before any rewrite.

## Possible later experiments

- Repeat on a medium app (several screens, saved data, sign-in), where handoffs and context limits start to bite. This is the open question that matters most.
- Run each way three times to see the spread.
- Run the same job and checklist on other providers' coding agents. There is no standard benchmark for comparing cost across providers; the fair measure is cost per finished job: same job, same checklist, pass or fail, time, and what it used up.
- Run the full team with its normal mix of tiers and with GitHub in place.

[^1]: In money, at public pay-per-use prices on the day and counting re-read text at its discounted rate: about $0.80 (Thrifty), $3 (Balanced), $8 (one agent) and $114 (full team). The models were one provider's four tiers. On a subscription nobody is billed these amounts; they only show the proportions.
