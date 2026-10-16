"""Real-time use over many days with a simulated clock: midnight with the app open, days away,
coins/XP rollover, the weekly league, trips with real lengths, timers across midnight, DST, reload consistency."""
from harness import *

HOUR = 3600 * 1000
DAY = 24 * HOUR


def coins(a):
    return a.js("return c.coinsOf(c.state);")


def xp(a):
    return a.js("return c.xpOf(c.state);")


def persist(a):
    return a.js("return JSON.parse(JSON.stringify(c.persistable(c.state)));")


def now_str(a):
    return a.pg.evaluate("() => new Date().toString().slice(0, 24)")


def reopen_after(a, ms):
    """Close the app (it saves), let time pass, open it again."""
    a.save()
    a.blank()
    a.pg.clock.fast_forward(ms)
    a.open(700)


def main(browser, res):
    # ============ S1: two weeks of daily use ============
    a = App(browser, res, when=at(2026, 10, 15, 8, 0))  # Thursday
    a.clear(); a.open()
    onboard(a, focus=('health',))  # Drink water, Sleep by 11 PM, Walk
    a.dismiss_all()
    T0 = a.T()
    res.eq(a.state()['lastDay'], T0, 'lastDay set on day one')
    # Day 1: water 8, sleep done, walk not done
    a.tap('Log Drink water'); a.fill('#samount', '8'); a.tap('Save amount', wait=250); a.dismiss_all()
    a.tap('Mark Sleep by 11 PM done', wait=250); a.dismiss_all()
    c1, x1 = coins(a), xp(a)
    res.eq(c1, 150 + 20, 'day 1 coins: welcome gift + 2 check-ins')
    res.eq(x1, 20, 'day 1 XP')
    p_before = persist(a)
    a.save(); a.pg.reload(); a.wait(600); a.dismiss_all()
    p_after = persist(a)
    res.eq(p_after, p_before, 'reload keeps exactly the same data')
    res.eq((coins(a), xp(a)), (c1, x1), 'reload keeps coins and XP')
    # Midnight with the app open
    a.pg.clock.fast_forward('15:59:00')  # 08:00:?? -> ~23:59
    a.wait(400)
    res.eq(a.T(), T0, 'still day 1 at 23:59 (%s)' % now_str(a))
    a.pg.clock.fast_forward('00:02:00')
    a.wait(600)
    res.eq(a.T(), T0 + 1, 'new day after midnight with the app open (%s)' % now_str(a))
    res.eq(a.state()['day'], T0 + 1, 'Today screen moved to the new day')
    res.ok(a.has('Friday, 16 October'), 'header shows the new date')
    res.eq((coins(a), xp(a)), (c1, x1), 'coins and XP carried over exactly at midnight')
    res.ok(a.has('Yesterday you missed 1 habit'), 'asks why Walk was missed')
    a.check_errors('midnight')
    # Day 2: everything done -> all-done bonus
    titles = []
    a.tap('Log Drink water'); a.fill('#samount', '8'); a.tap('Save amount', wait=250); titles += a.dismiss_all()
    a.tap('Mark Sleep by 11 PM done', wait=250); titles += a.dismiss_all()
    a.tap('Log time for Walk: type it or start the timer'); a.pg.get_by_label('Minutes', exact=True).fill('30'); a.wait(60); a.tap('Save time', wait=300)
    titles += a.dismiss_all()
    res.ok('All habits done today!' in titles, 'all-done pop-up (%s)' % titles)
    res.eq(coins(a) - c1, 30 + 20, 'day 2: 3 check-ins + 20 all-done bonus')
    c2, x2 = coins(a), xp(a)
    # Trips: unlocked; send an adventure with the real length (15 min), close the app, come back later
    a.tap('Character'); a.pg.locator('button').filter(has_text='Explore').first.click(); a.wait(150)
    a.pg.locator('button').filter(has_text=re.compile('^Send ')).first.click(); a.wait(250)
    adv = a.state()['adv']
    res.ok(adv and abs((adv['end'] - adv['start']) - 15 * 60000) < 50, 'adventure lasts 15 minutes')
    res.ok(adv and adv['bonus'], 'all-done bonus applies to this trip')
    reopen_after(a, 16 * 60 * 1000)
    titles = a.dismiss_all()
    res.ok(any(t in ('Victory!', 'Your hero retreated') for t in titles), 'adventure result after reopening (%s)' % titles)
    st = a.state()
    res.eq(st['adv'], None, 'adventure finished')
    res.ok(st['advLog'] and st['advLog'][0]['zid'] == 'woods', 'adventure logged')
    res.ok(coins(a) > c2 and xp(a) > x2, 'adventure paid coins and XP')
    # Fishing: 3 hours, app open in the background (fast-forward)
    a.tap('Character'); a.pg.locator('button').filter(has_text='Explore').first.click(); a.wait(100)
    a.pg.locator('button').filter(has_text='Fishing').first.click(); a.wait(150)
    a.pg.locator('button').filter(has_text=re.compile('^Cast your line')).click(); a.wait(250)
    f = a.state()['fishing']
    res.ok(f and abs((f['end'] - f['start']) - 3 * HOUR) < 50, 'fishing lasts 3 hours')
    left = [l for l in a.text().split('\n') if 'left' in l]
    res.ok(not any(re.search(r'\d{3,}s left', l) for l in left), 'fishing countdown is not shown in raw seconds (%s)' % left[:3])
    a.pg.clock.fast_forward(3 * HOUR + 5000); a.wait(600)
    titles = a.dismiss_all()
    res.ok(any('fish' in (t or '') for t in titles), 'fish caught after 3 h (%s)' % titles)
    book = a.state()['book']
    res.ok(sum(b['caught'] for b in book.values()) >= 2, 'Fish Book has the catch (+1 bonus fish)')
    res.ok(a.has('Used today · back tomorrow'), 'fishing used for today')
    # Days away: close the app for 3 days
    c3, x3 = coins(a), xp(a)
    d3 = a.T()
    reopen_after(a, 4 * DAY)
    a.dismiss_all()
    res.eq(a.T(), d3 + 4, 'four days later (3 full days missed)')
    res.eq((coins(a), xp(a)), (c3, x3), 'coins and XP unchanged after days away')
    res.ok(a.has('Welcome back'), 'comeback card after 3 missed days')
    a.tap('Start comeback week', wait=250); a.dismiss_all()
    res.ok(a.has('Comeback week · day 1 of 7'), 'comeback banner')
    a.tap('Log Drink water'); a.fill('#samount', '4'); a.tap('Save amount', wait=250); a.dismiss_all()
    w = [h for h in a.state()['habits'] if h['name'] == 'Drink water'][0]
    res.eq(a.js("return c.build(arg)[c.T];", w), 'd', 'comeback week: the minimum counts as a full day')
    # Weekly league: cross Sunday midnight
    T = a.T()
    lg0 = a.state()['league']
    days_to_sunday = 7 - (T % 7)
    a.save(); a.blank(); a.pg.clock.fast_forward(days_to_sunday * DAY); a.open(700)
    titles = a.dismiss_all()
    lg1 = a.state()['league']
    res.eq(lg1['week'], lg0['week'] + 1, 'league week closed when the week ended')
    res.ok(any(t in ('Trophy won!', 'Promoted!', 'Moved down', 'Week complete') for t in titles), 'league result pop-up (%s)' % titles)
    res.eq(a.state()['weekBase'], 0, 'weekly XP reset')
    res.eq(a.js("return c.weekXp(c.state);"), 0, 'weekly XP starts at 0 in the new week')
    a.tap('Leaderboard')
    res.ok(a.has('You are'), 'league shows my rank')
    a.scan('league-after-week')
    # Two weeks in one jump (app closed for 15 days): one league close per week
    a.tap('Today')
    lgw = a.state()['league']['week']
    reopen_after(a, 15 * DAY)
    titles = a.dismiss_all()
    res.eq(a.state()['league']['week'], lgw + 1, 'only one league close for a long absence')
    a.check_errors('S1')
    res.ok(not a.has('NaN'), 'no NaN after long absence')
    a.scan('after-absence')
    a.close()

    # ============ S2: timer across midnight ============
    a = App(browser, res, when=at(2026, 10, 15, 23, 50))
    a.clear(); a.open(); onboard(a, focus=('health',)); a.dismiss_all()
    T0 = a.T()
    a.tap('Log time for Walk: type it or start the timer'); a.tap('Start timer'); a.tap('Close', nth=1)
    a.pg.clock.fast_forward('00:09:00'); a.wait(400)   # 23:59
    a.pg.clock.fast_forward('00:05:00'); a.wait(600)   # 00:04 next day
    st = a.state()
    w = [h for h in st['habits'] if h['name'] == 'Walk'][0]
    res.eq(a.T(), T0 + 1, 'timer case: new day')
    v_old = w['days'].get(str(T0), {}).get('v', 0)
    v_new = w['days'].get(str(T0 + 1), {}).get('v', 0)
    res.ok(v_old + v_new >= 13 * 60, 'no stopwatch time lost across midnight (%s + %s)' % (v_old, v_new))
    res.ok(v_old >= 13 * 60, 'a stopwatch session counts for the day it was started (%ss)' % v_old)
    a.check_errors('S2')
    a.close()

    # ============ S3: DST (New York, clocks go back on 1 Nov 2026) ============
    import datetime as _dt
    ny = _dt.timezone(_dt.timedelta(hours=-4))
    a = App(browser, res, tz='America/New_York', when=_dt.datetime(2026, 10, 31, 22, 0, tzinfo=ny))
    a.clear(); a.open(); onboard(a, focus=('health',)); a.dismiss_all()
    T0 = a.T()
    res.ok(a.has('Saturday, 31 October'), 'NY: Saturday 31 Oct')
    a.pg.clock.fast_forward('03:00:00'); a.wait(500)   # 01:00 EDT on 1 Nov
    res.eq(a.T(), T0 + 1, 'NY: Sunday after midnight')
    a.pg.clock.fast_forward('02:00:00'); a.wait(500)   # past the 02:00 -> 01:00 fall back
    res.eq(a.T(), T0 + 1, 'NY: still Sunday after the clocks go back')
    res.ok(a.has('Sunday, 1 November'), 'NY: date label after DST change')
    a.pg.clock.fast_forward('23:00:00'); a.wait(500)
    res.eq(a.T(), T0 + 2, 'NY: Monday')
    res.ok(a.has('Monday, 2 November'), 'NY: Monday label')
    a.check_errors('S3')
    a.close()

    # ============ S4: spring forward (Europe/London, 29 Mar 2026) and year end ============
    a = App(browser, res, tz='Europe/London', when=_dt.datetime(2026, 3, 28, 23, 30, tzinfo=_dt.timezone.utc))
    a.clear(); a.open(); onboard(a, focus=('health',)); a.dismiss_all()
    T0 = a.T()
    a.pg.clock.fast_forward('01:00:00'); a.wait(400)
    res.eq(a.T(), T0 + 1, 'London: Sunday 29 March')
    a.pg.clock.fast_forward('02:00:00'); a.wait(400)
    res.eq(a.T(), T0 + 1, 'London: same day after spring forward')
    res.ok(a.has('Sunday, 29 March'), 'London: label')
    a.check_errors('S4')
    a.close()

    a = App(browser, res, when=at(2026, 12, 31, 23, 58))
    a.clear(); a.open(); onboard(a, focus=('learn',)); a.dismiss_all()
    T0 = a.T()
    a.tap('Goals'); a.tap('+ New goal for a habit'); a.fill('#gtarget', '100'); a.tap('End of year', wait=100); a.tap('Add goal', wait=200)
    res.ok(a.has('31 Dec 2026 · due today'), 'end-of-year goal on 31 Dec: due today')
    a.pg.clock.fast_forward('00:05:00'); a.wait(600)
    res.eq(a.T(), T0 + 1, 'new year')
    a.tap('Goals')
    res.ok(a.has('31 Dec 2026 · overdue'), 'goal overdue after the year ends')
    a.tap('Today')
    res.ok(a.has('Friday, 1 January'), 'new year date label')
    a.check_errors('S4b')
    a.close()


if __name__ == '__main__':
    sys.exit(1 if run('days', main) else 0)
