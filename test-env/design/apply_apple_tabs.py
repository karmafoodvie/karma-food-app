#!/usr/bin/env python3
"""Fügt die Apple-Glass-Regeln (apple-glass.css), die Reiter-Quadrate (apple-tabs.css) und das Anpass-Skript für die Reiter in
public/index.html ein (idempotent):  python3 test-env/design/apply_apple_tabs.py"""
import os, re
here = os.path.dirname(__file__)
root = os.path.abspath(os.path.join(here, '..', '..'))
p = os.path.join(root, 'public', 'index.html')
def expand(c):
    """BG/FG/BD(#hex,...){...} -> Selektoren, die NUR exakte Farbwerte in Inline-Stilen treffen (Tönungen wie #F9731612 bleiben unberührt)."""
    def sel(kind, hexes):
        out = []
        for h in [x.strip() for x in hexes.split(',')]:
            if kind == 'BG':
                out += ['html.apple [style*="background:%s;" i]' % h, 'html.apple [style$="background:%s" i]' % h]
            elif kind == 'FG':
                out += ['html.apple [style*=";color:%s;" i]' % h, 'html.apple [style^="color:%s;" i]' % h, 'html.apple [style$=";color:%s" i]' % h]
            else:
                out += ['html.apple [style*="solid %s" i]' % h]
        return ','.join(out)
    return re.sub(r'^(BG|FG|BD)\(([^)]*)\)\{', lambda m: sel(m.group(1), m.group(2)) + '{', c, flags=re.M)
rd = lambda f: open(os.path.join(here, f), encoding='utf-8').read()
s = open(p, encoding='utf-8').read()

# 1) CSS in den Apple-Stil
a = s.index('<style id="apple-skin">'); b = s.index('</style>', a)
blk = s[a:b]
blk = re.sub(r'/\* kf-tabs:start \*/.*?/\* kf-tabs:end \*/\n?', '', blk, flags=re.S)
blk = re.sub(r'/\* kf-themes:start \*/.*?/\* kf-themes:end \*/\n?', '', blk, flags=re.S)
blk = re.sub(r'/\* kf-calm:start \*/.*?/\* kf-calm:end \*/\n?', '', blk, flags=re.S)
blk = re.sub(r'/\* kf-shape:start \*/.*?/\* kf-shape:end \*/\n?', '', blk, flags=re.S)
blk = re.sub(r'/\* kf-fit:start \*/.*?/\* kf-fit:end \*/\n?', '', blk, flags=re.S)
blk = re.sub(r'/\* kf-glass:start \*/.*?/\* kf-glass:end \*/\n?', '', blk, flags=re.S)
blk += '/* kf-glass:start */\n' + rd('apple-glass.css') + '/* kf-glass:end */\n'
blk += '/* kf-tabs:start */\n' + rd('apple-tabs.css') + '/* kf-tabs:end */\n'
blk += '/* kf-fit:start */\n' + rd('apple-fit.css') + '/* kf-fit:end */\n'
blk += '/* kf-shape:start */\n' + rd('apple-shape.css') + '/* kf-shape:end */\n'
blk += '/* kf-calm:start */\n' + expand(rd('apple-calm-auto.css')) + expand(rd('apple-calm.css')) + '/* kf-calm:end */\n'
blk += '/* kf-themes:start */\n' + rd('apple-theme-lav.css') + rd('apple-theme-vio.css') + rd('apple-stores.css') + '/* kf-themes:end */\n'
s = s[:a] + blk + s[b:]

# 2) Anpass-Skript: Schrift und Symbol der Reiter schrumpfen, bis alles ins Quadrat passt (nur im Apple-Design aktiv)
fit = '''<script id="kf-tabfit">/* Reiter-Quadrate: Schrift und Symbol so anpassen, dass nichts abgeschnitten wird (nur mit Apple-Design) */
(function(){
  function on(){ return document.documentElement.classList.contains('apple'); }
  function over(t){ var l=t.querySelector('.kf-lb'); return t.scrollHeight>t.clientHeight+1||t.scrollWidth>t.clientWidth+1||(l&&l.scrollWidth>l.clientWidth+1); }
  function fit(t){
    var ic=t.querySelector('.kf-ic'), fs=12.5, iz=ic?(window.innerWidth<=420?24:28):0, g=0;
    function set(){ t.style.setProperty('--kf-fs',fs+'px'); if(ic) t.style.setProperty('--kf-ic',iz+'px'); }
    set();
    while(over(t)&&g++<30){ if(ic&&iz>20) iz-=1; else if(fs>10.5) fs-=0.5; else if(ic&&iz>14) iz-=1; else if(fs>9.5) fs-=0.5; else break; set(); }
  }
  function run(){ if(!on()) return; var all=document.querySelectorAll('.kf-tab'); for(var i=0;i<all.length;i++) fit(all[i]); var rows=document.querySelectorAll('.kf-tabrow'); for(var j=0;j<rows.length;j++){ var r=rows[j]; if(r.scrollWidth>r.clientWidth+1) r.setAttribute('data-wide','1'); else r.removeAttribute('data-wide'); } }
  var tm; function sched(){ clearTimeout(tm); tm=setTimeout(run,50); }
  document.addEventListener('DOMContentLoaded',function(){
    try{ new MutationObserver(sched).observe(document.body,{childList:true,subtree:true}); }catch(e){}
    window.addEventListener('resize',sched); if(document.fonts&&document.fonts.ready) document.fonts.ready.then(sched); sched();
  });
})();
</script>
'''
s = re.sub(r'<script id="kf-theme">.*?</script>\n', '', s, flags=re.S)
s = re.sub(r'<script id="kf-tabfit">.*?</script>\n', '', s, flags=re.S)
i = s.index('<style id="apple-skin">')
theme_js = '<script id="kf-theme">(function(){try{var m=location.search.match(/[?&]theme=(apple|lav|vio)\\b/);if(m)localStorage.setItem("kf_theme",m[1]);var t=localStorage.getItem("kf_theme");if(t==="lav"||t==="vio")document.documentElement.classList.add("theme-"+t);}catch(e){}})();</script>\n'
s = s[:i] + theme_js + fit + s[i:]
open(p, 'w', encoding='utf-8').write(s)
print('Glas-Regeln, Reiter-Quadrate und Anpass-Skript eingefügt')
