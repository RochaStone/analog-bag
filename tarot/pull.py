#!/usr/bin/env python3
"""Draw three Hook Tarot cards for a topic and an audience.

    python3 tarot/pull.py --topic "my spring retreat" --audience "burnt-out founders"

Prints three hook structures with their {slots} open. The agent fills the slots in
the user's own words. Use --seed for a repeatable draw and --json for machines.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

DECK_PATH = Path(__file__).resolve().parent / "deck.json"
SUITS = ("cups", "wands", "swords", "pentacles")


def load_deck(path: Path = DECK_PATH) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Could not read the deck at {path}: {exc}") from exc


def label(card: dict) -> str:
    if card["arcana"] == "major":
        return f"{card['name']} ({card['numeral']}, Major Arcana)"
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
                   "card": label(c), "structure": c["structure"], "example": c["example"],
                   "when_to_pull": c["when_to_pull"]}
                  for pos, c in zip(deck["positions"], cards)],
    }


def as_text(s: dict) -> str:
    lines = ["HOOK TAROT  three-card pull", f"Topic: {s['topic']}", f"Audience: {s['audience']}", ""]
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
    ap = argparse.ArgumentParser(description="Draw three Hook Tarot cards.")
    ap.add_argument("--topic", required=True, help="what the post, email or talk is about")
    ap.add_argument("--audience", required=True, help="who it is for")
    ap.add_argument("--seed", type=int, help="repeatable draw")
    ap.add_argument("--suit", choices=SUITS, help="draw only from one suit")
    ap.add_argument("--majors", action="store_true", help="draw only Major Arcana")
    ap.add_argument("--json", action="store_true", help="print JSON instead of text")
    a = ap.parse_args(argv)
    deck = load_deck()
    s = spread(deck, draw(deck, 3, a.seed, a.suit, a.majors), a.topic.strip(), a.audience.strip())
    sys.stdout.write((json.dumps(s, indent=2, ensure_ascii=False) if a.json else as_text(s)) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
