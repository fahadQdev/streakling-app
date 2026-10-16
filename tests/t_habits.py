"""Habit flows through the real UI: create (every type and option), validation, edit, logging, timer,
skip, quit, reasons, past days, edit window, archive, delete, reorder."""
from harness import *

WHEN = at(2026, 10, 15, 9, 0)  # Thursday morning


def H(a, name):
    return next((h for h in a.state()['habits'] if h['name'] == name), None)


def form_type(a, label):
    a.pg.locator('button').filter(has_text=re.compile('^' + label)).first.click(); a.wait(80)


def new_habit(a, emoji, name, typ='Yes / No', target=None, unit=None, th=None, tm=None, minv=None, part=None,
              freq=None, days=None, perweek=None, rem=None, goal=None, save=True):
    a.tap('New habit')
    if emoji is not None:
        a.fill('#hemoji', emoji)
    a.fill('#hname', name)
    form_type(a, typ)
    if target is not None: a.fill('#htarget', str(target))
    if unit is not None: a.fill('#hunit', unit)
    if th is not None: a.pg.get_by_label('Target hours').fill(str(th)); a.wait(60)
    if tm is not None: a.pg.get_by_label('Target minutes').fill(str(tm)); a.wait(60)
    if minv is not None: a.fill('#hmin', str(minv))
    if part: a.tap(part)
    if freq: a.tap(freq)
    if days is not None:
        for d in ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']:
            b = a.pg.get_by_role('button', name=d, exact=True)
            on = b.get_attribute('aria-pressed') == 'true'
            if on != (d in days): b.click(); a.wait(40)
    if perweek is not None:
        cur = a.state()['form']['perweek']
        while cur < perweek: a.tap('More times', wait=40); cur += 1
        while cur > perweek: a.tap('Fewer times', wait=40); cur -= 1
    if rem == 'off':
        a.tap('Reminder on or off')
    elif rem:
        h, m, ap = rem
        a.pg.get_by_label('Hour', exact=True).select_option(str(h)); a.wait(40)
        a.pg.get_by_label('Minute', exact=True).select_option(str(m)); a.wait(40)
        a.tap(ap)
    if goal:
        a.tap('Link a goal')
        if goal.get('title'): a.pg.get_by_label('Goal name').fill(goal['title'])
        if goal.get('target'): a.pg.get_by_label('Goal target').fill(str(goal['target']))
        if goal.get('deadline'): a.tap(goal['deadline'])
        if goal.get('date'): a.pg.locator('#fdate').fill(goal['date'])
        a.wait(60)
    if save:
        a.tap('Create habit', wait=250)


