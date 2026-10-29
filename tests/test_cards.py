"""The HOOK ORACLE card template: the words stay exact, three motifs, your own art, and no overflow."""
import html
import importlib.util
import json
import re
import tempfile
import unittest
from pathlib import Path

from core import motif as M
from core import render
from core import style as S
import cards as C
import pull

ROOT = Path(__file__).resolve().parent.parent
DECK = pull.load_deck()
spec = importlib.util.spec_from_file_location("tarot_print_cards", ROOT / "tarot" / "print.py")
TP = importlib.util.module_from_spec(spec)
spec.loader.exec_module(TP)

# Measures every card once fonts are in: the stub sits inside the gold frame, the object
# area keeps room, and no text runs outside its box (the text itself is measured, so the
# offset second ink never counts).
PROBE = """<script>
document.fonts.ready.then(function () {
  var bad = [];
  document.querySelectorAll('.card:not(.back)').forEach(function (card) {
    var r = card.getBoundingClientRect(), w = r.width, id = card.querySelector('.no').textContent;
    var stub = card.querySelector('.stub').getBoundingClientRect();
    if (stub.bottom > r.bottom - 0.024 * w + 1) bad.push(id + ' stub below the frame');
    if (card.querySelector('.hero').getBoundingClientRect().height < 0.2 * w) bad.push(id + ' object squeezed');
    ['.structure', '.name', '.when', '.ex'].forEach(function (sel) {
      var el = card.querySelector(sel);
      if (!el || getComputedStyle(el).display === 'none') return;
      var range = document.createRange(); range.selectNodeContents(el);
      var t = range.getBoundingClientRect(), b = el.getBoundingClientRect();
      var tall = sel !== '.name' && t.bottom > b.bottom + 1;  // the display face's tight leading is meant to overhang
      if (t.width > b.width + 1 || tall) bad.push(id + ' ' + sel + ' too wide (' + Math.round(t.width) + '/' + Math.round(b.width) + ')');
    });
  });
  document.body.setAttribute('data-bad', JSON.stringify(bad));
  document.body.setAttribute('data-n', document.querySelectorAll('.card:not(.back)').length);
});
</script>"""


