"""Random sessions: random taps, typing, time jumps and reloads, with checks after every step.
Usage: python3 t_monkey.py [steps] [seed...]"""
import random
from harness import *

TEXTS = ['', '0', '7', '42', '999999', '-5', '3.5', 'abc', '😀', '🇸🇦', '👨‍👩‍👧', 'Read', 'قراءة القرآن', ' ', 'x' * 80, '<b>hi</b>', '{{x}}', '1e9']
AVOID = re.compile(r'^(Tap again to wipe everything|Download backup)$')

CHECK_JS = r"""() => {
  const c = """ + INST + r""";
  const s = c.state, out = [];
  const coins = c.coinsOf(s), xp = c.xpOf(s), lv = c.levelInfo(xp).L;
  if (!(coins >= 0) || !isFinite(coins)) out.push('coins ' + coins);
  if (!isFinite(xp)) out.push('xp ' + xp);
  if (!(lv >= 1)) out.push('level ' + lv);
  if (!Array.isArray(s.habits) || !Array.isArray(s.goals) || !Array.isArray(s.celebrate)) out.push('broken arrays');
  if (s.goals.some(g => !s.habits.find(h => h.id === g.hid))) out.push('goal without habit');
  if (s.char) {
    const D = c.px();
    [s.char.clothes, s.char.shoes, s.char.hair, s.char.rod].forEach(id => { if (id && !D.items[id]) out.push('unknown item ' + id); });
    (s.char.acc || []).concat(s.char.weapon || [], s.char.hat ? [s.char.hat] : []).forEach(id => { if (s.owned.indexOf(id) < 0) out.push('wearing unowned ' + id); });
  }
  if (s.timer && !s.habits.find(h => h.id === s.timer.hid)) out.push('timer for a missing habit');
  if (s.sheet && !s.habits.find(h => h.id === s.sheet.hid)) out.push('sheet for a missing habit');
  // A pop-up's main button must be reachable on screen.
  const dlg = document.querySelector('[role=dialog][aria-modal=true]');
  if (dlg) {
    const btns = Array.from(dlg.querySelectorAll('button')).filter(b => b.getBoundingClientRect().height > 0);
    const host = document.querySelector('#app > div').getBoundingClientRect();
    const reach = btns.some(b => { const r = b.getBoundingClientRect(); return r.bottom <= host.bottom + 1 && r.top >= host.top - 1; });
    const scrollable = (() => { for (let e = btns[btns.length - 1]; e && e !== dlg.parentElement; e = e.parentElement) { const cs = getComputedStyle(e); if ((cs.overflowY === 'auto' || cs.overflowY === 'scroll') && e.scrollHeight > e.clientHeight) return true; } return false; })();
    if (btns.length && !reach && !scrollable) out.push('pop-up button off screen: ' + (dlg.getAttribute('aria-label') || ''));
  }
  return out;
}"""


