# Testing

Run from the repo root:

```sh
python3 -m unittest -v
```

35 tests, standard library only. One test renders a real PDF and skips itself when no Chrome is found.

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
  and handle; keys it leaves out fall back to the bundled example; the fallback order finds
  `./style.json`; unsafe colours and font names are refused; both bundled style files share keys.

## What was checked by eye, not by test
- Every printable was rendered to PNG with headless Chrome on macOS and looked at: the wordiest cards fit at
  both sizes, the launch page fits one A4 sheet, the week page fits A5.

## Not verified
- A real print run on paper: cut lines, card stock and double-sided back alignment have not been tested on a
  physical printer.
- Claude Cowork end to end. The scripts are plain Python, but the Cowork sandbox was not run.
- Windows and Linux. Chrome detection covers their usual paths, but only macOS was run.
- The photo readback itself. Reading handwriting is the agent's vision, which these tests can't cover. Only
  the format and merge step after it is tested.
- Imports of `launch.ics` into Google, Apple and Outlook calendars. The file follows RFC 5545 and passes the
  test parser, but no calendar app was tried.
