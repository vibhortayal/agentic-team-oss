#!/usr/bin/env python3
"""Free checks for the team itself: no model, no network, standard library only.

  python3 tools/teamcheck.py                 # everything below except replay
  python3 tools/teamcheck.py static          # role files, skills, vendor names, links, labels, handoff table, eval cases, plain words
  python3 tools/teamcheck.py install         # every installer, into a scratch folder; links still resolve
  python3 tools/teamcheck.py gates           # the gate kit's own self-test
  python3 tools/teamcheck.py replay STATE [--origin REPO]   # check a sandbox run's handoffs

Exit code 0 means every check passed. Each problem is one line: where, then what.
"""
import html, json, os, re, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAKE_GH = os.path.join(ROOT, "tools", "sandbox", "gh")

TIERS = {"deep", "standard", "fast"}
CAPS = {"read", "search", "web", "write", "edit", "shell"}
MEMORY = {"fish", "elephant"}
KINDS = {"handoff", "verdict", "blocker", "question", "report", "note", "approval"}
VERDICTS = {"PASS", "BLOCK", "INCONCLUSIVE"}
COORDINATORS = {"engagement-lead", "product-manager", "architect"}
# Tool and model names that must never appear in a role, playbook, template or the principles.
VENDOR = re.compile(r"\b(claude|anthropic|openai|chatgpt|gpt-?\d[\w.]*|gemini|codex|cursor|copilot|opus|sonnet|haiku|llama|mistral)\b", re.I)
NEUTRAL = ["roles", "playbooks", "templates", "skills", "principles.md"]
SKILL_NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
EVENT = re.compile(r"<!--\s*team-event\s+(.*?)\s*-->", re.S)
HEADER = re.compile(r"^\*\*[^*()]+\(([a-z-]+)\)\s*(?:→|->)")


def rel(p):
    return os.path.relpath(p, ROOT)


def md_files(base, skip=()):
    for d, dirs, files in os.walk(base):
        dirs[:] = [x for x in dirs if not x.startswith(".") and x not in ("runs", "node_modules") and os.path.join(d, x) not in skip]
        for f in files:
            if f.endswith(".md"):
                yield os.path.join(d, f)


def own_md(base, skip=()):
    """Markdown files we wrote: copied skills (folders with UPSTREAM.md) keep their upstream links unchanged, so they aren't link-checked."""
    sk = os.path.join(base, "skills")
    upstream = {os.path.join(sk, n) for n in os.listdir(sk) if os.path.exists(os.path.join(sk, n, "UPSTREAM.md"))} if os.path.isdir(sk) else set()
    return md_files(base, skip=set(skip) | upstream)


def roles(root=ROOT):
    return sorted(f[:-3] for f in os.listdir(os.path.join(root, "roles")) if f.endswith(".md") and not f.startswith("_"))


def frontmatter(path):
    text = open(path, encoding="utf-8").read()
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    out, key, block = {}, None, None
    for line in m.group(1).splitlines():
        if block is not None and (line.startswith((" ", "\t")) or not line.strip()):
            block.append(line.strip())
            continue
        if block is not None:
            out[key] = " ".join(x for x in block if x)
            block = None
        if ":" in line and not line.startswith((" ", "#")):
            key, v = line.split(":", 1)
            key, v = key.strip(), re.sub(r"\s+#.*$", "", v).strip()
            if v in (">", "|", ">-", "|-"):
                block = []  # YAML block scalar: the value is the indented lines below
                continue
            if len(v) > 1 and v[0] == v[-1] and v[0] in "\"'":
                v = v[1:-1]
            out[key] = v
    if block is not None:
        out[key] = " ".join(x for x in block if x)
    return out


# ---- static ---------------------------------------------------------------

