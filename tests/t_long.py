"""Stress test with the longest allowed texts (and Arabic) on every screen, at 320 and 390 px."""
from harness import *
from tour import states, reset_to, WHEN

LONG = 'Meditate every morning before work start'[:40]
AR = 'قراءة القرآن الكريم يومياً بعد صلاة الفجر'[:40]
UNIT = 'minutes of practice x'[:20]
HERO = 'WWWWWWWWWWWWWW'
TASK = 'Call the insurance company about the claim for the car repairs'[:60]
TASK_AR = 'الاتصال بشركة التأمين بخصوص مطالبة إصلاح السيارة قبل نهاية الأسبوع'[:60]


def main(browser, res):
    runs = [(w, h, theme, 'en') for w, h in [(320, 568), (390, 844)] for theme in ['light', 'dark']]
    runs += [(320, 568, 'light', 'ar'), (320, 568, 'dark', 'ar'), (360, 740, 'light', 'ar')]
    for w, h, theme, lang in runs:
        if True:
            tag = '' if lang == 'en' else '-ar'
            a = App(browser, res, width=w, height=h, when=WHEN, label='long-%d-%s%s:' % (w, theme, tag))
            a.clear(); a.open(); demo(a)
            a.js("""c.setState(s => ({
              char: Object.assign({}, s.char, { name: arg.hero }),
              habits: s.habits.map(h => h.id === 'read' ? Object.assign({}, h, { name: arg.long, unit: arg.unit, target: 999999 }) : (h.id === 'quran' ? Object.assign({}, h, { name: arg.ar }) : h)),
              goals: s.goals.map(g => Object.assign({}, g, { title: g.id === 'g1' ? 'A very long goal title that takes all sixty characters here' : g.title, target: g.id === 'g1' ? 9999999 : g.target })),
              tasks: s.tasks.map((t, i) => Object.assign({}, t, { name: i % 2 ? arg.task : arg.tar })),
              settings: Object.assign({}, s.settings, { theme: arg.theme }) }));""", {'hero': HERO, 'long': LONG, 'ar': AR, 'unit': UNIT, 'theme': theme, 'task': TASK, 'tar': TASK_AR})
            # Arabic: steps navigate with English names, then the screen is switched to Arabic in place.
            to_lang = (lambda: (a.js("c.setState(s => ({ settings: Object.assign({}, s.settings, { lang: 'ar' }) }));"), a.wait(150))) if lang == 'ar' else (lambda: None)
            a.wait(200); a.dismiss_all()
            snap = a.state()
            for name, fn in states():
                if name.startswith('ob-') or name in ('char-create',):
                    continue
                reset_to(a, snap)
                try:
                    fn(a); a.wait(200)
                except Exception as e:
                    # some tour steps look for the sample names that were renamed here
                    a.js("c.setState({ sheet: null, pcard: null, fishSel: null, celebrate: [] });")
                    continue
                to_lang()
                for it in a.scan(name, contrast=False):
                    pass
                if lang == 'ar' and w == 320 and theme == 'light' and name in ('today', 'detail-quran', 'stats', 'goals', 'char-hero', 'ranks-league-tier1', 'today-tasks', 'settings', 'explore', 'explore-book'):
                    a.shot('long-320-ar__' + name)
                if lang == 'en' and w == 320 and theme == 'light' and name in ('today', 'detail-read', 'detail-quran', 'stats', 'goals', 'sheet-amount', 'char-hero', 'ranks-league-tier1', 'archived-list', 'recap', 'today-tasks', 'task-sheet-date', 'stats-recap-locked'):
                    a.shot('long-320__' + name)
            a.check_errors('long %d %s %s' % (w, theme, lang))
            a.close()


if __name__ == '__main__':
    sys.exit(1 if run('long texts', main) else 0)
