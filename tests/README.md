# Streakling tests

Browser tests for the web build in `docs/`, written with Playwright for Python (Chromium). They drive the real app: taps, typing, a simulated clock, reloads.

## Run

```bash
pip install playwright && python3 -m playwright install chromium
cd docs && python3 -m http.server 8765 &      # the tests expect the app here (or set APP_URL)
cd ../tests
python3 t_habits.py                           # one suite
./runall.sh                                   # everything; results in logs/
```

Each suite prints `N passed, M failed` and a list of screen problems it found.

## Suites

| File | What it checks |
|---|---|
| `t_logic.py` | Day states, streaks and freezes against an independent re-implementation (600 random habits), badges, coin and XP caps, levels, goals, stats totals |
| `t_habits.py` | Creating every habit type and option, every form error, logging (check, amount, time, quit, skip, reasons), the stopwatch, past days and the edit window, editing, archive, delete, reorder |
| `t_days.py` | Weeks of use on a simulated clock: midnight with the app open, days away, coins and XP carried over, the weekly league, real trip lengths, a timer across midnight, daylight-saving changes, year end |
| `t_hero.py` | Hero setup, store, try-on, wardrobe rules, accessory slots, stats, adventures, fishing, bait, Fish Book rewards, selling, gear locked during trips, Change look |
| `t_settings.py` | Themes, switches, leaderboard actions, invites, backup and restore, bad files, demo tools, start over, broken and old saves, storage full or blocked, two tabs, offline |
| `t_more.py` | Coach tips, reasons card, heatmap taps, schedule edits, pop-up queue, trip shortcuts, countdowns, recap, the clock going back, skipping setup, singular words |
| `t_long.py` | The longest allowed names (and Arabic) on every screen |
| `t_pages.py` | Design boards, manifest, icons, service worker, theme colours |
| `tour.py` | Visits ~120 screens, sheets and pop-ups and scans each one (see below). `python3 tour.py 320-light 390-dark 1280-light …` |
| `t_monkey.py` | Random taps, typing, time jumps and reloads with checks after every step. `python3 t_monkey.py <steps> <seed…>` |

`scan.js` is the screen scanner used everywhere: it flags `undefined`/`NaN` text, content sticking out of the screen, clipped or spilling text, buttons covered by something else, low contrast, small tap targets, unnamed buttons and duplicate ids.

Small tap targets in the 7-column date grids (week strip, heatmap) on 320–375 px phones are known and accepted.
