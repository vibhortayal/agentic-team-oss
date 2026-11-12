#!/usr/bin/env python3
"""Self-test for the team's test tools. No model, no network, about a minute.

  python3 tools/sandbox/selftest.py

1. Plants mistakes in a copy of the repo; teamcheck static must catch each one.
2. Plants handoff mistakes in sandbox runs; the replayer must catch each one, and pass a clean run.
3. Runs eval cases with a scripted stand-in agent: every case's setup must build cleanly,
   an agent that does nothing must fail the cases, and a correct scripted fix loop
   (BLOCK, fix, PASS, owner merge) must pass end to end.
"""
import json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.dirname(HERE))
import teamcheck  # noqa: E402

results = []


def expect(name, ok, detail=""):
    results.append(ok)
    print(("ok    " if ok else "WRONG ") + name + ("" if ok or not detail else "\n      " + str(detail)[:400]))


def caught(errs, text):
    return any(text in e for e in errs)


# ---- 1. static checks ---------------------------------------------------------------

def static_tests():
    print("-- static checks catch planted mistakes")
    with tempfile.TemporaryDirectory() as tmp:
        for f in os.listdir(ROOT):
            if f in (".git", "evals"):
                continue
            src = os.path.join(ROOT, f)
            (shutil.copytree if os.path.isdir(src) else shutil.copy)(src, os.path.join(tmp, f))
        shutil.copytree(os.path.join(ROOT, "evals"), os.path.join(tmp, "evals"), ignore=shutil.ignore_patterns("runs"))
        expect("clean copy passes", not teamcheck.static(tmp), teamcheck.static(tmp))

        def edit(path, old, new):
            p = os.path.join(tmp, path)
            s = open(p).read()
            assert old in s, (path, old)
            open(p, "w").write(s.replace(old, new, 1))

        edit("roles/critic.md", "tier: deep", "tier: huge")
        edit("roles/ops.md", "name: ops", "name: opz")
        edit("roles/researcher.md", "# Researcher", "# Researcher\n\nUse opus for this.")
        edit("roles/verifier.md", "# Verifier", "# Verifier\n\n[x](../playbooks/build.md#no-such-heading) [y](missing.md)")
        edit("adapters/github/labels.sh", " critic architect", " architect")
        edit("playbooks/build.md", "# Build", "# Build\n\nAdd `human:dance` here.")
        edit("docs/github-state.md", "| Research question | `research` | researcher |", "| Research question | `research` | designer |")
        edit("evals/vera-passes-good-work/case.md", "kind: positive", "kind: maybe")
        edit("evals/vera-passes-good-work/case.md", "- no-event", "- teleport")
        edit("roles/budget-analyst.md", "skills: team-comment", "skills: team-comment, no-such-skill")
        edit("skills/explain-a-step/SKILL.md", "name: explain-a-step", "name: explain-step")
        edit("skills/debug-a-failure/SKILL.md", "## Steps", "## Steps\n\nSee [rules](../../principles.md).")
        edit("skills/testable-criteria/SKILL.md", "license: Apache-2.0\n", "")
        os.remove(os.path.join(tmp, "skills", "webapp-testing", "LICENSE.txt"))
        os.makedirs(os.path.join(tmp, "skills", "orphan"))
        open(os.path.join(tmp, "skills", "orphan", "SKILL.md"), "w").write("---\nname: orphan\ndescription: Nobody uses it.\nlicense: Apache-2.0\n---\n")
        open(os.path.join(tmp, "roles", "_template.md"), "a").close()
        edit("roles/architect.md", "**Grounded in:**", "**Based on:**")
        edit("docs/lifecycle.md", "[Handover test](../playbooks/production.md#handover-test)", "nothing yet")
        edit("skills/k6/UPSTREAM.md", "Copied unchanged", "Adapted")
        errs = teamcheck.static(tmp)
        for name, text in [("bad tier", "tier 'huge'"), ("name differs from file", "name is 'opz'"),
                           ("vendor model name in a role", "vendor name 'opus'"), ("broken anchor", "no heading for #no-such-heading"),
                           ("broken link", "broken link missing.md"), ("role without a label", "no label role:critic"),
                           ("label nobody creates", "`human:dance`"), ("unknown role in the handoff table", "'designer'"),
                           ("bad case kind", "kind must be positive or negative"), ("unknown check", "unknown check 'teleport'"),
                           ("a role naming a missing skill", "skill no-such-skill has no"), ("skill name differs from folder", "the folder is explain-a-step"),
                           ("a skill linking outside itself", "leaves debug-a-failure"), ("a skill with no licence", "testable-criteria/SKILL.md: no license"),
                           ("a copied skill without its licence", "copied skill without its LICENSE"), ("a skill no role uses", "skills/orphan: no role lists it"),
                           ("a role not grounded in outside practice", "architect.md: no 'Grounded in:'"),
                           ("a lifecycle stage with no rule", "has no rule linked"),
                           ("a copied skill that was changed", "k6/UPSTREAM.md: must say")]:
            expect("catches " + name, caught(errs, text), "\n".join(errs))


