# Changelog: the Streakling lifecycle

How the app went from an idea to the v0.9.2 prototype.

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

---

## What's next
See the **Roadmap** in [README.md](README.md#roadmap).
