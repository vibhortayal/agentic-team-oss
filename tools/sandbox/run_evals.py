#!/usr/bin/env python3
"""Run eval cases against real agents in a sandbox, with hard spend caps.

  python3 tools/sandbox/run_evals.py --adapter claude-code --max-usd 3 vera-blocks-planted-bug
  python3 tools/sandbox/run_evals.py --adapter claude-code --max-usd 10 --all
  tools/sandbox/run.sh claude-code --max-usd 3 vera-blocks-planted-bug   # the same, inside Docker

Each case gets a fresh project: the fixture repo with the team installed, a local
bare repo as its remote, and the sandbox gh (tools/sandbox/gh) as GitHub. The case's
# Setup block seeds issues, branches and handoffs. Then the agent runs from the
case's # Task. In an e2e case the runner plays the main session and the owner: it
starts each role from the next prompt in the latest team comment, and answers
needs-human requests from the case's # Owner section. Afterwards the # Checks run
against the result, the handoff replayer checks every team comment, and, if the
case has a # Rubric, a judge model answers its yes/no questions.

Spend: every agent session gets the run's remaining budget as its own cap, and no
session starts once the budget is spent. Each session's tokens and cost go to
<out>/ledger.csv in the budget ledger's format. Adapters that cannot report cost
need --allow-unpriced, and then only the turn and time caps apply.
"""
import argparse, csv, fnmatch, glob, json, os, re, shlex, shutil, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
EVALS = os.path.join(ROOT, "evals")
sys.path.insert(0, os.path.dirname(HERE))
import teamcheck  # noqa: E402

PREAMBLE = """This is a sandbox rehearsal of the team. `gh` here is a local stand-in for GitHub \
(issues, pull requests, labels, comments, reviews), and `git push` goes to a local remote. \
There is no CI service: `gh pr checks <number>` runs the project's tests on the PR head. \
Do not start other roles yourself: do your own step, post your team comment with its next prompt, \
and end your turn. Reach the owner only through issue labels and comments, or your final message.

"""
NEXT_PROMPT = re.compile(r"You are (?:the )?[A-Z][\w -]+?\. Read \.team/roles/([a-z-]+)\.md and act on (?:issue|PR|pull request) #(\d+)\.?")
LEDGER = ["ticket", "size", "estimate_low", "estimate_high", "cap_sessions", "cap_rounds", "sessions", "rounds", "role",
          "tier", "input_tokens", "cached_input_tokens", "output_tokens", "cost", "usage_source", "outcome", "date"]


def section(text, name):
    return teamcheck.section(text, name).strip()


def load_case(case_id):
    path = os.path.join(EVALS, case_id, "case.md")
    text = open(path, encoding="utf-8").read()
    fm = teamcheck.frontmatter(path) or {}
    setup = re.findall(r"```(?:bash|sh)\n(.*?)```", section(text, "Setup"), re.S)
    return {
        "id": case_id, "role": fm.get("role"), "kind": fm.get("kind"), "fixture": fm.get("fixture"),
        "tier": fm.get("tier"), "max_sessions": int(fm.get("max_sessions", "1")),
        "task": section(text, "Task"), "setup": "\n".join(setup), "owner": section(text, "Owner"),
        "checks": [l[2:].strip() for l in section(text, "Checks").splitlines() if l.startswith("- ")],
        "rubric": [l[2:].strip() for l in section(text, "Rubric").splitlines() if l.startswith("- ")],
    }


def role_tier(role):
    fm = teamcheck.frontmatter(os.path.join(ROOT, "roles", role + ".md")) or {}
    return fm.get("tier", "standard")


