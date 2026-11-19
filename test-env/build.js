#!/usr/bin/env node
/* Baut die eigenständige Test-Seite aus public/index.html:  node test-env/build.js
 *
 * Ergebnis: test-env/dist/index.html (+ Bilder). Die Seite läuft komplett im Browser:
 *   · eigene Test-Datenbank (JavaScript, src/mem-core.js) mit Startdaten aus data/ und src/fixtures.js
 *   · Speicherung in localStorage des Browsers, nichts verlässt die Seite
 *   · KEINE Verbindung zur echten Supabase-Datenbank (harte Sicherung unten), E-Mails gesperrt
 *   · Edge Functions und Storage antworten mit 501 (gibt es im Test nicht)
 * Die echte App (public/) wird nie verändert, nur gelesen.
 */
'use strict';
const fs = require('fs'), path = require('path');

const ROOT = path.join(__dirname, '..'), PUB = path.join(ROOT, 'public'), DIST = path.join(__dirname, 'dist');
const rd = f => fs.readFileSync(path.join(__dirname, f), 'utf8');
const BASE = 'http://localhost:3000'; // Pseudo-Adresse, wird in der Seite von der Test-Datenbank abgefangen
const must = (s, a, b) => { if (!s.includes(a)) throw new Error('Nicht gefunden: ' + a.slice(0, 70)); return s.replace(a, () => b); };

let html = fs.readFileSync(path.join(PUB, 'index.html'), 'utf8');

// 1) SICHERHEIT: jede Supabase-Adresse umbiegen. Bleibt danach irgendeine übrig, wird NICHT gebaut.
html = html.replace(/https:\/\/[a-z0-9]+\.supabase\.co/g, BASE);
if (/supabase\.co/i.test(html)) throw new Error('ABBRUCH: In der Test-Seite steht noch eine Supabase-Adresse. Es wurde nichts gebaut.');

