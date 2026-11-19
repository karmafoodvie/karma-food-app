#!/usr/bin/env python3
"""Live-Schutz für die Karma Food App (Claude-Code-Hook, PreToolUse).

Verhindert, dass in einer Claude-Session unabsichtlich die LIVE-App oder die LIVE-Datenbank verändert wird:
  · Push/Merge/Commit auf main oder master, Force-Push, Branch löschen, `gh pr merge`, `vercel --prod`
  · Datenbank-Änderungen über die Supabase-Verbindung (alles außer reinem Lesen)
  · Bearbeiten von public/ (die ausgelieferte App), solange der Branch main/master ist
Alles andere (Arbeiten auf entwicklung / Feature-Branches, Push auf diese Branches, Lesen der Datenbank) bleibt erlaubt.

Freigabe für bewusste Live-Änderungen: Datei .claude/live-unlock mit Ablaufzeit (Unix-Sekunden, höchstens 2 Stunden
in der Zukunft). Sie kann nur ein Mensch anlegen; Claude-Tools, die sie anlegen wollen, werden blockiert.
Dieser Schutz verhindert Versehen, keine absichtliche Umgehung. Blockiert wird mit Exit-Code 2 (Meldung geht an Claude).
"""
import json, os, re, subprocess, sys, time

LIVE_BRANCHES = ('main', 'master')
PROJECT = os.environ.get('CLAUDE_PROJECT_DIR') or os.getcwd()
UNLOCK = os.path.join(PROJECT, '.claude', 'live-unlock')


def deny(msg):
    sys.stderr.write('LIVE-SCHUTZ: ' + msg + '\n'
                     'Live geht nur bewusst: Pull Request auf GitHub selbst mergen (dein Klick), Datenbank-Änderungen im Supabase-Editor selbst ausführen, '
                     'oder eine Freigabe-Datei .claude/live-unlock (Ablaufzeit, max. 2 Std.) selbst anlegen. Claude kann das nicht für dich tun.\n')
    sys.exit(2)


def unlocked():
    try:
        exp = int(open(UNLOCK).read().strip().split()[0])
    except Exception:
        return False
    now = int(time.time())
    return now < exp <= now + 7200


def current_branch(cwd):
    try:
        return subprocess.run(['git', '-C', cwd or PROJECT, 'rev-parse', '--abbrev-ref', 'HEAD'],
                              capture_output=True, text=True, timeout=5).stdout.strip()
    except Exception:
        return ''


_TEXT_ARG = re.compile(r'''(\s(?:-m|--message|-b|--body|--title|-t)(?:=|\s+))("(?:[^"\\]|\\.)*"|'[^']*')''', re.S)


def mask_text_args(cmd):
    """Freitext-Argumente (Commit-Nachricht, PR-Titel/-Text) sind keine Befehle: ihren Inhalt vor der Prüfung ausblenden."""
    return _TEXT_ARG.sub(lambda m: m.group(1) + '""', cmd)


def split_commands(cmd):
    return [c.strip() for c in re.split(r'&&|\|\||;|\n|\|', cmd) if c.strip()]


def check_git_push(seg, branch):
    m = re.search(r'\bgit\b(?:\s+-C\s+\S+)?\s+push\b(.*)', seg)
    if not m:
        return
    args = [a.strip('\'"`)(') for a in m.group(1).split()]
    args = [a for a in args if a]
    flags = [a for a in args if a.startswith('-')]
    refs = [a for a in args if not a.startswith('-')]
    if any(f in ('--all', '--mirror') for f in flags):
        deny('`git push --all/--mirror` würde auch main überschreiben.')
    targets = refs[1:] if refs else []  # refs[0] ist der Remote-Name
    if not refs:
        targets = []
    for t in targets:
        spec = t.lstrip('+')
        dst = spec.split(':', 1)[1] if ':' in spec else spec
        dst = re.sub(r'^refs/heads/', '', dst)
        if dst in LIVE_BRANCHES or (spec in ('HEAD', '@') and branch in LIVE_BRANCHES):
            deny('Push auf %s ist gesperrt (löst sofort einen Live-Deploy aus).' % dst if dst != 'HEAD' else 'Push von %s ist gesperrt.' % branch)
        if spec.startswith(':') and spec[1:] in LIVE_BRANCHES:
            deny('Löschen von %s ist gesperrt.' % spec[1:])
    if any(f in ('-d', '--delete') for f in flags) and any(t in LIVE_BRANCHES for t in targets):
        deny('Löschen von main ist gesperrt.')
    if len(refs) <= 1 and branch in LIVE_BRANCHES:  # `git push` ohne Ziel auf main
        deny('Du bist auf %s: `git push` würde live gehen. Erst auf entwicklung wechseln.' % branch)