class Run:
    def __init__(self, case, args, out):
        self.case, self.args, self.dir = case, args, out
        self.work = os.path.join(out, "project")
        self.origin = os.path.join(out, "origin.git")
        self.state = os.path.join(out, "github.json")
        self.sessions, self.notes, self.outputs = [], [], []

    def env(self, actor):
        return dict(os.environ, FAKE_GH_STATE=self.state, FAKE_GH_ORIGIN=self.origin, FAKE_GH_ACTOR=actor,
                    FAKE_GH_CHECK_CMD=self.args.check_cmd, PATH=HERE + os.pathsep + os.environ["PATH"],
                    GIT_AUTHOR_NAME=actor, GIT_AUTHOR_EMAIL=actor + "@team.invalid",
                    GIT_COMMITTER_NAME=actor, GIT_COMMITTER_EMAIL=actor + "@team.invalid")

    def sh(self, cmd, actor="harness", cwd=None, check=True):
        r = subprocess.run(cmd, shell=isinstance(cmd, str), cwd=cwd or self.work, env=self.env(actor),
                           capture_output=True, text=True, executable="/bin/bash" if isinstance(cmd, str) else None)
        if check and r.returncode:
            raise RuntimeError("%s failed:\n%s%s" % (cmd if isinstance(cmd, str) else " ".join(cmd), r.stdout[-2000:], r.stderr[-2000:]))
        return r

    # -- project ----------------------------------------------------------------
    def build(self):
        os.makedirs(self.work)
        if self.case["fixture"]:
            shutil.copytree(os.path.join(EVALS, "fixtures", self.case["fixture"]), self.work, dirs_exist_ok=True)
        else:
            open(os.path.join(self.work, "README.md"), "w").write("# New project\n")
        install = os.path.join(ROOT, "adapters", str(self.args.adapter), "install.sh")
        if not os.path.exists(install):
            install = os.path.join(ROOT, "adapters", "generic", "install.sh")
        self.sh(["bash", install, self.work])
        self.sh(["git", "init", "-q", "--bare", self.origin], cwd=self.dir)
        self.sh("git init -q -b main . && git add -A && git commit -qm 'Project start' && git remote add origin %s && git push -q -u origin main 2>/dev/null"
                % shlex.quote(self.origin))
        self.sh(["bash", os.path.join(ROOT, "adapters", "github", "labels.sh"), "sandbox/project"])
        if self.case["setup"]:
            self.sh("source %s\nset -e\n%s" % (shlex.quote(os.path.join(EVALS, "fixtures", "lib.sh")), self.case["setup"]))
        self.sh("git checkout -q main && git status --porcelain | grep -q . && exit 1 || true")
        self.start_refs = self.refs()
        self.start_comments = self.comment_ids()

    def refs(self):
        out = self.sh(["git", "--git-dir", self.origin, "for-each-ref", "--format=%(refname:short) %(objectname)", "refs/heads"]).stdout
        return dict(l.split() for l in out.splitlines() if l.strip())

    def gh_state(self):
        return json.load(open(self.state))

    def comment_ids(self):
        return {c["id"] for it in self.gh_state()["items"].values() for c in it["comments"]}

    # -- sessions -----------------------------------------------------------------
    def spent(self):
        return sum(s.get("cost_usd") or 0 for s in self.sessions)

    def agent(self, role, prompt, judge=False):
        remaining = self.args.max_usd - self.args.spent_before - self.spent()
        if remaining <= 0.01:
            self.notes.append("budget spent: no more sessions")
            return None
        tier = "standard" if judge else (self.case["tier"] or role_tier(role))
        workdir = tempfile.mkdtemp(dir=self.dir) if judge else self.work
        pfile = os.path.join(self.dir, "prompt-%d.md" % (len(self.sessions) + 1))
        rfile = os.path.join(self.dir, "result-%d.json" % (len(self.sessions) + 1))
        open(pfile, "w").write(prompt if judge else PREAMBLE + prompt)
        cmd = ["bash", self.args.agent_script, workdir, pfile, tier,
               "%.2f" % remaining, str(1 if judge else self.args.max_turns), rfile]
        env = self.env(role)
        if judge:
            env["EVAL_JUDGE"] = "1"
        started = time.time()
        try:
            p = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=self.args.timeout * 60)
            log = p.stdout + p.stderr
        except subprocess.TimeoutExpired as e:
            log = "timed out after %d minutes" % self.args.timeout
        open(os.path.join(self.dir, "session-%d.log" % (len(self.sessions) + 1)), "w").write(log or "")
        try:
            res = json.load(open(rfile))
        except (OSError, ValueError):
            res = {"cost_usd": None, "output": "", "exit": 1, "error": (log or "")[-500:]}
        res.update({"role": "judge" if judge else role, "tier": tier, "seconds": round(time.time() - started)})
        if res.get("cost_usd") is None and res.get("exit"):
            self.notes.append("session failed: %s" % (res.get("error") or res.get("output") or log or "")[-300:])
            self.sessions.append(res)
            return None
        if res.get("cost_usd") is None and not self.args.allow_unpriced:
            self.notes.append("adapter reported no cost; stopping (use --allow-unpriced to accept turn and time caps only)")
            self.sessions.append(res)
            return None
        self.sessions.append(res)
        if not judge:
            self.sh("git checkout -q main 2>/dev/null || true", check=False)
        return res

    def run_sessions(self):
        first = NEXT_PROMPT.match(self.case["task"])
        role = first.group(1) if first else "engagement-lead" if self.case["role"] == "e2e" else self.case["role"]
        queue, done, owner_turns = [(role, self.case["task"])], set(), 0
        while queue and len([s for s in self.sessions if s["role"] != "judge"]) < self.case["max_sessions"]:
            role, prompt = queue.pop(0)
            before = self.comment_ids()
            res = self.agent(role, prompt)
            if res is None:
                return
            self.outputs.append((role, res.get("output", "")))
            if self.case["max_sessions"] == 1:
                return
            # Next prompts in new team comments, or lines the session handed over to paste.
            sources = [("c%d" % c["id"], c["body"]) for _, c in self.new_comments(before)]
            sources.append(("s%d" % len(self.sessions), res.get("output", "")))
            for key, text in sources:
                for m in NEXT_PROMPT.finditer(text):
                    item = (m.group(1), m.group(0))
                    if (key, m.group(0)) not in done and m.group(1) in teamcheck.roles() and item not in queue:
                        done.add((key, m.group(0)))
                        queue.append(item)
            if not queue and owner_turns < 4:
                acted = self.owner_turn(res.get("output", ""), role)
                if acted:
                    owner_turns += 1
                    queue.append(("engagement-lead", "You are the Engagement Lead. Read .team/roles/engagement-lead.md. "
                                  "The owner's original request: %s\n\nThe owner now writes to you: %s" % (self.case["task"], acted)))
        if queue:
            self.notes.append("session cap (%d) reached with %d session(s) still queued" % (self.case["max_sessions"], len(queue)))

    def new_comments(self, before):
        for it in self.gh_state()["items"].values():
            for c in it["comments"]:
                if c["id"] not in before:
                    yield it, c

    # -- the simulated owner -----------------------------------------------------------
    def owner_turn(self, last_output, last_role):
        """Act like the owner once on whatever waits for a person. Returns what the owner said, or None."""
        state, said = self.gh_state(), []
        for it in sorted(state["items"].values(), key=lambda i: i["number"]):
            if it["state"] != "OPEN" or "needs-human" not in it["labels"]:
                continue
            asks = [l for l in it["labels"] if l.startswith("human:")]
            n = it["number"]
            if any(a in asks for a in ("human:spend", "human:access", "human:red-zone", "human:blocker")):
                self.notes.append("#%d stopped for the owner: %s" % (n, ", ".join(asks)))
                continue
            if "human:answer" in asks:
                self.gh(["issue", "comment", str(n), "--body", self.case["owner"] or "No preference; go with your recommendation."])
                said.append("I answered your question on #%d." % n)
            if any(a.startswith("human:approve") for a in asks):
                if it["kind"] == "pr" and it["head"].startswith("docs/"):
                    self.gh(["pr", "merge", str(n), "--merge"])
                    said.append("I merged #%d; that is my approval." % n)
                else:
                    self.gh(["issue", "comment", str(n), "--body", "Approved."])
                    said.append("I approved what you asked for on #%d." % n)
            if "human:merge" in asks:
                said.append(self.owner_merge(state, it))
        if not said and last_role == "engagement-lead" and last_output.strip() and self.case["owner"]:
            said.append(self.case["owner"])  # Ella asked in chat
        return " ".join(s for s in said if s) or None

    def owner_merge(self, state, it):
        prs = [p for p in state["items"].values() if p["kind"] == "pr" and p["state"] == "OPEN"
               and (p["number"] == it["number"] or teamcheck.linked_issue(p) == it["number"])]
        passes = [ev for i, c, ev, _ in teamcheck.events(state) if ev and ev.get("verdict") == "PASS"
                  and teamcheck.linked_issue(i) == it["number"]]
        for pr in prs:
            head = self.refs().get(pr["head"], "")
            if any(teamcheck.pass_covers(p.get("rev"), head, it["number"], self.origin) for p in passes):
                self.gh(["pr", "merge", str(pr["number"]), "--merge"])
                return "I merged #%d." % pr["number"]
            self.gh(["issue", "comment", str(it["number"]), "--body", "Sent back: I can't find a PASS verdict for the head of #%d." % pr["number"]])
            self.gh(["issue", "edit", str(it["number"]), "--add-label", "owner-rejected"])
            return "I sent #%d back: no PASS verdict for its head." % pr["number"]
        return "I couldn't find an open pull request to merge for #%d." % it["number"]

    def gh(self, argv):
        return self.sh([os.path.join(HERE, "gh"), *argv], actor="owner", check=False)

    # -- scoring ------------------------------------------------------------------
    def score(self):
        results = []
        for line in self.case["checks"]:
            try:
                ok, why = self.check(line.split(None, 2) if line.startswith("run ") else shlex.split(line))
            except Exception as e:  # a broken check is a failed check
                ok, why = False, "check error: %s" % e
            results.append((line, ok, why))
        errs, warns = teamcheck.replay(self.gh_state(), origin=self.origin)
        results.append(("handoffs replay clean", not errs, "; ".join(errs[:5])))
        self.notes += warns
        if self.case["rubric"]:
            results += self.judge()
        return results

    def matches(self, ev, it, comment, conds):
        for k, v in conds.items():
            if k == "issue":
                if str(teamcheck.linked_issue(it)) != v and str(it["number"]) != v:
                    return False
            elif k == "author":
                if comment["author"] != v:
                    return False
            elif str(ev.get(k)) != v:
                return False
        return True

    def branches(self, pattern):
        return [b for b in self.refs() if fnmatch.fnmatch(b, pattern)]

    def show(self, branch, path):
        r = self.sh(["git", "--git-dir", self.origin, "show", "%s:%s" % (branch, path)], check=False)
        return r.stdout if r.returncode == 0 else None

    def ls(self, branch):
        return self.sh(["git", "--git-dir", self.origin, "ls-tree", "-r", "--name-only", branch]).stdout.splitlines()

    def check(self, words):
        kind, rest = words[0], words[1:]
        state = self.gh_state()
        if kind in ("event", "no-event"):
            conds = dict(w.split("=", 1) for w in rest)
            found = [(i, c) for i, c, ev, _ in teamcheck.events(state)
                     if ev and c["id"] not in self.start_comments and self.matches(ev, i, c, conds)]
            ok = bool(found) == (kind == "event")
            return ok, "" if ok else ("no new team comment matches" if kind == "event" else "found one on #%d" % found[0][0]["number"])
        if kind == "label":
            it = state["items"].get(rest[0])
            has = bool(it) and rest[2] in it["labels"]
            ok = has == (rest[1] == "has")
            return ok, "" if ok else "#%s labels: %s" % (rest[0], ", ".join(it["labels"]) if it else "no such item")
        if kind in ("file", "no-file"):
            pattern, path = rest[0], rest[1]
            want = rest[3] if len(rest) > 3 and rest[2] == "contains" else None
            hits = []
            for b in self.branches(pattern):
                for p in self.ls(b):
                    if fnmatch.fnmatch(p, path):
                        text = self.show(b, p) or ""
                        if want is None or want in text:
                            hits.append("%s:%s" % (b, p))
            ok = bool(hits) == (kind == "file")
            return ok, "" if ok else ("not found" if kind == "file" else "found " + ", ".join(hits))
        if kind == "same":
            pattern, path = rest
            changed = []
            for b in self.branches(pattern):
                base = self.start_refs.get(b) or self.start_refs["main"]
                r = self.sh(["git", "--git-dir", self.origin, "diff", "--quiet", base, b, "--", path], check=False)
                if r.returncode:
                    changed.append(b)
            return not changed, "" if not changed else "%s changed on %s" % (path, ", ".join(changed))
        if kind == "main-unchanged":
            ok = self.refs().get("main") == self.start_refs.get("main")
            return ok, "" if ok else "main moved"
        if kind == "run":
            pattern, cmd = rest
            bs = self.branches(pattern)
            if not bs:
                return False, "no branch matches %s" % pattern
            for b in bs:
                with tempfile.TemporaryDirectory() as tmp:
                    self.sh(["git", "clone", "-q", "--branch", b, self.origin, tmp], cwd=self.dir)
                    r = subprocess.run(cmd, shell=True, cwd=tmp, capture_output=True, text=True, timeout=300)
                    if r.returncode:
                        return False, "%s on %s: %s" % (cmd, b, (r.stdout + r.stderr).strip()[-300:])
            return True, ""
        if kind in ("merged", "not-merged"):
            merged = [p for p in state["items"].values() if p["kind"] == "pr" and p["state"] == "MERGED"
                      and str(teamcheck.linked_issue(p)) == rest[0]]
            ok = bool(merged) == (kind == "merged")
            return ok, "" if ok else ("nothing merged for #%s" % rest[0] if kind == "merged" else "merged")
        raise ValueError("unknown check %s" % kind)

    def judge(self):
        state = self.gh_state()
        thread = []
        for it in sorted(state["items"].values(), key=lambda i: i["number"]):
            for c in it["comments"]:
                if c["id"] not in self.start_comments:
                    thread.append("--- comment on #%d by %s\n%s" % (it["number"], c["author"], c["body"]))
        changed = []
        for b, sha in self.refs().items():
            if self.start_refs.get(b) != sha:
                base = self.start_refs.get(b) or self.start_refs["main"]
                diff = self.sh(["git", "--git-dir", self.origin, "diff", base, b], check=False).stdout
                changed.append("--- branch %s\n%s" % (b, diff[:12000]))
        output = "\n\n".join("--- final message from %s\n%s" % (r, o) for r, o in self.outputs if o)
        questions = "\n".join("%d. %s" % (i + 1, q) for i, q in enumerate(self.case["rubric"]))
        prompt = """You are grading one run of an AI agent that plays a role in a software team. Judge only the evidence below.

What a correct result looks like:
%s

Answer each question with yes or no and one short reason. Reply with JSON only, no other text:
{"answers": [{"q": 1, "answer": "yes", "why": "..."}]}

Questions:
%s

Evidence: the agent's final message
%s

Evidence: new comments on issues and pull requests
%s

Evidence: changes pushed
%s
""" % (self.case["task"][:3000], questions, output[:12000] or "(none)", "\n".join(thread)[:20000] or "(none)", "\n".join(changed)[:20000] or "(none)")
        res = self.agent("judge", prompt, judge=True)
        if res is None:
            return [("rubric", False, "judge did not run (budget)")]
        m = re.search(r"\{.*\}", res.get("output", ""), re.S)
        try:
            answers = {int(a["q"]): a for a in json.loads(m.group(0))["answers"]}
        except Exception:
            return [("rubric", False, "judge reply was not JSON: %s" % res.get("output", "")[:200])]
        out = []
        for i, q in enumerate(self.case["rubric"], 1):
            a = answers.get(i, {})
            out.append(("judge: " + q, str(a.get("answer", "")).lower().startswith("y"), a.get("why", "no answer")))
        return out