def check_roles(root=ROOT):
    errs, personas = [], {}
    for name in roles(root):
        path = os.path.join(root, "roles", name + ".md")
        fm = frontmatter(path)
        where = rel(path) if root == ROOT else os.path.relpath(path, root)
        if fm is None:
            errs.append("%s: no frontmatter" % where)
            continue
        for key in ("name", "persona", "department", "description", "tier", "capabilities", "memory", "version"):
            if not fm.get(key):
                errs.append("%s: frontmatter is missing %s" % (where, key))
        if fm.get("name") and fm["name"] != name:
            errs.append("%s: name is %r but the file is %s.md" % (where, fm["name"], name))
        if fm.get("tier") and fm["tier"] not in TIERS:
            errs.append("%s: tier %r is not one of %s" % (where, fm["tier"], ", ".join(sorted(TIERS))))
        caps = fm.get("capabilities", "")
        if caps and caps != "all":
            bad = [c for c in re.split(r"[ ,]+", caps) if c and c not in CAPS]
            if bad:
                errs.append("%s: unknown capabilities %s" % (where, ", ".join(bad)))
        if fm.get("memory") and fm["memory"] not in MEMORY:
            errs.append("%s: memory %r is not fish or elephant" % (where, fm["memory"]))
        if fm.get("version") and not re.fullmatch(r"\d+\.\d+\.\d+", fm["version"]):
            errs.append("%s: version %r is not x.y.z" % (where, fm["version"]))
        for s in [x for x in re.split(r"[ ,]+", fm.get("skills", "")) if x]:
            if not os.path.exists(os.path.join(root, "skills", s, "SKILL.md")):
                errs.append("%s: skill %s has no skills/%s/SKILL.md" % (where, s, s))
        p = fm.get("persona")
        if p and p in personas:
            errs.append("%s: persona %s is also used by %s" % (where, p, personas[p]))
        personas[p] = name
    return errs


def check_lifecycle(root=ROOT):
    """Every stage of docs/lifecycle.md links the rule that covers it, and every role names what it's grounded in."""
    errs, path = [], os.path.join(root, "docs", "lifecycle.md")
    if os.path.exists(path):
        rows = [l for l in open(path, encoding="utf-8") if re.match(r"\|\s*\d+\s*\|", l)]
        if not rows:
            errs.append("docs/lifecycle.md: no stages")
        for l in rows:
            cells = [c.strip() for c in l.strip().strip("|").split("|")]
            if len(cells) < 6 or not re.search(r"\]\([^)]+\)", cells[-1]):
                errs.append("docs/lifecycle.md: stage %s has no rule linked under Covered by" % cells[0])
    for name in roles(root):
        text = open(os.path.join(root, "roles", name + ".md"), encoding="utf-8").read()
        m = re.search(r"^\*\*Grounded in:\*\*(.*)$", text, re.M)
        if not m or not re.search(r"\]\(https?://", m.group(1)):
            errs.append("roles/%s.md: no 'Grounded in:' line linking an outside reference" % name)
    return errs


def check_vendor(root=ROOT):
    errs = []
    for top in NEUTRAL:
        path = os.path.join(root, top)
        files = [path] if path.endswith(".md") else md_files(path)
        for f in files:
            if upstream_skill(f, root):
                continue  # copied unchanged from its source, which names its own vendor
            for n, line in enumerate(open(f, encoding="utf-8"), 1):
                m = VENDOR.search(line)
                if m:
                    errs.append("%s:%d: vendor name %r (keep vendor mapping in adapters/)" % (os.path.relpath(f, root), n, m.group(0)))
    return errs


def upstream_skill(path, root=ROOT):
    """True for a file inside a skill copied from elsewhere (it has UPSTREAM.md)."""
    parts = os.path.relpath(path, root).split(os.sep)
    return len(parts) > 2 and parts[0] == "skills" and os.path.exists(os.path.join(root, "skills", parts[1], "UPSTREAM.md"))


