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
| `t_logic.py` | Day states, streaks and freezes against an independent re-implementation (600 random habits), badges, coin and XP caps, levels, goals, stats totals, which habits Today shows on which days (600 random habits), done-habit order and Hide done (random lists), task coins over 400 random steps, league diamonds by place and league, every diamond-item perk with fixed dice and its effect on XP (none), the 11 adventure places, 35 fish (each catchable) and the Fish Book save migration |
| `t_habits.py` | Creating every habit type and option, every form error, logging (check, amount, time, quit, skip, reasons), the stopwatch, past days and the edit window, editing, archive, delete, reorder, habits only on their scheduled days, done habits moving down, Hide done |
| `t_days.py` | Weeks of use on a simulated clock: midnight with the app open, days away, coins and XP carried over, the weekly league, real trip lengths, a timer across midnight, daylight-saving changes, year end, tasks and Hide done over days |
| `t_hero.py` | Hero setup, starter items per character, store, try-on, wardrobe rules, accessory slots, stats, adventures, fishing, bait, Fish Book rewards, selling, gear locked during trips, Change look, the Character tab going back to Hero, backgrounds (prices, levels, wardrobe, trips, day and night pictures, the hero standing out on each one), buying diamonds (payments off, test payments, one credit per purchase, saves), weapon types (tiers, filter, gates, the 30-day Ember), diamond-only items (prices, stats, gates) |
| `t_settings.py` | Themes, the English / Arabic switch (direction, reload, Western digits, first run on an Arabic phone), switches, leaderboard actions, invites, backup and restore (with tasks), bad files, demo tools, start over, broken and old saves (v0.12 starter items, damaged v0.13 fields), storage full or blocked, two tabs, offline |
| `t_more.py` | Coach tips, reasons card, heatmap taps, schedule edits, pop-up queue, trip shortcuts, countdowns, recap and its one-week lock, the clock going back, skipping setup, singular words, one-time tasks (sections, dates, edit, delete, coins and farming, the next day) |
| `t_long.py` | The longest allowed names (and Arabic), habit and task names, on every screen; also the whole app in Arabic at 320 and 360 px |
| `t_pages.py` | Design boards, manifest, icons, service worker, theme colours, the text tables, no raw text keys on screen |
| `tour.py` | Visits ~150 screens, sheets and pop-ups and scans each one (see below). `python3 tour.py 320-light 390-dark 1280-light …`. Configs ending in `-ar` (`390-light-ar`) show every screen in Arabic, right to left |
| `t_monkey.py` | Random taps, typing, time jumps and reloads with checks after every step (also task and background rules). `python3 t_monkey.py <steps> <seed…>` |

`scan.js` is the screen scanner used everywhere: it flags `undefined`/`NaN` text, content sticking out of the screen, clipped or spilling text, buttons covered by something else, low contrast, small tap targets, unnamed buttons and duplicate ids.

Small tap targets in the 7-column date grids (week strip, heatmap) on 320–375 px phones are known and accepted.
