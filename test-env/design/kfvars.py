"""Gemeinsame Farb-Variablen für das Apple-Design: Die Farbregeln stehen einmal im Stylesheet und nutzen var(--kf-…, Standardwert).
Filialen (gen_stores.py) und Farbwelten (gen_themes.py) setzen nur noch die Variablen, statt alle Regeln zu kopieren."""
import re
HEXKEYS=['#E95028','#C93F12','#FDEEE7','#F5C7B3','#F08A5F','#03272B','#566F73','#6F8588','#F5F2EC','#E3DDD2','#108474','#E0F2EF','#A9D8D0','#A61E1E','#8B0000','#FBE9E7','#F0B8B2','#E8A53A','#7A4E0A','#FDF1D9','#F0D497','#FF3B31','#F0D9CB','#D0431B','#BF370A','#0F7A6C','#0B6A5D','#C43B0C','#F26A3D','#F8C9B0']
RGBKEYS=['233,80,40','244,120,70','3,39,43','86,111,115','120,120,128','16,132,116','33,128,56','30,122,52','214,70,18','201,63,18']
NEON='#E0FF4F'
def hv(h): return '--kf-'+h.lstrip('#').lower()
def rv(t): return '--kf-rgb-'+t.replace(',','-')
_HS=set(HEXKEYS)
def transform(css):
    """Ersetzt Palettenfarben NUR in Deklarationen durch Variablen mit dem bisherigen Wert als Standard."""
    def decl(d):
        d=re.sub(r'(background(?:-color)?\s*:\s*)'+NEON,lambda m:m.group(1)+'\x00ACT\x00',d,flags=re.I)
        d=re.sub(NEON+r'\b','var(--kf-neon2,'+NEON+')',d,flags=re.I)
        d=d.replace('\x00ACT\x00','var(--kf-act,'+NEON+')')
        d=re.sub(r'#[0-9A-Fa-f]{6}\b',lambda x:('var(%s,%s)'%(hv(x.group(0).upper()),x.group(0).upper())) if x.group(0).upper() in _HS else x.group(0),d)
        d=re.sub(r'rgba\((\d+),(\d+),(\d+),',lambda x:('rgba(var(%s,%s),'%(rv('%s,%s,%s'%x.groups()),'%s,%s,%s'%x.groups())) if '%s,%s,%s'%x.groups() in RGBKEYS else x.group(0),d)
        return d
    return re.sub(r'([^{}]+)\{([^{}]*)\}',lambda r:r.group(1)+'{'+decl(r.group(2))+'}',css)
def block(selector,hexmap,rgbmap,act=None,neon2=None):
    out=[]
    for k,v in hexmap.items():
        k=k.upper()
        if k==NEON: act=act or v; neon2=neon2 or v; continue
        if k in _HS and v.upper()!=k: out.append('%s:%s'%(hv(k),v))
    for k,v in rgbmap.items():
        if k in RGBKEYS and v!=k: out.append('%s:%s'%(rv(k),v))
    if act: out.append('--kf-act:'+act)
    if neon2: out.append('--kf-neon2:'+neon2)
    return selector+'{'+';'.join(out)+';}\n'
