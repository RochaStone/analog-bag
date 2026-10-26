"""Readback merge: validation, dedupe, done state."""
import tempfile
import contextlib
import io
import unittest
from pathlib import Path

import merge as M

OLD = """# Tasks

## This week 2026-11-02
- [ ] Write the welcome email {due: 2026-11-03}
- [x] Tell the origin story
- [ ] Book the photographer
> number: waitlist 40

## Someday
"""

NEW = """## This week 2026-11-02
- [x] write the welcome email!
- [ ] Tell the origin story
- [ ] Book the photographer {due: 2026-11-06}
- [ ] Send the waitlist letter
> number: waitlist 40
> number: waitlist 58 by Sunday

## Launch: Spring Breath Retreat
- [ ] open the doors {due: 2026-11-17}
- [ ] open the doors
"""


def quiet(fn, args):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return fn(args)


class MergeTests(unittest.TestCase):
    def merged(self):
        return M.merge(M.parse(OLD), M.parse(NEW))

    def test_counts(self):
        _, stats = self.merged()
        self.assertEqual(stats, {"added": 2, "ticked": 1, "duplicates": 4, "notes": 1, "sections": 1})

    def test_done_wins_and_never_unticks(self):
        doc, _ = self.merged()
        tasks = {t.key: t for s in doc.sections for t in s.items if isinstance(t, M.Task)}
        self.assertTrue(tasks["write the welcome email"].done)   # ticked on the page
        self.assertTrue(tasks["tell the origin story"].done)     # stays ticked
        self.assertEqual(tasks["write the welcome email"].due, "2026-11-03")  # old due kept
        self.assertEqual(tasks["book the photographer"].due, "2026-11-06")    # due added

    def test_sections_and_render_roundtrip(self):
        doc, _ = self.merged()
        names = [s.name for s in doc.sections]
        self.assertEqual(names, ["This week 2026-11-02", "Someday", "Launch: Spring Breath Retreat"])
        text = M.render(doc)
        again, stats = M.merge(M.parse(text), M.parse(NEW))
        self.assertEqual(stats["added"], 0)
        self.assertEqual(M.render(again), text)

    def test_validation_errors(self):
        bad = "## Week\n- [ ] fine\n* bullet\n- [ ] x {due: next friday}\n"
        with self.assertRaises(M.FormatError) as cm:
            M.parse(bad, "bad.md")
        msg = str(cm.exception)
        self.assertIn("bad.md:3", msg)
        self.assertIn("bad.md:4", msg)
        with self.assertRaises(M.FormatError):
            M.parse("- [ ] task before any section\n")

    def test_cli_creates_file_and_refuses_bad_input(self):
        with tempfile.TemporaryDirectory() as d:
            tasks, new, bad = Path(d, "tasks.md"), Path(d, "new.md"), Path(d, "bad.md")
            new.write_text(NEW)
            self.assertEqual(quiet(M.main, [str(tasks), str(new)]), 0)
            self.assertIn("- [ ] open the doors {due: 2026-11-17}", tasks.read_text())
            before = tasks.read_text()
            bad.write_text("## X\nnot a task\n")
            self.assertEqual(quiet(M.main, [str(tasks), str(bad)]), 2)
            self.assertEqual(tasks.read_text(), before)
            self.assertEqual(quiet(M.main, ["--check", str(tasks)]), 0)


if __name__ == "__main__":
    unittest.main()
