# Analog Bag

*Rocha Coded. Free tools from the Rocheverse.*

**A printable founder kit for your bag.**

Plan offline, in pen.
Pull three cards for your next post.
Lay your launch on the real moon.
Photograph the page when you're done, and Claude reads it back into your tasks.

<p align="center"><img src="docs/img/hero.png" width="760" alt="Three printables on a hot pink desk: a pink lined launch calendar with a plum moon strip, four plum and gold Hook Tarot cards, and an A5 page that says THIS WEEK."></p>

<p align="center"><sub>Every example is written for Wren, a made-up breathwork teacher. Her numbers are invented to show the shape.</sub></p>

## What you get
- **Hook Tarot.** 78 hook structures as a real deck. Print it, cut it, keep it in your bag. 22 Major Arcana for the big ideas (The Receipt, The One Woman Show, The Guest Check, Too Busy, The Hotline, The Front Page). Cups for story and feeling. Wands for bold and contrarian. Swords for questions and challenges. Pentacles for numbers, proof and results.
- **A three-card pull.** What they believe, what you'll say, what they'll do. Claude fills every blank with your topic, in your words.
- **Sacred Launch Calendar.** Your launch in six stages: seed, build, open, peak, close, integrate. Each stage starts on a real moon phase, with two or three plain-language beats. One printable page, plus a calendar file for your phone.
- **Pocket Week.** One A5 page. THIS WEEK. The one thing. Three moves. One number to watch. What you're letting go of. The moon for each day.
- **The readback.** Snap a photo of any filled page. Claude reads your handwriting, ticks what's done and merges it into one running `tasks.md`. Nothing ever gets added twice, and nothing you finished gets unticked.

The moon is computed on your computer from the astronomy itself. No app, no account, no internet. It matches NASA's 2026 tables to the minute.

## Install
It runs inside Claude. Nothing to host, no account to make, and your pages stay on your computer.

| Where you use it | Install it | Start it |
|---|---|---|
| [Claude Code](#claude-code) (recommended) | clone into `~/.claude/skills` | ask "pull three cards" or "make my pocket week" |
| [Claude Cowork](#claude-cowork) | upload `analog-bag.zip` as a skill | ask for a launch calendar in a Cowork task |

You need Python 3.10 or newer. For PDFs you also need Google Chrome, Chromium or Microsoft Edge installed.
Without one you still get every page as a web page: open it, Print, Save as PDF.

### Claude Code
```sh
git clone https://github.com/RochaStone/analog-bag ~/.claude/skills/analog-bag
```
Open Claude Code in a folder where you want your pages saved, and ask: "Pull three cards for my spring retreat."
To update later: `git -C ~/.claude/skills/analog-bag pull`.

### Claude Cowork
Cowork (the Claude desktop app) runs tasks in a sandbox on your computer that can only reach the folders you give it.
1. Download `analog-bag.zip` from the [latest release](https://github.com/RochaStone/analog-bag/releases/latest).
2. In the Claude desktop app: Customize > Skills, then + > Create skill > Upload a skill, and pick the zip.
3. In Settings > Capabilities, turn on code execution and file creation.
4. Make a folder for your pages, for example `analog-bag` in your home folder. Start a Cowork task, give it
   access to that folder, and ask: "Make me a sacred launch calendar for my retreat, starting 2 November."
5. Your pages, the calendar file and `tasks.md` land in that folder.

The sandbox may not have Chrome. If it doesn't, you get the pages as web pages. Open them in your own browser
and print from there. Tell Claude your city so the moon lands on your local date.

## How to use it
**Pull three cards.** "Pull three cards for my retreat, for burnt-out founders." You get three hook shapes, filled in for you.

**Print the deck.** "Print the hook tarot." Card stock, actual size, cut on the marks. Tarot size is 70 x 120 mm, four to a page. Want nine to a page? Ask for the mini size (63 x 88 mm). For backs, print double-sided and flip on the long edge.

**Plan a launch.** "Make a moon launch calendar for my Spring Breath Retreat, starting 2 November, six weeks." Print the page, import `launch.ics` into your calendar, tick the beats in pen.

**Plan the week.** "Make my pocket week." Print it on A5, or ask for two-up to get two copies on one A4 sheet.

**Read it back.** Sunday night, take a photo of the page and drop it in: "Read my page." Claude tells you what's done, what's new and what's still open.

Prefer the terminal? Every piece runs on its own:
```sh
python3 tarot/pull.py --topic "my spring retreat" --audience "burnt-out founders"
python3 tarot/print.py --out out/
python3 launch/launch.py --offer "Spring Breath Retreat" --date 2026-11-02 --weeks 6 --out out/ --utc-offset +08:00
python3 week/week.py --out out/
python3 readback/merge.py tasks.md new.md
```

<p align="center"><img src="examples/launch.png" width="380" alt="A pink lined A4 page: SACRED LAUNCH CALENDAR, Spring Breath Retreat, a plum moon strip and six stage cards with tick boxes."> <img src="examples/week.png" width="268" alt="An A5 pink lined page: THIS WEEK with a moon for each day, the one thing, three moves, one number to watch and a let go line."></p>

## Make it yours
Every page reads one `style.json`: your colours, your fonts, your handle and your own words on the to-do line and the card backs.
Two come bundled: [Rocha's look](examples/style.rocha-coded.json) as the finished example, and a [blank one](style.example.json) to fill in. Or ask Claude to make yours from a few screenshots you love. The keys are in [STYLE.md](STYLE.md).
The same file works across every Rocha Coded tool, so you make it once.

## What's inside
| Path | What it is |
|---|---|
| `SKILL.md` | The instructions Claude follows for all four flows |
| `tarot/deck.json` | The 78 cards: name, structure with `{slots}`, example, when to pull |
| `tarot/pull.py`, `tarot/print.py` | The three-card pull and the printable deck |
| `launch/launch.py` | The launch arc, the moon page, the `.md` and the `.ics` |
| `week/week.py` | The Pocket Week page |
| `readback/merge.py` | Validates a read-back page and merges it into `tasks.md` |
| `STYLE.md`, `style.example.json`, `examples/style.rocha-coded.json` | Your look in one file, a blank to fill and Rocha's as the example |
| `core/` | Moon and season maths (Meeus), the calendar file writer, the printable look, the Chrome renderer |
| `examples/` | Sample cards, pages, a calendar file and a before and after `tasks.md` |
| `tests/` | `python3 -m unittest`. See [tests/TESTING.md](tests/TESTING.md) for what is and isn't tested |

## Licence
MIT. See [LICENSE](LICENSE). Copyright (c) 2026 Rochelle Livingstone / Thriving Era Studio.

## Made by Rocha

Rocha \
Brand Alchemist & AI Architect \
Author of *Brand Alchemy in the Thriving Era* \
Creator of [Conscious Founder OS](https://founders.thrivingera.com) \
Founder, [Thriving Era Studio](https://thrivingera.com)

I take female founders AI native in 7 days, and I build what they need next. \
Start with the audit: [thrivingera.com/audit](https://thrivingera.com/audit). \
Or book an exploratory call: [calendly.com/rochelle-thrivingera/exploratory-call](https://calendly.com/rochelle-thrivingera/exploratory-call). It is where we decide if we work together.

[Instagram @rocheverse](https://instagram.com/rocheverse) · [Substack](https://rochastone.substack.com) · [LinkedIn](https://www.linkedin.com/in/rochellelivingstonecosmic) · [More free tools](https://thrivingera.com/free) · [All tools on GitHub](https://github.com/RochaStone)
