"""Remaining UI flows: coach tips, reasons card, heatmap taps, comeback week, schedule edits,
pop-up queue, trip card shortcuts, recap, clock going back, countdown seconds, quit-habit comeback."""
import datetime as dt
from harness import *

WHEN = at(2026, 10, 15, 10, 0)


def H(a, name):
    return next((h for h in a.state()['habits'] if h['name'] == name), None)


def main(browser, res):
    a = App(browser, res, when=WHEN)
    a.clear(); a.open(); demo(a); a.dismiss_all()
    T = a.T()

    # ---------- Coach ----------
    res.ok(a.has('Quran: ready for 5 pages?'), 'coach suggests a higher target')
    q0 = H(a, 'Quran')
    a.tap('Raise to 5 pages', wait=200)
    q1 = H(a, 'Quran')
    res.eq(q1['target'], 5, 'coach raised the target')
    res.ok(q1['past'] and q1['past'][-1]['target'] == 4 and q1['past'][-1]['until'] == T - 1, 'old target kept for past days')
    res.ok(not a.has('Quran: ready for'), 'coach card gone after accepting')
    res.eq(a.state()['coachSkip'].get('quran'), T, 'tips paused for this habit')
    a.js("c.setState(s => ({ coachSkip: { quran: c.T - 6 }, habits: s.habits.map(h => h.id === 'quran' ? c.withDay(h, c.T, { v: 5 }) : h) }));"); a.wait(100)
    res.ok('COACH' not in a.text(), 'tips stay paused for 7 days')
    a.js("c.setState(s => ({ coachSkip: { quran: c.T - 7 } }));"); a.wait(100)
    res.ok('COACH' in a.text(), 'tips come back after 7 days')
    a.tap('Not now', wait=150)
    res.ok(not a.has('Quran: ready for 6 pages?'), 'Not now hides the tip')

    # ---------- Reasons card ----------
    a.js("const T = c.T; c.setState(s => ({ habits: s.habits.map(h => h.id === 'read' ? c.withDay(h, T - 1, { v: 0 }) : h) }));"); a.wait(120)
    res.ok(a.has('Yesterday you missed'), 'reasons card')
    n0 = len(a.js("return c.renderVals().ask;"))
    a.tap('Busy', wait=150)
    n1 = len(a.js("return c.renderVals().ask;"))
    res.eq(n1, n0 - 1, 'answering removes that habit from the card')
    res.eq(H(a, 'Read')['days'][str(T - 1)].get('reason') or H(a, 'Study')['days'].get(str(T - 1), {}).get('reason'), 'Busy', 'reason saved for yesterday')

    # ---------- Heatmap taps ----------
    a.set({'screen': 'detail', 'sel': 'read', 'from': 'today'})
    cells = a.pg.locator('button[aria-label*=": "]')
    lab = 'Upcoming'
    up = a.pg.locator('button[aria-label^="Upcoming"]')
    res.ok(up.count() >= 1 and up.first.is_disabled(), 'upcoming heatmap cells are disabled')
    d = a.js("return c.ctx('#2F5BEA', false).shortDate(c.T - 2);")
    a.pg.locator('button[aria-label^="%s:"]' % d).first.click(); a.wait(200)
    res.eq((a.state()['sheet'] or {}).get('day'), T - 2, 'tapping a heatmap day opens that day')
    a.tap('Close', nth=1)
    d10 = a.js("return c.ctx('#2F5BEA', false).shortDate(c.T - 10);")
    res.ok(a.pg.locator('button[aria-label^="%s:"]' % d10).first.is_disabled(), 'days outside the edit window are disabled')
    a.tap('Back')

    # ---------- Schedule edit keeps history ----------
    a.set({'screen': 'detail', 'sel': 'workout', 'from': 'today'})
    hist0 = a.js("return c.build(c.state.habits.find(h => h.id === 'workout')).slice(0, c.T).join('');")
    a.tap('Edit habit'); a.tap('Daily'); a.tap('Save changes', wait=200)
    w = H(a, 'Workout')
    res.eq(w['freq']['kind'], 'daily', 'schedule changed to daily')
    hist1 = a.js("return c.build(c.state.habits.find(h => h.id === 'workout')).slice(0, c.T).join('');")
    res.eq(hist1, hist0, 'past days keep the old schedule (no new misses)')
    a.tap('Back')

    # ---------- Pop-up queue through the button ----------
    a.set({'celebrate': [{'kind': 'badge', 'badge': '1', 'kicker': 'a', 'title': 'One', 'body': 'x'},
                         {'kind': 'badge', 'badge': '2', 'kicker': 'b', 'title': 'Two', 'body': 'y'},
                         {'kind': 'all', 'kicker': 'c', 'title': 'Three', 'body': 'z'}]})
    res.ok(a.has('Next (2 more)'), 'pop-up counts the queue')
    a.tap('Next (2 more)'); a.tap('Next (1 more)')
    res.ok(a.has('Three') and a.has('Keep going'), 'last pop-up says Keep going')
    a.tap('Keep going')
    res.eq(a.state()['celebrate'], [], 'queue empty')

    # ---------- Trip card shortcuts ----------
    a.js("c.setState({ trips: { day: c.T, adv: false, fish: false } });")
    a.js("c.setState(s => ({ habits: s.habits.map(h => c.withDay(h, c.T, h.type === 'quit' ? { clean: true } : { v: h.target })) }));"); a.wait(150); a.dismiss_all()
    a.tap('Today')
    a.pg.locator('button[aria-label^="Trips unlocked!"]').click(); a.wait(150)
    res.eq((a.state()['screen'], a.state()['ctab'], a.state()['etab']), ('char', 'explore', 'adventure'), 'trip card opens Explore → Adventure')
    a.js("c.setState({ trips: { day: c.T, adv: true, fish: false } });"); a.tap('Today')
    a.pg.locator('button[aria-label^="Trips unlocked!"]').click(); a.wait(150)
    res.eq(a.state()['etab'], 'fishing', 'after the adventure, the card opens Fishing')
    a.set({'habits': [], 'goals': []}); a.tap('Today')
    a.pg.locator('button[aria-label^="Add a habit to unlock trips"]').click(); a.wait(150)
    res.eq(a.state()['screen'], 'form', 'no habits: the card opens New habit')
    a.tap('Close'); res.eq(a.state()['screen'], 'today', 'closing goes back to Today')

    # ---------- Countdown shows seconds in the last hour ----------
    demo(a); a.dismiss_all()
    a.js("c.setState({ adv: { zid: 'woods', start: Date.now(), end: Date.now() + 15 * 60000, demo: false, chance: 0.7, bonus: false }, trips: { day: c.T, adv: true, fish: false } });"); a.wait(300)
    t1 = re.search(r'Back in ([^.]+)\.', a.text()).group(1)
    a.pg.clock.run_for(5000); a.wait(300)
    t2 = re.search(r'Back in ([^.]+)\.', a.text()).group(1)
    res.ok(t1 != t2 and 's' in t2, 'countdown moves every second (%s → %s)' % (t1, t2))
    a.js("c.setState({ adv: { zid: 'spire', start: Date.now(), end: Date.now() + 4 * 3600000, demo: false, chance: 0.4, bonus: false } });"); a.wait(300)
    t3 = re.search(r'Back in ([^.]+)\.', a.text()).group(1)
    res.eq(t3, '4h', 'long trips show hours and minutes')
    a.js("c.setState({ adv: null, fishing: { start: Date.now(), end: Date.now() + 3 * 3600000, demo: false, n: 1, bait: 'worm', sta: 40, bonus: false }, trips: { day: c.T, adv: false, fish: true } });"); a.wait(200)
    a.set({'screen': 'char', 'ctab': 'explore', 'etab': 'fishing'})
    res.ok(a.has('3h left') and not re.search(r'\d{4,}s left', a.text()), 'fishing painting shows 3h left')
    a.js("c.setState({ fishing: null });")

    # ---------- Recap ----------
    a.tap('Stats'); a.btn('Your 30-day recap', exact=False).click(); a.wait(150)
    res.ok(re.search(r'You showed up \d+ times\.', a.text()), 'recap headline')
    res.ok(a.has('Most consistent habit'), 'recap top habit')
    a.tap('Back'); res.eq(a.state()['screen'], 'stats', 'recap back goes to Stats')
    a.check_errors('more 1')
    a.close()

    # ---------- Clock going back (flying west, or the date set back) ----------
    b = App(browser, res, when=at(2026, 10, 15, 23, 50))
    b.clear(); b.open(); onboard(b); b.dismiss_all()
    b.tap('Mark Sleep by 11 PM done', wait=250); b.dismiss_all()
    b.pg.clock.fast_forward('00:20:00'); b.wait(500)   # 00:10 next day
    T1 = b.T()
    coins1 = b.js("return c.coinsOf(c.state);")
    b.tap('Mark Sleep by 11 PM done', wait=250); b.dismiss_all()
    coins2 = b.js("return c.coinsOf(c.state);")
    res.eq(coins2 - coins1, 10, 'new day check-in')
    b.pg.clock.set_system_time(at(2026, 10, 15, 23, 30)); b.wait(600)   # clock back to the previous evening
    res.eq(b.T(), T1, 'clock went back: the app stays on the latest day')
    res.eq(b.js("return c.coinsOf(c.state);"), coins2, 'clock went back: coins do not count twice')
    res.ok(b.has('Friday, 16 October'), 'clock went back: date label stays on the latest day (%s)' % ('Friday, 16' in b.text()))
    b.save(); b.pg.reload(); b.wait(700)
    res.eq(b.T(), T1, 'after reload with the clock still behind: same latest day')
    res.eq(b.js("return c.coinsOf(c.state);"), coins2, 'after reload: coins unchanged')
    b.pg.clock.set_system_time(at(2026, 10, 17, 9, 0)); b.wait(700)
    res.eq(b.T(), T1 + 1, 'clock forward again: next day')
    b.check_errors('clock back')
    b.close()

    # ---------- Setup can be skipped ----------
    g = App(browser, res, when=at(2026, 10, 15, 9, 0))
    g.clear(); g.open(); g.tap('Get started'); g.fill('#obname', 'Skipper'); g.tap('Create my hero')
    res.ok(g.has('Skip: I’ll add my own habits'), 'skip offered on the focus step')
    g.tap('Skip: I’ll add my own habits', wait=250)
    titles = g.dismiss_all()
    st = g.state()
    res.eq((st['screen'], st['habits'], st['onboard']), ('today', [], None), 'skipped setup: Today with no habits')
    res.ok('You and Skipper are ready!' in titles, 'skip shows the day-one pop-up')
    res.ok(g.has('Add a habit to unlock trips'), 'empty Today guides to the first habit')
    g.clear(); g.open(); g.tap('Get started'); g.tap('Create my hero')
    g.pg.locator('button[aria-pressed]').filter(has_text='Mindfulness').first.click(); g.wait(60); g.tap('Continue')
    g.tap('Skip: I’ll add my own habits', wait=250)
    res.eq(g.state()['habits'], [], 'skip on the habits step adds nothing')
    g.check_errors('skip setup')
    g.close()

    # ---------- Singular words and recap without reading/timed habits ----------
    h = App(browser, res, when=at(2026, 10, 15, 9, 0))
    h.clear(); h.open(); onboard(h, focus=('mind',), picks=['mind:1']); h.dismiss_all()   # Journal only
    h.tap('Mark Journal done', wait=250); h.dismiss_all()
    h.tap('Character'); h.pg.locator('button').filter(has_text='Explore').first.click(); h.wait(120)
    res.ok(h.has('1 of 1 habit done'), 'trip card: "1 of 1 habit done"')
    h.set({'screen': 'detail', 'sel': h.state()['habits'][0]['id'], 'from': 'today'})
    res.ok(h.has('day in a row') and not h.has('1\ndays in a row'), 'streak label: day in a row')
    res.ok(re.search(r'65 days to go', h.text()), 'graduation days to go')
    h.tap('Stats'); h.btn('Your 30-day recap', exact=False).click(); h.wait(150)
    t = h.text()
    res.ok('pages read' not in t and 'focused time' not in t, 'recap leaves out pages/time when there are no such habits')
    res.ok('perfect day' in t and 'habit tracked' in t, 'recap shows perfect days and habits tracked instead')
    res.ok('1 check-in' in t.replace('\n', ' ') or '1\ncheck-in' in t, 'recap: 1 check-in (singular)')
    res.ok('1 day' in t.replace('\n', ' ') or '1 day\nlongest streak' in t, 'recap: 1 day streak (singular)')
    h.tap('Goals'); h.tap('+ New goal for a habit'); h.fill('#gtarget', '5'); h.tap('Pick a date'); h.pg.locator('#gdate').fill('2026-10-16'); h.wait(60); h.tap('Add goal', wait=200)
    res.ok(h.has('1 day left'), 'goal: 1 day left (singular)')
    h.js("c.setArchived(c.state.habits[0].id, true);"); h.wait(100)
    h.go_settings(); h.btn('Archived habits', exact=False).click(); h.wait(150)
    res.ok(h.has('1 badge') and not h.has('1 badges'), 'archived list: 1 badge')
    h.check_errors('plurals')
    h.close()

    # ---------- Reminders are honest ----------
    k = App(browser, res, when=at(2026, 10, 15, 9, 0))
    k.clear(); k.open(); onboard(k); k.dismiss_all()
    k.tap('New habit')
    res.ok(k.has('can’t send notifications yet'), 'form says notifications are not sent yet')
    k.close()

    # ---------- Sounds ----------
    snd = App(browser, res, when=at(2026, 10, 15, 9, 0))
    snd.ctx.add_init_script("""window.__tones = []; const AC = window.AudioContext; const oc = AC.prototype.createOscillator;
      AC.prototype.createOscillator = function () { const o = oc.call(this); const f = o.frequency.setValueAtTime.bind(o.frequency);
        o.frequency.setValueAtTime = (v, t) => { window.__tones.push(v); return f(v, t); }; return o; };""")
    snd.clear(); snd.open(); onboard(snd); snd.dismiss_all()
    tones = lambda: snd.pg.evaluate("() => { const t = window.__tones.slice(); window.__tones.length = 0; return t; }")
    tones()
    snd.tap('Stats', wait=250); res.eq(tones()[:2], [520, 780], 'navigation sound')
    snd.tap('Today', wait=250); tones()
    snd.tap('Mark Sleep by 11 PM done', wait=300); t = tones()
    res.ok(784 in t, 'first check-in plays the badge sound (%s)' % t)
    snd.dismiss_all()
    snd.tap('Log Drink water', wait=250); tones()
    snd.fill('#samount', '8'); snd.tap('Save amount', wait=300); t = tones()
    res.ok(t and t[0] in (660, 784, 523), 'check-in sound (%s)' % t)
    snd.dismiss_all(); snd.go_settings(); snd.tap('Sounds', wait=200); tones()
    snd.tap('Today', wait=250); res.eq(tones(), [], 'no sounds when switched off')
    snd.check_errors('sounds')
    snd.close()

    # ---------- Comeback with a quit habit ----------
    e = App(browser, res, when=at(2026, 10, 15, 9, 0))
    e.clear(); e.open(); onboard(e, focus=('quit',), picks=['quit:0']); e.dismiss_all()
    e.tap('New habit'); e.fill('#hemoji', '📖'); e.fill('#hname', 'Read'); e.tap('Create habit', wait=200)
    e.tap('Mark Read done', wait=250); e.dismiss_all()
    e.save(); e.blank(); e.pg.clock.fast_forward(4 * 24 * 3600 * 1000); e.open(700); e.dismiss_all()
    res.ok(e.has('Welcome back'), 'comeback card shows even with a quit habit')
    e.check_errors('comeback quit')
    e.close()


if __name__ == '__main__':
    sys.exit(1 if run('more', main) else 0)
