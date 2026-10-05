#!/usr/bin/env python3
"""Menü-Gegencheck: Leading Sheet (Excel aus Drive, Tab "Alle Menüs") gegen das Menü der App.

Aufruf:  python3 tools/menu_check.py <sheet.xlsm> [overrides.json] [--epoche herbstwinter2026_27]

- liest public/menu_data.js (relativ zum Repo) und wendet die freigegebenen Overrides darüber an
  (overrides.json = Liste von {woche, tag, alt_name, neu_name}, aus Tabelle menu_overrides)
- vergleicht pro Woche/Tag die Gerichtsnamen (ohne Salat-Slot) mit dem Sheet
- gibt JSON auf stdout aus: {"diffs":[{woche,tag,app_name,sheet_name,hinweis}], "geprueft":N}
Reine Schreibweisen-Unterschiede (Lasagna/Lasagne, Groß/Klein, Leerzeichen) zählen NICHT als Abweichung.
"""
import json, re, subprocess, sys, difflib, pathlib
import openpyxl

args=[a for a in sys.argv[1:] if not a.startswith('--')]
epoche='herbstwinter2026_27'
if '--epoche' in sys.argv: epoche=sys.argv[sys.argv.index('--epoche')+1]
if not args: sys.exit(__doc__)
sheet_path=args[0]
overrides=json.load(open(args[1])) if len(args)>1 else []
repo=pathlib.Path(__file__).resolve().parent.parent
VAR={'herbstwinter2026_27':'MENU_DATA_HERBST_WINTER_2026_27','sommer2026':'MENU_DATA_SOMMER_2026'}[epoche]

DAYS={'montag':'mo','dienstag':'di','mittwoch':'mi','donnerstag':'do','freitag':'fr'}
norm=lambda s: re.sub(r'\s+',' ',s.strip()).lower().replace('lasagna','lasagne')

def sheet_menu():
    wb=openpyxl.load_workbook(sheet_path,data_only=True)
    ws=wb['Alle Menüs']
    out={}; blk=None; day=None
    for r in ws.iter_rows(min_row=1,max_row=120,max_col=4,values_only=True):
        a=r[0]
        if isinstance(a,str) and a.strip().startswith('MENÜ'):
            blk=int(re.findall(r'\d',a)[0]); day=None; continue
        if isinstance(a,str) and a.strip().lower() in DAYS: day=DAYS[a.strip().lower()]
        name=r[2]
        if blk and day and isinstance(name,str) and name.strip() and name.strip()!='Gericht DE':
            out.setdefault((blk,day),[]).append(re.sub(r'\s+',' ',name.strip()))
    return out

def app_menu():
    js=f"""const s=require('fs').readFileSync({json.dumps(str(repo/'public/menu_data.js'))},'utf8');
const m=new Function(s+';return {VAR};')();const o={{}};
for(const k in m)o[k]=m[k].filter(e=>e.slot!=='salat').map(e=>e.name.trim());
console.log(JSON.stringify(o));"""
    raw=json.loads(subprocess.check_output(['node','-e',js]))
    out={}
    for k,v in raw.items():
        w,d=k[1:].split('_'); out[(int(w),d)]=list(v)
    for o in overrides:   # freigegebene Namensänderungen drüberlegen
        if o.get('epoche',epoche)!=epoche: continue
        lst=out.get((int(o['woche']),o['tag']),[])
        out[(int(o['woche']),o['tag'])]=[o['neu_name'] if x==o['alt_name'] else x for x in lst]
    return out

sheet=sheet_menu(); app=app_menu()
diffs=[]
for key in sorted(set(sheet)|set(app)):
    s=sheet.get(key,[]); a=app.get(key,[])
    s_only=[x for x in s if norm(x) not in {norm(y) for y in a}]
    a_only=[x for x in a if norm(x) not in {norm(y) for y in s}]
    # Paare nach Ähnlichkeit bilden (Umbenennung), Rest einzeln melden
    pairs=[]
    for x in list(a_only):
        best=max(s_only,key=lambda y:difflib.SequenceMatcher(None,norm(x),norm(y)).ratio(),default=None)
        if best is not None:
            pairs.append((x,best)); a_only.remove(x); s_only.remove(best)
    w,d=key
    for x,y in pairs: diffs.append({'woche':w,'tag':d,'app_name':x,'sheet_name':y,'hinweis':None})
    for x in a_only: diffs.append({'woche':w,'tag':d,'app_name':x,'sheet_name':None,'hinweis':'Steht nur in der App, nicht im Sheet'})
    for y in s_only: diffs.append({'woche':w,'tag':d,'app_name':None,'sheet_name':y,'hinweis':'Steht nur im Sheet, nicht in der App'})
print(json.dumps({'diffs':diffs,'geprueft':len(set(sheet)|set(app))},ensure_ascii=False,indent=1))
