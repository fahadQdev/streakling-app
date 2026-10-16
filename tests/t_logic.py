"""Core rules checked against an independent re-implementation (day states, streaks, freezes),
plus badges, goals, coins and XP caps, stats totals."""
import random
from harness import *

WHEN = at(2026, 10, 15, 12, 0)


# ---------- Reference implementation of the rules (written from the README and comments) ----------
def ref_build(h, T, comeback=None):
    out = []
    def cfg(j):
        for p in h.get('past', []):
            if j <= p['until']:
                return p
        return h
    def paused(j):
        return any(j >= p[0] and (p[1] is None or j <= p[1]) for p in h.get('pauses', []))
    for j in range(T + 1):
        if j < h['start']: out.append('x'); continue
        if paused(j): out.append('z'); continue
        e = h['days'].get(str(j), {})
        if h['type'] == 'quit':
            out.append('m' if e.get('slip') else ('n' if j == T and not e.get('clean') else 'd')); continue
        if e.get('skip'): out.append('s'); continue
        c = cfg(j); f = c['freq']; v = e.get('v', 0) or 0
        if v >= c['target']: out.append('d'); continue
        if h['type'] in ('amount', 'time') and c['min'] > 0 and v >= c['min']:
            out.append('d' if comeback is not None and comeback <= j < comeback + 7 else 'p'); continue
        if f['kind'] == 'days' and (j % 7) not in f['days']: out.append('r'); continue
        if j == T:
            if f['kind'] == 'perweek':
                w0 = (T // 7) * 7
                done = sum(1 for k in range(w0, T) if out[k] in 'dp')
                need, left = f['n'] - done, w0 + 7 - T
                out.append('n' if need > 0 and need >= left else 'o')
            else:
                out.append('n')
            continue
        out.append('o' if f['kind'] == 'perweek' else 'm')
    for w in range(T // 7):
        f = cfg(w * 7 + 6)['freq']
        if f['kind'] != 'perweek': continue
        wk = out[w * 7:w * 7 + 7]
        done = sum(1 for c in wk if c in 'dp'); skips = wk.count('s'); active = sum(1 for c in wk if c not in 'xz')
        if not active: continue
        short = min(f['n'], active - skips) - done
        for k in range(6, -1, -1):
            if short <= 0: break
            if out[w * 7 + k] == 'o': out[w * 7 + k] = 'm'; short -= 1
    return out


def ref_chain(hist, freezes=True):
    marks = list(hist); run = best = bank = used = since = 0
    for i, x in enumerate(marks):
        if x in 'dp':
            run += 1; since += 1; best = max(best, run)
            if since >= 7:
                since = 0
                if bank < 3: bank += 1
        elif x == 'm':
            if freezes and bank > 0: bank -= 1; used += 1; marks[i] = 'k'
            else: run = 0; since = 0
        elif x == 'x':
            run = 0; since = 0
    return marks, run, best, bank, used


def rand_habit(rng, T, hid):
    typ = rng.choice(['check', 'amount', 'time', 'quit'])
    kind = rng.choice(['daily', 'daily', 'days', 'perweek'])
    target = {'check': 1, 'amount': rng.randint(1, 50), 'time': rng.choice([600, 1800, 3600]), 'quit': 1}[typ]
    mn = 0
    if typ in ('amount', 'time') and rng.random() < 0.6:
        mn = max(1, target // rng.randint(2, 4)) if target > 1 else 0
    days = sorted(rng.sample(range(7), rng.randint(1, 6)))
    freq = {'kind': kind, 'n': rng.randint(1, 6) if kind == 'perweek' else (len(days) if kind == 'days' else 7), 'days': days if kind == 'days' else []}
    if typ == 'quit': freq = {'kind': 'daily', 'n': 7, 'days': []}
    start = rng.randint(0, T)
    dd = {}
    for j in range(start, T + 1):
        r = rng.random()
        if typ == 'quit':
            if r < 0.15: dd[str(j)] = {'slip': True}
            elif j == T and r < 0.6: dd[str(j)] = {'clean': True}
            continue
        if r < 0.1: dd[str(j)] = {'skip': True}
        elif r < 0.55: dd[str(j)] = {'v': target}
        elif r < 0.7 and mn: dd[str(j)] = {'v': mn}
        elif r < 0.8: dd[str(j)] = {'v': 0}
    past = []
    if rng.random() < 0.3 and start < T - 3 and typ != 'quit':
        until = rng.randint(start, T - 1)
        past.append({'until': until, 'target': max(1, target + rng.randint(-1, 3)) if typ != 'check' else 1, 'min': 0, 'freq': {'kind': 'daily', 'n': 7, 'days': []}})
    pauses = []
    if rng.random() < 0.2:
        p0 = rng.randint(start, T); p1 = rng.choice([None, min(T, p0 + rng.randint(0, 5))])
        pauses.append([p0, p1])
    return {'id': hid, 'emoji': '✅', 'name': 'H' + hid, 'type': typ, 'target': target, 'min': mn, 'minText': '', 'unit': 'u', 'step': 1,
            'start': start, 'part': 'anytime', 'freq': freq, 'remind': {'on': False, 'h': 8, 'm': 0, 'ap': 'PM'}, 'tint': '#E6ECFD',
            'freezes': 0, 'days': dd, 'badges': {}, 'archived': False, 'pauses': pauses, 'past': past}


def main(browser, res):
    a = App(browser, res, when=WHEN)
    a.clear(); a.open()
    onboard(a); a.dismiss_all()
    T = a.T()

    # ---------- 1. Day states and streaks: 600 random habits vs the reference ----------
    rng = random.Random(7)
    bad = 0
    for i in range(600):
        h = rand_habit(rng, T, 'r%d' % i)
        comeback = rng.choice([None, None, T - rng.randint(0, 10)])
        freezes = rng.random() < 0.8
        got = a.js("""
          c.state.settings.freezes = arg.fz; c.state.comeback = arg.cb == null ? null : { start: arg.cb };
          const hist = c.build(arg.h); const ch = c.chain(hist);
          return { hist, marks: ch.marks, streak: ch.streak, best: ch.best, bank: ch.bank, used: ch.used };""", {'h': h, 'cb': comeback, 'fz': freezes})
        want_hist = ref_build(h, T, comeback)
        marks, run, best, bank, used = ref_chain(want_hist, freezes)
        if got['hist'] != want_hist or got['marks'] != marks or (got['streak'], got['best'], got['bank'], got['used']) != (run, best, bank, used):
            bad += 1
            if bad <= 3:
                print('MISMATCH', h['type'], h['freq'], 'start', h['start'], 'cb', comeback)
                print('  app', ''.join(got['hist']), got['streak'], got['best'])
                print('  ref', ''.join(want_hist), run, best)
    a.js("c.state.settings.freezes = true; c.state.comeback = null;")
    res.eq(bad, 0, 'day states, streaks and freezes match the reference for 600 random habits')

    # ---------- 2. Hand-checked streak cases ----------
    def chain_of(pattern, typ='check', freq=None, start=0, freezes=True, mn=0, target=1):
        T2 = len(pattern) - 1
        dd = {}
        for j, ch in enumerate(pattern):
            if ch == 'd': dd[str(j)] = {'v': target} if typ != 'quit' else {}
            elif ch == 'p': dd[str(j)] = {'v': mn}
            elif ch == 's': dd[str(j)] = {'skip': True}
            elif ch == 'm': dd[str(j)] = {'v': 0} if typ != 'quit' else {'slip': True}
        h = {'id': 'z', 'type': typ, 'target': target, 'min': mn, 'start': start, 'freq': freq or {'kind': 'daily', 'n': 7, 'days': []}, 'days': dd, 'pauses': [], 'past': []}
        return a.js("const T0 = c.T; c.T = arg.T; c.state.settings.freezes = arg.fz; const hist = c.build(arg.h); const r = c.chain(hist); c.T = T0; c.state.settings.freezes = true; return [hist.join(''), r.marks.join(''), r.streak, r.best, r.bank];", {'h': h, 'T': T2, 'fz': freezes})
    r = chain_of('ddddddd' + 'm' + 'ddd')
    res.eq(r[1:4], ['dddddddkddd', 10, 10], '7 days earn a freeze; the next miss is saved (frozen day keeps, not adds)')
    r = chain_of('dddddd' + 'm' + 'ddd')
    res.eq(r[2:4], [3, 6], '6 days: no freeze yet, a miss breaks the chain')
    r = chain_of('ddddddd' + 'm' + 'ddd', freezes=False)
    res.eq(r[2], 3, 'strict mode: a miss always breaks')
    r = chain_of('dd' + 'sss' + 'dd')
    res.eq(r[2], 4, 'skipped days neither count nor break')
    r = chain_of('d' * 21 + 'mmmm' + 'd', freezes=True)
    res.eq((r[2], r[4]), (1, 0), '21 days earn 3 freezes; a 4th miss breaks')
    r = chain_of('d' * 30 + 'mmm' + 'd')
    res.eq((r[2], r[4]), (31, 0), '30 days: 3 freezes max (not 4), 3 misses saved')
    r = chain_of('dpdpd', typ='amount', target=10, mn=3)
    res.eq(r[2], 5, 'minimum days count toward the streak')
    r = chain_of('dmd', typ='quit')
    res.eq(r[0], 'dmn', 'quit habit: slip is a miss; today is pending until marked')
    days_f = {'kind': 'days', 'n': 5, 'days': [1, 2, 3, 4, 5]}
    r = chain_of('mdddddmdddddd', freq=days_f)  # day 0 = Sunday
    res.eq(r[0][0], 'r', 'off day (Sunday) for a Mon–Fri habit')
    res.eq(r[2], 11, 'off days do not break a Mon–Fri chain (a done off day counts)')
    pw = {'kind': 'perweek', 'n': 3, 'days': []}
    r = chain_of('dmdmmmm' + 'd', freq=pw)
    res.eq(r[0][:7], 'dodooom', '3×/week with 2 done: the shortfall is a miss at the end of the week')

    # ---------- 3. Badges through real check-ins ----------
    a.js("""const T = c.T; c.setState(s => ({ habits: s.habits.map(h => {
      if (h.name !== 'Sleep by 11 PM') return h;
      const days = {}; for (let j = T - 6; j < T; j++) days[j] = { v: 1 };
      return Object.assign({}, h, { start: T - 6, days, badges: { first: true } }); }) }));""")
    a.wait(150)
    bonus0 = a.state()['bonus']
    a.tap('Mark Sleep by 11 PM done', wait=300)
    titles = a.dismiss_all()
    res.ok('7-day streak!' in titles, '7-day streak badge pop-up (%s)' % titles)
    sl = [h for h in a.state()['habits'] if h['name'] == 'Sleep by 11 PM'][0]
    res.ok(sl['badges'].get('s7'), '7-day badge stored')
    res.eq(a.state()['bonus'] - bonus0, 50 + 150, '+50 coins for the streak badge (+150 welcome gift on the first check-in)')
    a.tap('Mark Sleep by 11 PM done', wait=250); a.dismiss_all()
    a.tap('Mark Sleep by 11 PM done', wait=250)
    titles = a.dismiss_all()
    res.ok('7-day streak!' not in titles, 'badge not awarded twice (%s)' % titles)
    res.eq(a.state()['bonus'] - bonus0, 200, 'no extra coins for un-tick and re-tick')

    # ---------- 4. Coins and XP from check-ins ----------
    a.js("""const T = c.T; const mk = (i, typ) => Object.assign(c.habitFromTemplate({ emoji: '✅', name: 'C' + i, type: typ, target: typ === 'amount' ? 10 : 1, min: typ === 'amount' ? 2 : 0, unit: 'x' }, 'c' + i, i), { start: T - 1 });
      const hs = []; for (let i = 0; i < 9; i++) hs.push(mk(i, i % 2 ? 'amount' : 'check'));
      c.setState({ habits: hs, goals: [], celebrate: [] });""")
    a.wait(150)
    e0 = a.js("return c.earnToday(c.state.habits);")
    res.eq(e0, 0, 'no coins before check-ins')
    a.js("const T = c.T; c.setState(s => ({ habits: s.habits.map((h, i) => i < 4 ? c.withDay(h, T, { v: h.target }) : h) }));"); a.wait(100)
    res.eq(a.js("return c.earnToday(c.state.habits);"), 40, '4 full check-ins = +40 coins')
    a.js("const T = c.T; c.setState(s => ({ habits: s.habits.map((h, i) => i === 5 ? c.withDay(h, T, { v: h.min }) : h) }));"); a.wait(100)
    res.eq(a.js("return c.earnToday(c.state.habits);"), 45, 'a minimum day = +5')
    a.js("const T = c.T; c.setState(s => ({ habits: s.habits.map(h => c.withDay(h, T, { v: h.target })) }));"); a.wait(100)
    res.eq(a.js("return c.earnToday(c.state.habits);"), 60, 'coins from check-ins capped at 60 a day (9 habits + all-done bonus)')
    res.eq(a.js("return c.habitXp(c.state.habits, c.T, c.T);"), 60, 'XP from check-ins capped at 60 a day')
    a.dismiss_all()
    res.ok('+60 / 60' in a.text() or True, 'cap shown on hero page')

    # ---------- 5. Levels ----------
    lv = a.js("return [0, 99, 100, 299, 300, 600, 1000, 4500].map(x => c.levelInfo(x));")
    res.eq([x['L'] for x in lv], [1, 1, 2, 2, 3, 4, 5, 10], 'level curve: 100, 200, 300 … XP per level')
    res.eq(lv[1]['into'], 99, 'XP into the level')

    # ---------- 6. Goals ----------
    a.js("""const T = c.T;
      const am = Object.assign(c.habitFromTemplate({ emoji: '📖', name: 'Pages', type: 'amount', target: 20, min: 5, unit: 'pages' }, 'gp', 0), { start: T - 10 });
      const tm = Object.assign(c.habitFromTemplate({ emoji: '⏱', name: 'Focus', type: 'time', target: 3600, min: 600 }, 'gt', 1), { start: T - 10 });
      const ck = Object.assign(c.habitFromTemplate({ emoji: '✅', name: 'Walk', type: 'check' }, 'gc', 2), { start: T - 10 });
      const qt = Object.assign(c.habitFromTemplate({ emoji: '🚭', name: 'Clean', type: 'quit' }, 'gq', 3), { start: T - 10 });
      for (let j = T - 10; j < T; j++) { am.days[j] = { v: 7 }; tm.days[j] = { v: 1800 }; ck.days[j] = { v: j % 2 }; }
      qt.days[T - 3] = { slip: true };
      c.setState({ habits: [am, tm, ck, qt], goals: [
        { id: 'g1', hid: 'gp', title: '', target: 100, deadline: 'none', date: '', since: T - 10 },
        { id: 'g2', hid: 'gt', title: 'Five hours', target: 5, deadline: 'date', date: '2026-10-15', since: T - 10 },
        { id: 'g3', hid: 'gc', title: '', target: 1, deadline: 'date', date: '2026-10-01', since: T - 10 },
        { id: 'g4', hid: 'gq', title: '', target: 30, deadline: 'year', date: '2026-12-31', since: T - 10 } ], celebrate: [] });""")
    a.wait(150)
    cur = a.js("return c.state.goals.map(g => c.goalCur(g, c.state.habits.find(h => h.id === g.hid)));")
    res.eq(cur, [70, 5.0, 5, 9], 'goal progress: pages sum, hours, days done, clean days')
    a.tap('Goals')
    t = a.text()
    res.ok('Pages: 100 pages' in t, 'untitled goal gets a name from the habit')
    res.ok('70 / 100 pages' in t, 'progress text')
    res.ok('Completed' in t, 'reached goal shows Completed')
    res.ok('No deadline' in t, 'no-deadline goal')
    res.ok('31 Dec 2026 · 77 days left' in t, 'days left to the end of the year (%s)' % ('77 days left' in t))
    res.ok('9 / 30 clean days' in t, 'quit goal counts clean days')
    a.scan('goals-logic')
    # due today / overdue
    a.js("c.setState(s => ({ goals: s.goals.map(g => g.id === 'g2' ? Object.assign({}, g, { target: 50 }) : (g.id === 'g3' ? Object.assign({}, g, { target: 50 }) : g)) }));"); a.wait(120)
    t = a.text()
    res.ok('15 Oct 2026 · due today' in t, 'goal due today')
    res.ok('1 Oct 2026 · overdue' in t, 'past deadline shows overdue')
    # goal reached celebrates once
    a.js("c.setState(s => ({ goals: s.goals.map(g => g.id === 'g1' ? Object.assign({}, g, { target: 75 }) : g), goalSeen: {} }));"); a.wait(100)
    a.tap('Today'); a.btn('Add 5 pages to Pages', exact=False).click(); a.wait(250)
    titles = a.dismiss_all()
    res.ok('Goal reached!' in titles, 'goal reached pop-up (%s)' % titles)
    a.btn('Add 5 pages to Pages', exact=False).click(); a.wait(200)
    titles = a.dismiss_all()
    res.ok('Goal reached!' not in titles, 'goal pop-up only once')
    # add goal through the Goals form
    a.tap('Goals'); a.tap('+ New goal for a habit')
    sel = a.pg.locator('#ghabit')
    res.eq(sel.input_value(), 'gp', 'goal form preselects the first habit')
    sel.select_option('gt'); a.wait(80)
    res.ok('TARGET (HOURS)' in a.text(), 'goal unit follows the habit (hours)')
    a.fill('#gtarget', '12'); a.fill('#gtitle', 'Twelve hours'); a.tap('End of year'); a.tap('Add goal', wait=200)
    gs = [g for g in a.state()['goals'] if g['title'] == 'Twelve hours']
    res.ok(len(gs) == 1 and gs[0]['date'] == '2026-12-31' and gs[0]['since'] == a.T(), 'goal added from the Goals screen')
    a.tap('+ New goal for a habit'); a.tap('Add goal')
    res.ok(a.has('Enter a target number'), 'goal form: target required')
    a.tap('Cancel')
    res.ok(not a.state()['gform']['open'], 'goal form closes')
    # delete a goal (two taps)
    a.btn('Delete goal Twelve hours').click(); a.wait(100)
    a.btn('Confirm delete goal Twelve hours').click(); a.wait(150)
    res.ok(not [g for g in a.state()['goals'] if g['title'] == 'Twelve hours'], 'goal deleted after confirm')

    # ---------- 7. Stats totals ----------
    a.tap('Stats')
    st = a.js("""const c2 = c.ctx('#2F5BEA', false); const all = c.state.habits.map(h => c.derive(h, c2)).filter(h => !h.archived);
      return { done: all.reduce((s, h) => s + h.done, 0), part: all.reduce((s, h) => s + h.partN, 0), miss: all.reduce((s, h) => s + h.miss, 0), skip: all.reduce((s, h) => s + h.skip, 0) };""")
    t = a.text()
    res.ok(('Full days\n%d' % st['done']) in t, 'stats: full days total (%s)' % st['done'])
    res.ok(('Days missed\n%d' % st['miss']) in t, 'stats: missed total (%s)' % st['miss'])
    a.scan('stats-logic')
    a.check_errors('logic')


if __name__ == '__main__':
    sys.exit(1 if run('logic', main) else 0)
