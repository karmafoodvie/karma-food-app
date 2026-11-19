#!/usr/bin/env node
/* UI-Audit nach Apple-HIG-Maßstäben (accessibility.md, typography.md): misst in jeder Ansicht
 *  · Tippflächen: kleinste Kante < 28 px (unter HIG-Minimum) und < 44 px (unter HIG-Standard)
 *  · Schriftgröße < 11 px (unter HIG-Minimum)
 *  · Textkontrast < 4,5:1 (normaler Text) bzw. < 3:1 (großer/fetter Text)
 * Aufruf: node test-env/tests/ui_audit.js [URL] [design]   (design: off | apple | karma)
 */
'use strict';
const fs = require('fs'), path = require('path');
const { chromium } = require('playwright');
const URL_ = process.argv[2] || 'http://localhost:8082/index.html', MODE = process.argv[3] || 'off';
const html = fs.readFileSync(path.join(__dirname, '..', 'dist', 'index.html'), 'utf8');
const VIEWS = [...new Set([...html.matchAll(/id="v-([a-z0-9_-]+)"/g)].map(m => m[1]))];
const ROLES = { zentrale: 'Zentrale / Transporter', '1020': 'Ausstellungsstraße 1020', kitchen: 'Kitchen 3400' };
(async () => {
  const b = await chromium.launch(); const rows = [];
  for (const [sid, sname] of Object.entries(ROLES)) {
    const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
    await ctx.addInitScript(([sid, sname, mode]) => { try { localStorage.setItem('kf_store', JSON.stringify({ id: sid, name: sname })); localStorage.setItem('kf_design', mode); } catch (e) {} }, [sid, sname, MODE]);
    const p = await ctx.newPage(); await p.goto(URL_, { waitUntil: 'networkidle' }); await p.waitForTimeout(1200);
    for (const v of (sid === 'zentrale' ? VIEWS : VIEWS.slice(0, 14))) {
      await p.evaluate(v => { try { goTo(v); } catch (e) {} }, v); await p.waitForTimeout(500);
      const r = await p.evaluate(() => {
        const vis = el => { const r = el.getBoundingClientRect(); const cs = getComputedStyle(el); return r.width > 0 && r.height > 0 && cs.visibility !== 'hidden' && cs.display !== 'none' && r.bottom > 0; };
        const root = document.querySelector('.view.show') || document.body;
        const lum = c => { const [r, g, b] = c.map(x => { x /= 255; return x <= 0.03928 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4); }); return 0.2126 * r + 0.7152 * g + 0.0722 * b; };
        const parse = s => { const m = s && s.match(/rgba?\(([^)]+)\)/); if (!m) return null; const a = m[1].split(',').map(parseFloat); return { c: a.slice(0, 3), a: a.length > 3 ? a[3] : 1 }; };
        const bgOf = el => { let e = el; while (e) { const p = parse(getComputedStyle(e).backgroundColor); if (p && p.a > 0.9) return p.c; e = e.parentElement; } return [255, 255, 255]; };
        const out = { small28: 0, small44: 0, interactive: 0, font11: 0, text: 0, lowContrast: 0, samples: [] };
        root.querySelectorAll('button,a[href],[onclick],input:not([type=hidden]):not([type=checkbox]):not([type=radio]),select,textarea,summary').forEach(el => {
          if (!vis(el)) return; out.interactive++; const r = el.getBoundingClientRect(); const m = Math.min(r.width, r.height);
          if (m < 28) { out.small28++; if (out.samples.length < 3) out.samples.push('Tippfläche ' + Math.round(r.width) + '×' + Math.round(r.height) + ' ' + (el.textContent || el.getAttribute('aria-label') || el.tagName).trim().slice(0, 22)); }
          if (m < 44) out.small44++;
        });
        const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
        let n; while ((n = walker.nextNode())) {
          const t = n.nodeValue.trim(); if (t.length < 2) continue; const el = n.parentElement; if (!el || !vis(el)) continue;
          const cs = getComputedStyle(el); const fs = parseFloat(cs.fontSize); out.text++;
          if (fs < 11) out.font11++;
          const fg = parse(cs.color); if (!fg) continue; const bg = bgOf(el);
          const a = fg.a, c = fg.c.map((x, i) => Math.round(x * a + bg[i] * (1 - a)));
          const L1 = lum(c), L2 = lum(bg), ratio = (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05);
          const large = fs >= 24 || (fs >= 18.66 && parseInt(cs.fontWeight) >= 700); const need = large ? 3 : 4.5;
          if (ratio < need) { out.lowContrast++; if (out.samples.length < 5) out.samples.push('Kontrast ' + ratio.toFixed(1) + ':1 „' + t.slice(0, 22) + '“'); }
        }
        return out;
      });
      rows.push({ role: sid, view: v, ...r });
    }
    await ctx.close();
  }
  await b.close();
  const sum = k => rows.reduce((a, r) => a + r[k], 0);
  console.log(`Design ${MODE}: ${rows.length} Ansichten × Rollen geprüft`);
  console.log(`  Tippflächen: ${sum('interactive')} Elemente | unter 28 px (HIG-Minimum): ${sum('small28')} (${(100 * sum('small28') / sum('interactive')).toFixed(0)} %) | unter 44 px (HIG-Standard): ${sum('small44')} (${(100 * sum('small44') / sum('interactive')).toFixed(0)} %)`);
  console.log(`  Schrift unter 11 px: ${sum('font11')} von ${sum('text')} Textstellen (${(100 * sum('font11') / sum('text')).toFixed(1)} %)`);
  console.log(`  Kontrast unter Grenzwert: ${sum('lowContrast')} von ${sum('text')} Textstellen (${(100 * sum('lowContrast') / sum('text')).toFixed(1)} %)`);
  const worst = rows.filter(r => r.role === 'zentrale').sort((a, b) => (b.small28 + b.lowContrast) - (a.small28 + a.lowContrast)).slice(0, 6);
  console.log('  Auffälligste Ansichten (Zentrale):'); worst.forEach(r => console.log(`    ${r.view}: ${r.small28} kleine Tippflächen, ${r.lowContrast} Kontrastfälle, ${r.font11} zu kleine Schrift`));
  fs.writeFileSync(path.join(__dirname, '..', 'dist', 'ui_audit_' + MODE + '.json'), JSON.stringify(rows));
})();