def text_of(fragment: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", fragment))


def block(front: str, cls: str) -> str:
    m = re.search(rf"<div class='{cls}'[^>]*>(.*?)</div>", front, re.S)
    return m.group(1) if m else ""


class CardTests(unittest.TestCase):
    def setUp(self):
        S.use(str(S.BUNDLED))

    def tearDown(self):
        S.use(str(S.BUNDLED))

    def test_structure_text_unchanged_on_every_card(self):
        for motif in M.MOTIFS:
            for card in DECK["cards"]:
                front = C.front_html(card, motif)
                self.assertEqual(text_of(block(front, "structure")), card["structure"], f"{card['name']} {motif}")
                self.assertEqual(text_of(block(front, r"ex torn-ex")), card["example"], card["name"])
                self.assertIn(html.escape(card["when_to_pull"], quote=True), front, card["name"])
                self.assertIn(f">{html.escape(card['name'])}</div>", front, card["name"])
                self.assertEqual(front.count("class='blank'"), card["structure"].count("{"), card["name"])

    def test_each_motif_has_its_chrome(self):
        card = DECK["cards"][2]
        marks = {"analog": None, "cyberpunk": "rocheverse:~$", "y2k-blog": "the-receipt.txt"}
        for motif, mark in marks.items():
            front = C.front_html(card, motif)
            self.assertIn(f"m-{motif}", front)
            if mark:
                self.assertIn(mark, front)
            others = [v for k, v in marks.items() if k != motif and v]
            for other in others:
                self.assertNotIn(other, front, f"{motif} leaks {other}")
        self.assertIn("lore pixel", C.back_html("cyberpunk"))
        self.assertIn("lore holo", C.back_html("analog"))

    def test_all_22_majors_are_painted(self):
        for f in set(C.MAJOR_OBJECT.values()) | {x for s in C.SUITS.values() for x in s[2:]}:
            self.assertTrue((C.OBJECTS / f).is_file(), f)
        self.assertEqual(sorted(C.MAJOR_OBJECT), [c["id"] for c in DECK["cards"][:22]])
        self.assertIn("All 22 Major Arcana are painted", (ROOT / "docs" / "MAJORS-TO-PAINT.md").read_text(encoding="utf-8"))
        for card in DECK["cards"][:22]:
            front = C.front_html(card, "analog")
            self.assertIn(C.MAJOR_OBJECT[card["id"]], front, card["name"])
            self.assertNotIn("hero type", front, card["name"])
        door = C.front_html(DECK["cards"][9], "analog")
        self.assertIn("obj major framed", door)  # a vignette: drop shadow, no white outline
        self.assertNotIn("framed", C.front_html(DECK["cards"][8], "analog"))

    def test_a_missing_painting_falls_back_to_the_pixel_sticker(self):
        by = {c["id"]: c for c in DECK["cards"]}
        with tempfile.TemporaryDirectory() as d:
            for f in C.MAJOR_OBJECT.values():
                if f != "door.png":
                    Path(d, f).write_bytes((C.OBJECTS / f).read_bytes())
            real, C.OBJECTS = C.OBJECTS, Path(d)
            try:
                painted = C.front_html(by["major-08"], "analog")
                waiting = C.front_html(by["major-09"], "analog")
            finally:
                C.OBJECTS = real
        self.assertIn("envelope.png", painted)
        self.assertNotIn("hero type", painted)
        self.assertIn("hero type px", waiting)  # door.png gone: the pixel sticker stands in
        self.assertNotIn("door.png", waiting)

    def test_your_own_objects_and_font_file(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, "art").mkdir()
            Path(d, "art", "cup.png").write_bytes(b"\x89PNG\r\n\x1a\n")
            Path(d, "MyHand.woff2").write_bytes(b"wOF2")
            Path(d, "style.json").write_text(json.dumps({
                "fonts": {"scrawl": "My Hand"}, "font_files": {"scrawl": "MyHand.woff2"},
                "tarot": {"objects": {"cups": "art/cup.png", "The Receipt": "none", "wands": "missing.png"}}}))
            S.use(str(Path(d, "style.json")))
            by = {c["name"]: c for c in DECK["cards"]}
            self.assertIn("art/cup.png", C.front_html(by["Ace of Cups"], "analog"))
            self.assertIn("hero type", C.front_html(by["The Receipt"], "analog"))
            self.assertIn("pillar-candle.png", C.front_html(by["Ace of Wands"], "analog"))  # bad path falls back
            page = TP.build_html([by["Ace of Cups"]], "tarot", "a4", "none")
            self.assertIn("@font-face{font-family:'My Hand';src:url('file://", page)
            self.assertNotIn("family=My+Hand", page)

    @unittest.skipUnless(render.find_chrome(), "no Chrome on this machine")
    def test_three_motifs_and_three_sizes_print_without_overflow(self):
        cards = pull.load_deck(sets=list(pull.load_sets()))["cards"]
        with tempfile.TemporaryDirectory() as d:
            jobs = [(f"{m}-tarot", TP.build_html(cards, "tarot", "a4", "none", m)) for m in M.MOTIFS]
            jobs.append(("mini", TP.build_html(cards, "mini", "letter", "none", "analog")))
            story_css = (":root{--cw:1080px;--ch:1920px}" + C.css() + ".card{position:relative}")
            body = C.fonts_extra() + f"<style>{C.tile_css()}</style>" + "".join(
                C.front_html(c, "cyberpunk", None, None, "what you'll say") for c in cards[::5])
            jobs.append(("story", S.page("story probe", story_css, body)))
            for name, page in jobs:
                path = Path(d, f"{name}.html")
                path.write_text(page.replace("</body>", PROBE + "</body>"), encoding="utf-8")
                ok, dom = render.dump_dom(path, 1200, 900)
                self.assertTrue(ok, name)
                count = int(re.search(r'data-n="(\d+)"', dom).group(1))
                self.assertEqual(count, len(cards) if name != "story" else len(cards[::5]), name)
                bad = json.loads(html.unescape(re.search(r'data-bad="([^"]*)"', dom).group(1)))
                self.assertEqual(bad, [], f"{name}: {bad[:6]}")


if __name__ == "__main__":
    unittest.main()