def check_skills(root=ROOT):
    """Each skill follows the open Agent Skills format, keeps its links inside its folder, and some role uses it."""
    errs, base = [], os.path.join(root, "skills")
    if not os.path.isdir(base):
        return errs
    used = set()
    for name in roles(root):
        fm = frontmatter(os.path.join(root, "roles", name + ".md")) or {}
        used |= {x for x in re.split(r"[ ,]+", fm.get("skills", "")) if x}
    for name in sorted(os.listdir(base)):
        d = os.path.join(base, name)
        if not os.path.isdir(d):
            continue
        where = "skills/%s" % name
        path = os.path.join(d, "SKILL.md")
        if not os.path.exists(path):
            errs.append("%s: no SKILL.md" % where)
            continue
        fm = frontmatter(path)
        if fm is None:
            errs.append("%s/SKILL.md: no frontmatter" % where)
            continue
        if fm.get("name") != name:
            errs.append("%s/SKILL.md: name is %r but the folder is %s" % (where, fm.get("name"), name))
        if not SKILL_NAME.fullmatch(name) or len(name) > 64:
            errs.append("%s: name must be lowercase letters, digits and single hyphens, at most 64" % where)
        desc = fm.get("description", "")
        if not desc or desc in (">", "|") or len(desc) > 1024:
            errs.append("%s/SKILL.md: description must be one line of 1 to 1024 characters" % where)
        if os.path.exists(os.path.join(d, "UPSTREAM.md")):
            if not [f for f in os.listdir(d) if f.upper().startswith("LICENSE")]:
                errs.append("%s: copied skill without its LICENSE file" % where)
        elif not fm.get("license"):
            errs.append("%s/SKILL.md: no license field" % where)
        if name not in used:
            errs.append("%s: no role lists it under skills:" % where)
        if not os.path.exists(os.path.join(d, "UPSTREAM.md")):
            errs += [where + "/" + e for e in check_links(d, boundary=d)]
        elif "copied unchanged" not in open(os.path.join(d, "UPSTREAM.md"), encoding="utf-8").read().lower():
            errs.append("%s/UPSTREAM.md: must say the folder is copied unchanged, with its source and commit" % where)
    return errs


def check_team_comment(root=ROOT):
    """The team-comment script writes comments the replayer accepts, and refuses one it rejects."""
    script = os.path.join(root, "skills", "team-comment", "scripts", "team_comment.py")
    if not os.path.exists(script):
        return []
    errs, rdir = [], os.path.join(root, "roles")
    with tempfile.TemporaryDirectory() as tmp:
        body = os.path.join(tmp, "body.md")
        open(body, "w").write("Rows: AC1 · Revision: abc1234 · Files: n/a · Command: n/a · Expected / actual: n/a · Repro: n/a\n")
        good = subprocess.run([sys.executable, script, "--roles", rdir, "--from", "verifier", "--to", "implementer", "--kind", "verdict",
                               "--verdict", "BLOCK", "--rev", "abc1234", "--round", "1", "--issue", "7", "--body", body],
                              capture_output=True, text=True)
        if good.returncode:
            return ["skills/team-comment: script failed: " + good.stderr.strip()[-300:]]
        state = {"items": {"7": {"number": 7, "kind": "issue", "state": "CLOSED", "labels": [], "comments": [
            {"id": 1, "author": "verifier", "body": good.stdout}]}}, "label_events": [], "calls": []}
        found, _ = replay(state, names=roles(root))
        errs += ["skills/team-comment: replayer rejects the script's comment: " + e for e in found]
        bad = subprocess.run([sys.executable, script, "--roles", rdir, "--from", "implementer", "--to", "verifier", "--kind", "verdict",
                              "--verdict", "PASS", "--rev", "abc1234", "--issue", "7"], capture_output=True, text=True)
        if bad.returncode == 0:
            errs.append("skills/team-comment: script wrote a verdict from the implementer")
    return errs


def slug(heading, seen):
    s = re.sub(r"[`*_~]|<[^>]+>", "", heading.strip().lower())
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)
    s = re.sub(r"[^\w\- ]", "", s).replace(" ", "-")
    n = seen.get(s, 0)
    seen[s] = n + 1
    return s if n == 0 else "%s-%d" % (s, n)


_anchor_cache = {}


def anchors(path):
    if path not in _anchor_cache:
        seen, out, fence = {}, set(), False
        for line in open(path, encoding="utf-8"):
            if line.lstrip().startswith(("```", "~~~")):
                fence = not fence
                continue
            m = re.match(r"#{1,6}\s+(.*?)\s*#*\s*$", line)
            if m and not fence:
                out.add(slug(m.group(1), seen))
        _anchor_cache[path] = out
    return _anchor_cache[path]


LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")


def check_links(base, files=None, boundary=None):
    """Every relative link resolves, and every #anchor names a heading. Links may not leave `boundary`."""
    errs = []
    boundary = os.path.abspath(boundary or base)
    for f in files or md_files(base):
        fence = False
        for n, line in enumerate(open(f, encoding="utf-8"), 1):
            if line.lstrip().startswith(("```", "~~~")):
                fence = not fence
                continue
            if fence:
                continue
            for target in LINK.findall(re.sub(r"`[^`]*`", "", line)):
                if re.match(r"[a-z]+:", target) or target.startswith("<"):
                    continue
                path, _, anchor = target.partition("#")
                dest = os.path.normpath(os.path.join(os.path.dirname(f), path)) if path else f
                where = "%s:%d" % (os.path.relpath(f, base), n)
                if not os.path.abspath(dest).startswith(boundary + os.sep) and os.path.abspath(dest) != boundary:
                    errs.append("%s: link %s leaves %s" % (where, target, os.path.basename(boundary)))
                elif not os.path.exists(dest):
                    errs.append("%s: broken link %s" % (where, target))
                elif anchor and dest.endswith(".md") and anchor.lower() not in anchors(dest):
                    errs.append("%s: no heading for #%s in %s" % (where, anchor, os.path.relpath(dest, base)))
    return errs


def label_set(root=ROOT):
    """Run the real label script against the sandbox gh and read back what it created."""
    with tempfile.TemporaryDirectory() as tmp:
        env = dict(os.environ, FAKE_GH_STATE=os.path.join(tmp, "s.json"), FAKE_GH_ACTOR="harness",
                   PATH=os.path.dirname(FAKE_GH) + os.pathsep + os.environ["PATH"])
        r = subprocess.run(["bash", os.path.join(root, "adapters", "github", "labels.sh"), "sandbox/project"],
                           env=env, capture_output=True, text=True)
        if r.returncode:
            raise SystemExit("labels.sh failed: " + r.stderr)
        return set(json.load(open(env["FAKE_GH_STATE"]))["labels"])


def check_labels(root=ROOT):
    errs, labels = [], label_set(root)
    want_roles = {"role:" + r for r in roles(root)}
    have_roles = {l for l in labels if l.startswith("role:")}
    for l in sorted(want_roles - have_roles):
        errs.append("adapters/github/labels.sh: no label %s for an existing role" % l)
    for l in sorted(have_roles - want_roles):
        errs.append("adapters/github/labels.sh: label %s has no role file" % l)
    pattern = re.compile(r"`((?:role|stage|human|blocker|mode|class):[a-z-]+|needs-human|verified|owner-rejected|[a-z-]+-approved)`")
    for f in md_files(root, skip={os.path.join(root, "docs", "research"), os.path.join(root, "evals")}):
        for n, line in enumerate(open(f, encoding="utf-8"), 1):
            for l in pattern.findall(line):
                if l not in labels and not l.startswith("role:<"):
                    errs.append("%s:%d: label `%s` is not created by labels.sh" % (os.path.relpath(f, root), n, l))
    return errs


def check_handoff_table(root=ROOT):
    """The event table in docs/github-state.md names only real roles and stages."""
    errs, path = [], os.path.join(root, "docs", "github-state.md")
    names = set(roles(root))
    stages = {"intake", "research", "spec", "ready", "building", "verifying", "review", "done"}
    in_table = False
    for n, line in enumerate(open(path, encoding="utf-8"), 1):
        if line.startswith("| Event |"):
            in_table = True
            continue
        if in_table and not line.startswith("|"):
            break
        if not in_table or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        for s in re.findall(r"`([a-z-]+)`", cells[1]):
            if s not in stages:
                errs.append("docs/github-state.md:%d: unknown stage %s" % (n, s))
        for word in re.findall(r"[a-z]+(?:-[a-z]+)+|\b[a-z]{3,}\b", cells[2]):
            if word in ("none", "the", "coordinator", "role", "that", "stopped", "asked", "must", "supply", "missing",
                        "evidence", "then", "label", "removes", "next", "board", "read", "her", "or", "on"):
                continue
            if word not in names:
                errs.append("docs/github-state.md:%d: role column names %r, which is not a role" % (n, word))
    if not in_table:
        errs.append("docs/github-state.md: the event table (| Event | ...) is missing")
    return errs


