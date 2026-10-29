"""HOOK ORACLE: the sets, the core words staying exact, and oracle.html in a real browser."""
import hashlib
import html
import importlib.util
import json
import re
import tempfile
import unittest
from pathlib import Path

from core import render
from core import style as S
import cards as C
import oracle
import pull

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "oracle.html"
spec = importlib.util.spec_from_file_location("tarot_print_oracle", ROOT / "tarot" / "print.py")
TP = importlib.util.module_from_spec(spec)
spec.loader.exec_module(TP)

# A fingerprint of the 78 cards' ids, structures, examples and "pull it when" lines, taken from
# deck.json before the cards moved to sets/core.json. Any change to a word changes it.
CORE_WORDS = "5d46bbdd2ed474c3bb5d6b37e4c64a578b5454f3e170ea76458681eb39a27367"
BANNED_REVERSED = ("yllautca", "ylpmis", "tsuj", "detnemucodnu", "yltsenoh em llet")


def fingerprint(cards: list[dict]) -> str:
    rows = [[c["id"], c["structure"], c["example"], c["when_to_pull"]] for c in cards]
    return hashlib.sha256(json.dumps(rows, ensure_ascii=False).encode()).hexdigest()


def probe(page_hash: str, width: int) -> dict:
    """Open oracle.html in an iframe of the given width and read back what its test hook reports."""
    with tempfile.TemporaryDirectory() as d:
        p = Path(d, "probe.html")
        p.write_text(
            f"<!doctype html><body style='margin:0'><iframe id='f' src='{PAGE.as_uri()}#{page_hash}' "
            f"style='width:{width}px;height:900px;border:0'></iframe><script>"
            "var t=setInterval(function(){var d=document.getElementById('f').contentDocument;"
            "if(d&&d.body&&d.body.dataset.ready){document.body.setAttribute('data-r',JSON.stringify(d.body.dataset));"
            "clearInterval(t);}},50);</script></body>", encoding="utf-8")
        ok, dom = render.dump_dom(p, max(width + 20, 500), 900)
    assert ok, dom[-300:]
    m = re.search(r'data-r="([^"]*)"', dom)
    assert m, "oracle.html did not report back"
    return json.loads(html.unescape(m.group(1)))


