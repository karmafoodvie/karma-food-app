#!/usr/bin/env node
/* Durchklick-Test: jede Ansicht, mehrere Rollen, Handy + Desktop. Prüft: Ansicht wird angezeigt, kein waagrechter Überlauf,
 * keine neuen JS-Fehler. Gibt es den Design-Schalter, wird mit und ohne Design getestet und verglichen.
 * Aufruf:  node test-env/tests/regress.js [URL]      (Standard: http://localhost:8082/index.html, Playwright muss installiert sein)
 */
'use strict';
const fs = require('fs'), path = require('path');
const { chromium } = require('playwright');
const URL_ = process.argv[2] || 'http://localhost:8082/index.html';
const DIST = path.join(__dirname, '..', 'dist');
const html = fs.readFileSync(path.join(DIST, 'index.html'), 'utf8');
const VIEWS = [...new Set([...html.matchAll(/id="v-([a-z0-9_-]+)"/g)].map(m => m[1]))];
const MODES = html.includes('kf_design') ? ['off', 'apple', 'karma'] : ['off'];
const STORES = { '1020': 'Ausstellungsstraße 1020', kitchen: 'Kitchen 3400', zentrale: 'Zentrale / Transporter', lb: 'Laurenzerberg 1010', '3400': 'Stadtplatz 3400' };
(async () => {
  const b = await chromium.launch(); const res = [];
  for (const mode of MODES) for (const [sid, sname] of Object.entries(STORES)) for (const [vpName, vp] of [['handy', { width: 390, height: 844 }], ['desktop', { width: 1280, height: 800 }]]) {
    const ctx = await b.newContext({ viewport: vp, isMobile: vpName === 'handy', hasTouch: vpName === 'handy' });
    await ctx.addInitScript(([sid, sname, mode]) => { try { localStorage.setItem('kf_store', JSON.stringify({ id: sid, name: sname })); localStorage.setItem('kf_design', mode); } catch (e) {} }, [sid, sname, mode]);
    const p = await ctx.newPage(); const errs = [];
    p.on('pageerror', e => errs.push(String(e).slice(0, 110)));
    await p.goto(URL_, { waitUntil: 'networkidle' }).catch(e => errs.push('goto ' + e.message));
    await p.waitForTimeout(1200);
    const views = (sid === 'zentrale' || sid === 'kitchen') ? VIEWS : VIEWS.slice(0, 12);
    for (const v of views) {
      const before = errs.length;
      await p.evaluate(v => { try { goTo(v); } catch (e) {} }, v); await p.waitForTimeout(400);
      const m = await p.evaluate(() => ({ sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth, shown: [...document.querySelectorAll('.view.show')].map(x => x.id).join(',') }));
      res.push({ mode, sid, vp: vpName, v, overflow: m.sw > m.cw + 1 ? m.sw - m.cw : 0, newErr: errs.length - before, shown: m.shown.split(',').includes('v-' + v) });
    }
    await ctx.close();
  }
  await b.close();
  fs.writeFileSync(path.join(DIST, 'regress.json'), JSON.stringify(res));
  for (const mode of MODES) {
    const r = res.filter(x => x.mode === mode);
    console.log(`Design ${mode}: ${r.length} Prüfungen | Ansicht angezeigt: ${r.filter(x => x.shown).length} | Überlauf: ${r.filter(x => x.overflow).length} | neue JS-Fehler: ${r.reduce((a, x) => a + x.newErr, 0)}`);
  }
  const bad = res.filter(x => x.overflow || x.newErr);
  bad.slice(0, 20).forEach(x => console.log('  Auffällig:', x.mode, x.sid, x.vp, x.v, 'Überlauf', x.overflow, 'Fehler', x.newErr));
  process.exit(bad.length ? 1 : 0);
})();
