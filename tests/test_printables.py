"""The printables build as HTML without a browser, and render with one when present."""
import importlib.util
import tempfile
import contextlib
import io
import unittest
from datetime import date, timedelta
from pathlib import Path

from core import render
from core.style import moon_svg
import week as W

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("tarot_print", ROOT / "tarot" / "print.py")
TP = importlib.util.module_from_spec(spec)
spec.loader.exec_module(TP)


def quiet(fn, args):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return fn(args)


class PrintableTests(unittest.TestCase):
    def test_tarot_html_pages(self):
        deck = TP.load_deck()
        html = TP.build_html(deck["cards"], "tarot", "a4", "interleave")
        self.assertEqual(html.count("class='sheet'"), 40)  # 20 fronts + 20 backs
        self.assertEqual(html.count("class='card'"), 78)
        self.assertEqual(html.count("class='card back'"), 78)
        mini = TP.build_html(deck["cards"], "mini", "letter", "end")
        self.assertEqual(mini.count("class='sheet'"), 10)  # 9 fronts + 1 back page
        self.assertIn("<b>{result}</b>", TP.slotted("Receipt for {result}."))

    def test_layouts_fit_paper(self):
        for size, (cw, ch, cols, rows, _) in TP.SIZES.items():
            for paper, (pw, ph) in TP.PAPERS.items():
                self.assertGreaterEqual(pw - cols * cw, 6, f"{size} {paper} width")
                self.assertGreaterEqual(ph - rows * ch, 6, f"{size} {paper} height")

    def test_week_html(self):
        html = W.build_html(date(2026, 11, 23), timedelta(0), fill={"one_thing": "Open <b>"})
        self.assertIn("THIS<br>WEEK", html)
        self.assertIn("full moon", html)  # 24 Nov 2026
        self.assertIn("Open &lt;b&gt;", html)
        self.assertEqual(html.count("class='move'"), 3)
        self.assertEqual(W.monday_on_or_after(date(2026, 10, 26)), date(2026, 10, 26))
        self.assertEqual(W.monday_on_or_after(date(2026, 10, 28)), date(2026, 11, 2))

    def test_moon_svg_shapes(self):
        self.assertIn("scale(-1,1)", moon_svg(0.7, 5))          # waning, northern sky: mirrored
        self.assertNotIn("scale(-1,1)", moon_svg(0.7, 5, "south"))
        self.assertNotIn("scale(-1,1)", moon_svg(0.2, 5))

    @unittest.skipUnless(render.find_chrome(), "no Chrome on this machine")
    def test_week_pdf_renders(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(quiet(W.main, ["--out", d, "--start", "2026-11-02"]), 0)
            pdf = Path(d, "week.pdf")
            self.assertTrue(pdf.exists())
            self.assertTrue(pdf.read_bytes().startswith(b"%PDF"))


if __name__ == "__main__":
    unittest.main()
