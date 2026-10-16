"""Shared helpers for the Streakling QA runs (Playwright, Chromium)."""
import datetime as dt
import json
import os
import re
import sys
import time
import traceback

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
URL = os.environ.get('APP_URL', 'http://localhost:8765/')
SHOTS = os.path.join(HERE, 'shots')
os.makedirs(SHOTS, exist_ok=True)
SCAN_JS = open(os.path.join(HERE, 'scan.js'), encoding='utf-8').read()
INST = "document.getElementById('app').__k.__k[0].__c"
RIYADH = dt.timezone(dt.timedelta(hours=3))

# Console noise that is not an app problem: web fonts can't load in this sandbox.
IGNORE_CONSOLE = re.compile(r'ERR_TUNNEL_CONNECTION_FAILED|fonts\.g|net::ERR_|Failed to load resource')


class Results:
    def __init__(self, name):
        self.name = name
        self.passed = 0
        self.failed = []
        self.issues = {}

    def ok(self, cond, msg):
        if cond:
            self.passed += 1
        else:
            self.failed.append(msg)
            print('  FAIL', msg, flush=True)
        return cond

    def eq(self, got, want, msg):
        return self.ok(got == want, '%s (got %r, want %r)' % (msg, got, want))

    def issue(self, where, item):
        key = (item['kind'], item['msg'], item['where'])
        self.issues.setdefault(key, []).append(where)

    def summary(self):
        print('\n== %s: %d passed, %d failed, %d distinct screen issues' % (self.name, self.passed, len(self.failed), len(self.issues)))
        for m in self.failed:
            print('  FAIL', m)
        kinds = {}
        for (k, msg, where), places in sorted(self.issues.items()):
            kinds.setdefault(k, []).append((msg, where, places))
        for k, rows in kinds.items():
            print('  [%s] %d' % (k, len(rows)))
            for msg, where, places in rows[:40]:
                print('     %s | %s | %s%s' % (msg, where, ', '.join(places[:3]), (' +%d' % (len(places) - 3)) if len(places) > 3 else ''))
        return len(self.failed)


def at(y, mo, d, h=10, mi=0):
    """A local Riyadh time as an aware datetime."""
    return dt.datetime(y, mo, d, h, mi, tzinfo=RIYADH)


