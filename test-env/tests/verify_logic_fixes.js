// Vorher/Nachher-Nachweis der Korrekturen. Aufruf: node verify_fixes.js <URL> <Name>
const { chromium } = require('playwright');
const URL_ = process.argv[2] || 'http://localhost:8082/index.html', NAME = process.argv[3] || 'Arbeitsumgebung';
(async () => {
  const b = await chromium.launch(); const res = {};
  const mk = async (opts = {}, store = { id: 'zentrale', name: 'Zentrale / Transporter' }, init) => {
    const ctx = await b.newContext({ timezoneId: 'Europe/Vienna', viewport: { width: 420, height: 900 }, ...opts });
    await ctx.addInitScript(([s]) => { try { localStorage.setItem('kf_store', JSON.stringify(s)); } catch (e) {} }, [store]);
    if (init) await ctx.addInitScript(init);
    const p = await ctx.newPage(); p.__errs = []; p.on('pageerror', e => p.__errs.push(String(e).slice(0, 100)));
    await p.goto(URL_, { waitUntil: 'networkidle' }); await p.waitForTimeout(1500); return { ctx, p };
  };
  // 1) Epochen-Check mit korrekten Forecast-Daten
  { const { ctx, p } = await mk();
    res.epochenCheck = await p.evaluate(async () => {
      const iso = d => d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
      const rows = []; for (let i = 0; i < 12; i++) { const d = new Date(); d.setDate(d.getDate() + i); const wd = WEEKDAY_STR[d.getDay()]; if (!wd) continue; for (const n of getMenuDishNamesForDay(wd, iso(d))) rows.push({ store_id: '1020', forecast_date: iso(d), dish_name: n, qty: 5, groesse: 'gross', source: 'auto' }); }
      await api('forecast_qty', { method: 'POST', body: JSON.stringify(rows) });
      goTo('epochenCheck'); await new Promise(r => setTimeout(r, 2500));
      const t = document.getElementById('v-epochenCheck').innerText; const m = t.match(/(\d+) Zeilen mit Gerichten/);
      return { eingefuegt: rows.length, falschAlsKarteileicheGemeldet: m ? +m[1] : 0, saubergemeldet: /Daten sind sauber/.test(t) };
    });
    await ctx.close(); }
  // 2) Feuerlöscher: +1 Jahr
  { const { ctx, p } = await mk();
    res.feuerloescher = await p.evaluate(() => ({ '2026-03-15': flAddYear('2026-03-15'), '2026-08-01': flAddYear('2026-08-01') }));
    await ctx.close(); }
  // 3) Fehlgeschlagenes Speichern: Meldung sichtbar?
  { const { ctx, p } = await mk({}, { id: '1020', name: 'Ausstellungsstraße 1020' });
    res.speicherfehler = await p.evaluate(async () => {
      const rf = window.fetch; window.fetch = (u, o) => (o && o.method === 'POST' && String(u).includes('checklist_done')) ? Promise.resolve(new Response('{"message":"x"}', { status: 500 })) : rf(u, o);
      try { toggleCl(1); } catch (e) {}
      await new Promise(r => setTimeout(r, 1200));
      const t = document.querySelector('.toast'); window.fetch = rf;
      return { meldungSichtbar: !!(t && /Speichern/.test(t.textContent)), text: t ? t.textContent.slice(0, 70) : null };
    });
    await ctx.close(); }
  // 4) Freitext mit HTML (Mangel-Beschreibung im Detail-Fenster): wird Skript-Code ausgeführt?
  { const { ctx, p } = await mk();
    res.freitextHtml = await p.evaluate(async () => {
      const r = await api('maengel', { method: 'POST', body: JSON.stringify([{ store_id: '1020', betreff: 'Test', beschreibung: 'Wert <5 & >3 <img src=x onerror="window.__xss=1"> <b>fett</b>' }]) });
      await openMangelDetail(r[0].id); await new Promise(r => setTimeout(r, 800));
      const txt = document.body.innerText;
      return { skriptAusgefuehrt: !!window.__xss, textMitKleinerAlsSichtbar: /Wert <5 & >3/.test(txt), tagWörtlichSichtbar: /<b>fett<\/b>/.test(txt), echteBilderMitOnerror: document.querySelectorAll('img[onerror]').length };
    });
    await ctx.close(); }
  // 5) Browser ohne nutzbaren Speicher (z. B. privater Modus): Login möglich?
  { const ctx = await b.newContext({ viewport: { width: 420, height: 900 } });
    await ctx.addInitScript(() => { Storage.prototype.setItem = function () { throw new DOMException('Quota', 'QuotaExceededError'); }; });
    const p = await ctx.newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 90)));
    await p.goto(URL_, { waitUntil: 'networkidle' }); await p.waitForTimeout(1200);
    await p.getByText('Ausstellungsstraße 1020').first().click(); await p.waitForTimeout(400);
    const inp = p.locator('input[type=password], input[inputmode=numeric]'); await inp.first().fill('1234'); await inp.first().press('Enter'); await p.waitForTimeout(3000);
    res.ohneSpeicher = { eingeloggt: await p.locator('#topbar').isVisible().catch(() => false), pinFehlerSichtbar: await p.locator('#pin-error').isVisible().catch(() => false), jsFehler: errs.length };
    await ctx.close(); }
  console.log('=== ' + NAME); console.log(JSON.stringify(res, null, 1)); await b.close();
})();