CHECK_WORDS = {"event", "no-event", "label", "file", "no-file", "same", "run", "merged", "not-merged", "main-unchanged"}


def check_cases(root=ROOT):
    errs, base = [], os.path.join(root, "evals")
    if not os.path.isdir(base):
        return errs
    names = set(roles(root)) | {"e2e"}
    for case in sorted(os.listdir(base)):
        d = os.path.join(base, case)
        if case in ("fixtures", "runs") or not os.path.isdir(d):
            continue
        path = os.path.join(d, "case.md")
        if not os.path.exists(path):
            errs.append("evals/%s: no case.md" % case)
            continue
        fm = frontmatter(path) or {}
        text = open(path, encoding="utf-8").read()
        if fm.get("role") not in names:
            errs.append("evals/%s/case.md: role %r is not a role or e2e" % (case, fm.get("role")))
        if fm.get("kind") not in ("positive", "negative"):
            errs.append("evals/%s/case.md: kind must be positive or negative" % case)
        fixture = fm.get("fixture")
        if fixture and not os.path.isdir(os.path.join(base, "fixtures", fixture)):
            errs.append("evals/%s/case.md: fixture %s not found" % (case, fixture))
        if "\n# Task\n" not in text:
            errs.append("evals/%s/case.md: no # Task section" % case)
        checks = section(text, "Checks")
        if not checks.strip() and not section(text, "Rubric").strip():
            errs.append("evals/%s/case.md: needs # Checks or # Rubric" % case)
        for line in checks.splitlines():
            if line.startswith("- ") and line[2:].split()[0] not in CHECK_WORDS:
                errs.append("evals/%s/case.md: unknown check %r" % (case, line[2:].split()[0]))
    return errs

# Words a newcomer page may use only if the Words lesson explains them (principles, Writing: readable at age 10).
JARGON = ["commit", "merge", "branch", "deploy", "CI", "API", "spec", "ticket", "gate", "label", "frontmatter", "stack",
          "staging", "repo", "token", "workflow", "ratchet", "mandate", "rubric", "subagent", "SDK", "verdict", "playbook",
          "red zone", "autonomy stage", "blocker", "handoff"]
MAX_WORDS = 25  # the rule asks for about 15; this only catches the clearly too long


def page_text(path):
    """The words a reader sees on a README or portal page: no front matter, styles, scripts, code or commands."""
    t = open(path, encoding="utf-8").read()
    if path.endswith(".html"):
        t = re.sub(r"\A---\n.*?\n---\n", "", t, flags=re.S)
        t = re.sub(r"<(style|script|pre)[^>]*>.*?</\1>", "\n", t, flags=re.S | re.I)
        t = re.sub(r'<div class="(?:code|cmd)[^"]*">.*?</div>', "\n", t, flags=re.S)
        t = re.sub(r"\{\{.*?\}\}|\{%.*?%\}", "", t, flags=re.S)
        t = re.sub(r"</?(?:p|li|h\d|div|dt|dd|br|section|ul|ol|td|th|tr|button|small)\b[^>]*>", "\n", t)
        t = html.unescape(re.sub(r"<[^>]+>", "", t))
    else:
        t = re.sub(r"```.*?```", "\n", t, flags=re.S)
        t = re.sub(r"`[^`]*`", "x", t)
        t = re.sub(r"\]\([^)]*\)", "]", t).replace("|", "\n")
    return t


