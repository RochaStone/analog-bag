# Testing

Run from the repo root:

```sh
python3 -m unittest -v
```

58 tests, standard library only. The tests that open Chrome (PDFs, overflow, oracle.html) skip themselves when no Chrome is found.

## What the tests prove
- **Moon phases.** All 13 full moons of 2026 land within one day, and in fact within two minutes, of NASA GSFC's
  phase table (eclipse.gsfc.nasa.gov/phase/phases2001.html, times in UT). Measured across all 50 phases of 2026,
  the largest difference is under one minute. The eclipse new moons (17 Feb, 12 Aug) and two quarters are
  checked too, and 2025, 2030 and 2040 are checked for a sane phase rhythm.
- **Equinoxes and solstices.** All four of 2026 land within five minutes of the published UT times.
- **Launch arc.** Six stages in order, no gaps, every beat inside its stage, stages snapping to the real new and
  full moons, the UTC offset moving a phase to the next local day, windows of 4 to 12 weeks.
- **The .ics.** Parsed by a small independent reader in the test: CRLF line ends, lines folded at 75 octets,
  BEGIN and END nesting, every VEVENT with UID, DTSTAMP, DTSTART, DTEND and SUMMARY, unique UIDs, commas and
  semicolons escaped. The event count equals beats plus moon phases.
- **The deck.** 78 cards, 22 Major Arcana, 14 per suit in rank order, every structure has `{slots}`, no
  example has a leftover slot, unique names, no em dashes or banned words, repeatable seeded draws.
- **Readback merge.** Dedupe across sections, done wins and never unticks, due dates kept or added, notes never
  duplicated, merge is stable when run twice, bad lines are reported with line numbers and nothing is written.
- **Printables.** The deck builds 40 pages (20 fronts, 20 backs) at tarot size and 10 at mini size, both card
  layouts fit A4 and Letter with margins, the week page escapes what it prints, and the moon drawing mirrors
  for waning moons and the southern sky.

- **Style.** A second `style.json` renders the week page with its own to-do line, hero colour, font
  and handle. A user's file borrows only missing colours and fonts from the bundled example: her
  lines, name, handle, site, references and notes stay blank, and the week page and card back show
  none of Rocha's words. The fallback order finds `./style.json`; unsafe colours and font names are refused; both bundled style files share keys.

- **Looks (motifs).** The launch page and the pocket week render in analog, cyberpunk and y2k-blog,
  each with its own signature (the lined sheet, the `rocheverse:~$` prompt and block progress, the
  `launch.exe` window and hit counter) and none of the others'. Every look carries the same beats and
  moon dates. Old motif names map to a family, an unknown one is refused, style.json picks the
  default and `--motif` overrides it. With Chrome present, every look of both pages prints as exactly
  one PDF page and is no wider than a 390px phone screen (measured in a 390px frame, because headless
  Chrome will not open a window narrower than 500px).

- **HOOK ORACLE sets.** The 78 core cards in `tarot/sets/core.json` match a fingerprint of every id,
  structure, example and "pull it when" line taken before the move, so no word changed. Every set file has
  the set shape, unique ids and open slots. The Samhain 2026 set has eight cards, real objects, its name on
  the face and the back, and none of the banned words. A set prints as its own deck, and a draw with a set
  mixes both.
- **Painted majors.** A major uses its painted PNG when the file is in `tarot/objects/`, and keeps its pixel
  sticker when the file is missing (both branches run against a temporary objects folder). The paint list
  and the code agree.
- **oracle.html.** The committed page equals a fresh build, carries no absolute paths, loads nothing beyond
  Google Fonts, and every object it points at exists. In headless Chrome: a three-card pull reveals three
  distinct cards; the full spread with the Samhain set on reveals every card, stays within a 390px phone
  width, and the story export is a 1080 x 1920 PNG.

## What was checked by eye, not by test
- oracle.html at 390 and 1080 wide, mid-reveal, served from a local folder and opened in Chromium: the
  riffle, the flip, the riso flash, the live pink blanks and a saved full-spread story.
- Every printable was rendered to PNG with headless Chrome on macOS and looked at: the wordiest cards fit at
  both sizes, the launch page fits one A4 sheet, the week page fits A5.

## Not verified
- A real print run on paper: cut lines, card stock and double-sided back alignment have not been tested on a
  physical printer.
- oracle.html in Safari and Firefox, and on a real phone. Only Chromium was run.
- The reveal sound. It is synthesised in the browser and was not listened to in a test.
- Claude Cowork end to end. The scripts are plain Python, but the Cowork sandbox was not run.
- Windows and Linux. Chrome detection covers their usual paths, but only macOS was run.
- The photo readback itself. Reading handwriting is the agent's vision, which these tests can't cover. Only
  the format and merge step after it is tested.
- Imports of `launch.ics` into Google, Apple and Outlook calendars. The file follows RFC 5545 and passes the
  test parser, but no calendar app was tried.
