# Streakling

A gamified habit tracker for a worldwide audience. You build real habits, and a pixel-art hero levels up with you. Finishing habits earns coins and XP, unlocks the hero's daily trips, and fills a collection you want to complete.

> **Status:** interactive prototype, **v0.9.2**. Not a released app yet.

---

## The idea

Most habit trackers are checklists. People drop them after about two weeks because nothing pulls them back. Streakling keeps the core tracker fast and honest, and adds a light RPG layer on top as the reason to come back:

- **Do your habits:** earn coins and XP.
- **Finish half of today's habits:** your hero can go on one adventure and one fishing trip.
- **Come back later:** the hero returns with loot, fish and progress.

The habit tracking comes first. The game exists to support it, not to replace it.

---

## Features (as of v0.9.2)

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
- **Settings** with Light, Dark and System themes, plus app preferences.

---

## Development history

See **[CHANGELOG.md](CHANGELOG.md)** for the full lifecycle, from the first idea to v0.9.2.

---

## Repository layout

```
prototype/
  Main.dc.html        The interactive app (phone screen, 390×844)
  Characters.dc.html  Pixel character style sheet
  Items.dc.html       Items, stats and economy design board
  Fishing.dc.html     Fishing, Fish Book and league design board
  canvas.json         Board layout for the design canvas
```

### Important: how to run it

These files were built in **Claude's design canvas**. Each one loads `support.js`, which is that canvas's runtime and is **not included** in this repo. **Opening the files directly from GitHub or your disk will not work.**

The repo is the source record of the prototype. A standalone build that runs in any browser (and on GitHub Pages) is planned. See the roadmap.

---

## How it was built

- UI prototyped as interactive components in Claude's design canvas.
- Pixel art (hero, gear, 25 fish, fishing scene) generated with Python/PIL scripts.
- Game economy balanced with simulations of casual, regular and dedicated player types over a full year (coins, XP, leveling, item prices).
- QA with automated checks: Node.js logic harnesses with simulated dates and timers, a template checker for undefined/NaN/clipped text, and Playwright browser runs covering every screen in light and dark mode.

---

## Roadmap

**Next**
- [ ] Standalone web build (plain HTML/JS) with a live GitHub Pages demo
- [ ] Real local data storage (offline-first)

**Later**
- [ ] Mobile app
- [ ] Real accounts, friends and leaderboard (needs a backend)
- [ ] Real push notifications and habit reminders (needs a server)
- [ ] Home-screen widget with one-tap check-in
- [ ] Full Arabic + RTL support

**Known limitations of the prototype**
- Leaderboard, friends and league data are simulated.
- Not yet verified on mobile Safari.
- Reminders and notifications are not real yet.

---

## Author

**Fahad Al-Moussa**, Computer Science student at Imam Muhammad Ibn Saud Islamic University (IMSIU), Riyadh.

© 2026 Fahad Al-Moussa. All rights reserved.
