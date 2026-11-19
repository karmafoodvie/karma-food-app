#!/usr/bin/env python3
"""Bindet das Karma-Food-Design (design/karma-skin.css) in public/index.html ein (idempotent):  python3 test-env/design/apply_karma.py"""
import os, re, sys
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
p = os.path.join(root, 'public', 'index.html'); css = open(os.path.join(os.path.dirname(__file__), 'karma-skin.css'), encoding='utf-8').read()
s = open(p, encoding='utf-8').read()


def expand(c):
    """BG(#hex,...){…} / FG(#hex,...){…} -> Selektoren, die NUR exakte Farbwerte treffen (nicht Tönungen wie #F9731612)."""
    def sel(kind, hexes):
        out = []
        for h in [x.strip() for x in hexes.split(',')]:
            if kind == 'BG':
                out += ['html.karma [style*="background:%s;" i]' % h, 'html.karma [style$="background:%s" i]' % h]
            else:
                out += ['html.karma [style*=";color:%s;" i]' % h, 'html.karma [style^="color:%s;" i]' % h, 'html.karma [style$=";color:%s" i]' % h]
        return ','.join(out)
    return re.sub(r'^(BG|FG)\(([^)]*)\)\{', lambda m: sel(m.group(1), m.group(2)) + '{', c, flags=re.M)


css = expand(css)
act = '''<script>/* Karma-Food-Design: Einschalten mit ?design=karma, ausschalten mit ?design=off (gilt pro Gerät). Standard bleibt das bisherige Aussehen. */
(function(){try{var m=location.search.match(/[?&]design=(karma|apple|off)\\b/);if(m)localStorage.setItem('kf_design',m[1]);if(localStorage.getItem('kf_design')==='karma'){var h=document.documentElement;h.classList.remove('apple');h.classList.add('karma');var l=document.createElement('link');l.rel='stylesheet';l.href='https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&display=swap';document.head.appendChild(l);var v=document.querySelector('meta[name=viewport]');if(v&&v.content.indexOf('viewport-fit')<0)v.content+=', viewport-fit=cover';}}catch(e){}})();
</script>
'''
# Aktivierungs-Skript: nach dem Apple-Schalter
s = re.sub(r'<script>/\* Karma-Food-Design: Einschalten.*?</script>\n', '', s, flags=re.S)
a = s.index('<script>/* Apple-Design'); e = s.index('</script>\n', a) + len('</script>\n')
s = s[:e] + act + s[e:]
# Stylesheet: vor </head>, nach dem Apple-Stylesheet
s = re.sub(r'<style id="karma-skin">.*?</style>\n', '', s, flags=re.S)
i = s.index('</head>')
s = s[:i] + '<style id="karma-skin">\n' + css + '\n</style>\n' + s[i:]
open(p, 'w', encoding='utf-8').write(s)
print('Karma-Design eingebunden; Version:', re.search(r"APP_VERSION='([\d.]+)'", s).group(1))
