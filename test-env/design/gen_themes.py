#!/usr/bin/env python3
"""Erzeugt apple-theme-lav.css und apple-theme-vio.css: zwei Farbvarianten des Apple-Glas-Designs (Klassen html.theme-lav / html.theme-vio).
Basis: apple-calm.css + apple-calm-auto.css (Apple-Farben), alle Palettenwerte werden ersetzt, Selektoren bekommen die Theme-Klasse.
python3 test-env/design/gen_themes.py"""
import os, re
here=os.path.dirname(os.path.abspath(__file__))
rd=lambda f: open(os.path.join(here,f),encoding='utf-8').read()

def hexrgb(h): h=h.lstrip('#'); return '%d,%d,%d'%tuple(int(h[i:i+2],16) for i in (0,2,4))

# Schlüssel = Apple-Werte, Werte = Theme-Werte
def palette(acc,accD,accL,accB,accMid,ink,mute,gray,bg,bord,ok,okL,okB,err,errT,errL,errB,warn,warnT,warnL,warnB,grad):
    keys=['#E94E1B','#C93F12','#FDEEE7','#F5C7B3','#F08A5F','#1C1C1E','#6C6C70','#8E8E93','#F6F1EC','#E8DDD3','#248A3D','#E3F5E8','#B7E4C4','#D92D20','#B42318','#FDE8E6','#F4B8B2','#E8A317','#8A5A00','#FFF4D6','#F2D68A','#FF3B31','#EBDDD2','#F0D9CB']
    vals=[acc,accD,accL,accB,accMid,ink,mute,gray,bg,bord,ok,okL,okB,err,errT,errL,errB,warn,warnT,warnL,warnB,grad,bord,bord]
    m=dict(zip(keys,vals))
    rgb={'233,78,27':hexrgb(acc),'244,120,70':hexrgb(accMid),'28,28,30':hexrgb(ink),'60,60,67':hexrgb(mute),'120,120,128':hexrgb(gray),
         '36,138,61':hexrgb(ok),'76,160,104':hexrgb(ok)}
    return m,rgb

THEMES={
 # Inspiration 1: weiches Lavendel/Periwinkle, tiefes Marineblau, Mint und warmes Orange
 'lav':palette('#5C63D8','#4A50B8','#E6E8FA','#BFC4F0','#8D93E8','#25264F','#6A6C98','#8F91B8','#ECEEFA','#D3D6EE',
               '#2A9D78','#DDF3EA','#B4E3D0','#E5484D','#C93A3F','#FDE8E8','#F6BFC0','#F29D38','#A5600F','#FDF0DB','#F5D4A0','#8C93E6'),
 # Inspiration 2: kräftiges Violett, Navy, Koralle, Aqua
 'vio':palette('#6C3FD6','#5530B5','#EFE9FB','#CDBDF2','#9A74EE','#1E1B4B','#6B6794','#8E8AB5','#F3F0FB','#DCD6F0',
               '#1FA187','#DDF4EE','#AEE3D6','#F0506E','#C73555','#FDE6EC','#F7B8C6','#F5A04A','#9A5A10','#FEF0DC','#F6D2A0','#8B5CF6'),
}

def expand(c):
    def sel(kind,hexes):
        out=[]
        for h in [x.strip() for x in hexes.split(',')]:
            if kind=='BG': out+=['html.apple [style*="background:%s;" i]'%h,'html.apple [style$="background:%s" i]'%h]
            elif kind=='FG': out+=['html.apple [style*=";color:%s;" i]'%h,'html.apple [style^="color:%s;" i]'%h,'html.apple [style$=";color:%s" i]'%h]
            else: out+=['html.apple [style*="solid %s" i]'%h]
        return ','.join(out)
    return re.sub(r'^(BG|FG|BD)\(([^)]*)\)\{',lambda m:sel(m.group(1),m.group(2))+'{',c,flags=re.M)

def recolor(css,m,rgb):
    """Ersetzt Farbwerte NUR in den Deklarationen (nicht in Selektoren, die App-Originalfarben enthalten)."""
    def decl(d):
        d=re.sub(r'#[0-9A-Fa-f]{6}\b',lambda x:m.get(x.group(0).upper(),x.group(0)),d)
        d=re.sub(r'rgba\((\d+),(\d+),(\d+),',lambda x:'rgba(%s,'%rgb.get('%s,%s,%s'%x.groups(),'%s,%s,%s'%x.groups()),d)
        return d
    return re.sub(r'([^{}]+)\{([^{}]*)\}',lambda r:r.group(1)+'{'+decl(r.group(2))+'}',css)

base=expand(rd('apple-calm-auto.css'))+expand(rd('apple-calm.css'))
for name,(m,rgb) in THEMES.items():
    css=recolor(base,m,rgb)
    css=css.replace('html.apple','html.apple.theme-'+name)
    extra=rd('apple-theme-%s-extra.css'%name) if os.path.exists(os.path.join(here,'apple-theme-%s-extra.css'%name)) else ''
    open(os.path.join(here,'apple-theme-%s.css'%name),'w',encoding='utf-8').write('/* GENERIERT von gen_themes.py (Theme %s) */\n'%name+css+extra)
    print(name,len(css))
