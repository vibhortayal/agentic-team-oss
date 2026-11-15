// Scores one app against scoring-checklist.md. usage: node score.js <arm-a|arm-b|arm-c|arm-d>  (a = one agent, b = full team, c = thrifty, d = balanced)
const { chromium } = require('playwright');
const path = require('path');
const A = {
  'arm-b': {"file": "apps/2-full-team.html", "name": "#team-name", "add": "#add-team", "rounds": "#rounds", "start": "#start-game", "startTimer": "#start-timer", "timer": "#countdown", "sang": "#sang-it", "pass": "#passed", "letter": "#letter-input", "save": "#save-letter", "letterErr": "#letter-error", "big": "#letter", "turn": "#turn-team", "scores": "#scores", "undo": "#undo", "undoEnd": "#undo", "newGame": "#new-game", "yes": "#confirm-yes", "no": "#confirm-no", "teamList": "#team-list", "winner": "#result", "setup": "#screen-setup", "end": "#screen-result"},
  'arm-a': { file: 'apps/1-one-agent.html', name: '#teamInput', add: '#addBtn', rounds: '#roundsSelect', start: '#startGameBtn', startTimer: '#startTimerBtn', timer: '#timer',
    sang: '#sangBtn', pass: '#passBtn', letter: '#letterInput', save: '#saveLetterBtn', letterErr: '#letterError', big: '#letterBig', turn: '#turnName', scores: '#scoreList',
    undo: '#undoBtn', undoEnd: '#undoBtn2', newGame: '#newGameBtn', yes: '#confirmYes', no: '#confirmNo', teamList: '#teamList', winner: '#winnerText', setup: '#setup', end: '#done' },
  'arm-c': { file: 'apps/3-thrifty.html', name: '#teamName', add: '#addTeam', rounds: '#rounds', start: '#startGame', startTimer: '#startTimer', timer: '#timerNum',
    sang: '#sang', pass: '#passed', letter: '#letterInput', save: '#confirmLetter', letterErr: '#letterError', big: '#letterBig', turn: '#turnName', scores: '#scores',
    undo: '#undo', undoEnd: '#undo', newGame: '#newGame', yes: '#yesNew', no: '#noNew', teamList: '#teamList', winner: '#winnerText', setup: '#setup', end: '#finished' },
  'arm-d': { file: 'apps/4-balanced.html', name: '#name', add: '#add', rounds: '#rounds', start: '#start', startTimer: '#startTimer', timer: '#timer',
    sang: '#sang', pass: '#passed', letter: '#lastLetter', save: '#saveLetter', letterErr: '#letterErr', big: '#letter', turn: '#curName', scores: '#scoreList',
    undo: '#undo', undoEnd: '#undo2', newGame: '#newGame', nativeConfirm: true, teamList: '#teamList', winner: '#winner', setup: '#setup', end: '#finished' },
};
const arm = process.argv[2];
const s = A[arm];
const url = 'file://' + path.resolve(__dirname, s.file);
const results = [];
const rec = (n, ok, note = '') => { results.push({ n, ok: !!ok, note }); };

