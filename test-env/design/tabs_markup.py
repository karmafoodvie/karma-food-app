#!/usr/bin/env python3
"""Kennzeichnet alle Reiter-Zeilen der App mit Klassen (kf-tabrow / kf-tab / kf-on) und trennt Emoji und Beschriftung (kfTabLabel).
Ohne Apple-Design ändert sich dadurch nichts am Aussehen. Idempotent:  python3 test-env/design/tabs_markup.py"""
import os, re, sys
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
p = os.path.join(root, 'public', 'index.html')
s = open(p, encoding='utf-8').read()
if 'kfTabLabel' in s.split('<style', 1)[0] and 'class="kf-tabrow"' in s:
    print('schon angewendet'); sys.exit(0)

def sub_once(old, new, label):
    global s
    n = s.count(old); assert n == 1, f'{label}: erwartet 1, gefunden {n}'
    s = s.replace(old, new, 1); print('ok ', label)

def on_line(anchor, pairs, label):
    """Ersetzungen nur in der (einzigen) Zeile, die `anchor` enthält."""
    global s
    lines = s.split('\n'); idx = [i for i, l in enumerate(lines) if anchor in l]
    assert len(idx) == 1, f'{label}: Zeile erwartet 1, gefunden {len(idx)}'
    l = lines[idx[0]]
    for old, new in pairs:
        assert l.count(old) == 1, f'{label}: "{old[:40]}" erwartet 1, gefunden {l.count(old)}'
        l = l.replace(old, new, 1)
    lines[idx[0]] = l; s = '\n'.join(lines); print('ok ', label)

# 0) Helfer: Emoji vom Rest der Beschriftung trennen (im Grundlagen-Skript)
sub_once("  window.escHtml=function(v){",
"""  window.kfTabLabel=function(l){ l=String(l==null?'':l); var m=l.match(/^((?:\\p{Extended_Pictographic}(?:\\uFE0F|\\u200D\\p{Extended_Pictographic})*))\\s*([\\s\\S]*)$/u); return m?'<span class="kf-ic">'+m[1]+'</span> <span class="kf-lb">'+m[2]+'</span>':'<span class="kf-lb">'+l+'</span>'; };
  window.escHtml=function(v){""", 'Helfer kfTabLabel')

# 1) tabBarHtml (Sweets/Packliste u. a.)
on_line("return `<button onclick=\"${onclickFn}('${t.key}')\" style=\"flex:1;padding:9px 4px;", [
    ("return `<button onclick=\"${onclickFn}('${t.key}')\" style=\"flex:1;padding:9px 4px;",
     "return `<button class=\"kf-tab${active?' kf-on':''}\" onclick=\"${onclickFn}('${t.key}')\" style=\"--kf-c:${color};flex:1;padding:9px 4px;"),
    ('>${t.label}</button>`;', '>${kfTabLabel(t.label)}</button>`;')], 'tabBarHtml Schaltfläche')
sub_once("return `<div style=\"display:flex;gap:6px;margin-bottom:14px;\">${btns}</div>`;", "return `<div class=\"kf-tabrow\" style=\"display:flex;gap:6px;margin-bottom:14px;\">${btns}</div>`;", 'tabBarHtml Zeile')

# 2) Bestell-Reiter
on_line("`<button onclick=\"switchOrderTab('${k}')\" style=\"flex:1;padding:9px 4px;", [
    ("`<button onclick=\"switchOrderTab('${k}')\" style=\"flex:1;padding:9px 4px;",
     "`<button class=\"kf-tab${activeOrderTab===k?' kf-on':''}\" onclick=\"switchOrderTab('${k}')\" style=\"--kf-c:${t.color};flex:1;padding:9px 4px;"),
    ('>${t.label}</button>', '>${kfTabLabel(t.label)}</button>')], 'Bestell-Reiter Schaltfläche')
sub_once("let html=`<div style=\"display:flex;gap:6px;margin-bottom:12px;\">${tabHtml}</div>`;", "let html=`<div class=\"kf-tabrow\" style=\"display:flex;gap:6px;margin-bottom:12px;\">${tabHtml}</div>`;", 'Bestell-Reiter Zeile')

# 3) Küchen-Reiter
on_line("`<button class=\"cl-tab\" onclick=\"switchKitchenTab('${key}')\" style=\"border-color:", [
    ("`<button class=\"cl-tab\" onclick=\"switchKitchenTab('${key}')\" style=\"border-color:",
     "`<button class=\"cl-tab kf-tab${active?' kf-on':''}\" onclick=\"switchKitchenTab('${key}')\" style=\"--kf-c:${KTAB_UNIFIED_COLOR};border-color:"),
    ('>${label}</button>', '>${kfTabLabel(label)}</button>')], 'Küchen-Reiter')

# 4) Team-/Sweets-Reiter
on_line("`<button class=\"cl-tab\" onclick=\"switchTeamTab('${key}')\" style=\"border-color:${col};", [
    ("`<button class=\"cl-tab\" onclick=\"switchTeamTab('${key}')\" style=\"border-color:${col};",
     "`<button class=\"cl-tab kf-tab${active?' kf-on':''}\" onclick=\"switchTeamTab('${key}')\" style=\"--kf-c:${col};border-color:${col};"),
    ('>${label}</button>', '>${kfTabLabel(label)}</button>')], 'Team-Reiter')

# 5) Kochplan-Wochen
sub_once("html+=`<div style=\"display:flex;gap:6px;margin-bottom:14px;\">`;\n    for(let w=1;w<=4;w++){", "html+=`<div class=\"kf-tabrow\" style=\"display:flex;gap:6px;margin-bottom:14px;\">`;\n    for(let w=1;w<=4;w++){", 'Wochen-Reiter Zeile')
on_line("onclick=\"window.kochplanWoche=${w};renderKitchen()\" style=\"flex:1;padding:8px 4px;", [
    ("<button onclick=\"window.kochplanWoche=${w};renderKitchen()\" style=\"flex:1;padding:8px 4px;",
     "<button class=\"kf-tab${active?' kf-on':''}\" onclick=\"window.kochplanWoche=${w};renderKitchen()\" style=\"--kf-c:${col};flex:1;padding:8px 4px;")], 'Wochen-Reiter Schaltfläche')

# 6) Checklisten-Reiter (Öffnung/Reinigung/Abschluss)
sub_once("`<button class=\"cl-tab${t===activeCl?' active':''}\" onclick=\"switchCl('${t}')\">${CL_LABELS[t]}</button>`",
         "`<button class=\"cl-tab kf-tab${t===activeCl?' active kf-on':''}\" style=\"--kf-c:var(--green);\" onclick=\"switchCl('${t}')\">${kfTabLabel(CL_LABELS[t])}</button>`", 'Checklisten-Reiter')

# 7) alle .cl-tabs-Container als Reiter-Zeile kennzeichnen
n = s.count('<div class="cl-tabs">'); assert n == 3, f'cl-tabs: erwartet 3, gefunden {n}'
s = s.replace('<div class="cl-tabs">', '<div class="cl-tabs kf-tabrow">'); print(f'ok  cl-tabs-Container ({n}×)')

open(p, 'w', encoding='utf-8').write(s); print('fertig')
