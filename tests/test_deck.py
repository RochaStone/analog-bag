"""The Hook Tarot deck: shape, slots, voice rules and the draw."""
import re
import unittest

import pull

DECK = pull.load_deck()
RANKS = ["Ace", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten",
         "Page", "Knight", "Queen", "King"]


class DeckTests(unittest.TestCase):
    def test_78_cards_22_majors_14_per_suit(self):
        cards = DECK["cards"]
        self.assertEqual(len(cards), 78)
        self.assertEqual(sum(c["arcana"] == "major" for c in cards), 22)
        for suit in pull.SUITS:
            ranks = [c["rank"] for c in cards if c.get("suit") == suit]
            self.assertEqual(ranks, RANKS, suit)

    def test_fields_and_slots(self):
        for c in DECK["cards"]:
            for k in ("id", "name", "structure", "example", "when_to_pull"):
                self.assertTrue(str(c.get(k, "")).strip(), f"{c.get('name')} missing {k}")
            self.assertRegex(c["structure"], r"\{[^{}]+\}", c["name"])
            self.assertEqual(c["structure"].count("{"), c["structure"].count("}"), c["name"])
            self.assertNotRegex(c["example"], r"[{}]", c["name"])

    def test_unique_names_and_ids(self):
        for k in ("id", "name"):
            vals = [c[k] for c in DECK["cards"]]
            self.assertEqual(len(vals), len(set(vals)), k)

    def test_requested_major_names_present(self):
        names = {c["name"] for c in DECK["cards"]}
        for n in ("The Receipt", "The One Woman Show", "The Guest Check", "Too Busy",
                  "The Hotline", "The Front Page"):
            self.assertIn(n, names)

    def test_voice_rules(self):
        text = str(DECK)
        self.assertNotIn(chr(0x2014), text)  # no em dashes
        # banned words are stored reversed so the repo never spells them out
        for word in ("yllautca", "detnemucodnu", "srepleh", "yltsenoh em llet", "laitnetop ruoy kcolnu"):
            banned = word[::-1]
            self.assertNotIn(banned, text.lower())

    def test_draw_three_distinct_and_repeatable(self):
        a = pull.draw(DECK, 3, seed=11)
        b = pull.draw(DECK, 3, seed=11)
        self.assertEqual([c["id"] for c in a], [c["id"] for c in b])
        self.assertEqual(len({c["id"] for c in a}), 3)
        s = pull.spread(DECK, a, "my retreat", "tired founders")
        self.assertEqual([x["time"] for x in s["cards"]], ["past", "present", "future"])
        text = pull.as_text(s)
        self.assertIn("WHAT THEY BELIEVE", text)
        self.assertIn("fill every {slot}", text)

    def test_suit_filter(self):
        for c in pull.draw(DECK, 3, seed=1, suit="swords"):
            self.assertEqual(c["suit"], "swords")


if __name__ == "__main__":
    unittest.main()