class SetTests(unittest.TestCase):
    def test_core_words_unchanged(self):
        core = json.loads((ROOT / "tarot" / "sets" / "core.json").read_text(encoding="utf-8"))
        self.assertEqual(len(core["cards"]), 78)
        self.assertEqual(fingerprint(core["cards"]), CORE_WORDS)
        self.assertEqual(fingerprint(pull.load_deck()["cards"]), CORE_WORDS)

    def test_every_set_has_the_shape(self):
        sets = pull.load_sets()
        self.assertEqual(list(sets)[0], "core")
        for key, s in sets.items():
            for k in pull.SET_KEYS:
                self.assertIn(k, s, key)
            self.assertRegex(s["released"], r"^\d{4}-\d{2}-\d{2}$")
            for c in s["cards"]:
                for k in ("id", "arcana", "name", "structure", "example", "when_to_pull"):
                    self.assertTrue(str(c.get(k, "")).strip(), f"{key} {c.get('name')} {k}")
                self.assertRegex(c["structure"], r"\{[^{}]+\}")
                self.assertNotRegex(c["example"], r"[{}]")
                self.assertEqual(c["set"], key)
        ids = [c["id"] for s in sets.values() for c in s["cards"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_samhain_set(self):
        s = pull.load_sets()["samhain-2026"]
        self.assertEqual(s["name"], "Samhain 2026")
        self.assertEqual(len(s["cards"]), 8)
        text = json.dumps(s, ensure_ascii=False)
        self.assertNotIn(chr(0x2014), text)
        for word in BANNED_REVERSED:
            self.assertNotRegex(text.lower(), r"\b" + word[::-1] + r"\b")
        for c in s["cards"]:
            self.assertTrue((C.OBJECTS / c["object"]).is_file(), c["object"])
            front = C.front_html(c, "analog")
            self.assertIn("Samhain 2026", front)
            self.assertIn(c["object"], front)
        self.assertIn("HOOK ORACLE &middot; Samhain 2026", C.back_html("analog", set_name="Samhain 2026"))

    def test_load_and_draw_with_a_set(self):
        deck = pull.load_deck(sets=["core", "samhain-2026"])
        self.assertEqual(len(deck["cards"]), 86)
        with self.assertRaises(SystemExit):
            pull.load_deck(sets=["core", "no-such-set"])
        seen = {c["set"] for seed in range(40) for c in pull.draw(deck, 3, seed=seed)}
        self.assertEqual(seen, {"core", "samhain-2026"})
        text = pull.as_text(pull.spread(deck, pull.draw(deck, 3, seed=2), "a", "b"))
        self.assertTrue(text.startswith("HOOK ORACLE three-card pull"))

    def test_a_set_prints_as_its_own_deck(self):
        S.use(str(S.BUNDLED))
        cards = pull.load_deck(sets=["samhain-2026"])["cards"]
        page = TP.build_html(cards, "tarot", "a4", "interleave", "analog", "Samhain 2026")
        self.assertEqual(page.count("class='sheet'"), 4)
        self.assertEqual(page.count("HOOK ORACLE &middot; Samhain 2026"), 8)
        self.assertNotIn("Hook Tarot", page)

    def test_spreads(self):
        spreads = pull.load_deck()["spreads"]
        self.assertEqual([len(spreads[k]) for k in ("one", "two", "three")], [1, 2, 3])
        self.assertTrue(7 <= len(spreads["full"]) <= 10)
        self.assertEqual([p["label"] for p in spreads["three"]],
                         ["What they believe", "What you'll say", "What they'll do"])


class OraclePageTests(unittest.TestCase):
    def setUp(self):
        S.use(str(S.BUNDLED))

    def test_page_is_current_and_travels(self):
        page = PAGE.read_text(encoding="utf-8")
        self.assertEqual(page, oracle.build(), "oracle.html is stale: run python3 tarot/oracle.py "
                                               "--style examples/style.rocha-coded.json")
        self.assertIn("<title>ROCHEVERSE HOOK ORACLE</title>", page)
        self.assertNotIn("file:///", page)  # no absolute paths to this machine
        self.assertNotRegex(page, r"<script[^>]+src=")
        hosts = set(re.findall(r"https?://([a-z0-9.-]+)", page))
        self.assertLessEqual(hosts, {"fonts.googleapis.com", "fonts.gstatic.com", "www.w3.org"})  # w3.org: SVG namespace, never fetched
        for src in set(re.findall(r"tarot/objects/([a-z0-9-]+\.png)", page)):
            self.assertTrue((C.OBJECTS / src).is_file(), src)
        self.assertNotIn(chr(0x2014), page)
        self.assertNotIn("base64", page)  # tiles are drawn in the browser, so the key scan stays clean

    @unittest.skipUnless(render.find_chrome(), "no Chrome on this machine")
    def test_three_card_pull_reveals_three_distinct_cards(self):
        r = probe("auto=three&seed=7&reveal=all", 1080)
        ids = r["dealt"].split(",")
        self.assertEqual(len(ids), 3)
        self.assertEqual(len(set(ids)), 3)
        self.assertEqual(r["revealed"], "3")

    @unittest.skipUnless(render.find_chrome(), "no Chrome on this machine")
    def test_full_spread_fits_a_phone_and_exports_a_story(self):
        r = probe("auto=full&seed=3&reveal=all&export=1&sets=samhain-2026", 390)
        self.assertTrue(7 <= int(r["slots"]) <= 10)
        self.assertEqual(r["revealed"], r["slots"])
        self.assertLessEqual(int(r["sw"]), 390)
        self.assertEqual(r["export"], "1080x1920")
        self.assertEqual(r["exportPng"], "1")


if __name__ == "__main__":
    unittest.main()
