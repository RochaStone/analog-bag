#!/usr/bin/env python3
"""Draw three HOOK ORACLE cards for a topic and an audience.

    python3 tarot/pull.py --topic "my spring retreat" --audience "burnt-out founders"
    python3 tarot/pull.py --topic "..." --audience "..." --set samhain-2026

Prints three hook structures with their {slots} open. The agent fills the slots in
the user's own words. Use --seed for a repeatable draw and --json for machines.
The core deck is always in the draw; --set adds a monthly set from tarot/sets/.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DECK_PATH = HERE / "deck.json"
SETS_DIR = HERE / "sets"
SUITS = ("cups", "wands", "swords", "pentacles")
SET_KEYS = ("set", "name", "released", "theme", "cards")


def _read(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Could not read {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"{path} must hold one JSON object.")
    return data


def load_sets(folder: Path = SETS_DIR) -> dict[str, dict]:
    """Every tarot/sets/*.json, keyed by its "set" id, core first, then by release date."""
    sets = {}
    for path in sorted(folder.glob("*.json")):
        data = _read(path)
        missing = [k for k in SET_KEYS if k not in data]
        if missing:
            raise SystemExit(f"The set {path.name} is missing {', '.join(missing)}.")
        for card in data["cards"]:
            card["set"], card["set_name"] = data["set"], data["name"]
        sets[data["set"]] = data
    if "core" not in sets:
        raise SystemExit(f"No core set found in {folder}.")
    order = sorted(sets, key=lambda k: (k != "core", sets[k]["released"], k))
    return {k: sets[k] for k in order}


def load_deck(path: Path = DECK_PATH, sets: list[str] | tuple[str, ...] = ("core",),
              folder: Path = SETS_DIR) -> dict:
    """The deck meta (positions, spreads) with the cards of the chosen sets."""
    deck = _read(path)
    have = load_sets(folder)
    unknown = [s for s in sets if s not in have]
    if unknown:
        raise SystemExit(f"No set called {', '.join(unknown)}. Sets here: {', '.join(have)}.")
    deck["cards"] = [c for s in sets for c in have[s]["cards"]]
    deck["set_names"] = {k: v["name"] for k, v in have.items()}
    return deck


def label(card: dict) -> str:
    if card["arcana"] == "major":
        where = "Major Arcana" if card.get("set", "core") == "core" else card["set"]
        return f"{card['name']} ({card['numeral']}, {where})"
    return f"{card['name']}: {card['title']}"


def draw(deck: dict, n: int = 3, seed: int | None = None, suit: str | None = None,
         majors_only: bool = False) -> list[dict]:
    cards = deck["cards"]
    if suit:
        cards = [c for c in cards if c.get("suit") == suit]
    if majors_only:
        cards = [c for c in cards if c["arcana"] == "major"]
    if len(cards) < n:
        raise SystemExit(f"Only {len(cards)} cards match; cannot draw {n}.")
    return random.Random(seed).sample(cards, n)


def spread(deck: dict, cards: list[dict], topic: str, audience: str) -> dict:
    return {
        "topic": topic, "audience": audience,
        "cards": [{"position": pos["label"], "time": pos["key"], "position_note": pos["note"],
                   "card": label(c), "set": c.get("set", "core"), "structure": c["structure"],
                   "example": c["example"], "when_to_pull": c["when_to_pull"]}
                  for pos, c in zip(deck["positions"], cards)],
    }


def as_text(s: dict) -> str:
    lines = ["HOOK ORACLE three-card pull", f"Topic: {s['topic']}", f"Audience: {s['audience']}", ""]
    for i, c in enumerate(s["cards"], 1):
        lines += [f"{i}. {c['position'].upper()} ({c['time']})  {c['card']}",
                  f"   {c['position_note']}",
                  f"   Structure:    {c['structure']}",
                  f"   Example:      {c['example']}",
                  f"   Pull it when: {c['when_to_pull']}", ""]
    lines.append("Next: fill every {slot} with the topic and audience above, in the user's words. "
                 "Read the three hooks as one arc: belief, turn, action.")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Draw three HOOK ORACLE cards.")
    ap.add_argument("--topic", required=True, help="what the post, email or talk is about")
    ap.add_argument("--audience", required=True, help="who it is for")
    ap.add_argument("--seed", type=int, help="repeatable draw")
    ap.add_argument("--suit", choices=SUITS, help="draw only from one suit")
    ap.add_argument("--majors", action="store_true", help="draw only Major Arcana")
    ap.add_argument("--json", action="store_true", help="print JSON instead of text")
    ap.add_argument("--set", action="append", default=[], metavar="SET",
                    help="add a monthly set to the draw (core is always in), for example samhain-2026")
    ap.add_argument("--story", metavar="FOLDER", help="also render each card as a 1080 x 1920 story PNG here")
    ap.add_argument("--style", help="a style.json for the story cards")
    ap.add_argument("--motif", help="analog, cyberpunk or y2k-blog for the story cards")
    a = ap.parse_args(argv)
    extra = [x.strip() for v in a.set for x in v.split(",") if x.strip() and x.strip() != "core"]
    deck = load_deck(sets=["core", *extra])
    cards = draw(deck, 3, a.seed, a.suit, a.majors)
    s = spread(deck, cards, a.topic.strip(), a.audience.strip())
    sys.stdout.write((json.dumps(s, indent=2, ensure_ascii=False) if a.json else as_text(s)) + "\n")
    if a.story:
        for line in stories(deck, cards, Path(a.story), a.style, a.motif):
            sys.stderr.write(line + "\n")
    return 0


def stories(deck: dict, cards: list[dict], folder: Path, style: str | None = None,
            motif: str | None = None) -> list[str]:
    """Write story-1-past.png, story-2-present.png, story-3-future.png (or the HTML when no
    browser is found). Returns one line per file for the user."""
    root = Path(__file__).resolve().parent.parent
    for p in (str(root), str(root / "tarot")):
        if p not in sys.path:
            sys.path.insert(0, p)
    from core import motif as M
    from core import render
    from core import style as S
    import cards as C
    S.use(style)
    look = M.resolve(motif)
    folder.mkdir(parents=True, exist_ok=True)
    out = []
    for i, (pos, card) in enumerate(zip(deck["positions"], cards), 1):
        html = folder / f"story-{i}-{pos['key']}.html"
        html.write_text(C.story_html(card, look, pos["label"]), encoding="utf-8")
        png = html.with_suffix(".png")
        ok, err = render.html_to_png(html, png, 1080, 1920, 1)
        out.append(f"story: {png}" if ok else f"story not rendered ({err}). HTML: {html}")
    return out


if __name__ == "__main__":
    raise SystemExit(main())