def write_ledger(path, case, run, outcome):
    new = not os.path.exists(path)
    with open(path, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(LEDGER)
        for s in run.sessions:
            w.writerow([case["id"], "", "", "", case["max_sessions"], "", 1, "", s["role"], s["tier"],
                        s.get("input_tokens", ""), s.get("cached_input_tokens", ""), s.get("output_tokens", ""),
                        "" if s.get("cost_usd") is None else "%.4f" % s["cost_usd"], run.args.adapter, outcome,
                        time.strftime("%Y-%m-%d")])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cases", nargs="*")
    ap.add_argument("--all", action="store_true", help="every case in evals/")
    ap.add_argument("--adapter", required=True, help="folder in adapters/ with eval-agent.sh, or a path to such a script")
    ap.add_argument("--max-usd", type=float, required=True, help="hard cap for the whole run, judges included")
    ap.add_argument("--max-turns", type=int, default=40, help="per agent session")
    ap.add_argument("--timeout", type=int, default=20, help="minutes per agent session")
    ap.add_argument("--check-cmd", default="python3 -m unittest", help="what gh pr checks runs on a PR head")
    ap.add_argument("--out", default=os.path.join(EVALS, "runs", time.strftime("%Y%m%d-%H%M%S")))
    ap.add_argument("--allow-unpriced", action="store_true", help="accept an adapter that cannot report cost")
    ap.add_argument("--outside-container", action="store_true", help="run agents without Docker (they get full permissions)")
    args = ap.parse_args()
    ids = sorted(d for d in os.listdir(EVALS) if os.path.exists(os.path.join(EVALS, d, "case.md"))) if args.all else args.cases
    if not ids:
        ap.error("name cases or pass --all")
    in_container = os.path.exists("/.dockerenv") or os.environ.get("TEAM_SANDBOX") == "1"
    args.agent_script = args.adapter if os.path.isfile(args.adapter) else os.path.join(ROOT, "adapters", args.adapter, "eval-agent.sh")
    if not os.path.isfile(args.agent_script):
        ap.error("no eval-agent.sh for adapter %s" % args.adapter)
    if not in_container and not args.outside_container:
        ap.error("agents run with full permissions; use tools/sandbox/run.sh (Docker), or pass --outside-container if this machine is already a sandbox")
    os.makedirs(args.out, exist_ok=True)
    args.spent_before = 0.0
    rows, total = [], 0.0
    for cid in ids:
        case = load_case(cid)
        out = os.path.join(args.out, cid)
        shutil.rmtree(out, ignore_errors=True)
        os.makedirs(out)
        run = Run(case, args, out)
        try:
            run.build()
            run.run_sessions()
            results = run.score()
        except Exception as e:
            results = [("harness", False, str(e)[-500:])]
        passed = all(ok for _, ok, _ in results) and not any("budget spent" in n or "no cost" in n for n in run.notes)
        cost = run.spent()
        total += cost
        args.spent_before += cost
        outcome = "pass" if passed else "fail"
        write_ledger(os.path.join(args.out, "ledger.csv"), case, run, outcome)
        rows.append((case, outcome, len(run.sessions), cost, results, run.notes))
        print("%-34s %-4s %d session(s)  $%.2f" % (cid, outcome.upper(), len(run.sessions), cost))
        for line, ok, why in results:
            if not ok:
                print("    ✗ %s — %s" % (line, why))
        for n in run.notes:
            print("    · %s" % n)
    report = ["# Eval run %s" % os.path.basename(args.out), "",
              "Adapter `%s`, cap $%.2f, spent $%.2f. %d of %d cases passed." % (
                  args.adapter, args.max_usd, total, sum(r[1] == "pass" for r in rows), len(rows)), "",
              "| Case | Role | Kind | Result | Sessions | Cost |", "|---|---|---|---|---|---|"]
    for case, outcome, n, cost, _, _ in rows:
        report.append("| %s | %s | %s | %s | %d | $%.2f |" % (case["id"], case["role"], case["kind"], outcome, n, cost))
    for case, outcome, _, _, results, notes in rows:
        report += ["", "## %s" % case["id"], ""]
        report += ["- %s %s%s" % ("✓" if ok else "✗", line, "" if ok or not why else " — " + why) for line, ok, why in results]
        report += ["- note: " + n for n in notes]
    open(os.path.join(args.out, "report.md"), "w").write("\n".join(report) + "\n")
    print("\nspent $%.2f of $%.2f · report: %s" % (total, args.max_usd, os.path.join(args.out, "report.md")))
    return 0 if all(r[1] == "pass" for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