# ---- 2. replay ----------------------------------------------------------------------

def sandbox():
    tmp = tempfile.mkdtemp()
    origin, work = os.path.join(tmp, "origin.git"), os.path.join(tmp, "work")
    env = dict(os.environ, FAKE_GH_STATE=os.path.join(tmp, "s.json"), FAKE_GH_ORIGIN=origin,
               PATH=HERE + os.pathsep + os.environ["PATH"])
    subprocess.run("git init -q --bare %s && git init -q -b main %s && cd %s && echo x > a && git add a && "
                   "git -c user.name=t -c user.email=t@t commit -qm a && git remote add origin %s && git push -q origin main 2>/dev/null"
                   % (origin, work, work, origin), shell=True, check=True)
    subprocess.run(["bash", os.path.join(ROOT, "adapters", "github", "labels.sh"), "x"], env=dict(env, FAKE_GH_ACTOR="harness"),
                   capture_output=True, check=True)

    def gh(actor, *args):
        return subprocess.run([os.path.join(HERE, "gh"), *args], env=dict(env, FAKE_GH_ACTOR=actor), cwd=work, capture_output=True, text=True)
    return tmp, origin, work, env, gh


def team(frm, to, kind, **extra):
    ev = {"from": frm, "to": to, "kind": kind, **extra}
    nxt = "" if to == "owner" else "\n```\nYou are the X. Read .team/roles/%s.md and act on issue #1.\n```\n" % to
    return "**%s (%s) → %s** · %s\n\nbody%s\n<!-- team-event %s -->" % (frm, frm, to, kind, nxt, json.dumps(ev))


def replay_tests():
    print("-- replay catches planted handoff mistakes")
    tmp, origin, work, env, gh = sandbox()
    gh("engagement-lead", "issue", "create", "--title", "t", "--body", "b", "--label", "role:product-manager,stage:spec")
    gh("engagement-lead", "issue", "comment", "1", "--body", team("engagement-lead", "product-manager", "handoff"))
    gh("product-manager", "issue", "comment", "1", "--body", team("product-manager", "verifier", "handoff"))
    gh("verifier", "issue", "comment", "1", "--body", team("verifier", "implementer", "handoff"))
    clean = json.load(open(env["FAKE_GH_STATE"]))
    errs, warns = teamcheck.replay(clean)
    expect("a clean run replays clean", not errs, errs)
    expect("an unanswered handoff is a warning", caught(warns, "never picked up"), warns)

    def planted(name, text, *comments, labels=None, actor="implementer", merge=False):
        t2 = tempfile.mkdtemp()
        st = os.path.join(t2, "s.json")
        shutil.copy(env["FAKE_GH_STATE"], st)
        e2 = dict(env, FAKE_GH_STATE=st)
        for body in comments:
            subprocess.run([os.path.join(HERE, "gh"), "issue", "comment", "1", "--body", body], env=dict(e2, FAKE_GH_ACTOR=actor), cwd=work, capture_output=True)
        if labels:
            subprocess.run([os.path.join(HERE, "gh"), "issue", "edit", "1", *labels], env=dict(e2, FAKE_GH_ACTOR=actor), cwd=work, capture_output=True)
        if merge:
            subprocess.run("git checkout -q -B team/1-x && echo y >> a && git -c user.name=t -c user.email=t@t commit -qam y && git push -q -f origin team/1-x 2>/dev/null",
                           shell=True, cwd=work, check=True)
            subprocess.run([os.path.join(HERE, "gh"), "pr", "create", "--title", "t", "--body", "Closes #1", "--head", "team/1-x"],
                           env=dict(e2, FAKE_GH_ACTOR="implementer"), cwd=work, capture_output=True)
            subprocess.run([os.path.join(HERE, "gh"), "pr", "merge", "2"], env=dict(e2, FAKE_GH_ACTOR=merge), cwd=work, capture_output=True)
            subprocess.run("git checkout -q main", shell=True, cwd=work)
        errs, _ = teamcheck.replay(json.load(open(st)), origin=origin)
        expect("catches " + name, caught(errs, text), errs)

    planted("a team comment without its event line", "no team-event line", "**Ian (implementer) → Vera (verifier)** · handoff\n\nDone.")
    planted("broken event JSON", "not valid JSON", "**Ian (implementer) → Vera (verifier)**\n<!-- team-event {from:implementer} -->")
    planted("a verdict from the builder", "only the Verifier gives verdicts", team("implementer", "verifier", "verdict", verdict="PASS", rev="abc"))
    planted("a role acting out of turn", "acted on #1 after a handoff to implementer", team("critic", "verifier", "note"), actor="critic")
    planted("a handoff with no next prompt", "without a next prompt", "**Ian (implementer) → Vera (verifier)**\n<!-- team-event %s -->"
            % json.dumps({"from": "implementer", "to": "verifier", "kind": "handoff"}))
    planted("a fourth BLOCK", "BLOCK round 4", *[team("verifier", "implementer", "verdict", verdict="BLOCK", rev="a%d" % i, round=i) for i in range(1, 5)], actor="verifier")
    planted("asking a person without the label", "never added", team("implementer", "owner", "question", human="human:answer"))
    planted("two role labels", "2 role: labels", labels=["--add-label", "role:verifier"])
    planted("needs-human without a human: label", "go together", labels=["--add-label", "needs-human"])
    planted("an agent trying to merge", "tried to merge", merge="implementer")
    planted("a merge with no PASS", "without a PASS verdict", merge="owner")
    shutil.rmtree(tmp)


