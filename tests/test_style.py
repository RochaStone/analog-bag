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
        self.assertIn("--ground:#50163C", rocha)
        with tempfile.TemporaryDirectory() as d:
            path = Path(d, "style.json")
            path.write_text(json.dumps(SECOND))
            S.use(str(path))
            theirs = self.week_html()
        self.assertIn("TO DO: SWIM BEFORE EMAIL", theirs)
        self.assertNotIn("BUILD YOUR FOUNDER WORLD", theirs)
        self.assertIn("--ground:#1F6F8B", theirs)
        self.assertNotIn("--ground:#50163C", theirs)
        self.assertIn("'Cormorant Garamond'", theirs)
        self.assertIn("@seasaltstudio", theirs)
        self.assertIn("--plum:#50163C", theirs)  # keys left out fall back to the example

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
        self.assertEqual(st["palette"]["hero"], "#50163C")  # unsafe colour refused
        self.assertEqual(st["fonts"]["body"], "Fraunces")  # unsafe font name refused
        self.assertEqual(st["lines"]["todo"], "")  # her words never fall back

    def test_user_style_never_inherits_her_words(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "tarot_print_style", Path(S.__file__).resolve().parent.parent / "tarot" / "print.py")
        tp = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tp)
        with tempfile.TemporaryDirectory() as d:
            path = Path(d, "style.json")
            path.write_text(json.dumps({"palette": {"hero": "#1F6F8B"}}))
            st = S.use(str(path))
            week = self.week_html()
            card_back = tp.back("tarot", 0, 0)
        self.assertEqual(st["palette"]["plum"], "#50163C")    # palette may fall back
        self.assertEqual(st["fonts"]["scrawl"], "Permanent Marker")  # fonts may fall back
        self.assertTrue(all(v == "" for v in st["lines"].values()))
        for k in ("name", "owner", "handle", "site", "notes"):
            self.assertEqual(st[k], "", k)
        self.assertEqual(st["references"], [])
        for html in (week, card_back):
            for hers in ("FOUNDER WORLD", "founder world", "LORE", "@rocheverse", "ROCHEVERSE"):
                self.assertNotIn(hers, html)
        S.use(str(S.BUNDLED))
        self.assertIn("LORE", tp.back("tarot", 0, 0))  # her lines appear only with her whole file

    def test_bundled_files_share_keys(self):
        root = Path(S.__file__).resolve().parent.parent
        rocha = json.loads(S.BUNDLED.read_text())
        blank = json.loads((root / "style.example.json").read_text())
        self.assertEqual(set(rocha), set(blank))
        for k in ("palette", "fonts", "lines"):
            self.assertEqual(set(rocha[k]), set(blank[k]), k)


if __name__ == "__main__":
    unittest.main()
