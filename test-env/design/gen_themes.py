#!/usr/bin/env python3
"""Erzeugt apple-theme-lav.css und apple-theme-vio.css: zwei Farbvarianten des Apple-Glas-Designs (Klassen html.theme-lav / html.theme-vio).
Basis: apple-calm.css + apple-calm-auto.css (Apple-Farben), alle Palettenwerte werden ersetzt, Selektoren bekommen die Theme-Klasse.
python3 test-env/design/gen_themes.py"""
import os, re
here=os.path.dirname(os.path.abspath(__file__))
rd=lambda f: open(os.path.join(here,f),encoding='utf-8').read()

def darken(h,f):
    h=h.lstrip('#'); c=[int(h[i:i+2],16) for i in (0,2,4)]
    return '#%02X%02X%02X'%tuple(int(x*(1-f)) for x in c)

def hexrgb(h): h=h.lstrip('#'); return '%d,%d,%d'%tuple(int(h[i:i+2],16) for i in (0,2,4))

# Schlüssel = Apple-Werte, Werte = Theme-Werte
def palette(acc,accD,accL,accB,accMid,ink,mute,gray,bg,bord,ok,okL,okB,err,errT,errL,errB,warn,warnT,warnL,warnB,grad):
    keys=['#E95028','#C93F12','#FDEEE7','#F5C7B3','#F08A5F','#03272B','#566F73','#6F8588','#F5F2EC','#E3DDD2','#108474','#E0F2EF','#A9D8D0','#A61E1E','#8B0000','#FBE9E7','#F0B8B2','#E8A53A','#7A4E0A','#FDF1D9','#F0D497','#FF3B31','#E3DDD2','#F0D9CB','#D0431B','#BF370A','#0F7A6C','#0B6A5D','#C43B0C','#F26A3D','#F8C9B0','#E0FF4F']
    vals=[acc,accD,accL,accB,accMid,ink,mute,gray,bg,bord,ok,okL,okB,err,errT,errL,errB,warn,warnT,warnL,warnB,grad,bord,bord,acc,accD,ok,darken(ok,.25),accD,accMid,accB,accB]
    m=dict(zip(keys,vals))
    rgb={'233,80,40':hexrgb(acc),'244,120,70':hexrgb(accMid),'3,39,43':hexrgb(ink),'86,111,115':hexrgb(mute),'120,120,128':hexrgb(gray),
         '16,132,116':hexrgb(ok),'16,132,116':hexrgb(ok),'33,128,56':hexrgb(ok),'30,122,52':hexrgb(ok),'214,70,18':hexrgb(acc),'201,63,18':hexrgb(accD)}
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