# ---- 3. harness with a scripted agent ---------------------------------------------------

STUB = r'''#!/usr/bin/env python3
# Stand-in agent for the self-test. STUB_MODE=idle does nothing; STUB_MODE=good plays the fix loop correctly.
import json, os, subprocess, sys
work, prompt, tier, budget, turns, out = sys.argv[1:7]
role, mode = os.environ["FAKE_GH_ACTOR"], os.environ.get("STUB_MODE", "idle")
def sh(cmd): return subprocess.run(cmd, shell=True, cwd=work, capture_output=True, text=True, check=True).stdout.strip()
def ev(d): return "<!-- team-event %s -->" % json.dumps(d)
def nxt(r, title): return "\n```\nYou are the %s. Read .team/roles/%s.md and act on issue #1.\n```\n" % (title, r)
def gh(*a): subprocess.run(["gh", *a], cwd=work, check=True, capture_output=True)
if mode == "good" and role in ("verifier", "implementer", "product-manager"):
    sh("git fetch -q origin && git checkout -q -B team/1-lines-option origin/team/1-lines-option")
    if role == "verifier":
        bug = 'text.count("\\n")' in open(os.path.join(work, "wc.py")).read()
        rev = sh("git rev-parse HEAD")
        state = json.load(open(os.environ["FAKE_GH_STATE"]))
        rnd = 1 + sum('"verdict"' in c["body"] for c in state["items"]["1"]["comments"])
        os.makedirs(os.path.join(work, "verification/1/checks"), exist_ok=True)
        open(os.path.join(work, "verification/1/checks/ac1.sh"), "w").write("printf 'a\\nb' > t && test \"$(python3 wc.py --lines t)\" = 2\n")
        v = "BLOCK" if bug else "PASS"
        json.dump({"issue": 1, "rev": rev, "verdict": v, "round": rnd, "checks": []}, open(os.path.join(work, "verification/1/verdict.json"), "w"))
        sh("git add -A && git commit -qm 'Verdict for #1' && git push -q origin HEAD 2>/dev/null")
        if bug:
            gh("issue", "edit", "1", "--remove-label", "role:verifier,stage:verifying", "--add-label", "role:implementer,stage:building")
            gh("issue", "comment", "1", "--body", "**Vera (verifier) → Ian (implementer)** · verdict · BLOCK\n\nAC1: 'a\\nb' gives 1, expected 2." + nxt("implementer", "Implementer") + ev({"from": "verifier", "to": "implementer", "kind": "verdict", "verdict": "BLOCK", "rev": rev, "round": rnd}))
        else:
            gh("pr", "review", "2", "--approve")
            gh("issue", "edit", "1", "--remove-label", "role:verifier", "--add-label", "role:product-manager")
            gh("issue", "comment", "1", "--body", "**Vera (verifier) → Priya (product-manager)** · verdict · PASS" + nxt("product-manager", "Product Manager") + ev({"from": "verifier", "to": "product-manager", "kind": "verdict", "verdict": "PASS", "rev": rev, "round": rnd}))
    elif role == "implementer":
        p = os.path.join(work, "wc.py")
        src = open(p).read().replace('text.count("\\n")', "len(text.splitlines())")
        open(p, "w").write(src)
        sh("git commit -qam 'Count a last line without a newline (#1)' && git push -q origin HEAD 2>/dev/null")
        rev = sh("git rev-parse HEAD")
        gh("issue", "edit", "1", "--remove-label", "role:implementer,stage:building", "--add-label", "role:verifier,stage:verifying")
        gh("issue", "comment", "1", "--body", "**Ian (implementer) → Vera (verifier)** · handoff\n\nFixed." + nxt("verifier", "Verifier") + ev({"from": "implementer", "to": "verifier", "kind": "handoff", "rev": rev}))
    elif role == "product-manager":
        gh("issue", "edit", "1", "--remove-label", "stage:verifying", "--add-label", "stage:review,needs-human,human:merge")
        gh("issue", "comment", "1", "--body", "**Priya (product-manager) → owner** · handoff\n\nPASS and checks green; please merge #2.\n" + ev({"from": "product-manager", "to": "owner", "kind": "handoff", "human": "human:merge"}))
    sh("git checkout -q main")
json.dump({"cost_usd": 0.0, "input_tokens": 0, "output_tokens": 0, "turns": 1, "output": "", "exit": 0}, open(out, "w"))
'''


