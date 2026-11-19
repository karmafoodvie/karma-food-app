#!/usr/bin/env python3
"""Erzeugt apple-calm-auto.css: ordnet JEDE 6-stellige Farbe in Inline-Stilen/Stilblöcken von public/index.html nach Farbton und Helligkeit
einer Familie der ruhigen Dashboard-Palette zu (Rot/Grün/Orange/Gelb/Blau/Neutral/Tinte).  python3 test-env/design/gen_calm.py"""
import os, re, colorsys, collections
here=os.path.dirname(os.path.abspath(__file__)); root=os.path.abspath(os.path.join(here,'..','..'))
s=open(os.path.join(root,'public','index.html'),encoding='utf-8').read()
s=re.sub(r'<style id="(apple|karma)-skin">.*?</style>','',s,flags=re.S)
s=re.sub(r'<script id="kf-[a-z]+">.*?</script>','',s,flags=re.S)
hexes=sorted(set(h.upper() for h in re.findall(r'#[0-9a-fA-F]{6}\b',s)))
# Apple-Systemfarben (iOS, hell): Blau = Aktion/Info, Grün = erledigt, Rot = Problem, Orange = Hinweis, Grau = neutral, Tinte #1C1C1E
STRONG={'err':'#FF3B30','ok':'#248A3D','acc':'#007AFF','warn':'#FF9500','info':'#007AFF','ink':'#1C1C1E','neu':'#8E8E93'}
LIGHT={'err':'#FFE9E7','ok':'#E3F5E8','acc':'#E5F1FF','warn':'#FFF1DB','info':'#E5F1FF','ink':'#1C1C1E','neu':'#F2F2F7'}
TEXT={'err':'#D70015','ok':'#248A3D','acc':'#0062CC','warn':'#B25000','info':'#0062CC','ink':'#1C1C1E','neu':'#6C6C70'}
BORD={'err':'#FFC4BF','ok':'#B7E4C4','acc':'#B3D4FF','warn':'#FFD9A0','info':'#B3D4FF','ink':'#1C1C1E','neu':'#D1D1D6'}
def fam(h):
    r,g,b=[int(h[i:i+2],16)/255 for i in (1,3,5)]
    hh,l,sat=colorsys.rgb_to_hls(r,g,b); hh*=360
    if l>0.97: return None,l
    if sat<0.14: return 'neu',l
    if l<0.2: return 'ink',l
    if hh<15 or hh>=340: return 'err',l
    if hh<42 or 300<=hh<340: return 'warn',l
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
    elif f=='neu': bg=LIGHT['neu'] if l>0.8 else ('#1C1C1E' if l<0.3 else '#8E8E93')
    else: bg=LIGHT[f] if l>0.82 else STRONG[f]
    out.append('BG(%s){background:%s !important;}'%(h,bg))
    # Text
    if f=='neu': fg='#1C1C1E' if l<0.3 else '#6C6C70'
    elif f=='ink': fg='#1C1C1E'
    elif l>0.8: fg=None  # helle Schrift auf dunklem Grund unverändert lassen
    else: fg=TEXT[f]
    if fg: out.append('FG(%s){color:%s !important;}'%(h,fg))
    # Rahmen
    bd=BORD[f] if f!='ink' else '#1C1C1E'
    out.append('BD(%s){border-color:%s !important;}'%(h,bd))
open(os.path.join(here,'apple-calm-auto.css'),'w',encoding='utf-8').write('\n'.join(out)+'\n')
print(len(hexes),'Farben ->',dict(cnt))
