# Streakling

A gamified habit tracker for a worldwide audience. You build real habits, and a pixel-art hero levels up with you. Finishing habits earns coins and XP, unlocks the hero's daily trips, and fills a collection you want to complete.

> **Status:** working prototype, **v0.17.0**. Usable day to day on one device; not a released app yet.

## ▶ Try it

**Live app: https://fahadqdev.github.io/streakling-app/**

- **On a phone:** it opens full-screen. Add it to your home screen to use it like an app (Safari: Share → Add to Home Screen; Chrome: ⋮ → Add to Home screen). It also works offline after the first visit.
- **On a computer:** it opens in a phone-sized frame.
- **Design boards:** [Pixel character](https://fahadqdev.github.io/streakling-app/design/characters.html) · [Items, stats and economy](https://fahadqdev.github.io/streakling-app/design/items.html) · [Fishing, Fish Book and league](https://fahadqdev.github.io/streakling-app/design/fishing.html)

**Your data stays on your device.** Everything is saved automatically in the browser you use, nothing is sent anywhere, and there is no account. That also means:
- Use **one device and one browser**. A phone and a laptop do not sync.
- **Clearing browser data deletes it.** Settings → *Download backup* saves a file you can restore later (also onto another device).
- On iPhone, **open it from the home-screen icon**. As far as we know, Safari may clear data of websites you have not visited for 7 days; home-screen apps are not affected.

**Demo tools** (Settings → Testing): sample data, trips that finish in seconds, free coins and levels. Off by default.

---

## The idea

Most habit trackers are checklists. People drop them after about two weeks because nothing pulls them back. Streakling keeps the core tracker fast and honest, and adds a light RPG layer on top as the reason to come back:

- **Do your habits:** earn coins and XP.
- **Finish half of today's habits:** your hero can go on one adventure and one fishing trip.
- **Come back later:** the hero returns with loot, fish and progress.

The habit tracking comes first. The game exists to support it, not to replace it.

---

## Features (as of v0.17.0)

### Habit tracking
- **Four habit types:** Yes/No, Amount (e.g. pages), Time (with a wall-clock stopwatch), and Quit (breaking a bad habit).
- **Day states:** Done, Minimum, Skipped, Missed, plus Clean/Slipped for Quit habits.
- **Schedules:** daily, specific days (Mon–Fri is the default, chosen for a worldwide audience) or times per week. A specific-days habit only shows on Today on its scheduled days (and on an off day you logged); times-a-week habits show every day.
- **Streaks** with **streak freeze** protection.
- **Manual logging:** a log sheet for every habit. Amounts can be typed or adjusted with −/+, and time can be typed or recorded with the stopwatch.
- **A tidy Today:** inside each time of day, habits still to do come first and done ones (done, minimum, skipped) move to the bottom, both in your own order. **Hide done** hides finished habits (the choice is remembered) and shows "All done for today" when nothing is left.
- **Past days:** go back to earlier days from the week strip or the heatmap. Future days are locked.
- **Emoji-only habit icons.** The field is empty until the user picks one, with no fake defaults.

### Tasks
- **One-time tasks** on Today, behind a Habits / Tasks switch: for today or a date you pick. Today's and overdue tasks first, upcoming ones in their own section. Tick, untick, edit, delete.
- **5 coins per finished task**, no XP, for up to 5 tasks a day. Unticking or deleting a task takes its coins back, so tasks can't be farmed. Tasks never count toward streaks, trips or the league.

### Goals and stats
- **Long-term goals** with a deadline picked from a calendar, linked to a habit and filled automatically from its logs.
- **Stats dashboard:** a GitHub-style heatmap per habit, current vs best streak, and completion trends.
- **30-day recap** card (check-ins, best streak, top habit, totals). It opens a week after your first day in the app.
- **Milestone badges per habit:** first check-in, then 7, 14, 30, 90 and 365-day streaks. They are earned automatically and can't be edited.
- **Celebration pop-ups** for badges and for finishing every habit of the day.

### The hero (RPG layer)
- **Character first:** the user creates their pixel hero (boy or girl) before adding any habit. Name, character and skin are permanent after setup; hair colour and outfits can change. Rude hero names are refused (habit names are private and not checked).
- **Character tab** in the center of the bottom navigation. Tapping it again from anywhere inside Character goes back to the Hero page.
- **Starter items by character:** a boy starts with the boy outfit and hair, a girl with the girl ones. The other character's starters are in the Store (clothes 150, hair 120).
- **Wardrobe and Store:** hats, weapons, fishing rods and accessories are separate equipment slots, bought with coins. Gear is locked while the hero is on a trip.
- **Three weapon types:** swords (balanced), maces (more Health) and spears (more Power), 6 of each from Lv 2 (200 coins) to Lv 16 (1,800). In each tier the three have the same total strength, so the choice is about the adventures you plan. A filter in the Weapons section shows one type at a time. The **Ember of Thirty** can't be bought: it unlocks when any habit reaches a 30-day streak.
- **Backgrounds:** 10 pixel-art scenes behind the hero (Common 250, Rare 500, Epic 900, Legendary 1,500), each with a night version for dark mode. Style only, no stats; the plain background is free.
- **Welcome gift:** 150 coins once, on the first check-in, so a new player can buy a first item.
- **Stats:** Health, Power and Stamina. Each adventure location tests a different mix, so every item has places where it's the best pick.

### Daily trips
- **Unlocked at 50%:** once half of today's due habits are done (rounded up), trips open for the day. If nothing is due today, trips are open by default.
- **Adventure:** once a day. It can succeed or fail depending on the hero's gear and level.
- **Fishing:** once a day, running in parallel with the adventure. The hero is away for 3 hours with a painted fishing scene and a countdown, and comes back with 1–4 fish based on level.
- **Fish Book:** 25 fish across Common, Rare, Epic and Legendary.

### Diamonds (the rare currency)
- **Two currencies.** Coins come from habits and tasks, as before. **Diamonds** are rare: they come from the weekly league and from packs, and are shown next to coins at the top of the Character tab.
- **League rewards:** the top 10 of each week earn diamonds, more in higher leagues (1st place: 30 in Bronze, 45 in Silver, 60 in Gold, 90 in Diamond). Hidden players earn none. The League tab shows this week's rewards.
- **Packs:** 100, 550 (+10%), 1,200 (+20%) and 2,500 (+25%). Payments are not connected yet: the packs say Coming soon. With Demo tools on, a test payment step (clearly marked, no money) lets you try the whole flow.
- Diamonds never change coins, XP or the weekly league score.

### Social (simulated in the prototype)
- **Weekly league / leaderboard**, friends, and a **Hall of Fame**.
- **Invite a friend** through the phone's share sheet (or a copied link). The friends list itself is still simulated.

### App
- **Saved on the device:** automatic saving, history without limit, days that roll over at midnight even with the app open.
- **Backup and restore** as a file, from Settings.
- **Installable and offline:** home-screen icon, works without a connection after the first visit.
- **Sound effects** for taps, check-ins, badges and finishing the day, made with Web Audio (no sound files). Can be turned off in Settings.
- **English and Arabic.** A Language switch in Settings; a phone set to Arabic starts in Arabic. Arabic is fully right to left (layout, icons, progress bars, switches) with proper Arabic plural forms, an Arabic font, and Western digits.
- **Settings** with Light, Dark and System themes, plus app preferences and a Demo tools switch.

---

## Development history

See **[CHANGELOG.md](CHANGELOG.md)** for the full lifecycle, from the first idea to today.

---

## Repository layout

```
docs/                   The standalone web app (served by GitHub Pages)
  index.html            The app — generated, do not edit by hand
  runtime.js            Small renderer for the app's template and logic
  vendor/preact.min.js  Preact 10 (MIT), the UI library underneath
  sw.js                 Offline support (generated)
  manifest.webmanifest  Home-screen app settings
  icons/                App icons, drawn from the hero sprite
  design/               The three design boards as plain pages
prototype/              Source of truth, in Claude's design-canvas format
  Main.dc.html          The app: template + logic (this is the main version now)
  i18n/en.json          Every piece of text the app shows, by key (more languages go next to it)
  Characters.dc.html    Pixel character style sheet
  Items.dc.html         Items, stats and economy design board
  Fishing.dc.html       Fishing, Fish Book and league design board
  canvas.json           Board layout for the design canvas
scripts/build.mjs       Turns prototype/ into docs/
tests/                  Browser tests (Playwright for Python), see tests/README.md
```

### How it works

The app is designed in `prototype/Main.dc.html`: an HTML template with `{{value}}` placeholders, `<sc-if>` / `<sc-for>` blocks, and a logic class whose `renderVals()` returns everything the template shows. Text is never written into the template or logic: the template reads `{{L.someKey}}` and the logic calls `tr('someKey', [values])`, both looked up in `prototype/i18n/<lang>.json`. Those files only run inside Claude's design canvas, so `scripts/build.mjs` converts them into `docs/`, where `runtime.js` renders the same template and logic with Preact in any browser.

### Run it locally

No install needed. Open `docs/index.html` in a browser, or serve the folder:

```bash
cd docs && python3 -m http.server 8000
# then open http://localhost:8000
```

### Rebuild after changing the prototype

```bash
node scripts/build.mjs   # needs Node.js 18+
```

Never edit `docs/index.html`, `docs/sw.js` or `docs/design/*` directly; change `prototype/` and rebuild.

---

## How it was built

- UI prototyped as interactive components in Claude's design canvas.
- Pixel art (hero, gear, 25 fish, fishing scene, 10 backgrounds with day and night versions) generated with Python/PIL scripts.
- Game economy balanced with simulations of casual, regular and dedicated player types over a full year (coins, XP, leveling, item prices).
- QA with automated checks: Node.js logic harnesses with simulated dates and timers, a template checker for undefined/NaN/clipped text, and Playwright browser runs covering every screen in light and dark mode.
- Browser test suite in [`tests/`](tests/README.md): every habit and task flow, weeks of use on a simulated clock (midnight, days away, daylight saving, time-zone changes), the hero, backgrounds and trips, settings and backups, a screen scanner run on ~145 screens at sizes from 320 px to desktop, and random sessions.
- Saving tested with a simulated clock in a real browser: first-time setup, reloads, midnight with the app open, a full week of use, time away, real-length trips, backup and restore, a year of history, and long random sessions that reload and compare the screen.

---

## Roadmap

**Done**
- [x] Standalone web build with a live GitHub Pages demo
- [x] Save data on the device, offline, with backup and restore
- [x] Real first-run experience; demo data behind a switch
- [x] Full Arabic + RTL support

**Next**
- [ ] A 7-day real-use trial, then fix what it shows

**Later**
- [ ] Mobile app
- [ ] Real accounts, friends and leaderboard (needs a backend)
- [ ] Google Play release with Play Billing for diamond packs (needs the server above first)
- [ ] Real push notifications and habit reminders (needs a server)
- [ ] Home-screen widget with one-tap check-in

**Known limitations**
- Data lives on one device; there is no sync between devices.
- **Diamonds with a simulated league.** The 19 other players in your league are generated on the device from a seed, with weekly XP in a fixed range for each league. Your place is your real weekly XP against those numbers, so league diamonds are in practice a reward for keeping your habits up (about 60–90 a week for a steady player in Gold or Diamond); nobody is competing against you. Before real payments go live, the diamond balance, purchases and the league must move to a server: on the device, paid diamonds would be lost when browser data is cleared, and a balance could be edited.
- Leaderboard, friends and league data are simulated.
- Reminders and notifications do not fire yet (the app says so where you set them).
- Not yet verified on a real iPhone or in Safari (tested in Chromium at phone sizes; CSS features that need iOS 16.2+ were removed).

---

## Author

**Fahad Almousa**, Computer Science student at Imam Muhammad Ibn Saud Islamic University (IMSIU), Riyadh.

© 2026 Fahad Almousa. All rights reserved.
