#!/usr/bin/env python3
"""Build oracle.html: the HOOK ORACLE on screen, one self-contained page.

    python3 tarot/oracle.py                         # writes oracle.html next to README.md
    python3 tarot/oracle.py --style my-style.json   # bake your own look in
    python3 tarot/oracle.py --out somewhere/oracle.html

The page uses the same card markup and CSS as print.py, the same painted objects (by the
relative path tarot/objects/, so keep the page next to the tarot folder), and every set in
tarot/sets/. It needs no account and no network beyond Google Fonts.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tarot"))

from core import style as S  # noqa: E402
import cards as C  # noqa: E402
from pull import DECK_PATH, load_sets  # noqa: E402

TEMPLATE = ROOT / "tarot" / "oracle.template.html"
OUT = ROOT / "oracle.html"


def relative(html: str) -> str:
    """Absolute file:// links to the objects become tarot/objects/..., so the page travels."""
    return html.replace(C.OBJECTS.as_uri(), "tarot/objects")


def data() -> dict:
    deck = json.loads(DECK_PATH.read_text(encoding="utf-8"))
    sets = load_sets()
    cards = []
    for s in sets.values():
        for card in s["cards"]:
            cards.append({"id": card["id"], "set": s["set"], "name": card["name"],
                          "structure": card["structure"], "example": card["example"],
                          "face": relative(C.front_html(card, "analog", None, None))})
    style = S.current()
    return {
        "spreads": deck["spreads"],
        "sets": [{"set": s["set"], "name": s["name"], "released": s["released"], "theme": s["theme"],
                  "count": len(s["cards"]),
                  "back": relative(C.back_html("analog", None, None, "" if k == "core" else s["name"]))}
                 for k, s in sets.items()],
        "cards": cards,
        "style": {"palette": style["palette"], "fonts": style["fonts"]},
    }


def tiles() -> str:
    """The pattern tiles that are vectors or files. The PNG dot screens and the stamp mask are
    drawn by the page itself at load (so they re-tone, and no base64 blobs sit in the file)."""
    css = re.sub(r"--[a-z-]+:url\('data:image/png;base64,[^']*'\);?", "", C.tile_css())
    return relative(css.replace(";}", "}"))


def build() -> str:
    page = TEMPLATE.read_text(encoding="utf-8")
    style = S.current()
    payload = json.dumps(data(), ensure_ascii=False).replace("</", "<\\/")
    css = relative(S.root_css(style) + ":root{--cw:70mm;--ch:120mm}" + C.css().replace(C.ink_tile(), "var(--stamp)"))
    head = S.fonts_link(style) + C.fonts_extra()
    return (page.replace("%HEAD%", head)
                .replace("%TILES%", tiles())
                .replace("%CARD_CSS%", css)
                .replace("%TITLE%", C.ransom("HOOK ORACLE", "word"))
                .replace("%DATA%", payload))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Build oracle.html, the HOOK ORACLE on screen.")
    ap.add_argument("--style", help="a style.json to bake in (default: ./style.json, then "
                                    "~/.rocha-coded/style.json, then the bundled example)")
    ap.add_argument("--out", default=str(OUT), help="where to write the page")
    a = ap.parse_args(argv)
    S.use(a.style)
    out = Path(a.out)
    out.write_text(build(), encoding="utf-8")
    print(f"Style: {S.current().get('name') or 'unnamed'} ({S.source()})")
    print(f"oracle: {out}  (open it in a browser; keep it next to the tarot folder)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
