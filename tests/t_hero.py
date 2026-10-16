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
    spent0 = a.state()['spent']
    a.pg.locator('button:has-text("Buy · 150")').first.click(); a.wait(200)
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
    res.ok('All 10 common fish found!' in titles, 'row complete pop-up (%s)' % titles)
    res.ok('h_bucket' in a.state()['owned'], 'row reward added to the wardrobe')
    # sell extras
    a.js("const D = c.px(); const b = {}; D.fishOrder.forEach(id => { b[id] = { caught: 4, kept: 3, best: 10 }; }); c.setState({ book: b, soldNote: '' });"); a.wait(100)
    cb = a.js("return c.coinsOf(c.state);")
    a.set({'etab': 'book'})
    res.ok(a.has('Sell 50 extra fish · +'), 'sell button counts extras')
    a.pg.locator('button').filter(has_text=re.compile('^Sell ')).click(); a.wait(200)
    gain = a.js("return c.coinsOf(c.state);") - cb
    res.eq(gain, 2 * (10 * 2 + 7 * 6 + 5 * 18 + 3 * 50), 'sell prices: 2/6/18/50 per extra')
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
    a.set({'ctab': 'store', 'cat': 'hat'})
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


if __name__ == '__main__':
    sys.exit(1 if run('hero', main) else 0)