(async () => {
  const browser = await chromium.launch();
  let dialogAnswer = true, dialogs = 0;
  async function fresh(opts = {}) {
    const ctx = await browser.newContext({ viewport: { width: opts.w || 375, height: 740 } });
    const page = await ctx.newPage();
    page.errors = []; page.reqs = [];
    page.on('pageerror', e => page.errors.push(String(e)));
    page.on('console', m => { if (m.type() === 'error') page.errors.push(m.text()); });
    page.on('request', r => { if (!r.url().startsWith('file:') && !r.url().startsWith('data:')) page.reqs.push(r.url()); });
    page.on('dialog', async d => { dialogs++; dialogAnswer ? await d.accept() : await d.dismiss(); });
    await page.clock.install();
    await page.goto(url);
    return page;
  }
  const vis = async (p, sel) => { try { return await p.locator(sel).first().isVisible(); } catch { return false; } };
  const txt = async (p, sel) => ((await p.locator(sel).first().textContent().catch(() => '')) || '').trim();
  async function addTeam(p, n) { await p.fill(s.name, n); await p.click(s.add); }
  const teamCount = async p => p.locator(s.teamList + ' li').count();
  async function setup(p, names, rounds) {
    for (const n of names) await addTeam(p, n);
    if (rounds) await p.selectOption(s.rounds, String(rounds));
    await p.click(s.start);
  }
  async function scores(p) {
    const out = {};
    const items = await p.locator(s.scores + ' li').evaluateAll(ls => ls.map(li => { const sp = li.querySelectorAll('span'); return [sp[0] ? sp[0].textContent : li.textContent, sp.length > 1 ? sp[sp.length - 1].textContent : '']; }));
    for (const [n, v] of items) { const m = v.replace(/\u2212/g, '-').match(/-?\d+/); if (m) out[n.trim()] = Number(m[0]); }
    return out;
  }
  const scoreOf = async (p, n) => { const sc = await scores(p); const k = Object.keys(sc).find(k => k.toLowerCase().includes(n.toLowerCase())); return k === undefined ? NaN : sc[k]; };
  async function sang(p, letter) { await p.click(s.sang); await p.fill(s.letter, letter); await p.click(s.save); }
  async function timeout(p) { await p.click(s.startTimer); await p.clock.runFor(31000); }
  const turn = p => txt(p, s.turn);
  const big = p => txt(p, s.big);
  async function guard(n, fn) { try { await fn(); } catch (e) { rec(n, false, 'error: ' + String(e).split('\n')[0].slice(0, 160)); } }

  // 1
  await guard(1, async () => { const p = await fresh(); await setup(p, ['Tigers', 'Lions'], 1); await p.click(s.pass);
    rec(1, p.errors.length === 0 && p.reqs.length === 0, [...p.errors, ...p.reqs].join(' | ').slice(0, 200)); });
  // 2
  await guard(2, async () => { const p = await fresh(); await addTeam(p, 'Solo');
    const dis = await p.locator(s.start).isDisabled(); if (!dis) await p.click(s.start).catch(() => {});
    const stillSetup = await vis(p, s.setup) && !(await vis(p, s.sang));
    for (const n of ['B', 'C', 'D', 'E', 'F']) await addTeam(p, n);
    const c6 = await teamCount(p); await p.fill(s.name, 'Seventh').catch(() => {}); await p.click(s.add, { timeout: 1500 }).catch(() => {});
    const c7 = await teamCount(p);
    rec(2, stillSetup && c6 === 6 && c7 === 6, `oneTeamBlocked=${stillSetup} six=${c6} afterSeventh=${c7}`); });
  // 3
  await guard(3, async () => { const p = await fresh(); await addTeam(p, ''); await addTeam(p, '   '); rec(3, (await teamCount(p)) === 0, 'count=' + await teamCount(p)); });
  // 4
  await guard(4, async () => { const p = await fresh(); await addTeam(p, 'Tigers'); await addTeam(p, ' tigers '); await addTeam(p, 'TIGERS');
    rec(4, (await teamCount(p)) === 1, 'count=' + await teamCount(p)); });
  // 5
  await guard(5, async () => { const p = await fresh(); const v = await p.inputValue(s.rounds);
    const opts = await p.locator(s.rounds + ' option').evaluateAll(o => o.map(x => x.value));
    rec(5, v === '3' && !opts.includes('0') && !opts.includes('11') && opts.length === 10, `default=${v} options=${opts.join(',')}`); });
  // 6
  await guard(6, async () => { const p = await fresh(); await setup(p, ['Zed', 'Amy', 'Mid'], 2); const seq = [];
    for (let i = 0; i < 4; i++) { seq.push(await turn(p)); await p.click(s.pass); }
    rec(6, seq[0].includes('Zed') && seq[1].includes('Amy') && seq[2].includes('Mid') && seq[3].includes('Zed'), seq.join('>')); });
  // 7
  await guard(7, async () => { const p = await fresh(); await setup(p, ['A1', 'B1'], 1);
    const t0 = await txt(p, s.timer); await p.clock.runFor(5000); const t1 = await txt(p, s.timer);
    await p.click(s.startTimer); await p.clock.runFor(3000); const t2 = await txt(p, s.timer);
    const num = t => Number((t.match(/\d+/) || [NaN])[0]);
    rec(7, num(t0) === 30 && num(t1) === 30 && num(t2) <= 28 && num(t2) >= 26, `${t0}|${t1}|${t2}`); });
  // 8
  await guard(8, async () => { const p = await fresh(); await setup(p, ['A1', 'B1'], 2); await p.click(s.sang);
    const bad = [];
    for (const v of ['', 'ab', '7']) { await p.fill(s.letter, v).catch(() => {}); const val = await p.inputValue(s.letter); await p.click(s.save).catch(() => {});
      const stillAsking = await vis(p, s.letter); const t = await turn(p);
      if (!(stillAsking || val !== v) || (t.includes('B1') && !stillAsking)) bad.push(JSON.stringify(v)); if (!stillAsking) break; }
    if (await vis(p, s.letter)) { await p.fill(s.letter, 'k'); await p.click(s.save); }
    const sc = await scoreOf(p, 'A1'); const t = await turn(p); const b = await big(p);
    rec(8, bad.length === 0 && sc === 10 && t.includes('B1') && /k/i.test(b), `badAccepted=${bad} score=${sc} turn=${t} letter=${b}`); });
  // 9
  await guard(9, async () => { const p = await fresh(); await setup(p, ['A1', 'B1'], 2); await sang(p, 'm'); await p.click(s.pass);
    rec(9, (await scoreOf(p, 'B1')) === 0 && (await turn(p)).includes('A1') && /m/i.test(await big(p)), `B1=${await scoreOf(p, 'B1')} turn=${await turn(p)} letter=${await big(p)}`); });
  // 10
  await guard(10, async () => { const p = await fresh(); await setup(p, ['A1', 'B1'], 2); await sang(p, 'm'); await timeout(p);
    rec(10, (await scoreOf(p, 'B1')) === -5 && (await turn(p)).includes('A1') && /m/i.test(await big(p)), `B1=${await scoreOf(p, 'B1')} turn=${await turn(p)} letter=${await big(p)}`); });
  // 11
  await guard(11, async () => { const p = await fresh(); await setup(p, ['A1', 'B1'], 3); await sang(p, 'm'); await sang(p, 'q');
    await p.click(s.undo); const a = [await scoreOf(p, 'B1'), await turn(p), await big(p)];
    const dis = await p.locator(s.undo).isDisabled().catch(() => true); if (!dis) await p.click(s.undo).catch(() => {});
    const b = [await scoreOf(p, 'A1'), await turn(p)];
    rec(11, a[0] === 0 && a[1].includes('B1') && /m/i.test(a[2]) && !/q/i.test(a[2]) && b[0] === 10 && b[1].includes('B1'), `afterUndo=${a} afterSecond=${b}`); });
  // 12
  await guard(12, async () => { const p = await fresh(); await setup(p, ['A1', 'B1'], 3); await timeout(p); await p.click(s.undo);
    const a = [await scoreOf(p, 'A1'), await turn(p)]; await p.clock.runFor(40000); const b = [await scoreOf(p, 'A1'), await scoreOf(p, 'B1'), await turn(p)];
    const okLater = (b[0] === 0 && b[2].includes('A1')) || (b[0] === -5 && b[2].includes('B1')); // a still-running or restarted clock may legitimately expire once
    rec(12, a[0] === 0 && a[1].includes('A1') && okLater && b[1] === 0, `afterUndo=${a} later=${b}`); });
  // 13 + 18
  await guard(13, async () => { const p = await fresh(); await setup(p, ['A1', 'B1', 'C1'], 2);
    await sang(p, 'a'); for (let i = 0; i < 4; i++) await p.click(s.pass);
    const notEarly = !(await vis(p, s.end)); await p.click(s.pass); const ended = await vis(p, s.end); const w = await txt(p, s.winner);
    rec(13, notEarly && ended && w.includes('A1'), `notEarly=${notEarly} ended=${ended} winner="${w.slice(0, 80)}"`);
    const before = JSON.stringify(await scores(p));
    for (const b of [s.sang, s.pass, s.startTimer]) await p.click(b, { timeout: 700 }).catch(() => {});
    await p.clock.runFor(40000);
    const visBtns = (await vis(p, s.sang)) || (await vis(p, s.pass));
    const after = JSON.stringify(await scores(p));
    rec(18, !visBtns && (before === after || after === '{}'), `turnButtonsVisible=${visBtns}`); });
  // 14
  await guard(14, async () => { const p = await fresh(); await setup(p, ['Ann', 'Bob', 'Cat'], 1); await sang(p, 'a'); await sang(p, 'b'); await p.click(s.pass);
    const w = await txt(p, s.winner); const body = await p.locator(s.end).textContent();
    rec(14, /tie/i.test(body) && w.includes('Ann') && w.includes('Bob') && !w.includes('Cat'), `"${w.slice(0, 100)}"`); });
  // 15
  await guard(15, async () => { const p = await fresh(); await setup(p, ['A1', 'B1'], 3); await sang(p, 'm'); await p.click(s.pass); await sang(p, 'z');
    await p.reload(); const st = [await scoreOf(p, 'A1'), await scoreOf(p, 'B1'), await turn(p), await big(p)];
    rec(15, st[0] === 20 && st[1] === 0 && st[2].includes('B1') && /z/i.test(st[3]), String(st)); });
  // 16
  await guard(16, async () => { const p = await fresh(); await setup(p, ['A1', 'B1'], 3); await sang(p, 'm');
    dialogs = 0; dialogAnswer = false; await p.click(s.newGame);
    let asked = s.nativeConfirm ? dialogs === 1 : await vis(p, s.no);
    if (!s.nativeConfirm && asked) await p.click(s.no);
    const kept = (await scoreOf(p, 'A1')) === 10 && (await vis(p, s.turn));
    dialogAnswer = true; await p.click(s.newGame); if (!s.nativeConfirm) await p.click(s.yes);
    const cleared = (await vis(p, s.setup)) && (await teamCount(p)) === 0;
    await p.reload(); const clearedAfterReload = (await vis(p, s.setup)) && (await teamCount(p)) === 0;
    rec(16, asked && kept && cleared && clearedAfterReload, `asked=${asked} kept=${kept} cleared=${cleared} afterReload=${clearedAfterReload}`); });
  // 17
  await guard(17, async () => { const p = await fresh(); const notes = [];
    const check = async (label, sels) => {
      const sw = await p.evaluate(() => document.documentElement.scrollWidth); if (sw > 375) notes.push(`${label}: scrollWidth ${sw}`);
      for (const b of sels) { if (!(await vis(p, b))) continue; const bb = await p.locator(b).first().boundingBox();
        if (bb.height < 44) notes.push(`${label}: ${b} ${Math.round(bb.height)}px tall`); if (bb.x < 0 || bb.x + bb.width > 375.5) notes.push(`${label}: ${b} clipped`); } };
    for (const n of ['The Magnificent Singers', 'Grandma and Grandpa Team', 'Kids']) await addTeam(p, n);
    await check('setup', [s.add, s.start]); await p.selectOption(s.rounds, '1'); await p.click(s.start);
    await check('play', [s.startTimer, s.sang, s.pass, s.undo, s.newGame]);
    await p.click(s.sang); await check('letter', [s.save]); await p.fill(s.letter, 'w'); await p.click(s.save);
    await p.click(s.pass); await p.click(s.pass); await check('end', [s.undoEnd, s.newGame]);
    await p.screenshot({ path: path.resolve(__dirname, `shots/${arm}-end.png`), fullPage: true });
    rec(17, notes.length === 0, notes.join('; ')); });

  await browser.close();
  results.sort((a, b) => a.n - b.n);
  for (const r of results) console.log(`${r.ok ? 'PASS' : 'FAIL'} ${String(r.n).padStart(2)} ${r.note}`);
  console.log(`${arm}: ${results.filter(r => r.ok).length}/${results.length}`);
})();
