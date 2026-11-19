#!/usr/bin/env python3
"""Erzeugt apple-type.css: harmonisierte Typografie im Apple-Design.
- Familie: Geist für alles Lesbare (Text, Knöpfe, Felder, Tabellen); Archivo Black bleibt Titelschrift.
- Größenleiter: 12 / 14 / 16 / 18 / 22 / 26 px (größere Werte, z. B. Emojis, bleiben). Alle Inline-Größen und Klassen-Größen der App rasten darauf ein.
- Regeln stehen vor allen anderen Apple-Schichten und haben null Zusatz-Gewicht (:where), spätere Feinregeln gewinnen.
python3 test-env/design/gen_type.py"""
import os, re
here=os.path.dirname(os.path.abspath(__file__)); root=os.path.abspath(os.path.join(here,'..','..'))
s=open(os.path.join(root,'public','index.html'),encoding='utf-8').read()
s=re.sub(r'<style id="(apple|karma)-skin">.*?</style>','',s,flags=re.S)
s=re.sub(r'<script id="kf-[a-z]+">.*?</script>','',s,flags=re.S)
def snap(n):
    if n<=12.5: return 12
    if n<=14.5: return 14
    if n<=16.5: return 16
    if n<=19.5: return 18
    if n<=23: return 22
    if n<=28: return 26
    return None
out=['/* GENERIERT von gen_type.py: Typografie-System (Familie Geist, Leiter 12/14/16/18/22/26/32) */']
out.append('''html.apple,html.apple body{font-family:'Geist',-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;font-optical-sizing:auto;}
html.apple button,html.apple input,html.apple select,html.apple textarea{font-family:inherit;}
html.apple #content p,html.apple .cl-text,html.apple .item-name{text-wrap:pretty;}
html.apple .tb-title,html.apple .kf-dish-title,html.apple .kf-third-title,html.apple h1,html.apple h2,html.apple h3{text-wrap:balance;}
html.apple table,html.apple .qty-val,html.apple input[type=number],html.apple .kf-lb{font-variant-numeric:tabular-nums;}
html.apple #content{font-size:16px;line-height:1.45;}''')
# Inline-Größen (px)
vals=sorted(set(float(x) for x in re.findall(r'font-size:\s*([0-9]+(?:\.[0-9]+)?)px',s)))
for v in vals:
    t=snap(v)
    if t is None or abs(t-v)<1e-9: continue
    vs=('%g'%v)
    out.append('html.apple :where(#content,#topbar) [style*="font-size:%spx"],html.apple :where(#content,#topbar) [style*="font-size: %spx"]{font-size:%dpx !important;}'%(vs,vs,t))
# Klassen-Größen aus dem Original-Stylesheet
seen=set()
for m in re.finditer(r'<style[^>]*>(.*?)</style>',s,flags=re.S):
    for r in re.finditer(r'([^{}@]+)\{([^{}]*)\}',m.group(1)):
        sel,body=r.group(1).strip(),r.group(2)
        fm=re.search(r'(?<![-\w])font-size:\s*([0-9.]+)px',body)
        if not fm: continue
        v=float(fm.group(1)); t=snap(v)
        if t is None or abs(t-v)<1e-9: continue
        if re.search(r'nav-btn|login-logo|tb-title|kf-|badge|emoji',sel): continue   # eigene Feinregeln
        sels=[x.strip() for x in sel.split(',') if x.strip() and not x.strip().startswith(('html.','body.'))]
        if not sels: continue
        rule=','.join('html.apple '+x for x in sels)+'{font-size:%dpx;}'%t
        if rule in seen: continue
        seen.add(rule); out.append(rule)
open(os.path.join(here,'apple-type.css'),'w',encoding='utf-8').write('\n'.join(out)+'\n')
print('Inline-Werte:',vals,'| Klassenregeln:',len(seen))