def check_plain(root=ROOT):
    """Newcomer pages (README, portal home, lessons): no very long sentences, and no jargon the Words lesson doesn't explain."""
    errs, learn = [], os.path.join(root, "learn")
    words = os.path.join(learn, "words.html")
    if not os.path.exists(words):
        return errs
    glossary = page_text(words).lower()
    pages = [os.path.join(root, f) for f in ("README.md", "index.html", "about.html", "options.html")]
    pages += [os.path.join(learn, f) for f in sorted(os.listdir(learn)) if f.endswith(".html")]
    for path in (p for p in pages if os.path.exists(p)):
        text, where = page_text(path), rel(path) if root == ROOT else os.path.relpath(path, root)
        for line in text.split("\n"):
            for sent in re.split(r"(?<=[.!?:;])\s+", line):
                if len(sent.split()) > MAX_WORDS:
                    errs.append("%s: sentence of %d words, split it: %s..." % (where, len(sent.split()), sent.strip()[:60]))
        if path == words:
            continue
        for term in JARGON:
            pat = r"\b%s(?:s|es|ed|ing)?\b" % re.escape(term)
            if re.search(pat, text, 0 if term.isupper() else re.I) and not re.search(pat, glossary, 0 if term.isupper() else re.I):
                errs.append("%s: %r isn't explained in learn/words.html; explain it there or use an everyday word" % (where, term))
    return errs


def section(text, name):
    m = re.search(r"^# %s\n(.*?)(?=^# |\Z)" % re.escape(name), text, re.S | re.M)
    return m.group(1) if m else ""


def static(root=ROOT):
    out = []
    for fn in (check_roles, check_skills, check_team_comment, check_lifecycle, check_vendor, check_labels, check_handoff_table, check_cases, check_plain):
        out += fn(root)
    out += check_links(root, own_md(root, skip={os.path.join(root, "evals", "runs")}))
    return out


# ---- installers -----------------------------------------------------------

def install(root=ROOT):
    errs = []
    for adapter in sorted(os.listdir(os.path.join(root, "adapters"))):
        script = os.path.join(root, "adapters", adapter, "install.sh")
        if not os.path.exists(script):
            continue
        with tempfile.TemporaryDirectory() as proj:
            r = subprocess.run(["bash", script, proj], capture_output=True, text=True)
            if r.returncode:
                errs.append("adapters/%s/install.sh failed: %s" % (adapter, r.stderr.strip()[-300:]))
                continue
            team = os.path.join(proj, ".team")
            for name in roles(root):
                if not os.path.exists(os.path.join(team, "roles", name + ".md")):
                    errs.append("adapters/%s/install.sh: role %s not installed" % (adapter, name))
            errs += ["adapters/%s install: %s" % (adapter, e) for e in check_links(team, own_md(team), boundary=team)]
            for folder in (".agents/skills", ".claude/skills"):
                linked = os.path.join(proj, folder)
                if folder == ".claude/skills" and adapter != "claude-code":
                    continue
                for name in sorted(os.listdir(os.path.join(team, "skills"))):
                    if not os.path.exists(os.path.join(linked, name, "SKILL.md")):
                        errs.append("adapters/%s/install.sh: skill %s not reachable from %s" % (adapter, name, folder))
            if not os.path.exists(os.path.join(proj, "AGENTS.md")):
                errs.append("adapters/%s/install.sh: no AGENTS.md written" % adapter)
            # A second run must succeed and leave one copy.
            r = subprocess.run(["bash", script, proj], capture_output=True, text=True)
            if r.returncode or [d for d in os.listdir(proj) if d.startswith(".team.new")]:
                errs.append("adapters/%s/install.sh: a second install failed or left a temp folder" % adapter)
    return errs


def gates(root=ROOT):
    r = subprocess.run(["bash", os.path.join(root, "templates", "foundation", "tests", "selftest.sh")], capture_output=True, text=True)
    if r.returncode:
        return ["templates/foundation/tests/selftest.sh failed:\n" + "\n".join(l for l in r.stdout.splitlines() if not l.startswith("ok"))]
    return []


# ---- replay -----------------------------------------------------------------

