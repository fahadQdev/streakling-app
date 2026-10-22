"""Settings, saving, backup/restore, start over, demo tools, broken saves, storage failures,
two tabs, offline (service worker), leaderboard actions and invites."""
import json
from harness import *

WHEN = at(2026, 10, 15, 10, 0)


def main(browser, res):
    a = App(browser, res, when=WHEN)
    a.clear(); a.open()
    onboard(a); a.dismiss_all()
    a.tap('Mark Sleep by 11 PM done', wait=250); a.dismiss_all()

    # ---------- Theme ----------
    a.go_settings()
    for th in ['Dark', 'System', 'Light']:
        a.tap(th, wait=150)
        res.eq(a.state()['settings']['theme'], th.lower(), 'theme ' + th)
    a.tap('Dark', wait=150)
    bg = a.pg.evaluate("() => getComputedStyle(document.querySelector('#app > div')).backgroundColor")
    res.eq(bg, 'rgb(15, 17, 21)', 'dark theme background')
    a.pg.emulate_media(color_scheme='dark'); a.tap('System', wait=150)
    bg = a.pg.evaluate("() => getComputedStyle(document.querySelector('#app > div')).backgroundColor")
    res.eq(bg, 'rgb(15, 17, 21)', 'system theme follows the phone (dark)')
    a.pg.emulate_media(color_scheme='light'); a.wait(200)
    a.tap('Light', wait=50); a.tap('System', wait=200)
    bg = a.pg.evaluate("() => getComputedStyle(document.querySelector('#app > div')).backgroundColor")
    res.eq(bg, 'rgb(244, 243, 239)', 'system theme follows the phone (light)')
    a.tap('Light')

    # ---------- Language ----------
    dirs = "[document.documentElement.lang, document.documentElement.dir, document.querySelector('#app > div').getAttribute('dir')]"
    res.eq(a.state()['settings'].get('lang'), 'en', 'English by default on an English phone')
    res.eq(a.pg.evaluate(dirs), ['en', 'ltr', 'ltr'], 'English page is left to right')
    res.eq(a.btn('العربية').get_attribute('lang'), 'ar', 'each language name is marked with its own language')
    a.tap('العربية', wait=300)
    res.eq(a.state()['settings']['lang'], 'ar', 'switch to Arabic')
    res.eq(a.pg.evaluate(dirs), ['ar', 'rtl', 'rtl'], 'Arabic page is right to left')
    res.ok(a.has('الإعدادات') and a.has('اللغة') and a.has('السمة'), 'Settings shown in Arabic')
    res.ok(not a.has('Theme') and not a.has('All reminders') and not a.has('Language'), 'no English labels left in Arabic')
    res.eq(a.btn('العربية').get_attribute('aria-pressed'), 'true', 'Arabic shown as chosen')
    a.save(); a.open(wait=600)
    res.eq(a.state()['settings']['lang'], 'ar', 'Arabic kept after a reload')
    res.eq(a.pg.evaluate(dirs), ['ar', 'rtl', 'rtl'], 'still right to left after a reload')
    res.ok(a.has('اليوم') and a.has('العادات'), 'Today in Arabic after a reload')
    import re as _re
    res.ok(not _re.search('[٠-٩۰-۹]', a.text()), 'numbers use Western digits in Arabic')
    a.set({'screen': 'settings'}); a.tap('English', wait=300)
    res.eq(a.state()['settings']['lang'], 'en', 'switch back to English')
    res.eq(a.pg.evaluate(dirs), ['en', 'ltr', 'ltr'], 'English is left to right again')
    res.ok(a.has('Theme') and a.has('Language') and a.has('All reminders'), 'Settings back in English')
    b = App(browser, res, when=WHEN, locale='ar-SA')
    b.clear(); b.open()
    res.eq(b.state()['settings'].get('lang'), 'ar', 'a phone set to Arabic starts in Arabic')
    res.eq(b.pg.evaluate(dirs), ['ar', 'rtl', 'rtl'], 'first run on an Arabic phone is right to left')
    b.check_errors('arabic phone'); b.close()

    # ---------- Switches ----------
    for name, key in [('All reminders', 'remindersOn'), ('Celebration pop-ups', 'celebrate'), ('Streak freezes', 'freezes'), ('Sounds', 'sounds'), ('Demo tools', 'demoTools')]:
        v0 = a.state()['settings'].get(key, True if key == 'sounds' else None)
        a.tap(name, wait=120)
        v1 = a.state()['settings'].get(key)
        res.eq(bool(v1), not bool(v0), 'switch ' + name)
        res.eq(a.btn(name).get_attribute('aria-pressed'), 'true' if v1 else 'false', 'switch state announced: ' + name)
        a.tap(name, wait=120)
    for lab, k in [('30 days', 30), ('Unlimited', 0), ('7 days', 7)]:
        a.tap(lab); res.eq(a.state()['settings']['editWindow'], k, 'edit window ' + lab)
    # reminders paused shows on habit page
    a.tap('All reminders')
    a.set({'screen': 'detail', 'sel': a.state()['habits'][0]['id'], 'from': 'today'})
    res.ok('(paused)' in a.text(), 'paused reminders shown on the habit page')
    a.tap('Back'); a.go_settings(); a.tap('All reminders')
    # celebration pop-ups off: no pop-ups, rewards still given
    a.tap('Celebration pop-ups')
    a.tap('Today')
    b0 = a.state()['bonus']
    a.tap('Log Drink water'); a.fill('#samount', '8'); a.tap('Save amount', wait=250)
    res.eq(a.state()['celebrate'], [], 'no pop-ups when switched off')
    hs = [h for h in a.state()['habits'] if h['name'] == 'Drink water'][0]
    res.ok(hs['badges'].get('first'), 'badge still earned with pop-ups off')
    a.go_settings(); a.tap('Celebration pop-ups')

    # ---------- Hide from leaderboards ----------
    a.tap('Hide me from leaderboards')
    res.ok(a.state()['league']['hidden'], 'hidden switch in Settings')
    a.tap('Leaderboard')
    res.ok('(you, hidden)' in a.text(), 'leaderboard marks you as hidden')
    a.go_settings(); a.tap('Hide me from leaderboards')

    # ---------- Leaderboard actions ----------
    a.tap('Leaderboard')
    a.pg.locator('button[aria-label^="1st"]').first.click(); a.wait(150)
    nm = a.state()['pcard']
    res.ok(nm and a.has('Cheer'), 'player card opens')
    a.btn('Cheer', exact=False).click(); a.wait(120)
    res.ok(a.has('Cheered!'), 'cheered')
    res.ok(a.pg.locator('button:has-text("Cheered!")').is_disabled(), 'one cheer per week per player')
    a.tap('Close', nth=1)
    res.eq(a.state()['pcard'], None, 'player card closes')
    me = a.pg.locator('button[aria-label*="(you)"]').first
    me.click(); a.wait(150)
    res.eq((a.state()['screen'], a.state()['ctab']), ('char', 'hero'), 'my own row opens my hero')
    a.tap('Leaderboard')
    a.pg.get_by_role('tab', name='Friends').click(); a.wait(120)
    res.eq(a.state()['ltab'], 'friends', 'friends tab')
    a.tap('Invite a friend', wait=400)
    clip = a.pg.evaluate("() => navigator.clipboard.readText()")
    res.ok('localhost' in clip and 'Streakling' in clip, 'invite copied (%s)' % clip[:60])
    res.ok(a.has('Invite copied'), 'invite confirmation')
    # share sheet path
    a.pg.evaluate("() => { window.__shared = null; navigator.share = d => { window.__shared = d; return Promise.resolve(); }; }")
    a.tap('Invite a friend', wait=300)
    shared = a.pg.evaluate("() => window.__shared")
    res.ok(shared and shared.get('url', '').startswith('http') and 'Fahad' in shared.get('text', ''), 'share sheet gets text and link (%s)' % shared)
    res.ok(a.has('Invite sent'), 'invite sent confirmation')
    a.pg.evaluate("() => { navigator.share = () => Promise.reject(Object.assign(new Error('x'), { name: 'AbortError' })); }")
    a.set({'inviteMsg': ''})
    a.tap('Invite a friend', wait=300)
    res.ok(not a.has('Invite sent') and not a.has('Invite copied'), 'cancelled share: no message')
    a.pg.get_by_role('tab', name='Hall of Fame').click(); a.wait(120)
    res.ok(a.has('Highest level') and a.has('Rarest gear'), 'hall of fame lists')
    a.check_errors('leaderboard')

    # ---------- Backup and restore ----------
    a.tap('Today')
    a.pg.get_by_role('tab', name=re.compile('^Tasks')).click(); a.wait(150)
    a.tap('New task'); a.fill('#tname', 'Pay rent'); a.tap('Add task', wait=200)
    a.tap('Mark task Pay rent done', wait=200)
    a.pg.get_by_role('tab', name='Habits').click(); a.wait(150)
    a.tap('Hide done', wait=150)
    saved_tasks = a.state()['tasks']
    a.go_settings()
    with a.pg.expect_download() as dl:
        a.tap('Download backup', wait=300)
    path = dl.value.path()
    env = json.load(open(path))
    res.ok(env['app'] == 'streakling' and env['state']['habits'], 'backup file is a Streakling backup')
    res.ok('exportedAt' in env, 'backup has a date')
    res.ok(a.has('Last backup: 15 Oct 2026'), 'last backup date shown')
    res.ok(a.has('Backup saved'), 'backup confirmation')
    res.ok('sheet' not in env['state'] and 'screen' not in env['state'], 'backup leaves out screen state')
    res.eq(env['state'].get('tasks'), saved_tasks, 'backup includes the tasks')
    res.ok(env['state']['settings'].get('hideDone') is True and env['state'].get('schema') == 15 and isinstance(env['state'].get('firstDay'), int), 'backup includes Hide done, schema and first day')
    res.ok(isinstance(env['state'].get('gems'), dict) and isinstance(env['state'].get('purchases'), list), 'backup includes diamonds and purchases')
    res.ok('ttab' not in env['state'] and 'taskSheet' not in env['state'], 'backup leaves out the Tasks screen state')
    saved_habits = env['state']['habits']
    # change data, then restore
    a.tap('Today'); a.tap('New habit'); a.fill('#hemoji', '🎯'); a.fill('#hname', 'After backup'); a.tap('Create habit', wait=200)
    res.ok(any(h['name'] == 'After backup' for h in a.state()['habits']), 'habit added after backup')
    a.set({'tasks': [], 'settings': dict(a.state()['settings'], hideDone=False)})
    a.go_settings()
    a.pg.locator('#restoreFile').set_input_files(path); a.wait(400)
    res.ok(a.has('Restoring replaces everything on this device'), 'restore asks first')
    res.ok(a.has('3 habits'), 'restore preview counts habits (%s)' % a.has('habits'))
    a.tap('Cancel', wait=150)
    res.ok(not a.has('Restoring replaces'), 'restore cancelled')
    res.ok(any(h['name'] == 'After backup' for h in a.state()['habits']), 'nothing replaced after cancel')
    a.pg.locator('#restoreFile').set_input_files(path); a.wait(400)
    a.tap('Replace my data', wait=1200)
    a.dismiss_all()
    res.ok(not any(h['name'] == 'After backup' for h in a.state()['habits']), 'restore replaced the data')
    res.eq([h['name'] for h in a.state()['habits']], [h['name'] for h in saved_habits], 'restored habits match the backup')
    res.eq(a.state()['tasks'], saved_tasks, 'restored tasks match the backup')
    res.eq(a.state()['settings']['hideDone'], True, 'restored Hide done choice')
    # bad files
    a.go_settings()
    import tempfile
    tmp = tempfile.mkdtemp()
    bad = os.path.join(tmp, 'bad.json'); open(bad, 'w').write('{"hello": 1}')
    a.pg.locator('#restoreFile').set_input_files(bad); a.wait(300)
    res.ok(a.has('That file is not a Streakling backup'), 'random JSON refused')
    notjson = os.path.join(tmp, 'bad.txt'); open(notjson, 'w').write('not json at all')
    a.pg.locator('#restoreFile').set_input_files(notjson); a.wait(300)
    res.ok(a.has('That file is not a Streakling backup'), 'non-JSON refused')
    a.check_errors('backup')

    # ---------- Demo tools ----------
    a.tap('Demo tools')
    a.tap('Load sample data')
    res.ok(a.has('Tap again to replace everything'), 'sample data asks twice')
    a.tap('Tap again to replace everything', wait=300)
    a.dismiss_all()
    res.eq(a.state()['char']['name'], 'Kai', 'sample data loaded')
    res.eq(a.state()['settings']['demoTools'], True, 'settings kept')
    a.tap('Simulate a 4-day break', wait=300)
    res.ok(a.has('Welcome back'), 'simulated break shows the comeback card')
    a.tap('Dismiss', wait=150)
    res.ok(not a.has('Welcome back'), 'dismissed for today')
    a.tap('Character')
    for b in ['+500 coins', '+1 level', "Reset today's trips", 'Catch 10 fish', 'Unlock streak items']:
        a.tap(b, wait=200); a.dismiss_all()
    res.ok(a.state()['demoBadges'], 'unlock streak items')
    res.ok(sum(x['caught'] for x in a.state()['book'].values()) >= 10, 'catch 10 fish')
    a.pg.locator('button').filter(has_text='Explore').first.click(); a.wait(100)
    a.js("c.setState({ trips: { day: c.T, adv: false, fish: false } });"); a.wait(80)
    a.js("c.setState(s => ({ habits: s.habits.map(h => c.withDay(h, c.T, h.type === 'quit' ? { clean: true } : { v: h.target })) }));"); a.wait(150); a.dismiss_all()
    a.pg.locator('button').filter(has_text=re.compile('^Send ')).first.click(); a.wait(200)
    res.ok(a.state()['adv']['demo'], 'demo trips are short')
    a.tap('Finish now (demo)', wait=300); a.dismiss_all()
    res.eq(a.state()['adv'], None, 'finish now')
    a.tap('Leaderboard'); a.tap('End the week now (demo)', wait=300)
    titles = a.dismiss_all()
    res.ok(titles, 'end week pop-up (%s)' % titles)
    a.go_settings(); a.tap('Demo tools')
    res.ok(not a.has('Load sample data'), 'demo tools hidden when off')
    a.tap('Character')
    res.ok(not a.has('+500 coins'), 'demo buttons hidden on the hero page')

    # ---------- Start over ----------
    a.go_settings(); a.tap('Start over')
    res.ok(a.has('Tap again to wipe everything'), 'start over asks twice')
    a.go_settings()
    res.ok(a.has('Start over') and not a.has('Tap again to wipe'), 'confirmation resets after leaving')
    a.tap('Start over'); a.tap('Tap again to wipe everything', wait=300)
    st = a.state()
    res.eq((st['screen'], st['habits'], st['char']), ('onboard', [], None), 'wiped: first-time setup')
    res.eq(st['starterBonus'], False, 'welcome gift available again after start over')
    a.save(); a.pg.reload(); a.wait(600)
    res.ok(a.has('Get started'), 'after reload: still first-time setup')
    onboard(a); a.dismiss_all()
    a.check_errors('start over')

    # ---------- Broken and old saves ----------
    b = App(browser, res, when=WHEN)
    b.clear()
    b.blank(); b.pg.evaluate("() => localStorage.setItem('streakling:v1', '{broken json')")
    b.open()
    res.ok(b.has('Get started'), 'broken save: starts fresh')
    keys = b.pg.evaluate("() => Object.keys(localStorage)")
    res.ok(any(k.startswith('streakling:v1:unreadable:') for k in keys), 'broken save kept aside (%s)' % keys)
    b.check_errors('broken save')
    # save from v0.10 (no starterBonus, no sounds setting, no inviteMsg)
    env2 = json.loads(json.dumps(env))
    env2['state'].pop('starterBonus', None); env2['state']['settings'].pop('sounds', None)
    b.put_env(env2); b.open()
    res.eq(b.state()['settings']['sounds'], True, 'old save: sounds on by default')
    res.eq(b.state()['starterBonus'], False, 'old save: welcome gift pending')
    b.check_errors('old save')
    # v0.12 saves: every hero owned both characters' starter outfit and hair. Only this hero's set stays, plus anything worn.
    old = json.loads(json.dumps(env))
    for k in ('schema', 'firstDay', 'tasks'): old['state'].pop(k, None)
    old['state']['settings'].pop('hideDone', None)
    old['state']['char'].pop('bg', None)
    old['state']['owned'] = ['c_vest', 'c_dress', 'hr_short', 'hr_long', 's_boots', 'r_bamboo', 'h_cap']
    old['state']['char'].update({'sex': 'boy', 'clothes': 'c_vest', 'hair': 'hr_short'})
    starts = [h['start'] for h in old['state']['habits']]
    old['state']['habits'][0]['start'] = min(starts) - 3
    b.put_env(old); b.open()
    st = b.state()
    res.eq(sorted(st['owned']), sorted(['c_vest', 'hr_short', 's_boots', 'r_bamboo', 'h_cap', 'bg_plain', 'hr_buzz', 'hr_side']), 'old boy save: girl starter outfit and hair removed, plain background and the free boy hairstyles added')
    res.eq(st['char'].get('eyes'), 'round', 'old save: hero without eyes keeps the round ones')
    res.eq((st['schema'], st['char']['bg'], st['tasks'], st['settings']['hideDone']), (15, 'bg_plain', [], False), 'old save: new fields get their defaults')
    res.eq(st['firstDay'], min(starts) - 3, 'old save: first day comes from the oldest habit')
    b.set({'screen': 'char', 'ctab': 'store', 'cat': 'clothes'})
    res.ok('Coral Dress' in b.js("return c.renderVals().store.map(x => x.name);"), 'the removed outfit is back in the Store')
    b.check_errors('migrate boy')
    old2 = json.loads(json.dumps(old))
    old2['state']['char'].update({'sex': 'girl', 'clothes': 'c_vest', 'hair': 'hr_long'})
    b.put_env(old2); b.open()
    res.eq(sorted(b.state()['owned']), sorted(['c_vest', 'c_dress', 'hr_long', 's_boots', 'r_bamboo', 'h_cap', 'bg_plain', 'hr_bob', 'hr_pony']), 'old girl save wearing the boy vest: the vest stays, the boy hair goes, the free girl hairstyles are added')
    res.eq(b.state()['char']['clothes'], 'c_vest', 'still wearing the vest')
    b.check_errors('migrate girl')
    # A v0.13 save is not migrated again: a boy who bought the girl outfit keeps it.
    new = json.loads(json.dumps(env))
    new['state']['owned'] = new['state']['owned'] + ['c_dress']
    b.put_env(new); b.open()
    res.ok('c_dress' in b.state()['owned'], 'bought starter items are kept in v0.13 saves')
    # Damaged task list and background in a save
    bad2 = json.loads(json.dumps(env))
    bad2['state']['tasks'] = [None, 'x', {'name': ''}, {'name': 'No day', 'day': 'soon'}, {'name': '  Fine  ', 'day': 30, 'done': True, 'doneDay': 30, 'paid': True},
                              {'id': 'dup', 'name': 'A', 'day': 31}, {'id': 'dup', 'name': 'B', 'day': 32, 'done': 'yes'}]
    bad2['state']['char']['bg'] = 'bg_nowhere'
    bad2['state']['char']['eyes'] = 'laser'
    bad2['state']['firstDay'] = 'yesterday'
    b.put_env(bad2); b.open()
    st = b.state()
    res.eq([(x['name'], x['day'], x['done'], x['paid']) for x in st['tasks']], [('Fine', 30, True, True), ('A', 31, False, False), ('B', 32, False, False)], 'bad tasks dropped, good ones kept')
    res.eq(len(set(x['id'] for x in st['tasks'])), 3, 'task ids made unique')
    res.eq(st['char']['bg'], 'bg_plain', 'unknown background falls back to Plain')
    res.eq(st['char']['eyes'], 'round', 'unknown eyes fall back to round')
    res.ok(isinstance(st['firstDay'], int), 'bad first day replaced')
    b.pg.get_by_role('tab', name=re.compile('^Tasks')).click(); b.wait(150)
    b.tap('Stats')
    b.check_errors('damaged v0.13 save')
    bad3 = json.loads(json.dumps(env)); bad3['state']['tasks'] = 'not a list'
    b.put_env(bad3); b.open()
    res.eq(b.state()['tasks'], [], 'tasks that are not a list become an empty list')
    b.check_errors('tasks not a list')
    # unfinished onboarding resumes
    b.clear(); b.open(); b.tap('Get started'); b.fill('#obname', 'Resume'); b.tap('Create my hero')
    b.save(); b.pg.reload(); b.wait(600)
    res.eq((b.state()['screen'], b.state()['onboard']['step']), ('onboard', 2), 'unfinished setup resumes at the same step')
    b.close()

    # ---------- Storage failures ----------
    c = App(browser, res, when=WHEN)
    c.clear(); c.open(); onboard(c); c.dismiss_all()
    c.pg.evaluate("() => { const orig = Storage.prototype.setItem; window.__origSet = orig; Storage.prototype.setItem = function () { throw new DOMException('full', 'QuotaExceededError'); }; }")
    c.tap('Mark Sleep by 11 PM done', wait=900); c.dismiss_all()
    res.ok(c.state()['saveFail'], 'save failure detected')
    res.ok(c.has('could not be saved on this device'), 'save failure banner')
    c.pg.evaluate("() => { Storage.prototype.setItem = window.__origSet; }")
    c.tap('Mark Sleep by 11 PM done', wait=900); c.dismiss_all()
    res.ok(not c.state()['saveFail'], 'banner clears when saving works again')
    c.check_errors('storage failure')
    # localStorage completely blocked (some private modes)
    d = App(browser, res, when=WHEN)
    d.clear()
    d.ctx.add_init_script("Object.defineProperty(window, 'localStorage', { get() { throw new DOMException('denied', 'SecurityError'); } });")
    d.open()
    res.ok(d.has('Get started'), 'app opens when storage is blocked')
    d.check_errors('blocked storage')
    d.close()

    # ---------- Two tabs ----------
    e1 = App(browser, res, when=WHEN)
    e1.clear(); e1.open(); onboard(e1); e1.dismiss_all(); e1.save()
    e2pg = e1.ctx.new_page(); e2pg.goto(URL); e2pg.wait_for_timeout(700)
    e1.tap('Mark Sleep by 11 PM done', wait=900); e1.dismiss_all(); e1.save()
    e2pg.wait_for_timeout(1500)
    v = e2pg.evaluate("() => { const c = " + INST + "; const h = c.state.habits.find(x => x.name === 'Sleep by 11 PM'); return (h.days[c.T] || {}).v; }")
    res.eq(v, 1, 'a second tab reloads with the change')
    e1.check_errors('two tabs')
    e1.close(); c.close()

    # ---------- Offline (service worker) ----------
    f = App(browser, res, when=WHEN)
    f.clear(); f.open(1500)
    f.pg.wait_for_function("() => navigator.serviceWorker && navigator.serviceWorker.controller", timeout=10000)
    f.pg.reload(); f.wait(800)
    cached = f.pg.evaluate("async () => (await caches.keys())")
    res.ok(any(k.startswith('streakling-') for k in cached), 'service worker cache (%s)' % cached)
    f.ctx.set_offline(True)
    f.pg.reload(); f.wait(1500)
    res.ok(f.has('Get started') or f.has('Today'), 'app opens offline')
    f.ctx.set_offline(False)
    f.check_errors('offline')
    f.close()


if __name__ == '__main__':
    sys.exit(1 if run('settings', main) else 0)
