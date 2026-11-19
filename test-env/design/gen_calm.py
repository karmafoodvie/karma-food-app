#!/usr/bin/env python3
"""Erzeugt apple-calm-auto.css: ordnet JEDE 6-stellige Farbe in Inline-Stilen/Stilblöcken von public/index.html nach Farbton und Helligkeit
einer Familie der ruhigen Dashboard-Palette zu (Rot/Grün/Orange/Gelb/Blau/Neutral/Tinte).  python3 test-env/design/gen_calm.py"""
import os, re, colorsys, collections
here=os.path.dirname(os.path.abspath(__file__)); root=os.path.abspath(os.path.join(here,'..','..'))
s=open(os.path.join(root,'public','index.html'),encoding='utf-8').read()
s=re.sub(r'<style id="(apple|karma)-skin">.*?</style>','',s,flags=re.S)
s=re.sub(r'<script id="kf-[a-z]+">.*?</script>','',s,flags=re.S)
hexes=sorted(set(h.upper() for h in re.findall(r'#[0-9a-fA-F]{6}\b',s)))
STRONG={'err':'#B3261E','ok':'#2E7D55','acc':'#E94E1B','warn':'#C9A24A','info':'#5B7FA6','ink':'#2B211A','neu':'#7A6C5E'}
LIGHT={'err':'#F8E6E4','ok':'#E6F0EA','acc':'#FBE7DC','warn':'#F6EDD6','info':'#E6ECF3','ink':'#2B211A','neu':'#F1E7D6'}
TEXT={'err':'#B3261E','ok':'#2E7D55','acc':'#C93F12','warn':'#7A5A12','info':'#3F5F85','ink':'#2B211A','neu':'#7A6C5E'}
BORD={'err':'#E7B9B4','ok':'#BFD8CA','acc':'#F0C4AE','warn':'#E2CB8F','info':'#C5D2E0','ink':'#2B211A','neu':'#E4D9C6'}
def fam(h):
    r,g,b=[int(h[i:i+2],16)/255 for i in (1,3,5)]
    hh,l,sat=colorsys.rgb_to_hls(r,g,b); hh*=360
    if l>0.97: return None,l
    if sat<0.14: return 'neu',l
    if l<0.2: return 'ink',l
    if hh<15 or hh>=340: return 'err',l
    if hh<42 or 300<=hh<340: return 'acc',l
    if hh<68: return 'warn',l
    if hh<185: return 'ok',l
    if hh<300:
        return ('ink' if (sat<0.45 and l<0.32) else 'info'),l
    return 'neu',l
out=['/* GENERIERT von gen_calm.py: alle Farben der App -> ruhige Palette */']
cnt=collections.Counter()
for h in hexes:
    f,l=fam(h)
    if not f: continue
    cnt[f]+=1
    # Hintergrund
    if f=='ink': bg=STRONG['ink']
    elif f=='neu': bg=LIGHT['neu'] if l>0.8 else '#7A6C5E'
    else: bg=LIGHT[f] if l>0.82 else STRONG[f]
    out.append('BG(%s){background:%s !important;}'%(h,bg))
    # Text
    if f=='neu': fg='#2B211A' if l<0.3 else '#7A6C5E'
    elif f=='ink': fg='#2B211A'
    elif l>0.8: fg=None  # helle Schrift auf dunklem Grund unverändert lassen
    else: fg=TEXT[f]
    if fg: out.append('FG(%s){color:%s !important;}'%(h,fg))
    # Rahmen
    bd=BORD[f] if f!='ink' else '#2B211A'
    out.append('BD(%s){border-color:%s !important;}'%(h,bd))
open(os.path.join(here,'apple-calm-auto.css'),'w',encoding='utf-8').write('\n'.join(out)+'\n')
print(len(hexes),'Farben ->',dict(cnt))