def events(state):
    """Every team comment in order: (item, comment, event dict or None, problem or None)."""
    rows = []
    for it in state["items"].values():
        for c in it["comments"]:
            found = EVENT.findall(c["body"])
            header = next((l for l in c["body"].splitlines() if l.strip()), "")
            is_team = bool(HEADER.match(header.strip())) or bool(found)
            if not is_team:
                continue
            if not found:
                rows.append((it, c, None, "team comment has no team-event line"))
                continue
            if len(found) > 1:
                rows.append((it, c, None, "more than one team-event line"))
                continue
            raw = found[0]
            if "\n" in raw:
                rows.append((it, c, None, "team-event JSON is not on one line"))
                continue
            try:
                ev = json.loads(raw)
            except ValueError:
                rows.append((it, c, None, "team-event is not valid JSON: %s" % raw[:80]))
                continue
            rows.append((it, c, ev, None))
    rows.sort(key=lambda r: r[1]["id"])
    return rows


def linked_issue(it):
    if it["kind"] != "pr":
        return it["number"]
    m = re.search(r"(?i)\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+#(\d+)", it.get("body") or "")
    if m:
        return int(m.group(1))
    m = re.match(r"team/(\d+)-", it.get("head", ""))
    return int(m.group(1)) if m else it["number"]


def pass_covers(rev, head, issue, origin=None):
    """A PASS at rev still holds at head if head is rev, or only verification/<issue>/ changed in between."""
    if not rev or not head:
        return False
    if head.startswith(rev) or rev.startswith(head[:7]):
        return True
    if not origin:
        return False
    r = subprocess.run(["git", "--git-dir", origin, "diff", "--name-only", rev, head], capture_output=True, text=True)
    if r.returncode:
        return False
    ok_prefix = "verification/%s/" % issue
    base = subprocess.run(["git", "--git-dir", origin, "merge-base", "--is-ancestor", rev, head]).returncode == 0
    return base and all(p.startswith(ok_prefix) for p in r.stdout.split())


