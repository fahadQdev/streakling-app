"""Visit every screen, sheet and pop-up, scan it and take a screenshot.
Usage: python3 tour.py [configs...]   e.g. 390-light 390-dark 320-light 1280-light
"""
import sys
from harness import *

CONFIGS = {
    '320-light': (320, 568, 'light'), '320-dark': (320, 568, 'dark'),
    '360-light': (360, 740, 'light'),
    '375-light': (375, 667, 'light'),
    '390-light': (390, 844, 'light'), '390-dark': (390, 844, 'dark'),
    '430-light': (430, 932, 'light'), '430-dark': (430, 932, 'dark'),
    '667x375-light': (667, 375, 'light'),
    '1280-light': (1280, 800, 'light'), '1280-dark': (1280, 800, 'dark'),
}
WHEN = at(2026, 10, 15, 21, 0)  # a Thursday evening


def reset_to(a, snap):
    cur = a.state()
    patch = dict(snap)
    for k in cur:
        if k not in snap:
            patch[k] = None
    a.js("c.setState(arg);", patch)
    a.wait(120)


def states():
    S = []
    def st(name):
        def deco(fn):
            S.append((name, fn))
            return fn
        return deco

    # ---------- Today ----------
    @st('today')
    def _(a): pass

    @st('today-reorder')
    def _(a): a.tap('Reorder')

    @st('today-past')
    def _(a): a.set({'day': a.T() - 2})

    @st('today-past-locked')
    def _(a): a.set({'day': a.T() - 20})

    @st('today-oldest-week')
    def _(a): a.set({'day': (a.T() // 7 - 4) * 7})

    @st('today-comeback-card')
    def _(a):
        a.js("c.setState({ screen: 'settings' });"); a.wait(80)
        a.js("const v = c.renderVals(); v.simulateBreak();"); a.wait(200)

    @st('today-comeback-week')
    def _(a):
        a.js("const v = c.renderVals(); v.simulateBreak();"); a.wait(150)
        a.js("c.renderVals().startComeback();"); a.wait(150); a.dismiss_all()

    @st('today-savefail')
    def _(a): a.set({'saveFail': True})

    @st('today-ask')
    def _(a):
        T = a.T()
        a.js("const T = c.T; c.setState(s => ({ habits: s.habits.map(h => h.id === 'read' ? Object.assign({}, h, { days: Object.assign({}, h.days, { [T - 1]: { v: 0 } }) }) : h) }));")
        a.wait(150)

    @st('today-coach')
    def _(a):
        a.js("const T = c.T; c.setState(s => ({ coachSkip: {}, habits: s.habits.map(h => { if (h.id !== 'read') return h; const d = Object.assign({}, h.days); for (let j = T - 20; j <= T; j++) d[j] = { v: 40 }; return Object.assign({}, h, { days: d }); }) }));")
        a.wait(150)

    @st('today-empty')
    def _(a): a.set({'habits': [], 'goals': []})

    @st('today-flash')
    def _(a):
        a.btn('Add 5 pages to Read', exact=False).click(); a.wait(120)

    @st('today-hide-done')
    def _(a): a.set({'settings': dict(a.state()['settings'], hideDone=True)})

    @st('today-all-done-hidden')
    def _(a):
        a.js("c.setState(s => ({ settings: Object.assign({}, s.settings, { hideDone: true }), habits: s.habits.map(h => c.withDay(h, c.T, h.type === 'quit' ? { clean: true } : { v: h.target })) }));")
        a.wait(150); a.dismiss_all()

    @st('today-offday')
    def _(a): a.set({'day': a.T() - 6})   # last Friday: Study (Sun–Thu) is not on the list

    @st('today-nothing-scheduled')
    def _(a):
        a.js("c.setState(s => ({ habits: s.habits.filter(h => h.id === 'study'), day: c.T - 6 }));")

    # ---------- Tasks ----------
    @st('today-tasks')
    def _(a): a.pg.get_by_role('tab', name=re.compile('^Tasks')).click()

    @st('today-tasks-empty')
    def _(a):
        a.set({'tasks': []}); a.pg.get_by_role('tab', name=re.compile('^Tasks')).click()

    @st('today-tasks-flash')
    def _(a):
        a.pg.get_by_role('tab', name=re.compile('^Tasks')).click(); a.wait(100)
        a.tap('Mark task Call the dentist done', wait=120)

    @st('task-sheet-new')
    def _(a):
        a.pg.get_by_role('tab', name=re.compile('^Tasks')).click(); a.wait(100); a.tap('New task')

    @st('task-sheet-date')
    def _(a):
        a.pg.get_by_role('tab', name=re.compile('^Tasks')).click(); a.wait(100); a.tap('New task')
        a.fill('#tname', 'Renew the car registration'); a.pg.get_by_role('dialog').get_by_role('button', name='Pick a date').click()

    @st('task-sheet-error')
    def _(a):
        a.pg.get_by_role('tab', name=re.compile('^Tasks')).click(); a.wait(100); a.tap('New task'); a.tap('Add task')

    @st('task-sheet-edit-armed')
    def _(a):
        a.pg.get_by_role('tab', name=re.compile('^Tasks')).click(); a.wait(100)
        a.tap('Edit task Buy groceries'); a.tap('Delete task')

    # ---------- Sheets ----------
    @st('sheet-amount')
    def _(a): a.tap('Log Read')

    @st('sheet-amount-dirty')
    def _(a):
        a.tap('Log Read'); a.tap('Increase'); a.tap('Increase')

    @st('sheet-time-idle')
    def _(a): a.tap('Log Study')

    @st('sheet-time-running')
    def _(a):
        a.tap('Log Study'); a.tap('Start timer', wait=1300)

    @st('sheet-time-other-running')
    def _(a):
        a.js("c.setState({ timer: { hid: 'study', day: c.T, running: true, session: 0, since: Date.now(), base: 900 } });"); a.wait(100)
        a.set({'habits': a.state()['habits']})
        a.js("c.openSheet('read', c.T);"); a.wait(80)
        # a time habit sheet other than the running one
        a.js("const h = Object.assign({}, c.state.habits.find(x => x.id === 'study'), { id: 'study2', name: 'Practice guitar' }); c.setState(s => ({ habits: s.habits.concat([h]) }));"); a.wait(100)
        a.js("c.openSheet('study2', c.T);"); a.wait(150)

    @st('sheet-time-error')
    def _(a):
        a.tap('Log Study')
        a.pg.get_by_label('Hours', exact=True).fill('30'); a.wait(80)
        a.tap('Save time')

    @st('sheet-check')
    def _(a): a.js("c.openSheet('workout', c.T);")

    @st('sheet-check-past-missed')
    def _(a):
        a.js("const T = c.T; c.setState(s => ({ habits: s.habits.map(h => h.id === 'workout' ? Object.assign({}, h, { freq: { kind: 'daily', n: 7, days: [] }, days: Object.assign({}, h.days, { [T - 1]: { v: 0 } }) }) : h) }));"); a.wait(100)
        a.js("c.openSheet('workout', c.T - 1);")

    @st('sheet-quit-today')
    def _(a): a.js("c.openSheet('sugar', c.T);")

    @st('sheet-quit-past-slip')
    def _(a):
        a.js("const T = c.T; c.updateDay('sugar', T - 1, () => ({ slip: true, clean: false }));"); a.wait(100)
        a.js("c.openSheet('sugar', c.T - 1);")

    @st('sheet-skipped')
    def _(a):
        a.tap('Log Read'); a.tap('Skip this day (keeps streak)')

    @st('sheet-past-amount')
    def _(a): a.js("c.openSheet('read', c.T - 3);")

    # ---------- Detail ----------
    for hid in ['quran', 'study', 'workout', 'read', 'sugar']:
        def mk(hid):
            def f(a): a.set({'screen': 'detail', 'sel': hid, 'from': 'today'})
            return f
        S.append(('detail-' + hid, mk(hid)))

    @st('detail-archived')
    def _(a):
        a.js("c.setArchived('read', true);"); a.wait(80)
        a.set({'screen': 'detail', 'sel': 'read', 'from': 'archived'})

    @st('detail-delete-armed')
    def _(a):
        a.set({'screen': 'detail', 'sel': 'read', 'from': 'today'})
        a.tap('Delete habit')

    @st('detail-new-habit')
    def _(a):
        a.js("const h = Object.assign(c.habitFromTemplate(c.templates().health[0], 'hnew', 2)); c.setState(s => ({ habits: s.habits.concat([h]), screen: 'detail', sel: 'hnew', from: 'today' }));")

    # ---------- Stats / recap ----------
    @st('stats')
    def _(a): a.tap('Stats')

    @st('stats-empty')
    def _(a):
        a.set({'habits': [], 'goals': []}); a.tap('Stats')

    @st('recap')
    def _(a):
        a.tap('Stats'); a.tap('Your 30-day recap Check-ins, best streak, top habit, totals', exact=False)

    @st('stats-recap-locked')
    def _(a):
        a.set({'firstDay': a.T() - 2}); a.tap('Stats')

    @st('recap-empty')
    def _(a):
        a.set({'habits': [], 'goals': []}); a.set({'screen': 'recap'})

    # ---------- Goals ----------
    @st('goals')
    def _(a): a.tap('Goals')

    @st('goals-delete-armed')
    def _(a):
        a.tap('Goals'); a.btn('Delete goal', exact=False).first.click(); a.wait(150)

    @st('goals-form')
    def _(a):
        a.tap('Goals'); a.tap('+ New goal for a habit')

    @st('goals-form-date-error')
    def _(a):
        a.tap('Goals'); a.tap('+ New goal for a habit'); a.tap('Pick a date'); a.fill('#gtarget', '50'); a.tap('Add goal')

    @st('goals-empty')
    def _(a):
        a.set({'goals': []}); a.tap('Goals')

    # ---------- Habit form ----------
    @st('form-new')
    def _(a): a.tap('New habit')

    @st('form-new-amount')
    def _(a):
        a.tap('New habit'); a.tap('Amount Pages, glasses, reps.')

    @st('form-new-time-days')
    def _(a):
        a.tap('New habit'); a.tap('Time Type it or use a timer.'); a.tap('Specific days')

    @st('form-new-quit')
    def _(a):
        a.tap('New habit'); a.tap('Quit Days without it.')

    @st('form-new-perweek-goal')
    def _(a):
        a.tap('New habit'); a.tap('Times per week'); a.tap('Link a goal'); a.tap('Pick a date')

    @st('form-new-error')
    def _(a):
        a.tap('New habit'); a.tap('Create habit')

    @st('form-new-emoji-error')
    def _(a):
        a.tap('New habit'); a.fill('#hemoji', 'abc')

    @st('form-new-remoff')
    def _(a):
        a.tap('New habit'); a.tap('Reminder on or off')

    @st('form-edit')
    def _(a):
        a.set({'screen': 'detail', 'sel': 'study', 'from': 'today'}); a.tap('Edit habit')

    @st('form-edit-delete-armed')
    def _(a):
        a.set({'screen': 'detail', 'sel': 'quran', 'from': 'today'}); a.tap('Edit habit'); a.tap('Delete habit')

    # ---------- Settings ----------
    @st('settings')
    def _(a): a.tap('Settings')

    @st('settings-demo')
    def _(a):
        a.tap('Settings'); a.tap('Demo tools')

    @st('settings-confirms')
    def _(a):
        a.tap('Settings'); a.tap('Demo tools'); a.tap('Load sample data'); a.set({'confirmFresh': True})

    @st('settings-import')
    def _(a):
        a.tap('Settings'); a.set({'importInfo': {'text': 'Backup from 12 Oct 2026 · 5 habits · Kai'}, 'backupMsg': 'Backup saved. Keep the file somewhere safe (Files, Drive, email).'})

    @st('archived-empty')
    def _(a):
        a.tap('Settings'); a.tap('Archived habits 0', exact=False)

    @st('archived-list')
    def _(a):
        a.js("c.setArchived('read', true); c.setArchived('sugar', true);"); a.wait(80)
        a.tap('Settings'); a.tap('Archived habits 2', exact=False)

    # ---------- Character ----------
    @st('char-hero')
    def _(a): a.tap('Character')

    @st('char-hero-busy')
    def _(a):
        a.js("c.setState({ trips: { day: c.T, adv: false, fish: false } });")
        a.js("c.setState({ adv: { zid: 'woods', start: Date.now(), end: Date.now() + 15 * 60000, demo: false, chance: 0.7, bonus: false }, trips: { day: c.T, adv: true, fish: false } });")
        a.tap('Character')

    for cat in ['clothes', 'hat', 'hair', 'shoes', 'weapon', 'acc', 'rod', 'bg']:
        def mkw(cat):
            def f(a): a.set({'screen': 'char', 'ctab': 'wardrobe', 'cat': cat})
            return f
        def mks(cat):
            def f(a): a.set({'screen': 'char', 'ctab': 'store', 'cat': cat})
            return f
        S.append(('char-wardrobe-' + cat, mkw(cat)))
        S.append(('char-store-' + cat, mks(cat)))

    @st('char-store-tryon')
    def _(a):
        a.set({'screen': 'char', 'ctab': 'store', 'cat': 'clothes'}); a.btn('Try on', exact=False, nth=1).dispatch_event('click'); a.wait(150)

    @st('char-store-tryon-rod')
    def _(a):
        a.set({'screen': 'char', 'ctab': 'store', 'cat': 'rod'}); a.btn('Try on', exact=False).first.dispatch_event('click'); a.wait(150)

    @st('char-store-tryon-bg')
    def _(a):
        a.set({'screen': 'char', 'ctab': 'store', 'cat': 'bg'}); a.btn('Try on Beach Day').dispatch_event('click'); a.wait(150)

    for bid in ['bg_meadow', 'bg_room', 'bg_beach', 'bg_forest', 'bg_mushroom', 'bg_blossom', 'bg_frost', 'bg_cavern', 'bg_sky', 'bg_dragon']:
        def mkb(bid):
            def f(a):
                a.js("c.setState(s => ({ owned: s.owned.indexOf(arg) < 0 ? s.owned.concat([arg]) : s.owned, char: Object.assign({}, s.char, { bg: arg }), screen: 'char', ctab: 'hero' }));", bid)
            return f
        S.append(('char-hero-' + bid, mkb(bid)))

    @st('char-look-bg')
    def _(a):
        a.js("c.setState(s => ({ owned: s.owned.concat(['bg_dragon']), char: Object.assign({}, s.char, { bg: 'bg_dragon' }) }));"); a.tap('Character'); a.tap('Change look')

    @st('char-wardrobe-busy')
    def _(a):
        a.js("c.setState({ adv: { zid: 'woods', start: Date.now(), end: Date.now() + 15 * 60000, demo: false, chance: 0.7, bonus: false }, trips: { day: c.T, adv: true, fish: false } });")
        a.set({'screen': 'char', 'ctab': 'wardrobe', 'cat': 'clothes'})

    @st('char-wardrobe-empty')
    def _(a): a.set({'screen': 'char', 'ctab': 'wardrobe', 'cat': 'acc'})

    @st('char-store-empty')
    def _(a):
        a.js("const D = c.px(); c.setState(s => ({ owned: D.order.slice(), screen: 'char', ctab: 'store', cat: 'hat' }));")

    @st('char-look')
    def _(a):
        a.tap('Character'); a.tap('Change look')

    @st('char-look-namefix')
    def _(a):
        a.js("c.setState(s => ({ char: Object.assign({}, s.char, { name: 'shithead' }) }));"); a.tap('Character'); a.tap('Change look')

    @st('char-create')
    def _(a):
        a.set({'char': None, 'screen': 'char', 'cc': {'sex': 'girl', 'skin': 'deep', 'hc': 'red', 'name': ''}})

    @st('explore-adv-locked')
    def _(a):
        a.js("const T = c.T; c.setState(s => ({ trips: { day: T, adv: false, fish: false }, habits: s.habits.map(h => { const d = Object.assign({}, h.days); d[T] = h.type === 'quit' ? {} : { v: 0 }; return Object.assign({}, h, { days: d }); }) }));")
        a.set({'screen': 'char', 'ctab': 'explore', 'etab': 'adventure'})

    @st('explore-adv-ready')
    def _(a):
        a.js("c.setState({ trips: { day: c.T, adv: false, fish: false } });")
        a.set({'screen': 'char', 'ctab': 'explore', 'etab': 'adventure'})

    @st('explore-adv-away')
    def _(a):
        a.js("c.setState({ adv: { zid: 'spire', start: Date.now() - 3600000, end: Date.now() + 3 * 3600000, demo: false, chance: 0.42, bonus: true }, trips: { day: c.T, adv: true, fish: false }, advLog: [{ zid: 'woods', win: true, coins: 12, xp: 20, drop: 'h_cap' }, { zid: 'coast', win: false, coins: 6, xp: 20, drop: null }] });")
        a.set({'screen': 'char', 'ctab': 'explore', 'etab': 'adventure', 'demoXp': 5000})

    @st('explore-fish-idle')
    def _(a):
        a.js("c.setState({ trips: { day: c.T, adv: false, fish: false } });")
        a.set({'screen': 'char', 'ctab': 'explore', 'etab': 'fishing', 'bait': 'golden'})

    @st('explore-fish-on')
    def _(a):
        a.js("c.setState({ fishing: { start: Date.now() - 3600000, end: Date.now() + 2 * 3600000, demo: false, n: 3, bait: 'shiny', sta: 60, bonus: false }, trips: { day: c.T, adv: false, fish: true } });")
        a.set({'screen': 'char', 'ctab': 'explore', 'etab': 'fishing'})

    @st('explore-fish-bite')
    def _(a):
        a.js("c.setState({ fishing: { start: Date.now() - 3600000, end: Date.now() + 2500, demo: true, n: 2, bait: 'worm', sta: 60, bonus: false }, trips: { day: c.T, adv: false, fish: true } });")
        a.set({'screen': 'char', 'ctab': 'explore', 'etab': 'fishing'})

    @st('explore-fish-away')
    def _(a):
        a.js("c.setState({ adv: { zid: 'woods', start: Date.now(), end: Date.now() + 15 * 60000, demo: false, chance: 0.7, bonus: false }, trips: { day: c.T, adv: true, fish: false } });")
        a.set({'screen': 'char', 'ctab': 'explore', 'etab': 'fishing'})

    @st('explore-book')
    def _(a): a.set({'screen': 'char', 'ctab': 'explore', 'etab': 'book', 'soldNote': 'Sold 3 extra fish for 6 coins. One of each stays in your book.'})

    @st('explore-book-full')
    def _(a):
        a.js("const D = c.px(); const b = {}; D.fishOrder.forEach(id => { b[id] = { caught: 3, kept: 3, best: D.fish[id].size[1] }; }); c.setState({ book: b });")
        a.set({'screen': 'char', 'ctab': 'explore', 'etab': 'book'})

    @st('fish-detail-caught')
    def _(a): a.set({'screen': 'char', 'ctab': 'explore', 'etab': 'book', 'fishSel': 'salmon'})

    @st('fish-detail-unknown')
    def _(a): a.set({'screen': 'char', 'ctab': 'explore', 'etab': 'book', 'fishSel': 'kraken' if False else 'koi'})

    # ---------- Leaderboard ----------
    for tier in range(4):
        def mkl(tier):
            def f(a):
                a.js("c.setState(s => ({ league: Object.assign({}, s.league, { tier: arg, trophies: arg }) }));", tier)
                a.tap('Leaderboard')
            return f
        S.append(('ranks-league-tier%d' % tier, mkl(tier)))

    @st('ranks-hidden')
    def _(a):
        a.js("c.setState(s => ({ league: Object.assign({}, s.league, { hidden: true }) }));"); a.tap('Leaderboard')

    @st('ranks-friends')
    def _(a):
        a.tap('Leaderboard'); a.pg.get_by_role('tab', name='Friends').click(); a.wait(150); a.set({'inviteMsg': 'Invite copied. Paste it in any chat.'})

    @st('ranks-hall')
    def _(a):
        a.tap('Leaderboard'); a.pg.get_by_role('tab', name='Hall of Fame').click(); a.wait(150)

    @st('pcard-other')
    def _(a):
        a.tap('Leaderboard'); a.pg.locator('button[aria-label^="1st"]').first.click(); a.wait(150)

    @st('pcard-cheered')
    def _(a):
        a.tap('Leaderboard'); a.pg.locator('button[aria-label^="2nd"]').first.click(); a.wait(150); a.btn('Cheer', exact=False).click(); a.wait(150)

    @st('pcard-hall')
    def _(a):
        a.tap('Leaderboard'); a.pg.get_by_role('tab', name='Hall of Fame').click(); a.wait(150); a.pg.locator('button[aria-label^="Highest level"]').first.click(); a.wait(150)

    # ---------- Celebrations ----------
    def cele(name, item):
        def f(a): a.set({'celebrate': [item]})
        S.append(('cele-' + name, f))
    cele('badge', {'kind': 'badge', 'badge': '1st', 'kicker': '📖 Read', 'title': 'First check-in!', 'body': 'Day one is done. That is the hardest one. Badge unlocked. Keep it going for 7 days to earn your first streak badge and +50 coins.'})
    cele('badge-long', {'kind': 'badge', 'badge': '365', 'kicker': '🧘 Meditate every morning before work', 'title': '365-day streak: 1 year!', 'body': '365 days in a row without breaking the chain. Badge unlocked. +50 coins.'})
    cele('gift', {'kind': 'badge', 'badge': '+150', 'kicker': 'Welcome gift', 'title': '+150 coins!', 'body': 'A one-time gift for your first check-in: enough for your first item. Spend it in Character → Store.'})
    cele('all', {'kind': 'all', 'kicker': 'Thursday, 15 October', 'title': 'All habits done today!', 'body': 'Every habit on today’s list hit its full target. Bonus for Kai’s trips: +25% adventure coins and +1 fish.'})
    cele('adv-win', {'kind': 'adv', 'quiet': False, 'icon': 'spire', 'kicker': "Dragon's Spire", 'title': 'Victory!', 'body': 'Your hero faced the dragon and came home with treasure. +70 coins (+25% for finishing every habit), +90 XP. Found: Dragon Scale Armour!'})
    cele('adv-lose', {'kind': 'adv', 'quiet': True, 'icon': 'caverns', 'kicker': 'Ember Caverns', 'title': 'Your hero retreated', 'body': 'The heat was too much. Your hero retreated to cooler tunnels. +10 coins, +35 XP. Gear with the Health or Power this place tests raises the odds.'})
    cele('head', {'kind': 'head', 'kicker': 'Half of today done', 'title': 'Trips unlocked!', 'body': 'Kai can go on 1 adventure and 1 fishing trip today. Open the Character tab and pick one.'})
    cele('level', {'kind': 'badge', 'badge': 'Lv15', 'kicker': 'Level up', 'title': 'Level 15!', 'body': 'Health +8, Power +2, Stamina +3. A third accessory slot unlocked.'})

    @st('cele-fish-many')
    def _(a):
        a.js("const D = c.px(); const fish = D.fishOrder.slice(0, 9).map((id, i) => ({ id, size: D.fish[id].size[1], isNew: i % 3 === 0, isRecord: i % 3 === 1 })); c.setState({ celebrate: [{ kind: 'fish', quiet: false, kicker: 'Fishing trip', title: 'You caught 9 fish!', body: '3 new species for your Fish Book. 3 new size records. +45 XP.', fish }, { kind: 'badge', badge: '10', kicker: 'Fish Book', title: 'All 10 common fish found!', body: 'Reward unlocked: Fisher Bucket Hat. It is in your Wardrobe now.' }] });")
        a.wait(100)

    # ---------- Onboarding ----------
    @st('ob-welcome')
    def _(a): a.set({'screen': 'onboard', 'onboard': {'step': 0, 'focus': [], 'picks': []}, 'char': None})

    @st('ob-hero')
    def _(a): a.set({'screen': 'onboard', 'onboard': {'step': 1, 'focus': [], 'picks': []}, 'char': None, 'cc': {'sex': 'boy', 'skin': 'light', 'hc': 'black', 'name': ''}})

    @st('ob-hero-error')
    def _(a):
        a.set({'screen': 'onboard', 'onboard': {'step': 1, 'focus': [], 'picks': []}, 'char': None, 'cc': {'sex': 'girl', 'skin': 'tan', 'hc': 'blonde', 'name': 'bitch'}})
        a.tap('Create my hero')

    @st('ob-focus-none')
    def _(a): a.set({'screen': 'onboard', 'onboard': {'step': 2, 'focus': [], 'picks': []}})

    @st('ob-focus-two')
    def _(a): a.set({'screen': 'onboard', 'onboard': {'step': 2, 'focus': ['learn', 'quit'], 'picks': []}})

    @st('ob-picks-warn')
    def _(a): a.set({'screen': 'onboard', 'onboard': {'step': 3, 'focus': ['health', 'fitness'], 'picks': ['health:0', 'health:1', 'health:2', 'fitness:0', 'fitness:1', 'fitness:2']}})

    @st('ob-picks-none')
    def _(a): a.set({'screen': 'onboard', 'onboard': {'step': 3, 'focus': ['mind'], 'picks': []}})

    return S


def main(browser, res, configs):
    S = states()
    only = os.environ.get('ONLY')
    for cfg in configs:
        w, h, theme = CONFIGS[cfg]
        a = App(browser, res, width=w, height=h, when=WHEN, label=cfg + ':')
        a.clear(); a.open()
        demo(a)
        a.set({'settings': dict(a.state()['settings'], theme=theme)})
        a.dismiss_all()
        snap = a.state()
        shoot = cfg in ('390-light', '390-dark', '320-light', '320-dark', '1280-light', '1280-dark', '667x375-light')
        n = 0
        for name, fn in S:
            if only and only not in name:
                continue
            reset_to(a, snap)
            try:
                fn(a)
                a.wait(250)
            except Exception as e:
                res.failed.append('%s %s: setup failed: %s' % (cfg, name, str(e).splitlines()[0][:200]))
                print('  setup failed', cfg, name, str(e).splitlines()[0][:200], flush=True)
                a.js("c.setState({ sheet: null, pcard: null, fishSel: null, celebrate: [] });")
                continue
            a.scan(name)
            if shoot:
                a.shot('%s__%s' % (cfg, name))
            errs = a.check_errors(cfg + ' ' + name)
            n += 1
        print('%s: %d states' % (cfg, n), flush=True)
        a.close()


if __name__ == '__main__':
    cfgs = sys.argv[1:] or ['390-light']
    sys.exit(1 if run('tour ' + ' '.join(cfgs), lambda b, r: main(b, r, cfgs)) else 0)