class App:
    """One browser page running the app, with helpers."""

    def __init__(self, browser, res, width=390, height=844, tz='Asia/Riyadh', when=None, scheme='light', label=''):
        self.res = res
        self.ctx = browser.new_context(viewport={'width': width, 'height': height}, color_scheme=scheme, timezone_id=tz,
                                       locale='en-US', device_scale_factor=1, has_touch=False)
        try:
            self.ctx.grant_permissions(['clipboard-read', 'clipboard-write'], origin=URL.rstrip('/'))
        except Exception:
            pass
        self.pg = self.ctx.new_page()
        self.errors = []
        self.label = label
        self.pg.on('pageerror', lambda e: self.errors.append('pageerror: ' + str(e)))
        self.pg.on('console', lambda m: self.errors.append('console.' + m.type + ': ' + m.text) if m.type == 'error' and not IGNORE_CONSOLE.search(m.text) else None)
        if when is not None:
            self.pg.clock.install(time=when)

    # ---------- navigation and state ----------
    def open(self, wait=500):
        self.pg.goto(URL)
        self.pg.wait_for_selector('#app > div', timeout=10000)
        self.pg.wait_for_timeout(wait)
        return self

    def blank(self):
        """A same-origin page without the app, for editing storage safely."""
        self.pg.goto(URL + 'manifest.webmanifest')

    def put_env(self, env):
        self.blank()
        self.pg.evaluate("e => localStorage.setItem('streakling:v1', JSON.stringify(e))", env)

    def clear(self):
        self.blank()
        self.pg.evaluate("() => localStorage.clear()")

    def env(self):
        return self.pg.evaluate("() => JSON.parse(localStorage.getItem('streakling:v1') || 'null')")

    def js(self, body, arg=None):
        """Run JS with `c` bound to the app component."""
        return self.pg.evaluate('(arg) => { const c = ' + INST + '; ' + body + ' }', arg)

    def state(self):
        return self.js("return JSON.parse(JSON.stringify(c.state));")

    def T(self):
        return self.js("return c.T;")

    def set(self, patch, wait=150):
        self.js("c.setState(arg);", patch)
        self.pg.wait_for_timeout(wait)

    def save(self):
        self.js("c.saveNow();")

    def text(self):
        return self.pg.inner_text('#app')

    def wait(self, ms=200):
        self.pg.wait_for_timeout(ms)

    # ---------- interaction ----------
    def btn(self, name, exact=True, nth=0):
        loc = self.pg.get_by_role('button', name=name, exact=exact)
        return loc.nth(nth)

    def tap(self, name, exact=True, nth=0, wait=200, force=False):
        self.btn(name, exact, nth).click(force=force, timeout=5000)
        self.pg.wait_for_timeout(wait)

    def go_settings(self):
        if self.state()['screen'] != 'today':
            self.tap('Today')
        self.tap('Settings')

    def tap_text(self, text, exact=True, nth=0, wait=200):
        self.pg.get_by_text(text, exact=exact).nth(nth).click(timeout=5000)
        self.pg.wait_for_timeout(wait)

    def fill(self, sel, value, wait=100):
        loc = self.pg.locator(sel)
        loc.fill(value)
        self.pg.wait_for_timeout(wait)

    def has(self, text):
        return text in self.text()

    def dismiss_all(self, limit=200):
        """Close every celebration pop-up. Returns their titles."""
        titles = []
        for _ in range(limit):
            d = self.pg.locator('[role=dialog][aria-modal=true]')
            st = self.state()
            if not st.get('celebrate'):
                break
            titles.append(st['celebrate'][0].get('title'))
            self.js("c.setState(s => ({ celebrate: s.celebrate.slice(1) }));")
            self.pg.wait_for_timeout(60)
        return titles

    def scan(self, where, **opts):
        items = self.pg.evaluate(SCAN_JS, opts)
        for it in items:
            self.res.issue(self.label + where, it)
        return items

    def shot(self, name, full=False):
        path = os.path.join(SHOTS, name + '.png')
        self.pg.screenshot(path=path, full_page=full)
        return path

    def check_errors(self, where=''):
        errs = [e for e in self.errors]
        self.errors.clear()
        self.res.ok(not errs, 'no page/console errors %s: %s' % (where, errs[:3]))
        return errs

    def close(self):
        try:
            self.ctx.close()
        except Exception:
            pass


def run(name, fn):
    """Run one test module with its own browser and print a summary. Returns failure count."""
    res = Results(name)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            fn(browser, res)
        except Exception:
            res.failed.append('CRASH: ' + traceback.format_exc()[-1500:])
            print(traceback.format_exc(), flush=True)
        finally:
            browser.close()
    return res.summary()


def onboard(app, name='Fahad', focus=('health',), picks=None, sex=None):
    """Complete first-time setup through the UI."""
    pg = app.pg
    app.tap('Get started')
    app.fill('#obname', name)
    if sex == 'girl':
        pg.locator('button[aria-pressed]').filter(has_text='Girl').first.click()
    app.tap('Create my hero')
    for f in focus:
        pg.locator('button[aria-pressed]').filter(has_text=f.capitalize() if f != 'quit' else 'Quit a bad habit').first.click()
        app.wait(80)
    app.tap('Continue')
    if picks is not None:
        cur = app.state()['onboard']['picks']
        want = set(picks)
        for k in cur:
            if k not in want:
                app.js("const o = c.state.onboard; c.setState({ onboard: Object.assign({}, o, { picks: o.picks.filter(x => x !== arg) }) });", k)
        cur = app.state()['onboard']['picks']
        for k in picks:
            if k not in cur:
                app.js("const o = c.state.onboard; c.setState({ onboard: Object.assign({}, o, { picks: o.picks.concat([arg]) }) });", k)
        app.wait(100)
    pg.locator('button').filter(has_text=re.compile(r'^Start with')).click()
    app.wait(300)


def demo(app):
    """Replace data with the built-in sample data (Settings > Demo tools > Load sample data)."""
    app.js("c.resetEpoch(); c.setState(Object.assign(c.demoState(c.state.settings), { screen: 'today' }));")
    app.wait(250)