def replay(state, names=None, strict_identity=False, origin=None):
    """Returns (errors, warnings) for one sandbox run."""
    names = set(names or roles())
    errs, warns = [], []
    rows = events(state)
    rounds, last = {}, {}
    for it, c, ev, problem in rows:
        where = "#%d comment %d (%s)" % (it["number"], c["id"], c["author"])
        if problem:
            errs.append("%s: %s" % (where, problem))
            continue
        frm, to, kind = ev.get("from"), ev.get("to"), ev.get("kind")
        issue = linked_issue(it)
        if frm not in names and not (kind == "approval" and frm == "owner"):
            errs.append("%s: from %r is not a role" % (where, frm))
        if kind == "approval" and frm not in ("engagement-lead", "owner"):
            errs.append("%s: an approval receipt from %s; only Ella (or the owner) writes one" % (where, frm))
        if to is not None and to not in names | {"owner"}:
            errs.append("%s: to %r is not a role or owner" % (where, to))
        if kind not in KINDS:
            errs.append("%s: kind %r is not one of %s" % (where, kind, ", ".join(sorted(KINDS))))
        if kind == "verdict":
            if ev.get("verdict") not in VERDICTS:
                errs.append("%s: verdict %r is not PASS, BLOCK or INCONCLUSIVE" % (where, ev.get("verdict")))
            if frm != "verifier":
                errs.append("%s: a verdict from %s; only the Verifier gives verdicts" % (where, frm))
            if not ev.get("rev"):
                errs.append("%s: verdict without rev" % where)
            if ev.get("verdict") == "BLOCK":
                rounds[issue] = rounds.get(issue, 0) + 1
                if rounds[issue] > 3:
                    errs.append("%s: BLOCK round %d on #%d; three BLOCKs must stop with a typed blocker" % (where, rounds[issue], issue))
                elif rounds[issue] == 3 and to == "implementer":
                    errs.append("%s: third BLOCK sent to the implementer; it goes to the coordinator" % where)
        elif "verdict" in ev:
            errs.append("%s: verdict field on a %s" % (where, kind))
        if c["author"] not in ("harness", "owner") and frm and c["author"] != frm:
            (errs if strict_identity else warns).append("%s: posted by %s but signed from %s" % (where, c["author"], frm))
        if ev.get("human"):
            if not str(ev["human"]).startswith("human:"):
                errs.append("%s: human %r is not a human: label" % (where, ev["human"]))
            added = any(e["number"] in (it["number"], issue) and ev["human"] in e["add"] for e in state.get("label_events", []))
            if not added:
                errs.append("%s: asks for %s but that label was never added" % (where, ev["human"]))
        if kind in ("handoff", "verdict") and to in names and not re.search(r"You are (?:the )?[A-Z][\w -]*\. Read \S*roles/%s\.md" % re.escape(to), c["body"]):
            errs.append("%s: hands to %s without a next prompt for that role" % (where, to))
        # Did the previous handoff on this issue reach the role it named?
        prev = last.get(issue)
        if prev and prev["to"] not in (None, "owner") and frm != prev["to"] and frm not in COORDINATORS:
            errs.append("%s: %s acted on #%d after a handoff to %s" % (where, frm, issue, prev["to"]))
        last[issue] = {"to": to, "where": where, "kind": kind}
    open_items = {it["number"] for it in state["items"].values() if it["state"] == "OPEN"}
    for issue, prev in last.items():
        if prev["to"] not in (None, "owner") and prev["kind"] in ("handoff", "verdict") and issue in open_items:
            warns.append("%s: handoff to %s was never picked up" % (prev["where"], prev["to"]))
    for it in state["items"].values():
        if it["state"] != "OPEN" or it["kind"] != "issue":
            continue
        labels = it["labels"]
        r = [l for l in labels if l.startswith("role:")]
        s = [l for l in labels if l.startswith("stage:")]
        h = [l for l in labels if l.startswith("human:")]
        if len(r) > 1:
            errs.append("#%d: %d role: labels (%s); exactly one role holds it" % (it["number"], len(r), ", ".join(r)))
        if (r or s) and len(s) != 1:
            errs.append("#%d: %d stage: labels; exactly one" % (it["number"], len(s)))
        if ("needs-human" in labels) != bool(h):
            errs.append("#%d: needs-human and a human: label go together (%s)" % (it["number"], ", ".join(labels) or "no labels"))
    by_issue = {}
    for it, c, ev, problem in rows:
        if ev and ev.get("kind") == "verdict":
            by_issue.setdefault(linked_issue(it), []).append(ev)
    for it in state["items"].values():
        if it["kind"] != "pr" or it["state"] != "MERGED":
            continue
        if it.get("mergedBy") != "owner":
            errs.append("PR #%d: merged by %s; only the owner merges" % (it["number"], it.get("mergedBy")))
        if not it.get("head", "").startswith("team/"):
            continue
        head = it.get("mergeHead", "")
        passes = [v for v in by_issue.get(linked_issue(it), []) if v.get("verdict") == "PASS"]
        if not any(pass_covers(p.get("rev"), head, linked_issue(it), origin) for p in passes):
            errs.append("PR #%d: merged at %s without a PASS verdict for that revision" % (it["number"], head[:12]))
    for call in state.get("calls", []):
        if not call["ok"] and "never merge" in call.get("error", ""):
            errs.append("%s tried to merge: gh %s" % (call["actor"], " ".join(call["argv"])))
        elif not call["ok"] and "not available in the sandbox" in call.get("error", ""):
            warns.append("%s used gh %s, which the sandbox does not support" % (call["actor"], " ".join(call["argv"][:3])))
    return errs, warns


# ---- main -------------------------------------------------------------------

def main(argv):
    what = argv[0] if argv else "all"
    if what == "replay":
        if len(argv) < 2:
            raise SystemExit("usage: teamcheck.py replay <state.json> [--origin <bare repo>] [--strict-identity]")
        origin = argv[argv.index("--origin") + 1] if "--origin" in argv else None
        errs, warns = replay(json.load(open(argv[1])), strict_identity="--strict-identity" in argv, origin=origin)
        for w in warns:
            print("warn  " + w)
    else:
        steps = {"static": static, "install": install, "gates": gates}
        chosen = list(steps) if what == "all" else [what]
        if any(c not in steps for c in chosen):
            raise SystemExit(__doc__)
        errs = []
        for c in chosen:
            found = steps[c]()
            print("%-8s %s" % (c, "ok" if not found else "%d problem(s)" % len(found)))
            errs += found
    for e in errs:
        print("FAIL  " + e)
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
