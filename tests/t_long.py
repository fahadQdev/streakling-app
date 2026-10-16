"""Stress test with the longest allowed texts (and Arabic) on every screen, at 320 and 390 px."""
from harness import *
from tour import states, reset_to, WHEN

LONG = 'Meditate every morning before work start'[:40]
AR = 'قراءة القرآن الكريم يومياً بعد صلاة الفجر'[:40]
UNIT = 'minutes of practice x'[:20]
HERO = 'WWWWWWWWWWWWWW'


def main(browser, res):
    for w, h in [(320, 568), (390, 844)]:
        for theme in ['light', 'dark']:
            a = App(browser, res, width=w, height=h, when=WHEN, label='long-%d-%s:' % (w, theme))
            a.clear(); a.open(); demo(a)
            a.js("""c.setState(s => ({
              char: Object.assign({}, s.char, { name: arg.hero }),
              habits: s.habits.map(h => h.id === 'read' ? Object.assign({}, h, { name: arg.long, unit: arg.unit, target: 999999 }) : (h.id === 'quran' ? Object.assign({}, h, { name: arg.ar }) : h)),
              goals: s.goals.map(g => Object.assign({}, g, { title: g.id === 'g1' ? 'A very long goal title that takes all sixty characters here' : g.title, target: g.id === 'g1' ? 9999999 : g.target })),
              settings: Object.assign({}, s.settings, { theme: arg.theme }) }));""", {'hero': HERO, 'long': LONG, 'ar': AR, 'unit': UNIT, 'theme': theme})
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
                for it in a.scan(name, contrast=False):
                    pass
                if w == 320 and theme == 'light' and name in ('today', 'detail-read', 'detail-quran', 'stats', 'goals', 'sheet-amount', 'char-hero', 'ranks-league-tier1', 'archived-list', 'recap'):
                    a.shot('long-320__' + name)
            a.check_errors('long %d %s' % (w, theme))
            a.close()


if __name__ == '__main__':
    sys.exit(1 if run('long texts', main) else 0)
