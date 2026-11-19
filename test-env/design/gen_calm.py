#!/usr/bin/env python3
"""Erzeugt apple-calm-auto.css: ordnet JEDE 6-stellige Farbe in Inline-Stilen/Stilblöcken von public/index.html nach Farbton und Helligkeit
einer Familie der ruhigen Dashboard-Palette zu (Rot/Grün/Orange/Gelb/Blau/Neutral/Tinte).  python3 test-env/design/gen_calm.py"""
import os, re, colorsys, collections
here=os.path.dirname(os.path.abspath(__file__)); root=os.path.abspath(os.path.join(here,'..','..'))
s=open(os.path.join(root,'public','index.html'),encoding='utf-8').read()
s=re.sub(r'<style id="(apple|karma)-skin">.*?</style>','',s,flags=re.S)
s=re.sub(r'<script id="kf-[a-z]+">.*?</script>','',s,flags=re.S)
hexes=sorted(set(h.upper() for h in re.findall(r'#[0-9a-fA-F]{6}\b',s)))
# Apple-Systemfarben (iOS, hell): Blau = Aktion/Info, Grün = erledigt, Rot = Problem, Orange = Hinweis, Grau = neutral, Tinte #03272B
STRONG={'err':'#A61E1E','ok':'#0F7A6C','acc':'#D0431B','warn':'#E8A53A','info':'#D0431B','ink':'#03272B','neu':'#6F8588'}
LIGHT={'err':'#FBE9E7','ok':'#E0F2EF','acc':'#FDEEE7','warn':'#FDF1D9','info':'#FDEEE7','ink':'#03272B','neu':'#F5F2EC'}
TEXT={'err':'#8B0000','ok':'#0B6A5D','acc':'#BF370A','warn':'#7A4E0A','info':'#BF370A','ink':'#03272B','neu':'#566F73'}
BORD={'err':'#F0B8B2','ok':'#A9D8D0','acc':'#F5C7B3','warn':'#F0D497','info':'#F5C7B3','ink':'#03272B','neu':'#E3DDD2'}
BRAND_ORANGE={'#E94E1B','#E95028','#E0521F','#F15941','#E87B4B'}
def fam(h):
    if h.upper() in BRAND_ORANGE: return 'acc',0.5
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
    elif f=='neu': bg=LIGHT['neu'] if l>0.8 else ('#03272B' if l<0.3 else '#6F8588')
    else: bg=LIGHT[f] if l>0.82 else STRONG[f]
    out.append('BG(%s){background:%s !important;}'%(h,bg))
    # Text
    if f=='neu': fg='#03272B' if l<0.3 else '#566F73'
    elif f=='ink': fg='#03272B'
    elif l>0.8: fg=None  # helle Schrift auf dunklem Grund unverändert lassen
    else: fg=TEXT[f]
    if fg: out.append('FG(%s){color:%s !important;}'%(h,fg))
    # Rahmen
    bd=BORD[f] if f!='ink' else '#03272B'
    out.append('BD(%s){border-color:%s !important;}'%(h,bd))
open(os.path.join(here,'apple-calm-auto.css'),'w',encoding='utf-8').write('\n'.join(out)+'\n')
print(len(hexes),'Farben ->',dict(cnt))
