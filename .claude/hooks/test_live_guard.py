#!/usr/bin/env python3
"""Selbsttest des Live-Schutzes:  python3 .claude/hooks/test_live_guard.py   (legt nur temporäre Test-Repos an, pusht nichts)"""
import json, os, subprocess, sys, tempfile, time
HERE = os.path.dirname(os.path.abspath(__file__)); GUARD = os.path.join(HERE, 'live_guard.py')
UNLOCK_NAME = 'live' + '-unlock'  # getrennt geschrieben, damit dieses Skript selbst nicht wie ein Anlege-Versuch aussieht


def sh(*a, cwd=None): return subprocess.run(a, cwd=cwd, capture_output=True, text=True)


def make_repo(branch):
    d = tempfile.mkdtemp(); sh('git', 'init', '-q', '-b', branch, d); sh('git', '-C', d, 'config', 'user.email', 't@t'); sh('git', '-C', d, 'config', 'user.name', 't')
    os.makedirs(os.path.join(d, '.claude'), exist_ok=True); open(os.path.join(d, 'f'), 'w').write('x'); sh('git', '-C', d, 'add', '.'); sh('git', '-C', d, 'commit', '-q', '-m', 'i'); return d


def run(project, cwd, tool, inp):
    env = dict(os.environ, CLAUDE_PROJECT_DIR=project)
    p = subprocess.run([sys.executable, GUARD], input=json.dumps({'tool_name': tool, 'tool_input': inp, 'cwd': cwd}), capture_output=True, text=True, env=env)
    return p.returncode


dev, live = make_repo('entwicklung'), make_repo('main')
fails = 0


def t(name, project, cwd, tool, inp, want):
    global fails
    got = 'D' if run(project, cwd, tool, inp) == 2 else 'A'
    ok = got == want; fails += (not ok)
    print(('OK     ' if ok else 'FEHLER '), 'gesperrt' if want == 'D' else 'erlaubt ', name)


B = lambda c: ('Bash', {'command': c})
S = lambda q: ('mcp__Supabase__execute_sql', {'project_id': 'x', 'query': q})
UL = '.claude/' + UNLOCK_NAME
cases = [
    ('push HEAD:main', B('git push origin HEAD:main'), 'D'), ('push entwicklung:main', B('git push origin entwicklung:main'), 'D'),
    ('push --force origin main', B('git push --force origin main'), 'D'), ('push origin main', B('git push origin main'), 'D'),
    ('push origin :main (löschen)', B('git push origin :main'), 'D'), ('push --delete main', B('git push origin --delete main'), 'D'),
    ('push --all', B('git push --all'), 'D'), ('push refs/heads/main', B('git push origin refs/heads/main'), 'D'),
    ('verkettet: cd && push HEAD:refs/heads/main', B('cd x && git push origin HEAD:refs/heads/main'), 'D'),
    ('push +HEAD:main (force-Kurzform)', B('git push origin +HEAD:main'), 'D'),
    ('push -u origin entwicklung', B('git push -u origin entwicklung'), 'A'),
    ('push force-with-lease auf Feature-Branch', B('git push --force-with-lease=claude/apple-design:abc origin claude/apple-design'), 'A'),
    ('push origin HEAD auf entwicklung', B('git push origin HEAD'), 'A'), ('git push ohne Ziel auf entwicklung', B('git push'), 'A'),
    ('gh pr merge', B('gh pr merge 5 --squash'), 'D'), ('gh pr create', B('gh pr create --title a --body b'), 'A'),
    ('gh api PUT merge', B('gh api -X PUT repos/o/r/pulls/1/merge'), 'D'), ('gh api GET', B('gh api repos/o/r'), 'A'),
    ('vercel --prod', B('vercel --prod'), 'D'), ('vercel ls', B('vercel ls'), 'A'),
    ('Commit-Nachricht erwähnt gh pr merge', B('git commit -m "Schutz gegen gh pr merge und git push origin main"'), 'A'),
    ('Commit-Nachricht (Heredoc-Stil, mehrzeilig) erwähnt Befehle', B('git commit -q -m "Titel\n\nBlockiert: Push auf main, gh pr merge, vercel --prod\nFreigabe: ' + UNLOCK_NAME + ' (write)"'), 'A'),
    ('PR-Text erwähnt gh pr merge', B('gh pr create --title "x" --body "danach: gh pr merge 5"'), 'A'),
    ('Umweg über sh -c bleibt gesperrt', B("sh -c 'git push origin HEAD:main'"), 'D'),
    ('Commit-Nachricht + echter Push auf main bleibt gesperrt', B('git commit -m "ok" && git push origin HEAD:main'), 'D'),
    ('Freigabe anlegen: echo >', B('echo 9999999999 > ' + UL), 'D'), ('Freigabe anlegen: touch', B('touch ' + UL), 'D'),
    ('Freigabe lesen: cat', B('cat ' + UL), 'A'), ('git status && log', B('git status && git log --oneline'), 'A'),
    ('SQL select', S('select count(*) from orders'), 'A'), ('SQL created_at (Spaltenname)', S('select created_at from orders'), 'A'),
    ('SQL update', S('update orders set quantity=1'), 'D'), ('SQL delete', S('delete from orders where id=1'), 'D'),
    ('SQL insert in CTE', S('with x as (insert into t values (1) returning *) select * from x'), 'D'), ('SQL drop', S('drop table orders'), 'D'),
    ('SQL nextval', S("select nextval('orders_id_seq')"), 'D'), ('SQL Wort im Text', S("select 'insert into x' as t"), 'A'),
    ('SQL Wort im Kommentar', S('/* update */ select 1 -- delete'), 'A'), ('SQL alter', S('alter table orders add column x int'), 'D'),
    ('Supabase apply_migration', ('mcp__Supabase__apply_migration', {'project_id': 'x', 'name': 'a', 'query': 'select 1'}), 'D'),
    ('Supabase deploy_edge_function', ('mcp__Supabase__deploy_edge_function', {'project_id': 'x'}), 'D'),
    ('Supabase list_tables', ('mcp__Supabase__list_tables', {'project_id': 'x'}), 'A'),
    ('Write public/index.html auf entwicklung', ('Write', {'file_path': os.path.join(dev, 'public', 'index.html')}), 'A'),
    ('Write Freigabe-Datei', ('Write', {'file_path': os.path.join(dev, '.claude', UNLOCK_NAME)}), 'D'),
]
for name, (tool, inp), want in cases:
    t(name, dev, dev, tool, inp, want)
