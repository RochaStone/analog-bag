---
name: analog-bag
description: A printable founder kit for planning offline, in pen. Hook Tarot (78 hook structures as a printable deck, plus a three-card pull), Sacred Launch Calendar (a launch arc laid on the real moon phases, with an .ics), Pocket Week (an A5 weekly page) and readback (photograph a filled page and merge it into tasks.md). Use when the user says "hook tarot", "pull three cards", "launch calendar", "moon phase launch", "pocket week", "read my page", or asks for printable planning pages, hooks from a tarot deck, or a moon-timed launch.
---

# Analog Bag

Four flows. Python 3.10+ standard library only. Headless Chrome (or Chromium or Edge) turns
the pages into PDFs; without it every printable is still written as HTML the user can open and
print from any browser. Nothing needs the internet. Moon and season dates are computed locally.

Run every command from this skill's folder. Write outputs where the user wants them. In Claude
Cowork that is the folder they gave the task, for example `--out "<their folder>/analog-bag"`.
In Claude Code, default to `./analog-bag-out` in their current project unless they name a place.

Tell the user, in plain words, where each file landed and how to print it: actual size (100%),
margins none, background graphics on.

## 1. Hook Tarot

**Pull three cards** ("pull three cards", "hook tarot", "give me hooks"):

```sh
python3 tarot/pull.py --topic "<what it's about>" --audience "<who it's for>"
```

Optional: `--suit cups|wands|swords|pentacles`, `--majors`, `--seed N`, `--json`.

The draw is three positions: what they believe (past), what you'll say (present), what they'll
do (future). Then you do the writing:
1. Fill every `{slot}` in each structure with the user's topic and audience, in her words.
   Use what you know about her offer. Never invent numbers, results or client stories. If a
   slot needs a fact you don't have, leave it in brackets and ask for it.
2. Give the three filled hooks, then one line reading them as an arc (belief, turn, action).
3. Offer one redraw if a card doesn't fit. Don't redraw on your own.

Suits: Cups are story and feeling. Wands are contrarian and bold. Swords are questions and
challenges. Pentacles are numbers, proof and results. Major Arcana are big-idea hooks.

**Print the deck** ("print the tarot", "make the cards"):

```sh
python3 tarot/print.py --out <folder>                  # tarot size 70 x 120 mm, 4 per page
python3 tarot/print.py --out <folder> --size mini      # 63 x 88 mm, 9 per page
```

`--paper letter` for US paper. `--backs interleave` (default) alternates fronts and backs for a
double-sided print, flip on the long edge. `--backs end` adds one back page, `none` skips them.
Tell her: card stock, print at 100%, cut on the marks.

## 2. Sacred Launch Calendar

("launch calendar", "moon phase launch", "plan my launch with the moon"):

```sh
python3 launch/launch.py --offer "<offer name>" --date YYYY-MM-DD --weeks 6 --out <folder> \
  --utc-offset <+08:00> --hemisphere north
```

- `--date` is the first day of the launch window. Ask for it if she hasn't said.
- `--utc-offset` sets her clock so phases land on her local date. Ask her city if unsure; the
  default is this computer's clock, which inside Cowork may be UTC.
- `--hemisphere south` flips the season names and draws the moon as she sees it.
- `--align` moves the start to the nearest new moon. The script prints a tip when that's close.

It writes `launch.html` (one printable page), `launch.pdf`, `launch.md` and `launch.ics`. The six
stages are seed, build, open, peak, close and integrate. Each starts on a moon phase when one is
within three days, with two or three beats. Tell her the arc in a few lines: which stage meets
the full moon, when the doors open. Tell her the .ics imports into Google, Apple or Outlook
calendars as all-day events.

## 3. Pocket Week

("pocket week", "weekly page", "plan my week on paper"):

```sh
python3 week/week.py --out <folder>                 # the coming Monday, blank, A5
python3 week/week.py --out <folder> --two-up        # two copies on one A4 or Letter sheet
```

Optional prefill, only when she asks: `--one-thing "..."`, `--move "..."` (up to three),
`--number "..."`, `--let-go "..."`. Also `--start YYYY-MM-DD`, `--utc-offset`, `--hemisphere`.

## 4. Readback ("read my page", a photo of a filled page)

When she drops a photo of a filled page:

1. Look at the photo and read every handwritten line. A tick, cross, circled or struck-through
   item is done. If a word is unclear, write your best reading with `[?]` after it and ask her
   about those words only, once, before merging.
2. Write the page into a new file (for example `new.md`) in this exact format:

   ```
   ## Week of 2026-11-23
   - [x] Open the retreat waitlist
   - [ ] Book the venue walk-through {due: 2026-11-27}
   > number: waitlist signups, Monday 12, Sunday 31
   > let go: answering DMs after 8pm
   > win: three women replied to the origin story
   ```

   - One `## Section` per page. Pocket Week: `## Week of <Monday's date>`. Launch page:
     `## Launch: <offer name>`. Handwritten hooks: `## Hooks` with `- [ ] post: <hook>`.
   - Tasks are `- [ ] text` or `- [x] text`, with an optional `{due: YYYY-MM-DD}` when the page
     shows a date. Copy her words. Don't rephrase.
   - Everything that isn't a task is a note line starting with `> `: the number to watch, the
     let-go line, wins, margin thoughts.
3. Merge it:

   ```sh
   python3 readback/merge.py <her folder>/tasks.md new.md
   ```

   It creates `tasks.md` if there isn't one, never adds a task twice, and never unticks a done
   task. If it reports a format problem, fix `new.md` and run it again. Nothing is written until
   the format is clean. `--dry-run` shows the result first. `--check FILE` only validates.
4. Tell her what changed in one or two lines: what's newly done, what's new, what's still open.
   Delete `new.md` afterwards.

## Make it hers (style.json)

Every page reads one `style.json`: her palette, fonts, handle and her own lines (`lines.todo` on
the week page, `lines.stamp` and `lines.scrawl` on card backs and the launch page). The scripts
look for `--style PATH`, then `./style.json` in her folder, then `~/.rocha-coded/style.json`, then
the bundled example (`examples/style.rocha-coded.json`, Rocha's own look). Each script prints
which style it used. Her file borrows only missing colours and fonts from the example. Lines,
name and handle she leaves out stay blank on the page, never Rocha's words. The keys are in `STYLE.md`.

If she has no style.json, offer to make one before her first printable:
1. Ask for 3 to 5 references (screenshots, links, a Pinterest board), a palette if she has one,
   and the words she says a lot.
2. Look at the references. Start from `style.example.json`, fill it with colours and Google
   Fonts that match them, put her own words in `lines`, and her references in `references`.
3. Save it as `style.json` in her folder, render one sample (the Pocket Week is quickest) and
   show it to her. Adjust until she says yes.

Never assume her taste is Rocha's. Rocha's file is an example, not a default look to sell her.
The same file works in every Rocha Coded tool.

## Rules

- Plain, warm words. No em dashes. Never claim numbers she can't show.
- Never invent a client story, a quote or a result to fill a slot.
- Outputs go in her folder, never inside this skill folder.
- If Chrome is missing, say so once, hand her the HTML and the print settings. Don't try to
  install a browser unless she asks.
