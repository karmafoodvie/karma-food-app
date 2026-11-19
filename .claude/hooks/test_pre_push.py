#!/usr/bin/env python3
"""Selbsttest des git-pre-push-Hooks mit einem Wegwerf-Remote (pusht NIE ins echte Repo):  python3 .claude/hooks/test_pre_push.py"""
import os, shutil, subprocess, sys, tempfile, time
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
HOOK = os.path.join(ROOT, '.githooks', 'pre-push')
UNLOCK_NAME = 'live' + '-unlock'


def g(*a, cwd=None):
    return subprocess.run(['git', *a], cwd=cwd, capture_output=True, text=True)


tmp = tempfile.mkdtemp()
remote = os.path.join(tmp, 'remote.git'); work = os.path.join(tmp, 'work')
g('init', '-q', '--bare', '-b', 'main', remote)
g('clone', '-q', remote, work)
g('config', 'user.email', 't@t', cwd=work); g('config', 'user.name', 't', cwd=work)
os.makedirs(os.path.join(work, '.githooks')); os.makedirs(os.path.join(work, '.claude'))
shutil.copy(HOOK, os.path.join(work, '.githooks', 'pre-push')); os.chmod(os.path.join(work, '.githooks', 'pre-push'), 0o755)
g('config', 'core.hooksPath', '.githooks', cwd=work)
open(os.path.join(work, 'f'), 'w').write('1'); g('add', '.', cwd=work)
g('-c', 'core.hooksPath=/dev/null', 'commit', '-q', '-m', 'start', cwd=work)
g('checkout', '-q', '-b', 'main', cwd=work) if g('rev-parse', '--abbrev-ref', 'HEAD', cwd=work).stdout.strip() != 'main' else None
fails = 0


def check(name, args, want_ok):
    global fails
    r = g(*args, cwd=work); ok = (r.returncode == 0) == want_ok; fails += (not ok)
    print(('OK     ' if ok else 'FEHLER '), 'erlaubt ' if want_ok else 'gesperrt', name)


check('push main (ohne Freigabe)', ['push', 'origin', 'main'], False)
check('push HEAD:refs/heads/main', ['push', 'origin', 'HEAD:refs/heads/main'], False)
check('push --force origin main', ['push', '--force', 'origin', 'main'], False)
g('checkout', '-q', '-b', 'entwicklung', cwd=work)
open(os.path.join(work, 'g'), 'w').write('2'); g('add', '.', cwd=work); g('commit', '-q', '-m', 'x', cwd=work)
check('push entwicklung (Feature-Branch)', ['push', '-u', 'origin', 'entwicklung'], True)
check('push entwicklung:main (Umweg über anderen Namen)', ['push', 'origin', 'entwicklung:main'], False)
check('Löschen von main', ['push', 'origin', ':main'], False)
ul = os.path.join(work, '.claude', UNLOCK_NAME)
open(ul, 'w').write(str(int(time.time()) + 3600))
check('push entwicklung:main MIT gültiger Freigabe (1 Std.)', ['push', 'origin', 'entwicklung:main'], True)
open(ul, 'w').write(str(int(time.time()) + 20000))
g('checkout', '-q', 'main', cwd=work); open(os.path.join(work, 'h'), 'w').write('3'); g('add', '.', cwd=work); g('commit', '-q', '-m', 'y', cwd=work)
check('push main mit zu langer Freigabe (5,5 Std.)', ['push', 'origin', 'main'], False)
open(ul, 'w').write(str(int(time.time()) - 5))
check('push main mit abgelaufener Freigabe', ['push', 'origin', 'main'], False)
shutil.rmtree(tmp, ignore_errors=True)
print('\nalle Tests bestanden' if not fails else '\n%d FEHLER' % fails)
sys.exit(1 if fails else 0)
