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


  await guard('hindi-letter', async () => { const p = await fresh(); await setup(p, ['A1', 'B1'], 3); await p.click(s.sang); await p.fill(s.letter, '\u0915'); await p.click(s.save).catch(()=>{});
    rec('hindi-letter', (await turn(p)).includes('B1'), 'turn=' + await turn(p) + ' err=' + (await txt(p, s.letterErr)).slice(0,80)); });
  await guard('hindi-matra', async () => { const p = await fresh(); await setup(p, ['A1', 'B1'], 3); await p.click(s.sang); await p.fill(s.letter, '\u0915\u093E'); await p.click(s.save).catch(()=>{});
    rec('hindi-matra', (await turn(p)).includes('B1'), 'turn=' + await turn(p)); });
  await guard('double-tap', async () => { const p = await fresh(); await setup(p, ['A1', 'B1', 'C1'], 3); await p.locator(s.pass).dblclick();
    rec('double-tap', (await turn(p)).includes('B1'), 'turn=' + await turn(p)); });
  await guard('refresh-timer', async () => { const p = await fresh(); await setup(p, ['A1', 'B1'], 3); await p.click(s.startTimer); await p.clock.runFor(10000); await p.reload(); await p.clock.runFor(1000);
    rec('refresh-timer', true, 'timer after refresh=' + await txt(p, s.timer) + ' turn=' + await turn(p)); });
  await guard('sang-before-timer', async () => { const p = await fresh(); await setup(p, ['A1', 'B1'], 3); const dis = await p.locator(s.sang).isDisabled();
    rec('sang-before-timer', true, 'sang disabled before Start timer=' + dis); });
  await guard('shots', async () => { const p = await fresh(); await setup(p, ['The Magnificent Singers', 'Grandma and Grandpa', 'Kids'], 3); await sang(p, 'm'); await p.click(s.startTimer); await p.clock.runFor(4000);
    await p.screenshot({ path: path.resolve(__dirname, `shots/${arm}-play.png`), fullPage: true }); rec('shots', true); });
  await browser.close();
  for (const r of results) console.log(`${r.ok ? 'yes' : 'NO '} ${r.n} ${r.note}`);
})();
