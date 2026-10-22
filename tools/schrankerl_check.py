#!/usr/bin/env python3
"""Schrankerl-Menügegencheck: Leading Sheet (Excel aus Drive, Tab "Schrankerl") gegen Tabelle schrankerl_menu.

Aufruf:  python3 tools/schrankerl_check.py <sheet.xlsm> <schrankerl_menu.json>

- schrankerl_menu.json = Ausgabe von: select woche,slot,name,zutaten,allergene_codes,spezial from schrankerl_menu
  (Liste von Objekten; Supabase-Antwort {"j":[...]} wird ebenfalls akzeptiert)
- Tab "Schrankerl": Blöcke "MENÜ n" mit Zeilen Curry / Salad / Dessert
  (Spalten: Slot | Gericht DE | Spezial | Zutatenliste gesamt | Allergene)
- Sheet ist führend. Ausgabe JSON: {"rows":[fertige menu_sheet_diffs-Zeilen],"diffs":[{woche,slot,feld,app,sheet}],"geprueft":N,"hinweise":[...]}
- Nur LESEN, am Sheet wird nichts geändert.
Leere Sheet-Felder (noch nicht befüllt) zählen als Hinweis, nicht als Abweichung.
Reine Schreibweisen-Unterschiede (Groß/Klein, Leerzeichen, Lasagna/Lasagne) zählen nicht.
"""
import json, re, sys
import openpyxl

if len(sys.argv)<3: sys.exit(__doc__)
SLOT={'curry':'curry','salad':'salat','salat':'salat','dessert':'dessert'}
norm=lambda s: re.sub(r'\s+',' ',str(s or '').strip()).lower().replace('lasagna','lasagne')
def clean_zutaten(z):
    # Manche Sheet-Zellen beginnen mit "<Gerichtsname>   vegan/glutenfrei   " vor der eigentlichen Liste -> abschneiden
    z=re.sub(r'\s+',' ',str(z or '').strip())
    m=re.match(r'^.*?\b(?:vegan|vegetarisch)(?:/glutenfrei)?\s+(?=[A-ZÄÖÜ])',z)
    return z[m.end():] if m and ',' in z[m.end():] else z
normlist=lambda s: sorted(x for x in (norm(p) for p in re.split(r'[,;]',str(s or ''))) if x)
def codes(v):
    s=str(v or '').strip()
    return [] if s in ('','-') else sorted(c.strip().upper() for c in re.split(r'[,;/ ]+',s) if c.strip())

def sheet_rows(path):
    ws=openpyxl.load_workbook(path,data_only=True)['Schrankerl']
    out={}; blk=None
    for r in ws.iter_rows(min_row=1,max_row=200,max_col=5,values_only=True):
        a=r[0]
        if isinstance(a,str) and a.strip().upper().startswith('MENÜ'):
            blk=int(re.findall(r'\d+',a)[0]); continue
        if blk and isinstance(a,str) and a.strip().lower() in SLOT:
            out[(blk,SLOT[a.strip().lower()])]={'name':r[1],'spezial':r[2],'zutaten':clean_zutaten(r[3]) or None,'allergene':r[4]}
    return out

db=json.load(open(sys.argv[2]))
if isinstance(db,list) and db and isinstance(db[0],dict) and 'j' in db[0]: db=db[0]['j']
app={(int(x['woche']),x['slot']):x for x in db}
sheet=sheet_rows(sys.argv[1])
diffs=[]; hint=[]
for key in sorted(set(sheet)|set(app)):
    w,slot=key; s=sheet.get(key); a=app.get(key)
    if s is None: diffs.append({'woche':w,'slot':slot,'feld':'gericht','app':a['name'],'sheet':None}); continue
    if a is None: diffs.append({'woche':w,'slot':slot,'feld':'gericht','app':None,'sheet':s['name']}); continue
    if norm(s['name'])!=norm(a['name']): diffs.append({'woche':w,'slot':slot,'feld':'name','app':a['name'],'sheet':s['name']})
    if s['spezial'] and norm(s['spezial'])!=norm(a.get('spezial')): diffs.append({'woche':w,'slot':slot,'feld':'spezial','app':a.get('spezial'),'sheet':s['spezial']})
    if not s['zutaten']: hint.append(f"Menü {w} {slot}: Zutatenliste im Sheet noch leer")
    elif normlist(s['zutaten'])!=normlist(a.get('zutaten')): diffs.append({'woche':w,'slot':slot,'feld':'zutaten','app':a.get('zutaten'),'sheet':s['zutaten']})
    if s['allergene'] is None: hint.append(f"Menü {w} {slot}: Allergene im Sheet noch leer")
    elif codes(s['allergene'])!=sorted(a.get('allergene_codes') or []): diffs.append({'woche':w,'slot':slot,'feld':'allergene','app':a.get('allergene_codes'),'sheet':s['allergene']})
def tostr(v): return ', '.join(v) if isinstance(v,list) else (None if v is None else str(v))
rows=[{'epoche':'schrankerl','woche':d['woche'],'tag':d['slot'],'app_name':tostr(d['app']),'sheet_name':tostr(d['sheet']),'hinweis':d['feld']} for d in diffs]
print(json.dumps({'rows':rows,'diffs':diffs,'geprueft':len(set(sheet)|set(app)),'hinweise':hint},ensure_ascii=False,indent=1))
