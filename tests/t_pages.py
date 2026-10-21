"""The other published files: design boards, manifest, icons, service worker."""
import json, urllib.request
from harness import *


def main(browser, res):
    for path in ['design/characters.html', 'design/items.html', 'design/fishing.html']:
        a = App(browser, res, width=1280, height=900)
        a.pg.goto(URL + path); a.wait(800)
        res.ok(len(a.pg.inner_text('body')) > 50, path + ' has content')
        a.check_errors(path)
        a.close()
    m = json.loads(urllib.request.urlopen(URL + 'manifest.webmanifest').read())
    res.ok(m.get('name') and m.get('start_url') and m.get('display') == 'standalone', 'manifest basics (%s)' % {k: m.get(k) for k in ('name', 'start_url', 'display')})
    for ic in m.get('icons', []):
        code = urllib.request.urlopen(URL + ic['src']).status
        res.eq(code, 200, 'icon ' + ic['src'])
    sw = urllib.request.urlopen(URL + 'sw.js').read().decode()
    res.ok("streakling-v0.15.0" in sw, 'service worker cache named for this version')
    html = urllib.request.urlopen(URL).read().decode()
    res.ok('v0.15.0' in html, 'index built from v0.15.0')
    # Text comes from the language tables; a missing key would show up as the key itself.
    a = App(browser, res)
    a.clear(); a.open(); demo(a)
    keys = a.pg.evaluate("() => Object.keys(STREAKLING_STR.en).filter(k => /[a-z][A-Z]/.test(k))")
    res.ok(len(keys) > 500, 'English text table is inlined (%d camelCase keys)' % len(keys))
    seen = ''
    for tab in ['Today', 'Stats', 'Character', 'Goals', 'Leaderboard']:
        a.tap(tab, wait=400); seen += a.text()
    a.go_settings(); seen += a.text()
    shown = sorted(k for k in keys if k in seen)
    res.ok(not shown, 'no raw text keys on screen (%s)' % shown[:5])
    a.close()
    for th in ['light', 'dark']:
        a = App(browser, res)
        a.clear(); a.open(); demo(a); a.set({'settings': dict(a.state()['settings'], theme=th)})
        st = a.pg.evaluate("() => document.querySelector('#app > div').getAttribute('style')")
        res.ok('color-mix' not in st and '--accentSoft: #' in st, 'theme colours are plain hex, no color-mix() (%s)' % th)
        a.close()


if __name__ == '__main__':
    sys.exit(1 if run('pages', main) else 0)