def main(browser, res):
    a = App(browser, res, when=WHEN)
    a.clear(); a.open()
    onboard(a, focus=('health',), picks=['health:1'])  # just "Sleep by 11 PM"
    a.dismiss_all()
    T = a.T()
    res.eq([h['name'] for h in a.state()['habits']], ['Sleep by 11 PM'], 'onboarding created the picked habit')

    # ---------- Validation ----------
    a.tap('New habit'); a.tap('Create habit')
    res.ok(a.has('Choose an emoji'), 'error: emoji required')
    a.fill('#hemoji', 'hello')
    res.ok(a.has('Emoji only'), 'error: letters rejected in emoji field')
    res.eq(a.state()['form']['emoji'], '', 'letters not stored as emoji')
    a.fill('#hemoji', '🇸🇦')
    res.eq(a.state()['form']['emoji'], '🇸🇦', 'flag emoji accepted')
    a.fill('#hemoji', '👨‍👩‍👧')
    res.eq(a.state()['form']['emoji'], '👨‍👩‍👧', 'family (ZWJ) emoji kept whole')
    a.fill('#hemoji', '😀🎸')
    res.eq(a.state()['form']['emoji'], '🎸', 'two emojis: the last one is kept')
    a.fill('#hemoji', '1️⃣')
    res.eq(a.state()['form']['emoji'], '1️⃣', 'keycap emoji accepted')
    a.tap('Create habit')
    res.ok(a.has('Give the habit a name'), 'error: name required')
    a.fill('#hname', '   ')
    a.tap('Create habit')
    res.ok(a.has('Give the habit a name'), 'error: blank name rejected')
    a.fill('#hname', 'x' * 60)
    res.eq(len(a.state()['form']['name']), 40, 'name capped at 40 characters')
    a.tap('Specific days')
    for d in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
        a.pg.get_by_role('button', name=d, exact=True).click(); a.wait(30)
    a.tap('Create habit')
    res.ok(a.has('Pick at least one day'), 'error: no days picked')
    a.tap('Daily')
    form_type(a, 'Amount')
    a.tap('Create habit')
    res.ok(a.has('Enter a daily target'), 'error: amount target required')
    a.fill('#htarget', '0'); a.tap('Create habit')
    res.ok(a.has('Enter a daily target'), 'error: amount target 0 rejected')
    a.fill('#htarget', '12abc3')
    res.eq(a.state()['form']['target'], '123', 'non-digits stripped from target')
    a.fill('#htarget', '10'); a.fill('#hmin', '10'); a.tap('Create habit')
    res.ok(a.has('minimum must be lower'), 'error: minimum >= target')
    a.fill('#hmin', '')
    form_type(a, 'Time')
    a.pg.get_by_label('Target hours').fill('0'); a.pg.get_by_label('Target minutes').fill('0'); a.wait(60)
    a.tap('Create habit')
    res.ok(a.has('Set a daily target time'), 'error: time target 0')
    a.pg.get_by_label('Target hours').fill('25'); a.wait(60); a.tap('Create habit')
    res.ok(a.has('24 hours at most'), 'error: time target over 24h')
    a.pg.get_by_label('Target hours').fill('1'); a.pg.get_by_label('Target minutes').fill('0'); a.wait(60)
    a.fill('#hmin', '60'); a.tap('Create habit')
    res.ok(a.has('minimum must be lower'), 'error: time minimum >= target')
    a.fill('#hmin', '')
    a.tap('Link a goal'); a.tap('Create habit')
    res.ok(a.has('Enter a target for the goal'), 'error: goal target required')
    a.pg.get_by_label('Goal target').fill('10'); a.tap('Pick a date'); a.tap('Create habit')
    res.ok(a.has('Pick a date from the calendar for the goal'), 'error: goal date required')
    a.pg.locator('#fdate').fill('2026-10-15'); a.wait(60); a.tap('Create habit')
    res.ok(a.has('Pick a goal date after today'), 'error: goal date must be after today')
    a.tap('Close')
    res.eq(a.state()['screen'], 'today', 'closing the form goes back to Today')
    res.eq(len(a.state()['habits']), 1, 'nothing created by failed attempts')

    # ---------- Create every type ----------
    new_habit(a, '💧', 'Water', 'Amount', target=8, unit='glasses', minv=4, part='Morning', rem=(7, 30, 'AM'),
              goal={'title': '200 glasses', 'target': 200, 'deadline': 'End of month'})
    w = H(a, 'Water')
    res.ok(w is not None, 'amount habit created')
    if w:
        res.eq((w['type'], w['target'], w['min'], w['unit'], w['part'], w['step']), ('amount', 8, 4, 'glasses', 'morning', 1), 'amount habit fields')
        res.eq(w['remind'], {'on': True, 'h': 7, 'm': 30, 'ap': 'AM'}, 'reminder saved')
        res.eq(w['start'], T, 'habit starts today')
        g = [g for g in a.state()['goals'] if g['hid'] == w['id']]
        res.ok(len(g) == 1 and g[0]['target'] == 200 and g[0]['deadline'] == 'month' and g[0]['date'] == '2026-10-31', 'linked goal saved with end of month')
    res.eq(a.state()['screen'], 'today', 'after create: Today')
    new_habit(a, '📚', 'Study', 'Time', th=1, tm=30, minv=20, part='Afternoon', freq='Specific days', days=['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday'], rem='off')
    s = H(a, 'Study')
    if res.ok(s is not None, 'time habit created'):
        res.eq((s['type'], s['target'], s['min'], s['freq']['kind'], s['freq']['days'], s['remind']['on']), ('time', 5400, 1200, 'days', [0, 1, 2, 3, 4], False), 'time habit fields')
    new_habit(a, '🏃', 'Run', 'Yes / No', part='Evening', freq='Times per week', perweek=3)
    r = H(a, 'Run')
    if res.ok(r is not None, 'check habit created'):
        res.eq((r['type'], r['freq']['kind'], r['freq']['n']), ('check', 'perweek', 3), 'perweek habit fields')
    new_habit(a, '🚭', 'No smoking', 'Quit', part='Anytime')
    q = H(a, 'No smoking')
    if res.ok(q is not None, 'quit habit created'):
        res.eq((q['type'], q['freq']['kind']), ('quit', 'daily'), 'quit habit is daily')
    new_habit(a, '📖', 'Read', 'Amount', target=30, unit='pages', goal={'target': 500, 'deadline': 'Pick a date', 'date': '2027-01-31'})
    rd = H(a, 'Read')
    if rd:
        res.eq(rd['step'], 5, 'target over 10 uses steps of 5')
        g = [g for g in a.state()['goals'] if g['hid'] == rd['id']]
        res.ok(len(g) == 1 and g[0]['date'] == '2027-01-31', 'goal with picked date')
    new_habit(a, '🧘', 'Days all', 'Yes / No', freq='Specific days', days=['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'])
    da = H(a, 'Days all')
    if da: res.eq(da['freq']['kind'], 'daily', 'all 7 days saved as daily')
    new_habit(a, '🎸', 'Unitless', 'Amount', target=5, unit='   ')
    un = H(a, 'Unitless')
    if un: res.eq(un['unit'], 'units', 'empty unit becomes "units"')
    ids = [h['id'] for h in a.state()['habits']]
    res.eq(len(ids), len(set(ids)), 'habit ids are unique')
    gids = [g['id'] for g in a.state()['goals']]
    res.eq(len(gids), len(set(gids)), 'goal ids are unique')
    a.scan('today-many')
    txt = a.text()
    for grp in ['MORNING', 'AFTERNOON', 'EVENING', 'ANYTIME']:
        res.ok(grp in txt, 'Today shows group ' + grp)
    a.check_errors('create')

    # ---------- Logging ----------
    # check habit
    a.tap('Mark Sleep by 11 PM done', wait=300)
    a.dismiss_all()
    sl = H(a, 'Sleep by 11 PM')
    res.eq(sl['days'].get(str(T), {}).get('v'), 1, 'check: marked done')
    a.tap('Mark Sleep by 11 PM done', wait=250); a.dismiss_all()
    res.eq(H(a, 'Sleep by 11 PM')['days'].get(str(T), {}).get('v'), 0, 'check: tapping again un-marks')
    # amount via + button
    a.tap('Add 1 glass to Water', wait=200); a.dismiss_all()
    a.tap('Add 1 glass to Water', wait=200); a.dismiss_all()
    res.eq(H(a, 'Water')['days'].get(str(T), {}).get('v'), 2, 'amount: + adds the step')
    # amount sheet: type a value
    a.tap('Log Water')
    res.ok(a.has('Target 8'), 'amount sheet shows target')
    a.fill('#samount', '5'); a.tap('Save amount', wait=250); a.dismiss_all()
    res.eq(H(a, 'Water')['days'].get(str(T), {}).get('v'), 5, 'amount sheet saves typed value')
    a.tap('Log Water'); a.tap('Decrease'); a.tap('Decrease'); a.tap('Save amount', wait=250); a.dismiss_all()
    res.eq(H(a, 'Water')['days'].get(str(T), {}).get('v'), 3, 'amount sheet −/− then save')
    a.tap('Log Water'); a.fill('#samount', '0'); a.tap('Decrease'); a.tap('Save amount', wait=250)
    res.eq(H(a, 'Water')['days'].get(str(T), {}).get('v'), 0, 'amount never below 0')
    a.tap('Log Water'); a.fill('#samount', '4'); a.tap('Save amount', wait=250); a.dismiss_all()
    res.ok('minimum' in a.text(), 'amount at minimum shows "minimum"')
    a.tap('Log Water'); a.tap('Close', nth=1)
    res.eq(a.state()['sheet'], None, 'sheet closes with X')
    # time habit: typed time
    a.tap('Log time for Study: type it or start the timer')
    a.pg.get_by_label('Hours', exact=True).fill('1'); a.pg.get_by_label('Minutes', exact=True).fill('5'); a.wait(60)
    a.tap('Save time', wait=250); a.dismiss_all()
    res.eq(H(a, 'Study')['days'].get(str(T), {}).get('v'), 3900, 'time: typed 1h 5m saved')
    a.tap('Log time for Study: type it or start the timer')
    a.pg.get_by_label('Minutes', exact=True).fill('90'); a.wait(60)
    a.tap('Save time', wait=250); a.dismiss_all()
    res.eq(H(a, 'Study')['days'].get(str(T), {}).get('v'), 9000, 'time: 1h + 90 min = 2h30m')
    a.tap('Log time for Study: type it or start the timer')
    a.pg.get_by_label('Hours', exact=True).fill('24'); a.pg.get_by_label('Minutes', exact=True).fill('1'); a.wait(60)
    a.tap('Save time')
    res.ok(a.has('24 hours at most'), 'time: over 24h rejected')
    a.pg.get_by_label('Hours', exact=True).fill('0'); a.pg.get_by_label('Minutes', exact=True).fill('0'); a.wait(60)
    a.tap('Save time', wait=250)
    res.eq(H(a, 'Study')['days'].get(str(T), {}).get('v'), 0, 'time: cleared to 0')
    # stopwatch with a controlled clock
    a.tap('Log time for Study: type it or start the timer')
    a.tap('Start timer')
    a.pg.clock.run_for(65 * 1000); a.wait(300)
    v = H(a, 'Study')['days'].get(str(T), {}).get('v', 0)
    res.ok(64 <= v <= 66, 'stopwatch adds time while running (%s s)' % v)
    res.ok(a.has('Pause'), 'stopwatch shows Pause while running')
    a.tap('Pause'); t1 = H(a, 'Study')['days'].get(str(T), {}).get('v', 0)
    a.pg.clock.run_for(30 * 1000); a.wait(200)
    res.eq(H(a, 'Study')['days'].get(str(T), {}).get('v', 0), t1, 'paused stopwatch adds nothing')
    res.ok(a.has('Resume'), 'paused shows Resume')
    a.tap('Resume'); a.pg.clock.run_for(10 * 1000); a.wait(200)
    t2 = H(a, 'Study')['days'].get(str(T), {}).get('v', 0)
    res.ok(t1 + 9 <= t2 <= t1 + 11, 'resume continues (%s → %s)' % (t1, t2))
    # close the sheet while running: time keeps counting
    a.tap('Close', nth=1)
    a.pg.clock.run_for(20 * 1000); a.wait(200)
    t3 = H(a, 'Study')['days'].get(str(T), {}).get('v', 0)
    res.ok(t3 >= t2 + 19, 'timer keeps running with the sheet closed (%s → %s)' % (t2, t3))
    res.ok('timing' in a.text(), 'Today card shows the running timer')
    # app reload while running: timer survives
    a.save(); a.pg.reload(); a.wait(600)
    a.pg.clock.run_for(5000); a.wait(200)
    t4 = H(a, 'Study')['days'].get(str(T), {}).get('v', 0)
    res.ok(t4 >= t3 + 4, 'timer survives a reload (%s → %s)' % (t3, t4))
    a.dismiss_all()
    a.btn('Study timer is running', exact=False).click(); a.wait(200)
    a.tap('Stop', wait=200)
    res.eq(a.state()['timer'], None, 'Stop ends the timer')
    t5 = H(a, 'Study')['days'].get(str(T), {}).get('v', 0)
    a.pg.clock.run_for(10000); a.wait(200)
    res.eq(H(a, 'Study')['days'].get(str(T), {}).get('v', 0), t5, 'stopped timer adds nothing')
    # typing while the timer runs: time continues from the typed value
    a.tap('Start timer'); a.pg.clock.run_for(3000); a.wait(100)
    a.pg.get_by_label('Hours', exact=True).fill('1'); a.pg.get_by_label('Minutes', exact=True).fill('0'); a.wait(60)
    a.tap('Save time', wait=200)
    a.pg.clock.run_for(10000); a.wait(200)
    v = H(a, 'Study')['days'].get(str(T), {}).get('v', 0)
    res.ok(3609 <= v <= 3612, 'typed time while running, then it continues from there (%s)' % v)
    a.btn('Study timer is running', exact=False).click(); a.wait(150); a.tap('Stop'); a.tap('Close', nth=1)
    # typing in a form while a timer runs: text must not be wiped by the ticking
    a.btn('Log time for Study', exact=False).click(); a.wait(150); a.tap('Start timer'); a.tap('Close', nth=1)
    a.tap('New habit')
    a.pg.locator('#hname').click(); a.pg.keyboard.type('Typing while ticking', delay=60)
    a.pg.clock.run_for(3000); a.wait(300)
    res.eq(a.pg.locator('#hname').input_value(), 'Typing while ticking', 'form text survives timer re-renders')
    a.tap('Close'); a.btn('Study timer is running', exact=False).click(); a.wait(150); a.tap('Stop'); a.tap('Close', nth=1)
    a.dismiss_all()
    # quit habit
    a.tap('Mark No smoking clean today', wait=250); a.dismiss_all()
    res.eq(H(a, 'No smoking')['days'].get(str(T), {}).get('clean'), True, 'quit: clean today')
    a.tap('Undo clean day for No smoking', wait=250)
    res.ok(not H(a, 'No smoking')['days'].get(str(T), {}).get('clean'), 'quit: undo clean')
    a.tap('Log No smoking'); a.tap('Slipped', wait=250)
    d = H(a, 'No smoking')['days'].get(str(T), {})
    res.ok(d.get('slip') and not d.get('clean'), 'quit: slipped via sheet')
    res.ok('WHAT MADE YOU SLIP?' in a.text(), 'slip asks for a reason')
    a.tap('Tired'); res.eq(H(a, 'No smoking')['days'][str(T)].get('reason'), 'Tired', 'reason saved')
    a.tap('Tired'); res.eq(H(a, 'No smoking')['days'][str(T)].get('reason'), '', 'tapping the reason again clears it')
    a.tap('Close', nth=1)
    a.tap('Undo slip', wait=250)
    res.ok(not H(a, 'No smoking')['days'][str(T)].get('slip'), 'Undo slip from the card')
    # skip
    a.tap('Log Read'); a.tap('Skip this day (keeps streak)', wait=200)
    res.eq(H(a, 'Read')['days'].get(str(T), {}).get('skip'), True, 'skip saved')
    res.ok(a.has('Undo skip'), 'sheet offers Undo skip')
    a.tap('Undo skip', wait=200)
    res.ok(not H(a, 'Read')['days'].get(str(T), {}).get('skip'), 'undo skip')
    a.tap('Skip this day (keeps streak)', wait=200); a.tap('Close', nth=1)
    res.ok('Skipped' in a.text(), 'card shows Skipped')
    a.tap('Add 5 pages to Read', wait=250); a.dismiss_all()
    d = H(a, 'Read')['days'].get(str(T), {})
    res.ok(d.get('v') == 5 and not d.get('skip'), 'logging an amount clears the skip')
    a.check_errors('logging')

    # ---------- Past days and the edit window ----------
    a.set({'day': T - 1})
    res.ok('Fixing a past day' in a.text() or 'No habits on this day' in a.text(), 'past day banner')
    res.ok(a.has('No habits on this day yet'), 'habits created today are not on yesterday')
    # make the habits older so past days have them
    a.js("c.setState(s => ({ habits: s.habits.map(h => Object.assign({}, h, { start: c.T - 40 })) }));")
    a.wait(150)
    a.set({'day': T - 1})
    a.tap('Mark Sleep by 11 PM done', wait=250); a.dismiss_all()
    res.eq(H(a, 'Sleep by 11 PM')['days'].get(str(T - 1), {}).get('v'), 1, 'past day: check marked')
    st = a.state()
    res.ok(a.js("return c.coinsOf(c.state);") == a.js("return c.coinsOf(c.state);"), 'coins readable')
    a.set({'day': T - 8})
    res.ok(a.has('Locked. Only the last 7 days'), 'day 8 back is locked with 7-day window')
    res.ok(a.pg.get_by_role('button', name='Mark Sleep by 11 PM done').is_disabled(), 'locked day: buttons disabled')
    a.set({'settings': dict(a.state()['settings'], editWindow=30)}); a.set({'day': T - 8})
    res.ok(not a.has('Locked.'), '30-day window unlocks day 8')
    a.set({'settings': dict(a.state()['settings'], editWindow=0)}); a.set({'day': T - 28})
    res.ok(not a.has('Locked.'), 'unlimited window unlocks 4 weeks back')
    a.set({'settings': dict(a.state()['settings'], editWindow=7)})
    # week strip navigation
    a.tap('Back to today', wait=150)
    res.eq(a.state()['day'], T, 'Back to today')
    res.ok(a.pg.get_by_role('button', name='Next week').is_disabled(), 'next week disabled on this week')
    for i in range(4):
        a.tap('Previous week', wait=100)
    res.ok(a.pg.get_by_role('button', name='Previous week').is_disabled(), 'previous week stops after 4 weeks')
    for i in range(4):
        a.tap('Next week', wait=100)
    res.ok(a.state()['day'] <= T, 'next week never goes past today (day %s, T %s)' % (a.state()['day'], T))
    a.set({'day': T})
    res.ok(a.pg.locator('button[aria-label^="Upcoming"]').first.is_disabled(), 'future days in the strip are disabled')

    # ---------- Edit ----------
    a.tap('Log Read'); a.tap('Stats, badges, edit, archive')
    res.eq(a.state()['screen'], 'detail', 'sheet link opens the habit page')
    a.tap('Edit habit')
    res.eq(a.pg.locator('#hname').input_value(), 'Read', 'edit form prefilled with the name')
    res.eq(a.pg.locator('#htarget').input_value(), '30', 'edit form prefilled with the target')
    res.ok(a.pg.locator('button').filter(has_text=re.compile('^Time')).first.is_disabled(), 'type locked when editing')
    a.fill('#hname', 'Read books'); a.fill('#htarget', '40')
    a.tap('Save changes', wait=250)
    rd = H(a, 'Read books')
    res.ok(rd is not None and rd['target'] == 40, 'edit saved')
    res.ok(rd and rd['past'] and rd['past'][-1]['until'] == T - 1 and rd['past'][-1]['target'] == 30, 'target change keeps the old target for past days')
    res.eq(a.state()['screen'], 'detail', 'after edit: back on the habit page')
    a.tap('Edit habit'); a.fill('#hemoji', '📕'); a.tap('Save changes', wait=200)
    rd2 = H(a, 'Read books')
    res.eq(len(rd2['past']), len(rd['past']), 'emoji-only edit does not add a history version')
    res.eq(rd2['emoji'], '📕', 'emoji edited')
    a.tap('Edit habit'); a.tap('Close', wait=150)
    res.eq(a.state()['screen'], 'detail', 'closing edit returns to the habit page')
    a.tap('Back', wait=150)

    # ---------- Archive / restore / delete ----------
    a.set({'screen': 'detail', 'sel': H(a, 'Run')['id'], 'from': 'today'})
    a.tap('Archive habit (pause, keep history)', wait=200)
    res.ok(H(a, 'Run')['archived'], 'archived')
    res.ok(a.has('Archived. Hidden from Today'), 'archived banner')
    a.tap('Back'); a.tap('Today')
    res.ok('Run' not in [x.strip() for x in a.text().split('\n')], 'archived habit hidden from Today')
    a.tap('Settings'); res.ok(a.has('Archived habits'), 'settings shows archived link')
    a.btn('Archived habits', exact=False).click(); a.wait(150)
    res.ok(a.has('Run'), 'archived list shows the habit')
    a.tap('Restore', wait=200)
    res.ok(not H(a, 'Run')['archived'], 'restored from archived list')
    res.ok(a.has('Nothing archived'), 'archived list empty after restore')
    a.tap('Back')
    a.tap('Today')
    a.set({'screen': 'detail', 'sel': H(a, 'Unitless')['id'], 'from': 'today'})
    a.tap('Delete habit')
    res.ok(a.has('Tap again to delete for good'), 'delete asks for a second tap')
    res.ok(H(a, 'Unitless') is not None, 'not deleted after one tap')
    a.btn('Tap again to delete for good', exact=False).click(); a.wait(200)
    res.ok(H(a, 'Unitless') is None, 'deleted after second tap')
    res.eq(a.state()['screen'], 'today', 'after delete: Today')
    # delete removes linked goals
    wid = H(a, 'Water')['id']
    a.set({'screen': 'detail', 'sel': wid, 'from': 'today'}); a.tap('Edit habit'); a.tap('Delete habit')
    a.btn('Tap again to delete for good', exact=False).click(); a.wait(200)
    res.ok(not [g for g in a.state()['goals'] if g['hid'] == wid], 'deleting a habit removes its goals')
    # delete confirm resets when leaving
    a.set({'screen': 'detail', 'sel': H(a, 'Study')['id'], 'from': 'today'}); a.tap('Delete habit'); a.tap('Back')
    a.set({'screen': 'detail', 'sel': H(a, 'Study')['id'], 'from': 'today'})
    res.ok(a.has('Delete habit') and not a.has('Tap again to delete'), 'delete confirmation resets after leaving')
    a.tap('Back')

    # ---------- Reorder ----------
    order0 = [h['name'] for h in a.state()['habits']]
    a.tap('Reorder')
    evening = [h['name'] for h in a.state()['habits'] if h['part'] == 'evening' and not h['archived']]
    res.ok(len(evening) >= 2, 'two evening habits to reorder: %s' % evening)
    if len(evening) >= 2:
        a.tap('Move %s down' % evening[0], wait=150)
        ev2 = [h['name'] for h in a.state()['habits'] if h['part'] == 'evening' and not h['archived']]
        res.eq(ev2[:2], [evening[1], evening[0]], 'moved down within its group')
        res.ok(a.pg.get_by_role('button', name='Move %s up' % evening[1]).is_disabled(), 'first in group: up disabled')
    a.tap('Done')
    res.ok(not a.state()['reorder'], 'reorder mode off')
    a.scan('today-end')
    a.check_errors('habits end')


if __name__ == '__main__':
    sys.exit(1 if run('habits', main) else 0)
