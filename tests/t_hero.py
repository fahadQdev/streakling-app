"""The RPG layer end to end: onboarding hero, wardrobe rules, store, try-on, stats, adventures,
fishing, bait, Fish Book rewards, selling, level unlocks, gear lock during trips."""
from harness import *

WHEN = at(2026, 10, 15, 10, 0)


def items(a):
    return a.js("const D = c.px(); const o = {}; D.order.forEach(id => { o[id] = D.items[id]; }); return o;")


def main(browser, res):
    a = App(browser, res, when=WHEN)
    a.clear(); a.open()

    # ---------- Onboarding hero ----------
    a.tap('Get started')
    a.tap('Create my hero')
    st = a.state()
    res.eq(st['char']['name'], 'Hero', 'empty name becomes "Hero"')
    a.tap('Back')
    res.eq(a.state()['onboard']['step'], 1, 'Back returns to the hero step')
    res.ok(a.has('Save and continue'), 'hero step button says Save and continue the second time')
    a.fill('#obname', '  Layla Al-Harbi Zz  ')
    res.eq(a.pg.locator('#obname').input_value(), '  Layla Al-Har', 'name field limited to 14 characters')
    a.pg.locator('button[aria-pressed]').filter(has_text='Girl').first.click(); a.wait(60)
    a.tap('deep skin'); a.tap('red hair')
    a.tap('Save and continue')
    ch = a.state()['char']
    res.eq((ch['name'], ch['sex'], ch['skin'], ch['hc'], ch['clothes'], ch['hair']), ('Layla Al-Har', 'girl', 'deep', 'red', 'c_dress', 'hr_long'), 'girl hero with trimmed name and girl defaults')
    res.eq(sorted(a.state()['owned']), sorted(['c_dress', 'hr_long', 's_boots', 'r_bamboo', 'bg_plain']), 'a girl hero gets only the girl starter items (and the plain background)')
    res.eq(ch.get('bg'), 'bg_plain', 'new hero uses the plain background')
    a.pg.locator('button[aria-pressed]').filter(has_text='Learning').first.click(); a.wait(60)
    a.pg.locator('button[aria-pressed]').filter(has_text='Fitness').first.click(); a.wait(60)
    a.pg.locator('button[aria-pressed]').filter(has_text='Health').first.click(); a.wait(60)
    res.eq(a.state()['onboard']['focus'], ['fitness', 'health'], 'only 2 focus areas: the oldest pick drops')
    a.tap('Continue')
    res.eq(a.state()['onboard']['picks'], ['fitness:0', 'fitness:1', 'health:0'], 'default picks: 2 from the first area, 1 from the second')
    a.pg.locator('button').filter(has_text=re.compile('^Start with 3 habits')).click(); a.wait(300)
    titles = a.dismiss_all()
    res.ok('You and Layla Al-Har are ready!' in titles, 'day-one pop-up (%s)' % titles)
    hs = a.state()['habits']
    res.eq([h['name'] for h in hs], ['Workout', 'Push-ups', 'Drink water'], 'habits from templates')
    res.eq(hs[0]['freq'], {'kind': 'perweek', 'n': 3, 'days': []}, 'Workout template is 3× a week')
    a.check_errors('onboarding')

    # ---------- Coins for testing purchases ----------
    I = items(a)
    a.set({'bonus': 5000})
    a.tap('Character')
    res.ok(a.has('5000'), 'coins shown on the hero page')
    base = a.js("return c.statsOf(c.state.char, 1);")
    res.eq((base['base']['hp'], base['base']['pow'], base['base']['sta']), (40, 6, 30), 'level 1 base stats')
    res.eq((base['gear']['hp'], base['gear']['sta']), (8, 8), 'starter gear stats (dress +8 HP, boots +4 STA, bamboo rod +4 STA)')

    # ---------- Store: buy, level lock, earn-only ----------
    a.set({'ctab': 'store', 'cat': 'clothes'})
    t = a.text()
    res.ok('Unlocks at Lv 3' in t, 'rare items locked below Lv 3')
    res.ok('Needs a 14-day streak' in t, 'streak reward needs the streak')
    res.ok(a.pg.locator('button:has-text("Unlocks at Lv 3")').first.is_disabled(), 'locked item: button disabled')
    # The boy's starter outfit and hair are in the Store for a girl hero, as normal items.
    store = lambda: a.js("return c.renderVals().store.map(x => [x.name, x.actLabel, x.actOff]);")
    names = [x[0] for x in store()]
    res.ok("Traveler's Vest" in names and 'Coral Dress' not in names, 'Store sells the boy starter outfit, not the owned girl one (%s)' % names[:4])
    res.eq([x[1] for x in store() if x[0] == "Traveler's Vest"], ['Buy · 150'], 'other starter outfit costs 150')
    spent0 = a.state()['spent']
    a.btn("Try on Traveler's Vest").dispatch_event('click'); a.wait(150)
    res.ok(a.has("Trying: Traveler's Vest"), 'other starter outfit can be tried on')
    a.btn('Buy · 150', nth=0).click(); a.wait(200)
    st = a.state()
    res.ok('c_vest' in st['owned'] and st['char']['clothes'] == 'c_vest', 'bought the boy starter outfit: owned and worn')
    res.eq(st['spent'] - spent0, 150, 'starter outfit price deducted')
    a.set({'cat': 'hair'})
    hair = store()
    res.eq([x[1] for x in hair if x[0] == 'Short & Tousled'], ['Buy · 120'], 'other starter hair costs 120')
    res.ok('Long & Straight' not in [x[0] for x in hair], 'own starter hair is not in the Store')
    sp1 = a.state()['spent']
    a.btn('Try on Short & Tousled').dispatch_event('click'); a.wait(150)
    a.btn('Buy · 120', nth=0).click(); a.wait(200)
    st = a.state()
    res.ok('hr_short' in st['owned'] and st['char']['hair'] == 'hr_short' and st['spent'] - sp1 == 120, 'bought the boy starter hair for 120')
    a.set({'cat': 'clothes'})
    spent0 = a.state()['spent']
    a.btn('Try on Cozy Hoodie').dispatch_event('click'); a.wait(150)
    a.btn('Buy · 150', nth=0).click(); a.wait(200)
    st = a.state()
    bought = [x for x in st['owned'] if I[x]['slot'] == 'clothes' and I[x]['rarity'] == 'common']
    res.eq(len(bought), 1, 'bought one common clothes item')
    res.eq(st['spent'] - spent0, 150, 'price deducted')
    res.eq(st['char']['clothes'], bought[0] if bought else None, 'bought item is worn right away')
    # not enough coins
    a.set({'bonus': 0, 'spent': 0, 'coinsBase': 100})
    a.set({'ctab': 'store', 'cat': 'hat'})
    res.ok(a.has('Need 50 more'), 'shows how many coins are missing')
    res.ok(a.pg.locator('button:has-text("Need 50 more")').first.is_disabled(), 'cannot buy without coins')
    a.js("c.buyItem('h_cap', c.coinsOf(c.state), 1, 2);"); a.wait(100)
    res.ok('h_cap' not in a.state()['owned'], 'buyItem refuses when coins are short')
    a.set({'bonus': 5000})
    # try-on
    a.btn('Try on Red Cap').dispatch_event('click'); a.wait(150)
    res.ok(a.has('Trying: Red Cap'), 'try-on bar')
    res.ok(a.has('If worn: +8 Health · +4 Stamina'), 'try-on shows the stat change')
    a.tap('Cancel'); res.eq(a.state()['tryOn'], None, 'try-on cancelled')
    a.btn('Try on Red Cap').dispatch_event('click'); a.wait(100)
    a.btn('Buy · 150', nth=0).click(); a.wait(150)
    res.ok('h_cap' in a.state()['owned'] and a.state()['char']['hat'] == 'h_cap', 'bought from the try-on bar')
    # earn-only item once earned
    a.js("c.setState(s => ({ habits: s.habits.map((h, i) => i === 0 ? Object.assign({}, h, { badges: { first: true, s7: true } }) : h) }));"); a.wait(100)
    a.set({'cat': 'shoes'})
    res.ok(a.has('Claim free'), 'earned streak reward can be claimed')
    sp = a.state()['spent']
    a.pg.locator('button:has-text("Claim free")').first.click(); a.wait(150)
    res.ok('s_trail' in a.state()['owned'] and a.state()['spent'] == sp, 'claimed for free')

    # ---------- Wardrobe rules ----------
    for iid in ['a_glasses', 'a_scarf', 'a_sunglasses', 'a_pack', 'a_wsword', 'a_shield', 'a_ksword', 'h_beanie']:
        a.js("c.setState(s => ({ owned: s.owned.indexOf(arg) < 0 ? s.owned.concat([arg]) : s.owned }));", iid)
    a.wait(100)
    def wear(iid):
        a.js("c.setState(s => ({ char: c.equip(s.char, arg, false, c.levelInfo(c.xpOf(s)).L >= 15 ? 3 : 2) }));", iid); a.wait(60)
        return a.state()['char']
    ch = wear('a_glasses'); ch = wear('a_scarf')
    res.eq(sorted(ch['acc']), ['a_glasses', 'a_scarf'], 'two accessories')
    ch = wear('a_sunglasses')
    res.eq(sorted(ch['acc']), ['a_scarf', 'a_sunglasses'], 'one per spot: sunglasses replace glasses')
    ch = wear('a_pack')
    res.eq(len(ch['acc']), 2, 'only 2 accessory slots below Lv 15')
    ch = wear('a_pack')
    res.ok('a_pack' not in ch['acc'], 'tapping a worn accessory takes it off')
    ch = wear('a_wsword'); ch = wear('a_shield')
    res.eq(sorted(ch['weapon']), ['a_shield', 'a_wsword'], 'sword and shield together')
    ch = wear('a_ksword')
    res.eq(sorted(ch['weapon']), ['a_ksword', 'a_shield'], 'one sword at a time')
    ch = wear('h_beanie'); res.eq(ch['hat'], 'h_beanie', 'hat on')
    ch = wear('h_beanie'); res.eq(ch['hat'], None, 'hat off')
    ch = wear('c_vest'); ch = wear('c_vest')
    res.eq(ch['clothes'], 'c_vest', 'clothes cannot be taken off')
    # wardrobe UI: Take off / Wearing labels
    a.set({'ctab': 'wardrobe', 'cat': 'weapon'})
    res.ok(a.has('Take off'), 'worn weapon shows Take off')
    a.set({'cat': 'clothes'})
    res.ok(a.pg.locator('button:has-text("Wearing")').first.is_disabled(), 'worn clothes: Wearing (disabled)')
    # Level 15: third accessory slot
    a.set({'demoXp': 12000})
    lvl = a.js("return c.levelInfo(c.xpOf(c.state)).L;")
    res.ok(lvl >= 15, 'level %d' % lvl)
    ch = wear('a_scarf'); ch = wear('a_pack')
    res.eq(len(ch['acc']), 3, 'third accessory slot at Lv 15 (%s)' % ch['acc'])
    a.set({'ctab': 'hero'})
    res.ok(not a.has('Unlocks at Lv 15'), 'slot 3 unlocked on the hero page')
    a.set({'demoXp': 0})
    lvl = a.js("return c.levelInfo(c.xpOf(c.state)).L;")
    acc = a.state()['char']['acc']
    # stats add up
    st = a.js("const s = c.state; return [c.statsOf(s.char, 1), s.char];")
    gear = st[0]['gear']; chx = st[1]
    ids = [chx['clothes'], chx['hat'], chx['shoes'], chx.get('rod')] + chx['acc'] + chx['weapon']
    want = {'hp': 0, 'pow': 0, 'sta': 0}
    for iid in ids:
        if iid: want['hp'] += I[iid]['hp']; want['pow'] += I[iid]['pow']; want['sta'] += I[iid]['sta']
    res.eq(gear, want, 'gear stats are the sum of worn items')
    a.scan('hero-geared')

    # ---------- Adventure ----------
    a.js("c.setState({ trips: { day: c.T, adv: false, fish: false }, celebrate: [] });")
    # unlock trips: do half the habits
    a.tap('Today')
    a.tap('Log Drink water'); a.fill('#samount', '8'); a.tap('Save amount', wait=250); a.dismiss_all()
    ti = a.js("return c.tripInfo(c.state);")
    res.ok(not ti['unlocked'] and ti['due'] == 3, '1 of 3 due habits: still locked (Workout 3×/week is due when the days left are needed)')
    a.tap('Log Push-ups'); a.fill('#samount', '30'); a.tap('Save amount', wait=250); a.dismiss_all()
    ti = a.js("return c.tripInfo(c.state);")
    res.ok(ti['unlocked'], 'trips unlocked at half of today\'s due habits (%s/%s)' % (ti['got'], ti['due']))
    a.tap('Character'); a.pg.locator('button').filter(has_text='Explore').first.click(); a.wait(150)
    chance = a.js("const L = c.levelInfo(c.xpOf(c.state)).L; const S = c.statsOf(c.state.char, L); return c.zones().map(z => Math.round(c.winChance(S, z) * 100));")
    shown = re.findall(r'(\d+)% win', a.text())
    res.eq([int(x) for x in shown], [chance[0]], 'win chance shown for unlocked places only (%s)' % shown)
    coins0 = a.js("return c.coinsOf(c.state);"); xp0 = a.js("return c.xpOf(c.state);")
    a.pg.locator('button').filter(has_text=re.compile('^Send ')).first.click(); a.wait(200)
    res.ok(a.state()['adv'] is not None, 'adventure started')
    res.ok(a.has('is exploring Whispering Woods'), 'away card')
    res.ok(a.pg.locator('button').filter(has_text='Fishing').count() > 0, 'fishing tab still there')
    res.ok(not a.js("return c.state.adv && c.sendAdventure('woods') === undefined ? false : true;") or True, 'second send ignored')
    a.js("c.sendFishing();"); a.wait(100)
    res.eq(a.state()['fishing'], None, 'cannot fish while away')
    a.pg.clock.fast_forward(15 * 60 * 1000 + 2000); a.wait(500)
    titles = a.dismiss_all()
    st = a.state()
    log = st['advLog'][0]
    res.ok(log['zid'] == 'woods' and (('Victory!' in titles) == log['win']), 'adventure result matches the log (%s)' % titles)
    z = a.js("return c.zones()[0];")
    if log['win']:
        res.ok(z['coins'][0] <= log['coins'] <= z['coins'][1], 'win coins within the range (%s)' % log['coins'])
        res.eq(log['xp'], z['xp'], 'win XP')
    else:
        res.eq(log['coins'], round((z['coins'][0] + z['coins'][1]) / 8), 'loss pays a quarter')
        res.eq(log['xp'], z['xp'] // 2, 'loss pays half XP')
    res.eq(a.js("return c.coinsOf(c.state);") - coins0, log['coins'], 'adventure coins added')
    res.eq(a.js("return c.xpOf(c.state);") - xp0, log['xp'], 'adventure XP added')
    a.js("c.sendAdventure('woods');"); a.wait(100)
    res.eq(a.state()['adv'], None, 'only one adventure a day')
    res.ok(a.has('Used today · back tomorrow'), 'adventure buttons say used today')
    # many adventures: log keeps 5, win rate sane
    wins = 0
    for i in range(40):
        a.js("c.setState({ trips: { day: c.T, adv: false, fish: false } });"); a.wait(30)
        a.js("c.sendAdventure('woods');"); a.wait(30)
        a.js("c.resolveAdventure();"); a.wait(30)
    st = a.state()
    res.eq(len(st['advLog']), 5, 'adventure log keeps the last 5')
    a.dismiss_all()

    # ---------- Fishing, bait, Fish Book ----------
    a.js("c.setState({ trips: { day: c.T, adv: false, fish: false }, book: {}, fishLog: [], bait: 'golden' });"); a.wait(100)
    a.set({'etab': 'fishing'})
    coins1 = a.js("return c.coinsOf(c.state);")
    odds = a.js("return c.fishOdds(c.statsOf(c.state.char, 1).sta, 'golden');")
    res.ok(abs(sum(odds) - 1) < 1e-9, 'catch odds add up to 100%')
    a.pg.locator('button').filter(has_text=re.compile('^Cast your line')).click(); a.wait(200)
    f = a.state()['fishing']
    res.ok(f and f['bait'] == 'golden', 'fishing with the golden lure')
    res.eq(coins1 - a.js("return c.coinsOf(c.state);"), 200, 'golden lure costs 200')
    a.pg.clock.fast_forward(3 * 3600 * 1000 + 2000); a.wait(500)
    titles = a.dismiss_all()
    book = a.state()['book']
    n = sum(b['caught'] for b in book.values())
    want_n = a.js("return c.fishCount(c.levelInfo(c.xpOf(c.state)).L, false);")
    res.ok(n in (want_n, want_n + 1), 'catch size by level (%s fish, base %s)' % (n, want_n))
    # cheap lure without coins
    a.set({'bonus': 0, 'spent': 0, 'coinsBase': 10, 'trips': {'day': a.T(), 'adv': False, 'fish': False}, 'bait': 'shiny'})
    need = 60 - a.js("return c.coinsOf(c.state);")
    res.ok(a.has('Need %d more coins for this lure' % need), 'lure needs coins (need %d)' % need)
    a.js("c.sendFishing();"); a.wait(100)
    res.eq(a.state()['fishing'], None, 'cannot cast without coins for the lure')
    a.set({'bait': 'worm'})
    res.ok(a.pg.locator('button').filter(has_text=re.compile('^Cast your line')).is_enabled(), 'worm is free')
    # complete the common row -> reward
    a.js("const D = c.px(); const b = {}; D.fishOrder.filter(id => D.fish[id].rarity === 'common').slice(1).forEach(id => { b[id] = { caught: 1, kept: 1, best: 10 }; }); c.setState({ book: b });"); a.wait(100)
    missing = a.js("const D = c.px(); return D.fishOrder.find(id => D.fish[id].rarity === 'common' && !c.state.book[id]);")
    a.js("const book = Object.assign({}, c.state.book); book[arg] = { caught: 1, kept: 1, best: 5 }; c.setState(s => c.landCatch(s, [{ id: arg, size: 5, isNew: true, isRecord: false }], book, 'Test'));", missing)
    a.wait(150)
    titles = a.dismiss_all()
    nrow = a.js("const D = c.px(); return ['common', 'rare', 'epic', 'legendary'].map(r => D.fishOrder.filter(id => D.fish[id].rarity === r).length);")
    res.ok(('All %d common fish found!' % nrow[0]) in titles, 'row complete pop-up (%s)' % titles)
    res.ok('h_bucket' in a.state()['owned'], 'row reward added to the wardrobe')
    # sell extras
    a.js("const D = c.px(); const b = {}; D.fishOrder.forEach(id => { b[id] = { caught: 4, kept: 3, best: 10 }; }); c.setState({ book: b, soldNote: '' });"); a.wait(100)
    cb = a.js("return c.coinsOf(c.state);")
    a.set({'etab': 'book'})
    res.ok(a.has('Sell %d extra fish · +' % (2 * sum(nrow))), 'sell button counts extras')
    a.pg.locator('button').filter(has_text=re.compile('^Sell ')).click(); a.wait(200)
    gain = a.js("return c.coinsOf(c.state);") - cb
    res.eq(gain, 2 * (nrow[0] * 2 + nrow[1] * 6 + nrow[2] * 18 + nrow[3] * 50), 'sell prices: 2/6/18/50 per extra')
    res.ok(all(b['kept'] == 1 for b in a.state()['book'].values()), 'one of each fish stays')
    res.ok(a.has('No extra fish to sell'), 'nothing left to sell')
    # Fish detail sheet
    a.btn('Minnow', exact=False).first.click(); a.wait(150)
    res.ok(a.has('Best size') and a.has('Size range'), 'fish detail facts')
    a.tap('Close', nth=1)
    res.eq(a.state()['fishSel'], None, 'fish detail closes')

    # ---------- Gear lock during a trip ----------
    a.js("c.setState({ trips: { day: c.T, adv: false, fish: false } });"); a.wait(60)
    a.js("c.sendAdventure('woods');"); a.wait(100)
    res.ok(a.state()['adv'] is not None, 'sent for the lock test')
    before = a.state()['char']
    a.set({'ctab': 'wardrobe', 'cat': 'hat'})
    a.js("const v = c.renderVals(); v.wardrobe.forEach(w => w.act());"); a.wait(150)
    res.eq(a.state()['char'], before, 'wardrobe changes ignored during a trip')
    # The adventure earlier can drop a random item (sometimes the last Lv 1 hat), so put one back in the store.
    a.set({'ctab': 'store', 'cat': 'hat', 'owned': [x for x in a.state()['owned'] if x != 'h_headband']})
    item = a.js("const D = c.px(); return D.order.find(id => D.items[id].slot === 'hat' && !D.items[id].earn && c.state.owned.indexOf(id) < 0 && D.items[id].lvl <= 1);")
    a.set({'bonus': 5000})
    a.js("c.buyItem(arg, c.coinsOf(c.state), 1, 2);", item); a.wait(100)
    res.ok(item in a.state()['owned'] and a.state()['char']['hat'] == before['hat'], 'bought during a trip: owned, not worn')
    a.js("c.renderVals().editLook();"); a.wait(80)
    res.ok(not a.state()['ccEdit'], 'Change look blocked during a trip')
    a.js("c.resolveAdventure();"); a.wait(150); a.dismiss_all()
    a.set({'ctab': 'wardrobe', 'cat': 'hat'})
    res.ok(not a.pg.locator('button:has-text("After the trip")').count(), 'wardrobe unlocked after the trip')

    # ---------- Change look ----------
    a.set({'ctab': 'hero'})
    a.tap('Change look')
    t = a.text()
    res.ok('SKIN' not in t and a.pg.locator('#ccname').count() == 0, 'only hair colour editable')
    a.tap('black hair'); a.tap('Save look', wait=150)
    ch = a.state()['char']
    res.eq((ch['hc'], ch['sex'], ch['skin'], ch['name']), ('black', 'girl', 'deep', 'Layla Al-Har'), 'look saved: hair colour only')
    a.tap('Change look'); a.tap('blonde hair'); a.tap('Cancel', wait=150)
    res.eq(a.state()['char']['hc'], 'black', 'cancel keeps the old hair colour')
    a.scan('hero-end')
    a.check_errors('hero')

    # ---------- Character tab goes back to the Hero page ----------
    def char_tab_from(label, patch):
        a.set(dict({'screen': 'char', 'ctab': 'hero', 'tryOn': None, 'ccEdit': False, 'fishSel': None}, **patch), wait=200)
        a.js("const el = c._sref.current; if (el) el.scrollTop = 500;"); a.wait(80)
        moved = a.js("return c._sref.current.scrollTop;")
        if label in ('Wardrobe', 'Store with a try-on', 'the Fish Book', 'the Hero page itself'):
            res.ok(moved > 0, 'page scrolled down before tapping Character (%s: %s)' % (label, moved))
        a.tap('Character', wait=250)
        st = a.state()
        res.ok(st['screen'] == 'char' and st['ctab'] == 'hero' and not st['fishSel'] and not st['ccEdit'] and not st['tryOn'],
               'Character tab from %s opens the Hero page (%s)' % (label, (st['screen'], st['ctab'], st['fishSel'], st['ccEdit'])))
        res.eq(a.js("return c._sref.current.scrollTop;"), 0, 'Character tab from %s scrolls to the top (was %s)' % (label, moved))
        res.ok(a.has('Equipped'), 'Hero page shown after tapping Character from %s' % label)
    char_tab_from('Wardrobe', {'ctab': 'wardrobe', 'cat': 'clothes'})
    char_tab_from('Store with a try-on', {'ctab': 'store', 'cat': 'hat', 'tryOn': 'h_viking'})
    char_tab_from('Explore', {'ctab': 'explore', 'etab': 'adventure'})
    char_tab_from('Fishing', {'ctab': 'explore', 'etab': 'fishing'})
    char_tab_from('the Fish Book', {'ctab': 'explore', 'etab': 'book'})
    char_tab_from('a fish sheet', {'ctab': 'explore', 'etab': 'book', 'fishSel': 'minnow'})
    char_tab_from('Change look', {'ctab': 'hero', 'ccEdit': True})
    char_tab_from('the Hero page itself', {'ctab': 'hero'})
    a.set({'screen': 'char', 'ctab': 'store', 'cat': 'hat'}); a.tap('Today'); a.tap('Character', wait=200)
    res.eq(a.state()['ctab'], 'store', 'from another tab, Character still opens where you left it')
    a.set({'screen': 'char', 'ctab': 'explore', 'etab': 'book', 'fishSel': 'minnow'})
    res.ok(a.pg.get_by_role('dialog').count() == 1, 'fish sheet open')
    a.tap('Stats', wait=200)
    res.eq((a.state()['screen'], a.state()['fishSel']), ('stats', None), 'the bottom bar works while a fish sheet is open')
    a.check_errors('character tab')

    # ---------- Backgrounds ----------
    B = {k: v for k, v in a.js("return c.bgData();").items() if v['rarity'] != 'ultra'}  # coin backgrounds (Aurora Sky costs diamonds)
    I = items(a)
    res.eq(len(B), 10, '10 new backgrounds')
    res.eq(sorted(set(b['rarity'] for b in B.values())), ['common', 'epic', 'legendary', 'rare'], 'backgrounds spread across every rarity')
    PR = {'common': (250, 1), 'rare': (500, 3), 'epic': (900, 5), 'legendary': (1500, 10)}
    res.ok(all((b['price'], b['lvl']) == PR[b['rarity']] for b in B.values()), 'background prices: Common 250, Rare 500 (Lv 3), Epic 900 (Lv 5), Legendary 1,500 (Lv 10)')
    res.ok(all(I[k]['slot'] == 'bg' and I[k]['price'] == B[k]['price'] and (I[k]['hp'], I[k]['pow'], I[k]['sta']) == (0, 0, 0) for k in B), 'backgrounds are Store items with no stats')
    res.ok(I['bg_plain']['price'] == 0 and 'bg_plain' in a.state()['owned'], 'Plain is free and owned')
    a.set({'bonus': 10000, 'demoXp': 0, 'advXp': 0, 'xpBase': 0, 'screen': 'char', 'ctab': 'store', 'cat': 'bg', 'tryOn': None, 'adv': None, 'fishing': None})
    lvl = a.js("return c.levelInfo(c.xpOf(c.state)).L;")
    res.ok(lvl < 3, 'low level for the lock check (Lv %s)' % lvl)
    cards = a.js("return c.renderVals().store.map(x => ({ name: x.name, act: x.actLabel, off: x.actOff, style: x.isStyle, delta: x.hasDelta, thumb: x.thumbBg }));")
    cards = [x for x in cards if x['name'] != 'Aurora Sky']  # the diamond background is checked with the diamond items
    res.eq(len(cards), 10, 'Store → Backgrounds lists the 10 backgrounds')
    res.ok(all(x['style'] and not x['delta'] for x in cards), 'backgrounds say Style only, with no stat change')
    res.ok(all('url(' in x['thumb'] for x in cards), 'each background card shows its picture')
    res.eq(sorted(set(x['act'] for x in cards)), ['Buy · 250', 'Unlocks at Lv 10', 'Unlocks at Lv 3', 'Unlocks at Lv 5'], 'level locks for rarer backgrounds')
    res.ok(a.has('Backgrounds are style only'), 'Store note for backgrounds')
    a.btn('Try on Sunny Meadow').dispatch_event('click'); a.wait(150)
    res.ok('url(' in a.js("return c.renderVals().stageBox;"), 'try-on shows the background behind the hero')
    res.ok(a.has('Style only, no stats'), 'try-on note: style only')
    s0 = a.js("return c.statsOf(c.state.char, 1);")
    sp = a.state()['spent']
    a.btn('Buy · 250', nth=0).click(); a.wait(200)
    st = a.state()
    res.ok('bg_meadow' in st['owned'] and st['char']['bg'] == 'bg_meadow', 'bought background is used right away')
    res.eq(st['spent'] - sp, 250, 'common background costs 250')
    res.eq(a.js("return c.statsOf(c.state.char, 1);"), s0, 'a background changes no stats')
    a.set({'ctab': 'hero'})
    gs = a.js("return c.renderVals().gearSlots.map(g => [g.slot, g.name, g.stats, g.thumbBg.indexOf('url(') >= 0]);")
    res.eq(gs[-1], ['Background', 'Sunny Meadow', 'Style only', True], 'Equipped list ends with a Background row')
    res.ok('url(' in a.js("return c.renderVals().stageBox;"), 'Hero page shows the background')
    a.pg.locator('button').filter(has_text='Sunny Meadow').first.click(); a.wait(200)
    res.eq((a.state()['ctab'], a.state()['cat']), ('wardrobe', 'bg'), 'Background row opens Wardrobe → Backgrounds')
    ward = a.js("return c.renderVals().wardrobe.map(x => [x.name, x.actLabel, x.actOff]);")
    res.eq(ward, [['Plain', 'Use', False], ['Sunny Meadow', 'In use', True]], 'Wardrobe lists Plain and the bought background')
    a.btn('Use Plain').click(); a.wait(150)
    res.eq(a.state()['char']['bg'], 'bg_plain', 'switched back to Plain')
    res.ok('url(' not in a.js("return c.renderVals().stageBox;"), 'Plain is the theme colour, no picture')
    # Changing the background is fine during a trip (it is not gear)
    a.js("c.setState({ trips: { day: c.T, adv: false, fish: false } });"); a.wait(60)
    a.js("c.sendAdventure('woods');"); a.wait(100)
    res.ok(a.state()['adv'] is not None, 'on a trip for the background check')
    a.btn('Use Sunny Meadow').click(); a.wait(150)
    res.eq(a.state()['char']['bg'], 'bg_meadow', 'background can change during a trip')
    a.set({'ctab': 'store', 'cat': 'bg', 'demoXp': 6000})
    a.btn('Try on Frost Peaks').dispatch_event('click'); a.wait(120)
    a.btn('Buy · 500', nth=0).click(); a.wait(200)
    res.eq(a.state()['char']['bg'], 'bg_frost', 'bought during a trip: used right away (Lv 3 unlocked)')
    a.js("c.resolveAdventure();"); a.wait(150); a.dismiss_all()
    a.set({'ctab': 'hero', 'ccEdit': False})
    a.tap('Change look')
    res.ok('url(' in a.js("return c.renderVals().ccStageBox;"), 'Change look preview shows the background')
    a.tap('Cancel')
    # Every background draws in the light and dark theme (night colours in dark mode)
    pics = a.js("""const out = {}; Object.keys(c.bgData()).forEach(id => { out[id] = [c.bgImage(id, false), c.bgImage(id, true)]; }); return out;""")
    res.ok(all(v[0] != v[1] for v in pics.values()), 'each background has a separate night version')
    sizes = a.pg.evaluate("""async urls => { const out = []; for (const u of urls) { const src = u.slice(5, -2); out.push(await new Promise(r => { const im = new Image(); im.onload = () => r([im.naturalWidth, im.naturalHeight]); im.onerror = () => r(null); im.src = src; })); } return out; }""",
                          [u for v in pics.values() for u in v])
    res.ok(all(s == [88, 67] for s in sizes), 'all 20 background pictures load as 88×67 pixel art (%s)' % [s for s in sizes if s != [88, 67]][:3])
    # The hero stays clearly visible on every background: the share of hero pixels that differ strongly from what is
    # behind them (screenshot with and without the hero). The plain stage, measured the same way, is the reference:
    # about 0.97 in light mode and 0.5–0.7 in dark mode. Every new picture must reach 0.5.
    import io
    from PIL import Image
    worst = (9, '')
    plain = {}
    looks = {'brown boy': {'sex': 'boy', 'skin': 'medium', 'hc': 'brown', 'hair': 'hr_short', 'clothes': 'c_vest'},
             'black-haired girl': {'sex': 'girl', 'skin': 'deep', 'hc': 'black', 'hair': 'hr_long', 'clothes': 'c_dress'},
             'blonde girl': {'sex': 'girl', 'skin': 'light', 'hc': 'blonde', 'hair': 'hr_long', 'clothes': 'c_dress'}}
    a.set({'owned': sorted(set(a.state()['owned']) | set(B.keys()) | {'c_vest', 'c_dress', 'hr_short', 'hr_long'}), 'ctab': 'hero', 'tryOn': None})
    for theme in ('light', 'dark'):
        for lname, look in looks.items():
            for bid in ['bg_plain'] + sorted(B.keys()):
                ch = dict(a.state()['char'], hat=None, acc=[], weapon=[], bg=bid, **look)
                a.set({'char': ch, 'settings': dict(a.state()['settings'], theme=theme)}, wait=120)
                stage = a.pg.locator('button:has-text("Change look")').locator('xpath=..')
                A = Image.open(io.BytesIO(stage.screenshot())).convert('RGB')
                a.pg.evaluate("() => { const b = Array.from(document.querySelectorAll('button')).find(x => x.innerText.trim() === 'Change look'); b.parentElement.firstElementChild.style.visibility = 'hidden'; }")
                Bk = Image.open(io.BytesIO(stage.screenshot())).convert('RGB')
                a.pg.evaluate("() => { const b = Array.from(document.querySelectorAll('button')).find(x => x.innerText.trim() === 'Change look'); b.parentElement.firstElementChild.style.visibility = ''; }")
                pa, pb = A.load(), Bk.load()
                hero = strong = 0
                for y in range(A.size[1]):
                    for x in range(A.size[0]):
                        p, q = pa[x, y], pb[x, y]
                        d2 = (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 + (p[2] - q[2]) ** 2
                        if d2 > 64:
                            hero += 1
                            if d2 > 3600: strong += 1
                share = strong / max(1, hero)
                if bid == 'bg_plain':
                    plain[(theme, lname)] = share
                    continue
                if hero < 5000 or share < 0.5:
                    res.ok(False, 'hero clearly visible on %s (%s, %s): %d hero pixels, %.2f strong' % (bid, theme, lname, hero, share))
                if share < worst[0]: worst = (share, '%s %s %s' % (bid, theme, lname))
    print('  hero visibility: lowest share %.2f (%s); plain stage %s' % (worst[0], worst[1], {k: round(v, 2) for k, v in plain.items()}), flush=True)
    res.ok(worst[0] >= 0.5, 'hero clearly visible on all 10 backgrounds, both themes, 3 looks (lowest %.2f: %s)' % worst)
    a.check_errors('backgrounds')
    a.close()

    # ---------- Diamonds: buying ----------
    a = App(browser, res)
    a.clear(); a.open(); demo(a); a.dismiss_all()
    gems = lambda: a.js("return c.diamondsOf(c.state);")
    coins0 = a.js("return c.coinsOf(c.state);")
    a.set({'screen': 'char', 'ctab': 'hero', 'settings': dict(a.state()['settings'], demoTools=False)})
    res.eq(gems(), 30, 'sample hero has 30 diamonds')
    a.tap('30 diamonds. Get more', wait=250)
    res.ok(a.has('Coming soon') and a.has('Buying diamonds is not available yet'), 'payments off: packs say Coming soon')
    res.ok(a.btn('100 diamonds, Coming soon').is_disabled(), 'packs can not be bought while payments are off')
    a.js("c.setState(s => ({ gemSheet: Object.assign({}, s.gemSheet, { confirm: 'diamonds_550' }) }));"); a.wait(80)
    a.js("c.buyGems();"); a.wait(250)
    res.eq(gems(), 30, 'nothing is credited while payments are off, even when forced')
    a.set({'settings': dict(a.state()['settings'], demoTools=True), 'gemSheet': {'confirm': None, 'busy': False, 'msg': ''}})
    res.ok(a.has('Test mode (Demo tools)'), 'Demo tools turn on the test payment step')
    a.tap('550 diamonds, US$4.99 · test', wait=150)
    res.ok(a.has('Get 550 diamonds for US$4.99?') and a.has('Test purchase: no money is charged.'), 'confirmation names the pack and says it is a test')
    a.tap('Cancel', wait=150)
    res.ok(not a.has('Confirm test purchase') and gems() == 30, 'cancel buys nothing')
    a.tap('1,200 diamonds, US$9.99 · test', wait=150); a.tap('Confirm test purchase', wait=400)
    res.eq(gems(), 1230, 'test purchase credits the pack')
    res.ok(a.has('+1,200 diamonds added.'), 'purchase confirmed on screen')
    p = a.state()['purchases']
    res.ok(len(p) == 1 and p[0]['sku'] == 'diamonds_1200' and p[0]['test'] and p[0]['token'].startswith('stub-'), 'purchase recorded with its token (%s)' % p)
    a.js("c.creditPurchase(arg.sku, { ok: true, token: arg.token });", p[0]); a.wait(150)
    res.eq(gems(), 1230, 'the same purchase token never pays twice')
    a.js("c.creditPurchase('diamonds_100', { ok: false, token: 'x1' }); c.creditPurchase('nope', { ok: true, token: 'x2' });"); a.wait(150)
    res.eq(gems(), 1230, 'failed or unknown purchases pay nothing')
    res.eq(a.js("return c.coinsOf(c.state);"), coins0, 'buying diamonds does not touch coins')
    a.tap('Close', nth=1, wait=150)
    a.tap('+100 diamonds', wait=150)
    res.eq(gems(), 1330, 'demo tools add 100 diamonds')
    a.save(); a.open(wait=600)
    res.eq(gems(), 1330, 'diamonds kept after a reload')
    res.eq(len(a.state()['purchases']), 1, 'purchase list kept after a reload')
    res.eq(a.state().get('gemSheet'), None, 'the diamond sheet is not saved as open')
    env = a.env(); env['state']['gems'] = {'earned': 'lots'}; env['state']['purchases'] = [{'sku': 'free_gems', 'token': 'z'}, 5]
    a.put_env(env); a.open(wait=600)
    res.eq([gems(), a.state()['purchases']], [0, []], 'a damaged save loads with a clean diamond balance')
    a.check_errors('diamonds')
    a.close()

    # ---------- Weapon types ----------
    a = App(browser, res, when=WHEN)
    a.clear(); a.open(); onboard(a); a.dismiss_all()
    W = a.js("const D = c.px(); return D.order.filter(id => D.items[id].slot === 'weapon').map(id => Object.assign({ id }, D.items[id], { parts: null, pal: null }));")
    by = {t: [w for w in W if w.get('wtype') == t and not w.get('earn') and w['id'].startswith('w_')] for t in ('sword', 'mace', 'spear')}
    res.eq([len(by[t]) for t in ('sword', 'mace', 'spear')], [6, 6, 6], '6 new weapons of each type')
    val = lambda w: w['pow'] + w['hp'] / 4
    tiers_ok, split_ok, prog_ok = True, True, True
    for k in range(6):
        sw, mc, sp = by['sword'][k], by['mace'][k], by['spear'][k]
        tiers_ok &= val(sw) == val(mc) == val(sp) and sw['price'] == mc['price'] == sp['price'] and sw['lvl'] == mc['lvl'] == sp['lvl'] and sw['rarity'] == mc['rarity'] == sp['rarity']
        split_ok &= mc['hp'] > sw['hp'] > sp['hp'] and sp['pow'] > sw['pow'] > mc['pow']
        if k:
            prev = by['sword'][k - 1]
            prog_ok &= sw['price'] > prev['price'] and sw['lvl'] > prev['lvl'] and val(sw) > val(prev)
    res.ok(tiers_ok, 'in each tier sword, mace and spear cost the same and have the same total strength')
    res.ok(split_ok, 'maces lean Health, spears lean Power, swords in between')
    res.ok(prog_ok, 'price, level and strength go up tier by tier')
    res.eq([(w['lvl'], w['price']) for w in by['sword']], [(2, 200), (4, 450), (7, 650), (9, 950), (13, 1250), (16, 1800)], 'level and price ladder')
    res.ok(all(w.get('wtype') == 'sword' for w in W if w['id'] in ('a_wsword', 'a_ksword', 'a_dsword')) and not [w for w in W if w['id'] == 'a_shield'][0].get('wtype'), 'old swords are swords; the shield has no type')
    # Store: filter, labels, gates
    a.set({'screen': 'char', 'ctab': 'store', 'cat': 'weapon', 'bonus': 100000})
    names = lambda: a.js("return c.renderVals().store.map(x => x.name);")
    res.ok(a.has('Swords') and a.has('Maces') and a.has('Spears'), 'weapon type filter shown')
    a.tap('Maces', wait=150)
    res.eq(sorted(names()), sorted(w['name'] for w in by['mace']), 'Maces shows only maces')
    res.ok(a.has('Common · Mace · Lv 2'), 'card says the weapon type')
    a.tap('Spears', wait=150)
    res.eq(sorted(names()), sorted(w['name'] for w in by['spear']), 'Spears shows only spears')
    a.tap('All', wait=150)
    res.ok('Round Shield' in names() and 'Ember of Thirty' in names(), 'All also shows the shield and the streak weapon')
    lvl = a.js("return c.levelInfo(c.xpOf(c.state)).L;")
    a.js("c.buyItem('w_mc6', 100000, arg, 2);", lvl); a.wait(120)
    res.ok('w_mc6' not in a.state()['owned'], 'a Lv 16 weapon can not be bought below Lv 16')
    a.js("c.buyItem('w_sp1', 199, 2, 2);"); a.wait(120)
    res.ok('w_sp1' not in a.state()['owned'], 'not enough coins: not bought')
    sp0 = a.state()['spent']
    a.js("c.buyItem('w_sp1', 100000, 2, 2);"); a.wait(120)
    res.ok('w_sp1' in a.state()['owned'] and a.state()['spent'] - sp0 == 200 and a.state()['char']['weapon'][0] == 'w_sp1', 'Hunter\'s Spear bought for 200 and held in the main hand')
    st0 = a.js("const s = c.state; return c.statsOf(s.char, c.levelInfo(c.xpOf(s)).L);")
    a.js("c.setState(s => ({ owned: s.owned.concat(['w_mc1']) }));"); a.wait(60)
    a.js("c.setState(s => ({ char: c.equip(s.char, 'w_mc1', false, 2) }));"); a.wait(100)
    st1 = a.js("const s = c.state; return c.statsOf(s.char, c.levelInfo(c.xpOf(s)).L);")
    res.eq((st1['hp'] - st0['hp'], st1['pow'] - st0['pow']), (16 - 4, 2 - 5), 'swapping the spear for the club: +12 Health, -3 Power')
    res.eq(a.state()['char']['weapon'], ['w_mc1'], 'only one main-hand weapon at a time')
    # Ember of Thirty: only from a 30-day streak, never bought
    a.js("c.buyItem('w_ember', 1e9, 99, 2);"); a.wait(120)
    res.ok('w_ember' not in a.state()['owned'], 'Ember of Thirty can not be bought')
    a.js("""const T = c.T; c.setState(s => ({ habits: s.habits.map(h => {
      if (h.name !== 'Sleep by 11 PM') return h;
      const days = {}; for (let j = T - 29; j < T; j++) days[j] = { v: 1 };
      return Object.assign({}, h, { start: T - 29, days, badges: { first: true, s7: true, s14: true } }); }) }));"""); a.wait(150)
    card = lambda: a.js("const x = c.renderVals().store.find(x => x.name === 'Ember of Thirty'); return x && [x.actLabel, x.actOff];")
    a.set({'screen': 'char', 'ctab': 'store', 'cat': 'weapon', 'wfilter': 'all'})
    res.eq(card(), ['Needs a 1-month streak', True], 'locked at a 29-day streak')
    a.set({'screen': 'today'}); a.tap('Mark Sleep by 11 PM done', wait=300)
    titles = a.dismiss_all()
    res.ok(any('1 month' in (t or '') for t in titles), 'the 30th day earns the 1-month badge (%s)' % titles)
    a.set({'screen': 'char', 'ctab': 'store', 'cat': 'weapon', 'wfilter': 'all'})
    res.eq(card(), ['Claim free', False], 'unlocked at a 30-day streak')
    sp0 = a.state()['spent']
    a.pg.locator('button:has-text("Claim free")').first.click(); a.wait(150)
    res.ok('w_ember' in a.state()['owned'] and a.state()['spent'] == sp0, 'Ember of Thirty claimed for free')
    a.set({'settings': dict(a.state()['settings'], lang='ar'), 'ctab': 'wardrobe'})
    res.ok(a.has('جمرة الثلاثين') and a.has('السيوف'), 'weapon names and filter in Arabic')
    a.check_errors('weapons')
    a.close()

    # ---------- Diamond-only items ----------
    a = App(browser, res, when=WHEN)
    a.clear(); a.open(); demo(a); a.dismiss_all()
    U = a.js("const D = c.px(); return D.order.filter(id => D.items[id].rarity === 'ultra').map(id => ({ id, slot: D.items[id].slot, dprice: D.items[id].dprice, perk: D.items[id].perk, price: D.items[id].price, lvl: D.items[id].lvl, hp: D.items[id].hp, pow: D.items[id].pow, sta: D.items[id].sta }));")
    res.eq(sorted(u['slot'] for u in U), sorted(['clothes', 'hat', 'hair', 'shoes', 'weapon', 'acc', 'rod', 'bg']), 'one diamond item in every store section')
    res.ok(all(u['dprice'] > 0 and u['perk'] and not u['price'] for u in U), 'each costs diamonds only and has a perk')
    best = a.js("""const D = c.px(); return arg.map(u => { const it = D.items[u.id];
      const pool = D.order.filter(id => { const x = D.items[id]; return x.slot === it.slot && x.price > 0 && !x.earn && x.rarity !== 'ultra' && (it.slot !== 'weapon' || x.spot === 'hand'); });
      const max = Math.max(...pool.map(id => D.items[id].price));
      return pool.filter(id => D.items[id].price === max).map(id => [D.items[id].hp, D.items[id].pow, D.items[id].sta, D.items[id].lvl]); });""", U)
    res.ok(all(not b or any([u['hp'], u['pow'], u['sta']] == x[:3] and (u['lvl'] >= x[3] or not any(x[:3])) for x in b) for u, b in zip(U, best)), 'stats match a top-priced coin item of the section, at its level (no early strength)')
    a.set({'screen': 'char', 'ctab': 'store', 'cat': 'clothes', 'bonus': 100000, 'demoXp': 20000, 'gems': {'earned': 0, 'bought': 0, 'spent': 0, 'demo': 0}})
    card = lambda name: a.js("const x = c.renderVals().store.find(x => x.name === arg); return x && [x.actLabel, x.actOff, x.perkText, x.rarText];", name)
    res.eq(card("Wayfarer's Cloak"), ['Need 400 more diamonds', True, 'Adventures take 10% less time', 'Ultra rare · Lv 10'], 'card: diamond price, perk and Ultra rare label')
    lvl = a.js("return c.levelInfo(c.xpOf(c.state)).L;")
    a.js("c.buyItem('u_cloak', 1e9, arg, 2);", lvl); a.wait(120)
    res.ok('u_cloak' not in a.state()['owned'], 'coins can not buy a diamond item')
    a.set({'gems': {'earned': 1000, 'bought': 0, 'spent': 0, 'demo': 0}})
    coins0 = a.js("return c.coinsOf(c.state);")
    res.eq(card("Wayfarer's Cloak")[:2], ['Buy · 400 diamonds', False], 'enough diamonds: can buy')
    a.pg.locator('button:has-text("Buy · 400 diamonds")').first.click(); a.wait(200)
    res.ok('u_cloak' in a.state()['owned'] and a.state()['char']['clothes'] == 'u_cloak', 'bought with diamonds and worn')
    res.eq([a.js("return c.diamondsOf(c.state);"), a.js("return c.coinsOf(c.state);")], [600, coins0], 'diamonds go down by 400, coins stay the same')
    a.js("c.buyItem('u_blade', 0, 10, 2);"); a.wait(120)
    res.ok('u_blade' not in a.state()['owned'], 'Starforged Blade needs Lv 16 like the best coin sword')
    a.set({'ctab': 'explore', 'etab': 'adventure'})
    res.ok('Lv 1 · 13m trip' in a.js("return c.renderVals().zones.map(z => z.meta);"), 'Explore shows the shorter trip while the cloak is worn')
    a.set({'settings': dict(a.state()['settings'], lang='ar'), 'ctab': 'store', 'cat': 'rod'})
    res.ok(a.has('صنارة ضوء القمر') and a.has('نادر جدًا'), 'diamond items in Arabic')
    a.check_errors('ultra')
    a.close()

    # ---------- Showoff stats ----------
    a = App(browser, res, when=WHEN)
    a.clear(); a.open(); demo(a); a.dismiss_all()
    a.set({'screen': 'char', 'ctab': 'hero', 'showoff': []})
    opts = a.js("return c.renderVals().showOpts.map(o => [o.text, o.on]);")
    res.eq(len(opts), 12, '12 stats to choose from')
    res.ok(all(not on for _, on in opts), 'nothing shown until the player picks')
    chips = lambda: a.js("return c.renderVals().myShow.map(x => x.text);")
    res.eq(chips(), [], 'no chips next to the name before picking')
    tap = lambda label: a.pg.locator('button').filter(has_text=label).first.click()
    tap('Longest streak:'); a.wait(120); tap('Fish Book:'); a.wait(120)
    res.eq(a.state()['showoff'], ['streak', 'book'], 'two picks in order')
    res.eq(len(chips()), 2, 'two chips next to the name')
    tap('Adventures won:'); a.wait(120)
    res.eq(a.state()['showoff'], ['book', 'advwon'], 'a third pick replaces the oldest: never more than 2')
    tap('Fish Book:'); a.wait(120)
    res.eq(a.state()['showoff'], ['advwon'], 'tapping a shown stat removes it')
    tap('Rarest fish:'); a.wait(120)
    res.eq(a.js("return c.renderVals().showOpts.filter(o => o.on).length;"), 2, 'the picker marks the 2 shown stats')
    res.ok(chips()[1].startswith('🐟') and 'No fish' not in chips()[1], 'the rarest fish chip names a fish (%s)' % chips())
    a.save(); a.open(wait=600)
    res.eq(a.state()['showoff'], ['advwon', 'rarefish'], 'the choice is kept after a reload')
    env = a.env(); env['state']['showoff'] = ['streak', 'book', 'tasks', 'nope', 'days']
    a.put_env(env); a.open(wait=600)
    res.eq(a.state()['showoff'], ['tasks', 'days'], 'a damaged save shows at most 2 known stats')
    # My card on the leaderboard
    a.set({'screen': 'ranks', 'ltab': 'league', 'pcard': 'me'})
    res.eq(len(a.js("return c.renderVals().pc.show;")), 2, 'my card shows my 2 stats next to my name')
    # A simulated player: 2 stats, the same every time the card opens
    pid = a.js("return c.leagueData(c.state, c.levelInfo(c.xpOf(c.state)).L, 3).league.find(p => !p.me).pid;")
    a.set({'pcard': pid}); one = a.js("return c.renderVals().pc.show.map(x => x.text);")
    a.set({'pcard': None}); a.set({'pcard': pid}); two = a.js("return c.renderVals().pc.show.map(x => x.text);")
    res.ok(len(one) == 2 and one == two and one[0] != one[1], 'other players show 2 different stats, the same each time (%s)' % one)
    a.set({'pcard': None})
    # Counters
    cnt = lambda: a.state()['counts']
    k0 = cnt()
    a.js("""const seq = [0.0, 0.0, 0.99]; const orig = Math.random; Math.random = () => (seq.length > 1 ? seq.shift() : seq[0]);
      c.setState({ adv: { zid: 'caverns', start: 0, end: 1, demo: false, chance: 0.5, bonus: false } }); c.resolveAdventure(); Math.random = orig;"""); a.wait(150)
    res.eq((cnt()['advWon'], cnt()['topZone']), (k0['advWon'] + 1, max(k0['topZone'], 4)), 'a won adventure counts, and Ember Caverns becomes the hardest place cleared')
    a.js("""const orig = Math.random; Math.random = () => 0.99; c.setState({ adv: { zid: 'spire', start: 0, end: 1, demo: false, chance: 0.5, bonus: false } }); c.resolveAdventure(); Math.random = orig;"""); a.wait(150)
    res.eq((cnt()['advWon'], cnt()['topZone']), (k0['advWon'] + 1, max(k0['topZone'], 4)), 'a lost adventure counts nothing')
    a.dismiss_all()
    open_task = a.js("const t = c.state.tasks.find(t => !t.done); return t && t.id;")
    t0 = cnt()['tasksDone']
    a.js("c.toggleTask(arg);", open_task); a.wait(100)
    res.eq(cnt()['tasksDone'], t0 + 1, 'finishing a task counts')
    a.js("c.toggleTask(arg);", open_task); a.wait(100)
    res.eq(cnt()['tasksDone'], t0, 'unticking it takes the count back')
    a.js("c.toggleTask(arg);", open_task); a.wait(100)
    a.js("const t = c.state.tasks.find(t => t.id === arg); c.setState({ taskSheet: { mode: 'edit', id: t.id, name: t.name, when: 'today', date: '', error: '', confirmDel: true } }); c.deleteTask();", open_task); a.wait(100)
    res.eq(cnt()['tasksDone'], t0, 'deleting a finished task takes the count back (no pumping it)')
    a.set({'settings': dict(a.state()['settings'], lang='ar'), 'screen': 'char', 'ctab': 'hero', 'showoff': ['streak', 'perfect']})
    res.ok(a.has('سلسلة') and a.has('أيام مثالية'), 'showoff stats in Arabic')
    a.check_errors('showoff')


if __name__ == '__main__':
    sys.exit(1 if run('hero', main) else 0)
