"""Three motif families from one render path: analog, cyberpunk, y2k-blog."""
import importlib.util
import json
import re
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from core import motif as M
from core import render
from core import style as S
import launch as L
import launch_html as LH
import week as W

ROOT = Path(__file__).resolve().parent.parent
SIGNATURES = {
    "launch": {"analog": ["sheet lined", "Sacred launch calendar"],
               "cyberpunk": ["rocheverse:~$", "class='blocks'", "class='leds'"],
               "y2k-blog": ["launch.exe", "you are visitor no.", "guestbook"]},
    "week": {"analog": ["week lined", "class='moons'"],
             "cyberpunk": ["rocheverse:~$", "class='keypad'"],
             "y2k-blog": ["thisweek.exe", "you are visitor no.", "mood"]},
}


def launch_html(motif):
    return LH.to_html(L.plan("Spring Breath Retreat", date(2026, 11, 2), 6, timedelta(0)), motif)


def week_html(motif):
    return W.build_html(date(2026, 11, 23), timedelta(0), motif=motif)


class MotifTests(unittest.TestCase):
    def setUp(self):
        S.use(str(S.BUNDLED))

    def test_each_motif_has_its_signature(self):
        for page, build in (("launch", launch_html), ("week", week_html)):
            for motif, marks in SIGNATURES[page].items():
                html = build(motif)
                for mark in marks:
                    self.assertIn(mark, html, f"{page} {motif} missing {mark}")
                others = [m for m in M.MOTIFS if m != motif]
                for other in others:
                    self.assertNotIn(SIGNATURES[page][other][0], html, f"{page} {motif} leaks {other}")

    def test_same_data_in_every_motif(self):
        for motif in M.MOTIFS:
            html = launch_html(motif)
            for beat in ("tell the origin story", "open the doors", "rest and debrief"):
                self.assertIn(beat, html, motif)
            self.assertIn("Tue 24 Nov", html, motif)  # the full moon

    def test_aliases_and_unknown(self):
        self.assertEqual(M.resolve("guest-check"), "analog")
        self.assertEqual(M.resolve("retro-tv"), "cyberpunk")
        self.assertEqual(M.resolve("sticker-collage"), "y2k-blog")
        with self.assertRaises(SystemExit):
            M.resolve("vaporwave")

    def test_style_json_picks_the_motif(self):
        self.assertEqual(M.resolve(), "analog")  # the bundled example
        with tempfile.TemporaryDirectory() as d:
            path = Path(d, "style.json")
            path.write_text(json.dumps({"motif": "y2k-blog"}))
            S.use(str(path))
            self.assertIn("thisweek.exe", week_html(None))
            self.assertIn("rocheverse:~$", week_html("cyberpunk"))  # --motif still wins
        S.use(str(S.BUNDLED))

    def test_tarot_back_pixel_stamp_in_cyberpunk(self):
        spec = importlib.util.spec_from_file_location("tarot_print_motif", ROOT / "tarot" / "print.py")
        tp = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tp)
        self.assertIn("lore pixel", tp.back("tarot", 0, 0, "cyberpunk"))
        self.assertNotIn("lore pixel", tp.back("tarot", 0, 0, "analog"))

    def test_pixel_svgs_are_tiny(self):
        self.assertLess(len(M.star("3mm")), 600)
        self.assertLess(len(M.heart("3mm")), 600)

    @unittest.skipUnless(render.find_chrome(), "no Chrome on this machine")
    def test_every_motif_prints_on_one_page_and_fits_a_phone(self):
        with tempfile.TemporaryDirectory() as d:
            for page, build in (("launch", launch_html), ("week", week_html)):
                for motif in M.MOTIFS:
                    html = build(motif)
                    path = Path(d, f"{page}-{motif}.html")
                    path.write_text(html, encoding="utf-8")
                    pdf = Path(d, f"{page}-{motif}.pdf")
                    ok, err = render.html_to_pdf(path, pdf)
                    self.assertTrue(ok, err)
                    pages = len(re.findall(rb"/Type\s*/Page(?![a-zA-Z])", pdf.read_bytes()))
                    self.assertEqual(pages, 1, f"{page} {motif} printed {pages} pages")
                    # headless Chrome won't open a window narrower than 500px, so the page goes
                    # in a 390px iframe: a real phone-width viewport for its media queries
                    probe = Path(d, f"{page}-{motif}-phone.html")
                    probe.write_text(
                        f"<!doctype html><body><iframe id='f' src='{path.name}' style='width:390px;height:844px;border:0'"
                        " onload=\"document.body.dataset.sw=this.contentDocument.documentElement.scrollWidth\">"
                        "</iframe></body>", encoding="utf-8")
                    ok, dom = render.dump_dom(probe, 800, 900)
                    self.assertTrue(ok)
                    width = int(re.search(r'data-sw="(\d+)"', dom).group(1))
                    self.assertLessEqual(width, 390, f"{page} {motif} is {width}px wide on a phone")


if __name__ == "__main__":
    unittest.main()
