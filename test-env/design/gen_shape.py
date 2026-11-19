#!/usr/bin/env python3
"""Erzeugt apple-shape.css: alle Rundungen der App im Apple-Design deutlich eckiger (Faktor ~0.3, Kreise werden Quadrate mit kleiner Rundung).
Liest die Radien aus allen Stilblöcken (außer karma-skin) und aus Inline-Angaben von public/index.html.  python3 test-env/design/gen_shape.py"""
import os, re
here=os.path.dirname(os.path.abspath(__file__)); root=os.path.abspath(os.path.join(here,'..','..'))
s=open(os.path.join(root,'public','index.html'),encoding='utf-8').read()
s=re.sub(r'/\* kf-shape:start \*/.*?/\* kf-shape:end \*/','',s,flags=re.S)
def new(v):
    v=int(v)
    if v<=4: return v
    return max(4,min(12,round(v*0.3)))
SKIP=re.compile(r'dot|avatar|spinner|progress|toggle|switch|swatch|legend|bdot|pin-dot|kf-dot|confetti',re.I)
out=['/* GENERIERT von gen_shape.py: eckigere Rundungen (nur Apple-Design) */']
seen=set()
for m in re.finditer(r'<style[^>]*>(.*?)</style>',s,flags=re.S):
    head=s[max(0,m.start()-0):m.start()+30]
    if 'id="karma-skin"' in s[m.start():m.start()+40]: continue
    for r in re.finditer(r'([^{}@]+)\{([^{}]*)\}',m.group(1)):
        sel,body=r.group(1).strip(),r.group(2)
        bm=re.search(r'(?<![-\w])border-radius:\s*([^;!}]+)',body)
        if not bm or SKIP.search(sel): continue
        val=bm.group(1).strip()
        if not re.fullmatch(r'(\d+(px)?|50%|999px|100px)(\s+(\d+(px)?|50%|0))*',val): continue
        def conv(t):
            t=t.strip()
            if t in('50%','100%'): return '10px'
            n=re.match(r'(\d+)',t); return (str(new(n.group(1)))+'px') if n and t!='0' else t
        nv=' '.join(conv(x) for x in val.split())
        sels=[]
        for one in sel.split(','):
            one=one.strip()
            if not one or one.startswith('html.karma') or 'karma' in one: continue
            if one.startswith('html.apple'): one='html.apple.apple'+one[len('html.apple'):]
            else: one='html.apple.apple '+one
            sels.append(one)
        if not sels: continue
        rule=','.join(sels)+'{border-radius:'+nv+' !important;}'
        if rule in seen: continue
        seen.add(rule); out.append(rule)
# Inline-Radien (px): 8..999px -> kleiner; 50% bleibt (Punkte, Abzeichen)
vals=set(int(x) for x in re.findall(r'style="[^"]*?border-radius:\s*(\d+)px',s))
for v in sorted(vals):
    if v<=4: continue
    out.append('html.apple.apple [style*="border-radius:%dpx"],html.apple.apple [style*="border-radius: %dpx"]{border-radius:%dpx !important;}'%(v,v,new(v)))
open(os.path.join(here,'apple-shape.css'),'w',encoding='utf-8').write('\n'.join(out)+'\n')
print('Regeln:',len(out)-1,'Inline-Werte:',sorted(vals))