live_cases = [
    ('auf main: git push', B('git push'), 'D'), ('auf main: git push origin HEAD', B('git push origin HEAD'), 'D'), ('auf main: git commit', B('git commit -m x'), 'D'),
    ('auf main: git merge', B('git merge foo'), 'D'), ('auf main: git reset', B('git reset --hard HEAD~1'), 'D'),
    ('auf main: Write public/index.html', ('Write', {'file_path': os.path.join(live, 'public', 'index.html')}), 'D'),
    ('auf main: Write README.md', ('Write', {'file_path': os.path.join(live, 'README.md')}), 'A'),
    ('auf main: git checkout entwicklung', B('git checkout entwicklung'), 'A'), ('auf main: git status', B('git status'), 'A'), ('auf main: git fetch', B('git fetch origin'), 'A'),
]
for name, (tool, inp), want in live_cases:
    t(name, live, live, tool, inp, want)
# Freigabe-Datei: gültig (in 1 Std.) erlaubt; zu weit in der Zukunft oder abgelaufen weiter gesperrt
ul = os.path.join(dev, '.claude', UNLOCK_NAME)
for label, exp, want in (('Freigabe gültig (1 Std.)', int(time.time()) + 3600, 'A'), ('Freigabe zu lang (5 Std.)', int(time.time()) + 18000, 'D'), ('Freigabe abgelaufen', int(time.time()) - 10, 'D')):
    open(ul, 'w').write(str(exp)); t(label + ': push HEAD:main', dev, dev, 'Bash', {'command': 'git push origin HEAD:main'}, want)
os.remove(ul)
p = subprocess.run([sys.executable, GUARD], input='kein json', capture_output=True, text=True, env=dict(os.environ, CLAUDE_PROJECT_DIR=dev)); fails += (p.returncode != 0)
print('OK      erlaubt  kaputte Eingabe blockiert nie' if p.returncode == 0 else 'FEHLER  kaputte Eingabe')
print('\nalle Tests bestanden' if not fails else '\n%d FEHLER' % fails)
sys.exit(1 if fails else 0)