// 2) Menüdaten inline (statt document.write('<script src="/menu_data.js…'))
const menuJs = fs.readFileSync(path.join(PUB, 'menu_data.js'), 'utf8').replace(/<\/script/gi, '<\\/script');
const dw = /document\.write\('<script src="\/menu_data\.js[^\n]*\n/.exec(html);
if (!dw) throw new Error('menu_data.js-Ladestelle nicht gefunden (Aufbau der App geändert?)');
html = html.replace(dw[0], '/* menu_data.js ist inline eingebettet */\n');

// 3) Kein externes EmailJS (Versand gesperrt), eindeutiger Titel
html = html.replace(/<script src="https:\/\/cdn\.jsdelivr\.net\/npm\/@emailjs\/browser@[^"]*"><\/script>/, '');
html = html.replace(/<title>[^<]*<\/title>/, '<title>Karma Food Arbeitsumgebung</title>');

// 4) Test-Datenbank + fetch-Umleitung ganz oben im <head>
const hasDesign = html.includes('kf_design'); // Design-Schalter (?design=apple) vorhanden?
const boot = `<script>
/* ===== Karma Food Arbeitsumgebung: Datenbank läuft in dieser Seite (kein Server, keine echten Daten) ===== */
window.emailjs={init:function(){},send:function(s,t,p){console.warn('[TEST] E-Mail NICHT gesendet',s,t,p);return Promise.resolve({status:200});}};
${rd('src/mem-core.js')}
${rd('src/fixtures.js')}
(function(){
  var META=${rd('data/meta.json').trim()};
  var SEED=${rd('data/seed.json').trim()};
  var KEY='karma-arbeitsumgebung-db-v1', DATA=null;
  try{ var s=localStorage.getItem(KEY); if(s) DATA=JSON.parse(s); }catch(e){}
  if(!DATA||typeof DATA!=='object') DATA=window.KF_FIXTURES(JSON.parse(JSON.stringify(SEED)));
  var timer=null;
  function save(){ clearTimeout(timer); timer=setTimeout(function(){ try{ localStorage.setItem(KEY, JSON.stringify(mem.DATA)); }catch(e){} },300); }
  var mem=KarmaMem.makeMem(META,DATA,save);
  window.__resetTestDb=function(){ try{ localStorage.removeItem(KEY); }catch(e){} location.reload(); };
  try{ if(!localStorage.getItem('kf_design')) localStorage.setItem('kf_design','${process.env.DEFAULT_DESIGN||'off'}'); }catch(e){}
  var realFetch=window.fetch.bind(window), BASE='${BASE}';
  window.fetch=function(input,init){
    var url=typeof input==='string'?input:(input&&input.url)||'';
    if(url.indexOf(BASE)!==0) return realFetch(input,init);
    init=init||{}; var u=new URL(url), h={}, hd=init.headers||{};
    if(typeof hd.forEach==='function'&&!Array.isArray(hd)&&hd.constructor!==Object){ hd.forEach(function(v,k){h[k.toLowerCase()]=v;}); } else { for(var k in hd) h[k.toLowerCase()]=hd[k]; }
    var out=mem.handle({method:(init.method||'GET').toUpperCase(),path:u.pathname,params:u.searchParams,headers:h,body:typeof init.body==='string'?init.body:''});
    var st=out.status, body=(st===204||st===205)?null:out.body, headers=Object.assign({'Content-Type':'application/json'},out.headers);
    return new Promise(function(res,rej){
      if(init.signal&&init.signal.aborted){ rej(new DOMException('Aborted','AbortError')); return; }
      setTimeout(function(){ res(new Response(body,{status:st,headers:headers})); },5);
    });
  };
  document.addEventListener('DOMContentLoaded',function(){
    var cur='off'; try{ var cd=localStorage.getItem('kf_design'); cur=(cd==='apple'||cd==='karma')?cd:'off'; }catch(e){}
    var b=document.createElement('div'); b.id='__testbanner';
    b.style.cssText='background:#FFF3E0;color:#7A5710;font:600 11px/18px -apple-system,Helvetica,sans-serif;text-align:center;padding:2px 8px;position:relative;z-index:5;';
    function a(label,key){ return '<a href="#" data-d="'+key+'" style="color:inherit;margin:0 4px;'+(cur===key?'text-decoration:underline;font-weight:800;':'font-weight:500;')+'">'+label+'</a>'; }
    b.innerHTML='ARBEITSUMGEBUNG · lokale Testdaten, keine E-Mails'+${hasDesign ? "' · Design: '+a('Karma','karma')+'|'+a('Apple','apple')+'|'+a('Alt','off')" : "''"}+' · <a href="#" data-r="1" style="color:inherit;margin-left:4px;font-weight:500;">Daten zurücksetzen</a>';
    b.addEventListener('click',function(e){ var t=e.target; if(!t||!t.getAttribute) return; e.preventDefault();
      if(t.getAttribute('data-d')){ try{ localStorage.setItem('kf_design',t.getAttribute('data-d')); }catch(x){} location.reload(); }
      else if(t.getAttribute('data-r')){ window.__resetTestDb(); } });
    document.body.insertBefore(b,document.body.firstChild);
  });
})();
</script>
<script>
${menuJs}
</script>`;
html = must(html, '<head>', '<head>\n' + boot);

// 5) Absolute Pfade -> relativ (läuft dann auch unter einem Unterpfad)
html = html.replace(/(["'`(=])\/images\//g, '$1images/');
html = html.replace(/(href|src)="\/(manifest\.json|apple-touch-icon\.png|icon-192\.png|icon-512\.png)"/g, '$1="$2"');

// 6) dist/ schreiben
fs.rmSync(DIST, { recursive: true, force: true }); fs.mkdirSync(DIST, { recursive: true });
fs.writeFileSync(path.join(DIST, 'index.html'), html);
const walk = d => fs.readdirSync(d, { withFileTypes: true }).flatMap(e => e.isDirectory() ? walk(path.join(d, e.name)) : [path.join(d, e.name)]);
const copy = (a, b) => { fs.mkdirSync(path.dirname(b), { recursive: true }); fs.copyFileSync(a, b); };
for (const f of walk(path.join(PUB, 'images'))) copy(f, path.join(DIST, path.relative(PUB, f)));
for (const f of ['manifest.json', 'apple-touch-icon.png', 'icon-192.png', 'icon-512.png']) if (fs.existsSync(path.join(PUB, f))) copy(path.join(PUB, f), path.join(DIST, f));

// Liste der tatsächlich verwendeten Mediendateien (für das Veröffentlichen als Artifact)
const used = walk(path.join(PUB, 'images')).map(f => path.relative(PUB, f)).filter(f => /^images\/(dishes|kitchen-supply)\/|^images\/(hero|logo)\./.test(f)).concat(['icon-192.png', 'apple-touch-icon.png']);
fs.writeFileSync(path.join(DIST, '_publish_files.json'), JSON.stringify(used, null, 1));

const ver = (/APP_VERSION='([\d.]+)'/.exec(html) || [])[1];
console.log(`dist/index.html gebaut: App-Version ${ver}, ${(html.length / 1048576).toFixed(2)} MB, Design-Schalter: ${hasDesign ? 'ja' : 'nein'}`);
