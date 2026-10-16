# Changelog: the Streakling lifecycle

How the app went from an idea to the current version.

> **Note on version numbers:** version numbers started being used partway through development. Early stages are listed as phases. v0.7, v0.8 and v0.9.2 are confirmed version labels; the exact boundaries between some early phases are approximate.

---

## Phase 0: Idea and scoping
- The starting goal: a habit tracker the author would actually use every day.
- The idea was refined before building: habit types (Yes/No, Amount, Time, Quit), frequency, done/skip/miss states, streaks with freeze, a heatmap dashboard, and goals split into daily targets and long-term goals.
- Key early decision: keep logging to one or two taps, because a slow tracker gets abandoned.

## Phase 1: First interactive prototype
- First clickable phone-screen prototype built to visualize the idea.
- Today screen, habit cards, a week strip, and a stats view with heatmaps.

## Phase 2: Core tracker polish
- Emoji field starts **empty**: the user types an emoji or picks one from the quick set. No fake defaults.
- Congratulations pop-up when every habit of the day is done.
- Goals get a **deadline picked from a calendar**.
- **Per-habit milestone badges:** first check-in, 7, 14, 30, 90 and 365-day streaks. They are earned automatically and can't be edited by the user.
- **Settings** screen with dark theme and other app preferences.
- **Manual logging:** a log sheet per habit, typed amounts, typed time or a stopwatch.
- **Editing past days** from the week strip and heatmap. Future days are locked.
- **Linked goals** that fill automatically from a habit's logs.

## Phase 3: The pixel hero
- Decision: the app targets a **worldwide** audience, not only Saudi users.
- Pixel character redesigned from a raw first sketch to a cleaner retro RPG style, based on a reference image.
- Boy/girl hero, a **Character** tab, and coins from completed habits.
- Store and wardrobe. Every outfit is a layer on one shared body shape, so new items are cheap to add.
- Decision: **hats, weapons and fishing rods** are their own equipment slots, separate from generic accessories.

## Phase 4: Adventures and the economy (→ v0.7)
- Hero stats: Health, Power and Stamina.
- Adventures to different locations with success odds based on gear and level.
- Coin, XP and level curves balanced with **year-long simulations** of casual, regular and dedicated players.

## v0.8: Fair adventure formula
- Problem found: Stamina didn't count in fights and Power counted about twice as much as Health, so some items were must-buys even though same-rarity items cost the same.
- Fix: each location tests a different mix of Health, Power and Stamina, so every item has places where it's the best pick.
- Places re-tuned and the year simulation re-run, keeping progression close to v0.7.

## v0.9: Fishing, daily unlock and navigation redesign
- **Character first:** the hero must be created before any habit, in one quick pre-filled onboarding step.
- **Daily trips unlock at 50%** of today's due habits (rounded up). If nothing is due, trips are open.
- **Once a day each:** one adventure and one fishing trip.
- The stamina energy bar was **removed**, since the 50% gate and the daily limit already do its job.
- **Fishing ("Focused On Stamina Only"):** the hero is away for 3 hours, shown in a painted fishing scene with weather and lighting and a countdown, and returns with 1–4 fish based on level.
- **Fish Book:** 25 fish (10 Common, 7 Rare, 5 Epic, 3 Legendary).
- **Weekly league / leaderboard**, friends and Hall of Fame, so users can show off their effort (simulated data).
- **Navigation redesign:** the Character tab moved to the center of the bottom bar, and the "New habit" button moved onto the Today screen.
- Economy re-simulated for daily trips and fish sales.

## v0.9.1 – v0.9.2: QA and fixes (current)
- **Time habits:** Play now always opens the time-entry sheet. The stopwatch starts only from an explicit "Start timer" button.
- Stopwatch rewritten to use **wall-clock timestamps** instead of counting ticks, so time stays correct when the app is in the background.
- Today screen's bottom area redesigned so the Reorder and New habit controls never overlap habit cards.
- Closed a **coin-farming exploit**.
- Fixed once-per-day pop-ups that were firing again.
- Fixed pluralization and unit-naming bugs.
- Improved color contrast in both light and dark themes.
- Verified with thousands of automated checks and a manual screenshot review.

## Standalone web build (2026-10-13)
- The app now runs outside Claude, in any browser: `docs/` is served by GitHub Pages.
- `scripts/build.mjs` converts the prototype files into the web build, and `runtime.js` renders the same template and logic with Preact. The app's behaviour is unchanged.
- Full-screen on phones, and a phone-sized frame on computers.
- The three design boards are published as plain pages.
- Verified against the original: automated sessions drive the original and the web build through identical random taps and typing, and compare the visible text and screenshots after every step.

## v0.10.0: Saved on the device (2026-10-13)
The first version meant for real daily use.
- **Automatic saving** in the browser, on every change and when the app is closed. New users start empty with the first-time setup, not demo data.
- **Days tied to real dates.** The prototype numbered days from a point about 5 weeks back, which moved every time the app opened. History could never be longer than about 5 weeks, so the 90-day and 365-day badges could not really be earned. Day 0 is now a fixed date and history grows without limit.
- **Midnight handled, even with the app open.** Coins and XP used to count only today's check-ins live, and earlier days came from a total taken once at startup, so a new day would have wiped yesterday's rewards. The last day is now added to the totals when the date changes.
- **The weekly league closes itself** at the end of each calendar week, with results and promotion. Before, only the demo "End week" button ended a week.
- **Heatmap and week strip follow today** (the last 5 weeks) instead of being fixed to the first 5 weeks.
- **Real trip lengths:** adventures take 15 min to 4 h and fishing takes 3 h, measured by the clock, so they finish while the app is closed.
- **Demo tools switch** in Settings: sample data, trips in seconds, free coins and levels, and the demo buttons only appear when it is on.
- **Backup and restore** as a file, with a confirmation before anything is replaced.
- **Home-screen app:** icon drawn from the hero sprite, works offline.
- "Dismiss" on the comeback card and "Not now" on coach tips now last a day and a week, instead of forever.
- A warning banner if the browser refuses to save (private mode, full storage).

## v0.11.0: Feedback from real use (2026-10-16)
Fixes and requests from the first days of daily use.
- **Sound effects:** taps, the bottom navigation, check-ins, badges, purchases, returning trips, and a short fanfare for finishing every habit of the day. Made with Web Audio, so there are no files to download. Settings → Sounds turns them off.
- **Gear locked during trips:** while the hero is on an adventure or fishing, the Wardrobe and Change look are locked. Items bought during a trip go to the Wardrobe and can be worn after.
- **Hero identity is permanent:** name, character (boy/girl) and skin are chosen once at setup. Change look now only changes hair colour. The setup screen says so.
- **Hero name check:** rude names (English and Arabic, including spaced-out and digit spellings) are refused, because other players see the name. Habit names are private and not checked. A hero who already has a rude name gets one rename.
- **Welcome gift:** 150 coins once, on the first check-in (done or minimum, today only). Saves from older versions get it on their next check-in.
- **Tap your hero's name** (on the Character screen or your own leaderboard row) to open the Hero tab. "Hide me from leaderboards" moved to Settings → Leaderboard.
- **Invite a friend** opens the phone's share sheet with a link to the app, or copies the invite where sharing isn't available. The friends list is still simulated until there are accounts.
- **Store and Wardrobe:** the owned/total numbers next to each category were removed.
- **Trips catch up at once** when you come back to the app (switching apps, unlocking the phone), instead of on the next tick.

---

## What's next
See the **Roadmap** in [README.md](README.md#roadmap).
