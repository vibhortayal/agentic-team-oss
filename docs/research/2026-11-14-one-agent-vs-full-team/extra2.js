// extra probes, written after the builds; not part of the 18-point score
const { chromium } = require('playwright'); const path = require('path');
const A = { 'arm-a': ['apps/1-one-agent.html','#teamInput','#addBtn','#startGameBtn','#startTimerBtn','#sangBtn','#turnName','#letterInput'],
  'arm-b': ['apps/2-full-team.html','#team-name','#add-team','#start-game','#start-timer','#sang-it','#turn-team','#letter-input'],
  'arm-c': ['apps/3-thrifty.html','#teamName','#addTeam','#startGame','#startTimer','#sang','#turnName','#letterInput'],
  'arm-d': ['apps/4-balanced.html','#name','#add','#start','#startTimer','#sang','#curName','#lastLetter'] };
(async () => { const b = await chromium.launch();
  for (const arm of Object.keys(A)) { const [f, name, add, start, st, sang, turn, letter] = A[arm];
    const p = await (await b.newContext({ viewport: { width: 375, height: 740 } })).newPage(); await p.clock.install(); await p.goto('file://' + path.resolve(__dirname, f));
    for (const n of ['A1', 'B1', 'C1']) { await p.fill(name, n); await p.click(add); } await p.click(start);
    await p.click(st); await p.clock.runFor(30300);
    const t1 = (await p.textContent(turn)).trim(); let clicked = true; await p.click(sang, { timeout: 800 }).catch(() => { clicked = false; });
    const asking = clicked && await p.isVisible(letter);
    console.log(arm, 'late tap 0.3s after buzzer: turn is', t1, '| Sang it accepted for that next team =', asking);
  } await b.close(); })();