def step(a, rng, log):
    pg = a.pg
    r = rng.random()
    if r < 0.05:
        ms = rng.choice([60e3, 15 * 60e3, 3 * 3600e3, 20 * 3600e3, 3 * 86400e3])
        log.append('time +%dmin' % (ms / 60000))
        pg.clock.fast_forward(int(ms)); a.wait(300)
        return
    if r < 0.09:
        log.append('reload')
        before = a.js("return JSON.stringify(c.persistable(c.state));")
        a.save(); pg.reload(); a.wait(700)
        after = a.js("return JSON.stringify(c.persistable(c.state));")
        if before != after:
            import json as _j
            b, f = _j.loads(before), _j.loads(after)
            diff = [k for k in set(b) | set(f) if b.get(k) != f.get(k)]
            # day/lastDay can legitimately move only if the date changed
            if [k for k in diff if k not in ('lastDay',)]:
                a.res.failed.append('reload changed data: %s | steps: %s' % (diff, ' > '.join(log[-12:])))
        return
    if r < 0.22:
        ins = [x for x in pg.locator('#app input:not([type=file]), #app select').all() if x.is_visible()]
        if ins:
            el = rng.choice(ins)
            tag = el.evaluate('e => e.tagName')
            try:
                if tag == 'SELECT':
                    opts = el.evaluate('e => Array.from(e.options).map(o => o.value)')
                    if opts:
                        v = rng.choice(opts); el.select_option(v); log.append('select %s' % v)
                else:
                    t = rng.choice(TEXTS)
                    if el.get_attribute('type') == 'date':
                        t = rng.choice(['2026-10-01', '2026-10-15', '2027-02-28', '2030-01-01'])
                    el.fill(t); log.append('type %r into %s' % (t[:12], el.get_attribute('id') or el.get_attribute('aria-label')))
            except Exception as e:
                log.append('type failed %s' % str(e)[:60])
            a.wait(60)
            return
    btns = [b for b in pg.locator('#app button:enabled').all()]
    vis = []
    for b in btns:
        try:
            if not b.is_visible(): continue
            name = (b.get_attribute('aria-label') or b.inner_text() or '').strip()
            if AVOID.match(name): continue
            if name == 'Tap again to replace everything' and rng.random() < 0.8: continue
            vis.append((b, name))
        except Exception:
            pass
    if not vis:
        log.append('no buttons')
        return
    b, name = rng.choice(vis)
    log.append('tap %s' % name[:40].replace('\n', ' '))
    try:
        b.click(timeout=1500)
    except Exception:
        try:
            b.dispatch_event('click')
        except Exception:
            pass
    a.wait(rng.choice([40, 80, 160]))


def session(browser, res, seed, steps, w, h, tz='Asia/Riyadh'):
    rng = random.Random(seed)
    a = App(browser, res, width=w, height=h, tz=tz, when=at(2026, 10, rng.randint(1, 28), rng.randint(0, 23), rng.randint(0, 59)), label='seed%d-%dx%d:' % (seed, w, h))
    a.res = res
    a.clear(); a.open()
    if rng.random() < 0.5:
        demo(a)
    log = []
    for i in range(steps):
        try:
            step(a, rng, log)
        except Exception as e:
            log.append('step error %s' % str(e)[:80])
        if a.errors:
            res.failed.append('seed %d step %d: %s | steps: %s' % (seed, i, a.errors[:2], ' > '.join(log[-12:])))
            a.errors.clear()
        try:
            bad = a.pg.evaluate(CHECK_JS)
        except Exception as e:
            bad = ['check failed: %s' % str(e)[:100]]
        if bad:
            res.failed.append('seed %d step %d: %s | steps: %s' % (seed, i, bad, ' > '.join(log[-12:])))
        if i % 25 == 0:
            for it in a.scan('monkey', contrast=False):
                if it['kind'] in ('bad-text', 'bad-attr', 'bad-style', 'overflow-x', 'hscroll', 'dup-id'):
                    res.failed.append('seed %d step %d: %s %s %s | steps: %s' % (seed, i, it['kind'], it['msg'], it['where'], ' > '.join(log[-8:])))
    res.passed += steps
    a.close()


def main(browser, res, steps, seeds):
    sizes = [(390, 844), (320, 568), (667, 375), (430, 932)]
    for k, seed in enumerate(seeds):
        w, h = sizes[seed % len(sizes)]
        tz = ['Asia/Riyadh', 'America/New_York', 'Europe/London', 'Asia/Tokyo'][(seed // 4) % 4]
        session(browser, res, seed, steps, w, h, tz)
        print('seed %d done (%dx%d %s), failures so far %d' % (seed, w, h, tz, len(res.failed)), flush=True)


if __name__ == '__main__':
    steps = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    seeds = [int(x) for x in sys.argv[2:]] or [1, 2, 3, 4]
    sys.exit(1 if run('monkey', lambda b, r: main(b, r, steps, seeds)) else 0)
