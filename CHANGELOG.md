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

## v0.12.0: Full test pass (2026-10-16)
Every screen, sheet and pop-up checked at phone sizes from 320 px to desktop, in light and dark, plus long simulated use. What it found and fixed:
- **Fishing painting fits small phones.** It was a fixed 348 px wide, so on iPhone SE and mini models and 360 px Androids it stuck out of the screen and the whole page scrolled sideways. It now shrinks to fit (and refits when the phone rotates).
- **Fishing countdown in seconds.** The painting showed real trips as raw seconds ("10800s left"). It now shows "2h 59m", like the rest of the app.
- **Trip countdowns tick every second in the last hour** ("14m 05s"), so you can see progress right away. Before, they changed once a minute and looked stuck.
- **Pop-ups never taller than the screen.** On landscape phones and small screens, a big catch could push the pop-up's button off screen and leave the app stuck. Pop-ups now scroll.
- **Sheets on short screens** (landscape): buttons were squashed to a thin strip. Sheets now scroll instead.
- **Comeback card with a Quit habit.** Unlogged days of a Quit habit count as clean, which also made them look like "you used the app", so the comeback card never appeared for anyone with a Quit habit. Only logged Quit days count as use now.
- **The day never goes backwards.** Flying west across time zones (or setting the phone's date back) moved the app to the previous day and counted that day's coins and XP twice. The app now stays on the latest day it has seen (for small steps back of up to 2 days).
- **Older iPhones.** Some colours used CSS `color-mix()`, which iPhones before iOS 16.2 don't support, so those backgrounds were missing. The colours are now computed in the app.
- **First-time setup can be skipped** with "Skip: I'll add my own habits". Before, you could only go forward by picking one of the suggested habits.
- **Reminders are honest.** The habit form and Settings now say this version can't send notifications yet (the time is saved for later).
- **Recap fits your habits:** "pages read" only with a reading habit and "focused time" only with a timed habit; otherwise perfect days and habits tracked.
- **Singular words:** "1 day left", "1 of 1 habit done", "1 badge", "day in a row", "1 day to go", "1 check-in".
- **Long names wrap** instead of spilling out of cards (hero names up to 14 letters, long goal words), and small-screen fixes for the habit counters, Fish Book names and fish facts.
- Bigger tap target on the hero's name, a clearer bite marker, the recap emoji no longer cut.
- Demo tools: "Simulate a 4-day break" now leaves Quit days unlogged, like a real break.
- **Tests added** in `tests/`: about 480 checks across 8 suites, a scan of 118 screens at 11 sizes and themes, and random sessions with time jumps and reloads. See `tests/README.md`.

## v0.13.0: Tasks, backgrounds and a tidier Today (2026-10-18)
- **One-time tasks.** Today has a Habits / Tasks switch at the top (the bottom bar keeps its 5 tabs). A task has a name and is for today or a date you pick. The list shows today's tasks and overdue unfinished ones; upcoming tasks have their own section. Tick to finish, untick, and tap a task to edit or delete it.
- **Task coins can't be farmed.** A finished task gives 5 coins and no XP. Unticking or deleting it takes the coins back, and only 5 tasks a day pay, so ticking and unticking, deleting and adding again, or making lots of tasks never adds coins. Tasks never count toward streaks, trips or the league. They are saved on the device and in backups. Finished tasks leave the list the next day and are cleared after 30 days (their coins stay).
- **Habits only on their days.** A habit set to specific days (for example every day except Friday) no longer shows on Today on its off days, for today or for past days picked in the week strip. An off day that was logged still shows the habit, so the log can be changed. Times-a-week habits still show every day. Streaks and stats are worked out exactly as before.
- **Done habits move down.** In each time-of-day group, habits still to do come first and done ones (done, minimum or skipped) go to the bottom; both parts keep your own order. A habit (or task) you just ticked stays in place for under a second before it moves or hides, so a quick second tap can't land on the next one. Reorder mode shows your saved order, as before.
- **Hide done.** A "Hide done" / "Show done" button on Today hides the habits already finished that day. The choice is remembered. When everything is hidden, Today shows "All done for today" instead of an empty list.
- **Starter items by character.** A new boy hero gets only the boy starters (Traveler's Vest, Short & Tousled, Brown Boots, Bamboo Rod) and a girl only the girl ones (Coral Dress, Long & Straight, boots, rod). The other character's starter outfit and hair are in the Store like normal items: clothes 150 coins, hair 120. Older saves keep only their own set, plus anything the hero is wearing right now. Sample data updated to match.
- **Backgrounds.** A new Backgrounds category in the Store and the Wardrobe: 10 pixel-art scenes that sit behind the hero on the Hero page and in the Change look preview. 4 Common (250), 3 Rare (500, Lv 3), 2 Epic (900, Lv 5) and 1 Legendary (1,500, Lv 10), each with a day version for light mode and a night version for dark mode, drawn in the style of the fishing painting with a calm middle so the hero stands out. Style only, no stats. The plain background stays free for every hero, and the Equipped list has a Background row. A background is not gear, so it can be changed during a trip.
- **Character tab goes home.** Tapping Character in the bottom bar while already in Character (Wardrobe, Store, Explore, the Fish Book, a fish, Change look) goes back to the Hero page, scrolled to the top. The bottom bar stays usable while a fish's sheet is open.
- **30-day recap after a week.** The recap button on Stats appears once 7 days have passed since your first day in the app. Before that, a note says the date it unlocks. Older saves take the first day from their oldest habit.
- Saves are checked when loaded: a damaged task list, background or first day can't break the screens.
- Items design board: the boy and girl starter outfits and hair now show their price for the other character.
- **Tests:** about 700 checks across the 8 suites (up from about 480): tasks and their coins (including 400 random steps that try to farm them), which habits Today shows on which days (600 random habits against a reference), done order and Hide done, starter items and old saves, backgrounds (including a pixel check that the hero stands out on each one, in both themes), the Character tab and the recap lock. The tour now scans 144 screens at 11 sizes and themes, and random sessions also check the task and background rules.

---

## What's next
See the **Roadmap** in [README.md](README.md#roadmap).