def check_bash(cmd, cwd):
    branch = current_branch(cwd)
    cmd = mask_text_args(cmd)
    if 'live-unlock' in cmd and re.search(r'(>|\btouch\b|\btee\b|\bcp\b|\bmv\b|\bln\b|\bdd\b|\bsed\b|\bprintf\b|\becho\b|\binstall\b|open\(|write)', cmd):
        deny('Die Freigabe-Datei darf nur ein Mensch anlegen.')
    for seg in split_commands(cmd):
        check_git_push(seg, branch)
        if re.search(r'\bgh\s+pr\s+merge\b', seg):
            deny('`gh pr merge` ist gesperrt: Den Merge nach main klickst du selbst in GitHub.')
        if re.search(r'\bgh\s+api\b', seg) and re.search(r'(-X|--method)\s+(PUT|POST|PATCH|DELETE)', seg, re.I) and re.search(r'(/merges|/merge\b|branches/(main|master)|rulesets|protection|git/refs/heads/(main|master))', seg):
            deny('Schreibende GitHub-API-Aufrufe auf main/Schutzregeln sind gesperrt.')
        if re.search(r'\bvercel\b', seg) and re.search(r'(--prod\b|\bpromote\b|\balias\b|\brollback\b|\bremove\b|\brm\b)', seg):
            deny('Vercel-Produktions-Befehle sind gesperrt.')
        if branch in LIVE_BRANCHES and re.search(r'\bgit\s+(commit|merge|rebase|cherry-pick|revert|reset|am|apply|pull)\b', seg):
            deny('Du bist auf %s. Dort wird nicht committet oder verändert. Erst `git checkout entwicklung`.' % branch)


SQL_WRITE = re.compile(r'\b(insert|update|delete|alter|drop|create|truncate|grant|revoke|comment|vacuum|reindex|cluster|refresh|copy|call|do|merge|lock|reset|notify|listen|nextval|setval|lo_import|lo_export|pg_terminate_backend|pg_cancel_backend)\b|\bset\s+(role|session|local)\b', re.I)


def strip_sql(q):
    q = re.sub(r'/\*.*?\*/', ' ', q, flags=re.S)
    q = re.sub(r'--[^\n]*', ' ', q)
    q = re.sub(r"'(?:[^']|'')*'", "''", q)
    q = re.sub(r'\$([A-Za-z_]*)\$.*?\$\1\$', "''", q, flags=re.S)
    q = re.sub(r'"(?:[^"]|"")*"', '""', q)
    return q


def check_supabase(tool, inp):
    name = tool.split('__')[-1]
    if name in ('apply_migration', 'deploy_edge_function', 'create_edge_function_secret', 'merge_branch', 'reset_branch', 'rebase_branch',
                'delete_branch', 'pause_project', 'restore_project'):
        deny('Supabase-Aktion „%s“ verändert die Live-Datenbank/Funktionen und ist gesperrt.' % name)
    if name == 'execute_sql':
        q = strip_sql(inp.get('query', ''))
        m = SQL_WRITE.search(q)
        if m:
            deny('SQL mit „%s“ verändert Live-Daten. Nur lesende Abfragen (select) sind erlaubt.' % m.group(0))


def check_edit(inp, cwd):
    path = inp.get('file_path') or inp.get('notebook_path') or ''
    full = os.path.abspath(path if os.path.isabs(path) else os.path.join(cwd or PROJECT, path))
    if full.endswith(os.path.join('.claude', 'live-unlock')):
        deny('Die Freigabe-Datei darf nur ein Mensch anlegen.')
    rel = os.path.relpath(full, PROJECT)
    branch = current_branch(os.path.dirname(full) if os.path.isdir(os.path.dirname(full)) else cwd)
    if rel.startswith('public' + os.sep) and branch in LIVE_BRANCHES:
        deny('public/ ist die ausgelieferte Live-App und der Branch ist %s. Erst auf entwicklung wechseln.' % branch)


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0  # kaputte Eingabe nie zum Blockieren verwenden
    tool, inp, cwd = data.get('tool_name', ''), data.get('tool_input', {}) or {}, data.get('cwd')
    if unlocked():
        return 0
    if tool == 'Bash':
        check_bash(inp.get('command', ''), cwd)
    elif tool.startswith('mcp__Supabase__'):
        check_supabase(tool, inp)
    elif tool in ('Edit', 'Write', 'NotebookEdit'):
        check_edit(inp, cwd)
    return 0


if __name__ == '__main__':
    sys.exit(main())
