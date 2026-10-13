# Streakling

A gamified habit tracker for a worldwide audience. You build real habits, and a pixel-art hero levels up with you. Finishing habits earns coins and XP, unlocks the hero's daily trips, and fills a collection you want to complete.

> **Status:** working prototype, **v0.10.0**. Usable day to day on one device; not a released app yet.

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

## Features (as of v0.10.0)

### Habit tracking
- **Four habit types:** Yes/No, Amount (e.g. pages), Time (with a wall-clock stopwatch), and Quit (breaking a bad habit).
- **Day states:** Done, Minimum, Skipped, Missed, plus Clean/Slipped for Quit habits.
- **Schedules:** Mon–Fri is the default, chosen for a worldwide audience.
- **Streaks** with **streak freeze** protection.
- **Manual logging:** a log sheet for every habit. Amounts can be typed or adjusted with −/+, and time can be typed or recorded with the stopwatch.
- **Past days:** go back to earlier days from the week strip or the heatmap. Future days are locked.
- **Emoji-only habit icons.** The field is empty until the user picks one, with no fake defaults.

### Goals and stats
- **Long-term goals** with a deadline picked from a calendar, linked to a habit and filled automatically from its logs.
- **Stats dashboard:** a GitHub-style heatmap per habit, current vs best streak, and completion trends.
- **Milestone badges per habit:** first check-in, then 7, 14, 30, 90 and 365-day streaks. They are earned automatically and can't be edited.
- **Celebration pop-ups** for badges and for finishing every habit of the day.

### The hero (RPG layer)
- **Character first:** the user creates their pixel hero (boy or girl) before adding any habit.
- **Character tab** in the center of the bottom navigation.
- **Wardrobe and Store:** hats, weapons, fishing rods and accessories are separate equipment slots, bought with coins.
- **Stats:** Health, Power and Stamina. Each adventure location tests a different mix, so every item has places where it's the best pick.

### Daily trips
- **Unlocked at 50%:** once half of today's due habits are done (rounded up), trips open for the day. If nothing is due today, trips are open by default.
- **Adventure:** once a day. It can succeed or fail depending on the hero's gear and level.
- **Fishing:** once a day, running in parallel with the adventure. The hero is away for 3 hours with a painted fishing scene and a countdown, and comes back with 1–4 fish based on level.
- **Fish Book:** 25 fish across Common, Rare, Epic and Legendary.

### Social (simulated in the prototype)
- **Weekly league / leaderboard**, friends, and a **Hall of Fame**.

### App
- **Saved on the device:** automatic saving, history without limit, days that roll over at midnight even with the app open.
- **Backup and restore** as a file, from Settings.
- **Installable and offline:** home-screen icon, works without a connection after the first visit.
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
  Characters.dc.html    Pixel character style sheet
  Items.dc.html         Items, stats and economy design board
  Fishing.dc.html       Fishing, Fish Book and league design board
  canvas.json           Board layout for the design canvas
scripts/build.mjs       Turns prototype/ into docs/
```

### How it works

The app is designed in `prototype/Main.dc.html`: an HTML template with `{{value}}` placeholders, `<sc-if>` / `<sc-for>` blocks, and a logic class whose `renderVals()` returns everything the template shows. Those files only run inside Claude's design canvas, so `scripts/build.mjs` converts them into `docs/`, where `runtime.js` renders the same template and logic with Preact in any browser.

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
- Pixel art (hero, gear, 25 fish, fishing scene) generated with Python/PIL scripts.
- Game economy balanced with simulations of casual, regular and dedicated player types over a full year (coins, XP, leveling, item prices).
- QA with automated checks: Node.js logic harnesses with simulated dates and timers, a template checker for undefined/NaN/clipped text, and Playwright browser runs covering every screen in light and dark mode.
- Saving tested with a simulated clock in a real browser: first-time setup, reloads, midnight with the app open, a full week of use, time away, real-length trips, backup and restore, a year of history, and long random sessions that reload and compare the screen.

---

## Roadmap

**Done**
- [x] Standalone web build with a live GitHub Pages demo
- [x] Save data on the device, offline, with backup and restore
- [x] Real first-run experience; demo data behind a switch

**Next**
- [ ] A 7-day real-use trial, then fix what it shows

**Later**
- [ ] Mobile app
- [ ] Real accounts, friends and leaderboard (needs a backend)
- [ ] Real push notifications and habit reminders (needs a server)
- [ ] Home-screen widget with one-tap check-in
- [ ] Full Arabic + RTL support

**Known limitations**
- Data lives on one device; there is no sync between devices.
- Leaderboard, friends and league data are simulated.
- Reminders and notifications do not fire yet.
- Not yet verified on a real iPhone (tested in Chromium at phone sizes).

---

## Author

**Fahad Al-Moussa**, Computer Science student at Imam Muhammad Ibn Saud Islamic University (IMSIU), Riyadh.

© 2026 Fahad Al-Moussa. All rights reserved.