def harness_tests():
    print("-- harness runs cases with a scripted agent")
    tmp = tempfile.mkdtemp()
    stub = os.path.join(tmp, "stub-agent.py")
    open(stub, "w").write(STUB)
    wrapper = os.path.join(tmp, "eval-agent.sh")
    open(wrapper, "w").write('#!/usr/bin/env bash\nexec python3 %s "$@"\n' % stub)
    runner = [sys.executable, os.path.join(HERE, "run_evals.py"), "--adapter", wrapper, "--max-usd", "1", "--outside-container"]

    def run(mode, *cases):
        out = os.path.join(tmp, mode + "-" + "-".join(cases)[:40])
        r = subprocess.run(runner + ["--out", out, *cases], env=dict(os.environ, STUB_MODE=mode), capture_output=True, text=True)
        report = open(os.path.join(out, "report.md")).read() if os.path.exists(os.path.join(out, "report.md")) else r.stdout + r.stderr
        return r.returncode, report, out

    code, report, out = run("idle", "--all")
    expect("every case's setup builds without a harness error", "✗ harness" not in report,
           "\n".join(l for l in report.splitlines() if "harness" in l))
    cases = [d for d in os.listdir(os.path.join(ROOT, "evals")) if os.path.exists(os.path.join(ROOT, "evals", d, "case.md"))]
    passed_idle = [l for l in report.splitlines() if l.startswith("| ") and "| pass |" in l]
    no_det = []
    for c in cases:
        txt = open(os.path.join(ROOT, "evals", c, "case.md")).read()
        if "# Rubric" in txt:
            no_det.append(c)  # an idle agent can pass the deterministic checks of a judged case; the judge fails it
    wrongly = [l for l in passed_idle if not any(c in l for c in no_det)]
    expect("an agent that does nothing fails every unjudged case", not wrongly, wrongly)
    expect("the ledger has one row per session", os.path.exists(os.path.join(out, "ledger.csv")))
    code, report, _ = run("idle", "vera-blocks-planted-bug")
    expect("an idle Verifier fails the planted-bug case", code == 1 and "no new team comment matches" in report, report[-600:])
    code, report, out = run("good", "e2e-fix-loop")
    expect("a correct fix loop passes end to end (BLOCK, fix, PASS, owner merge)", code == 0, report[-1500:])
    state = json.load(open(os.path.join(out, "e2e-fix-loop", "github.json")))
    expect("the owner merged it", state["items"]["2"].get("mergedBy") == "owner")
    shutil.rmtree(tmp)


if __name__ == "__main__":
    static_tests()
    replay_tests()
    harness_tests()
    print("\n%d ok, %d wrong" % (results.count(True), results.count(False)))
    sys.exit(0 if all(results) else 1)
