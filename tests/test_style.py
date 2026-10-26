"""One style.json drives the look: a second style changes the week page."""
import json
import os
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from core import style as S
import week as W

SECOND = {
    "name": "Sea Salt Studio",
    "handle": "@seasaltstudio",
    "palette": {"hero": "#1F6F8B", "accent": "#9AD0DC", "paper_pink": "#EAF6F8"},
    "fonts": {"masthead": "Cormorant Garamond"},
    "lines": {"todo": "TO DO: SWIM BEFORE EMAIL", "stamp": "TIDE"},
}


class StyleTests(unittest.TestCase):
    def tearDown(self):
        S.use(str(S.BUNDLED))

    def week_html(self):
        return W.build_html(date(2026, 11, 23), timedelta(0))

    def test_second_style_changes_week_page(self):
        S.use(str(S.BUNDLED))
        rocha = self.week_html()
        self.assertIn("TO DO: BUILD YOUR FOUNDER WORLD", rocha)
        self.assertIn("--hot:#FF2D8A", rocha)
        with tempfile.TemporaryDirectory() as d:
            path = Path(d, "style.json")
            path.write_text(json.dumps(SECOND))
            S.use(str(path))
            theirs = self.week_html()
        self.assertIn("TO DO: SWIM BEFORE EMAIL", theirs)
        self.assertNotIn("BUILD YOUR FOUNDER WORLD", theirs)
        self.assertIn("--hot:#1F6F8B", theirs)
        self.assertNotIn("#FF2D8A", theirs)
        self.assertIn("'Cormorant Garamond'", theirs)
        self.assertIn("@seasaltstudio", theirs)
        self.assertIn("--plum:#4A1033", theirs)  # keys left out fall back to the example

    def test_fallback_order_and_bad_values(self):
        with tempfile.TemporaryDirectory() as d:
            old = os.getcwd()
            try:
                os.chdir(d)
                if not (Path.home() / ".rocha-coded" / "style.json").exists():
                    self.assertEqual(S.find_style(), S.BUNDLED)
                Path(d, "style.json").write_text(json.dumps(
                    {"palette": {"hero": "red;}</style>"}, "fonts": {"body": "x'</style>"}, "lines": {"todo": ""}}))
                self.assertEqual(S.find_style().resolve(), Path(d, "style.json").resolve())
                st = S.use()
            finally:
                os.chdir(old)
        self.assertEqual(st["palette"]["hero"], "#FF2D8A")  # unsafe colour refused
        self.assertEqual(st["fonts"]["body"], "Newsreader")  # unsafe font name refused
        self.assertEqual(st["lines"]["todo"], "TO DO: BUILD YOUR FOUNDER WORLD")  # blank falls back

    def test_bundled_files_share_keys(self):
        root = Path(S.__file__).resolve().parent.parent
        rocha = json.loads(S.BUNDLED.read_text())
        blank = json.loads((root / "style.example.json").read_text())
        self.assertEqual(set(rocha), set(blank))
        for k in ("palette", "fonts", "lines"):
            self.assertEqual(set(rocha[k]), set(blank[k]), k)


if __name__ == "__main__":
    unittest.main()
