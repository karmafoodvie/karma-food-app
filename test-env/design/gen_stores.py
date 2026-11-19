#!/usr/bin/env python3
"""Erzeugt apple-stores.css: pro Filiale eine eigene Hauptfarbe (html.store-<id>), gültig im Apple-Design.
Börse rot, Laurenzerberg grün, Ausstellungsstraße gelb, Stadtplatz orange (= Karma-Standard), Kitchen blau, Organisation Tinte-Petrol mit Neon.
Basis: apple-calm-auto.css + apple-calm.css; die Orange-Familie wird je Filiale ersetzt, Ink/Grün(Erfolg)/Rot(Fehler)/Gelb(Hinweis) bleiben.
python3 test-env/design/gen_stores.py"""
import os, re
here=os.path.dirname(os.path.abspath(__file__))
rd=lambda f: open(os.path.join(here,f),encoding='utf-8').read()
def rgb(h): h=h.lstrip('#'); return '%d,%d,%d'%tuple(int(h[i:i+2],16) for i in (0,2,4))

# decor = Markenton für Schatten/Linien, fill = Fläche mit weißer Schrift (>=4.5:1), text = Text auf Weiß/Tönung (>=4.5:1),
# tint/border = helle Fläche/Rand, mid = mittlerer Ton, light = heller Text auf Dunkel, act = aktive Fläche (Knopf, Reiter, Leiste), onact = Schrift darauf
STORES={
 '3400':dict(decor='#E95028',fill='#D0431B',text='#BF370A',tint='#FDEEE7',border='#F5C7B3',mid='#F08A5F',light='#F8C9B0',act='#D0431B',onact='#FFFFFF',ontab='#FFFFFF'),
 'boerse':dict(decor='#E53935',fill='#C62828',text='#B71C1C',tint='#FDECEC',border='#F3B8B8',mid='#E06A6A',light='#FAD4D4',act='#C62828',onact='#FFFFFF',ontab='#FFFFFF'),
 'lb':dict(decor='#43A047',fill='#2E7D32',text='#1B5E20',tint='#E8F5E9',border='#B7DFB9',mid='#66BB6A',light='#C8E6C9',act='#2E7D32',onact='#FFFFFF',ontab='#FFFFFF'),
 '1020':dict(decor='#F5B800',fill='#8F6200',text='#7A5400',tint='#FFF8DB',border='#F2DF8E',mid='#F5C400',light='#FFE680',act='#FFD21F',onact='#03272B',ontab='#03272B'),
 'kitchen':dict(decor='#2F6FE4',fill='#1E56C8',text='#1745A8',tint='#E8F0FD',border='#B9CFF4',mid='#5B8FE8',light='#C9DBF8',act='#1E56C8',onact='#FFFFFF',ontab='#FFFFFF'),
 'zentrale':dict(decor='#0E4A50',fill='#0B3B40',text='#0B3B40',tint='#E4EEEE',border='#B5CDCF',mid='#4F8589',light='#C5DADB',act='#03272B',onact='#E0FF4F',ontab='#E0FF4F'),
}
def hexmap(p):
    return {'#E95028':p['decor'],'#C93F12':p['text'],'#FDEEE7':p['tint'],'#F5C7B3':p['border'],'#F08A5F':p['mid'],'#F26A3D':p['mid'],'#F8C9B0':p['light'],
            '#D0431B':p['fill'],'#BF370A':p['text'],'#C43B0C':p['fill']}
def rgbmap(p):
    return {'233,80,40':rgb(p['decor']),'244,120,70':rgb(p['mid']),'214,70,18':rgb(p['fill']),'201,63,18':rgb(p['fill'])}

def expand(c):
    def sel(kind,hexes):
        out=[]
        for h in [x.strip() for x in hexes.split(',')]:
            if kind=='BG': out+=['html.apple [style*="background:%s;" i]'%h,'html.apple [style$="background:%s" i]'%h]
            elif kind=='FG': out+=['html.apple [style*=";color:%s;" i]'%h,'html.apple [style^="color:%s;" i]'%h,'html.apple [style$=";color:%s" i]'%h]
            else: out+=['html.apple [style*="solid %s" i]'%h]
        return ','.join(out)
    return re.sub(r'^(BG|FG|BD)\(([^)]*)\)\{',lambda m:sel(m.group(1),m.group(2))+'{',c,flags=re.M)

def recolor(css,p):
    hm,rm=hexmap(p),rgbmap(p)
    def decl(d):
        # Neon: als Hintergrund = aktive Fläche, als Schriftfarbe = heller Ton auf Dunkel
        d=re.sub(r'(background(?:-color)?\s*:\s*)#E0FF4F',lambda m:m.group(1)+p['act'],d,flags=re.I)
        d=re.sub(r'#E0FF4F',p['onact'] if p['onact']!='#03272B' else p['mid'],d,flags=re.I)
        d=re.sub(r'#[0-9A-Fa-f]{6}\b',lambda x:hm.get(x.group(0).upper(),x.group(0)),d)
        d=re.sub(r'rgba\((\d+),(\d+),(\d+),',lambda x:'rgba(%s,'%rm.get('%s,%s,%s'%x.groups(),'%s,%s,%s'%x.groups()),d)
        return d
    def rule(r):
        nd=decl(r.group(2))
        return r.group(1)+'{'+nd+'}' if nd!=r.group(2) else ''   # unveränderte Regeln gelten schon vom Standard-Apple-Design
    return re.sub(r'([^{}]+)\{([^{}]*)\}',rule,css)

def extras(sid,p):
    P='html.apple.store-%s'%sid
    return f'''
/* Hauptfarbe {sid}: Knöpfe, aktive Seite und aktiver Reiter in der Filialfarbe */
{P} .login-btn,{P} .submit-btn,{P} #topbar button[onclick="goTo('hilfe')"]{{background:{p['act']} !important;color:{p['onact']} !important;border:1px solid {p['fill']} !important;box-shadow:0 6px 16px rgba({rgb(p['decor'])},.28) !important;}}
{P}.apple.apple .nav-btn.active{{background:{p['act']} !important;color:{p['onact']} !important;box-shadow:0 4px 12px rgba({rgb(p['decor'])},.30) !important;}}
{P}.apple.apple .nav-btn.active svg{{stroke:{p['onact']} !important;}}
{P} .kf-tab.kf-on{{background:{p['act']} !important;border-color:{p['act']} !important;color:{p['ontab']} !important;box-shadow:0 12px 26px rgba({rgb(p['decor'])},.34),inset 0 1px 0 rgba(255,255,255,.35) !important;}}
{P} .kf-tab.kf-on .kf-lb,{P} .kf-tab.kf-on .kf-ic{{color:{p['ontab']} !important;}}
{P} .section-banner[style*="#F97316" i]{{border-left-color:{p['decor']} !important;background:rgba({rgb(p['decor'])},.08) !important;}}
{P} .section-banner[style*="#F97316" i] *{{color:{p['text']} !important;}}
'''
base=expand(rd('apple-calm-auto.css'))+expand(rd('apple-calm.css'))
out=['/* GENERIERT von gen_stores.py: Hauptfarbe je Filiale */']
for sid,p in STORES.items():
    css=recolor(base,p).replace('html.apple','html.apple.store-%s'%sid)
    out.append(css+extras(sid,p))
open(os.path.join(here,'apple-stores.css'),'w',encoding='utf-8').write('\n'.join(out))
print('Filialen:',list(STORES),'| Größe',sum(map(len,out)))
