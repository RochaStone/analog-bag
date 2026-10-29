#!/usr/bin/env python3
"""Print the whole HOOK ORACLE deck: fronts and backs, ready to cut.

    python3 tarot/print.py --out out/                 # tarot size 70 x 120 mm, 4 per page
    python3 tarot/print.py --out out/ --size mini     # 63 x 88 mm, 9 per page
    python3 tarot/print.py --out out/ --only "The Receipt,Ace of Cups" --strip cards.png
    python3 tarot/print.py --out out/ --set samhain-2026   # one monthly set as its own mini deck

Fronts and backs alternate page by page so a double-sided print (flip on long edge)
lines the backs up behind the fronts. Writes hook-oracle.html, and hook-oracle.pdf when
Chrome is available.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tarot"))

from core import render  # noqa: E402
from core import motif as M  # noqa: E402
from core import style as S  # noqa: E402
from core.style import esc, page  # noqa: E402
import cards as C  # noqa: E402
from pull import load_deck  # noqa: E402

SIZES = {"tarot": (70.0, 120.0, 2, 2, 1.0), "mini": (63.0, 88.0, 3, 3, 0.8)}
PAPERS = {"a4": (210.0, 297.0), "letter": (215.9, 279.4)}

SHEET_CSS = """
@page{size:var(--pw) var(--ph);margin:0}
body{background:#fff}
.sheet{position:relative;width:var(--pw);height:var(--ph);overflow:hidden;page-break-after:always;break-after:page;background:#fff}
.cut{position:absolute;border-color:#9b8a93;border-style:dashed;border-width:0}
.cut.v{border-left-width:.2mm;width:0}
.cut.h{border-top-width:.2mm;height:0}
.inline{border-color:rgba(246,239,228,.35)}
.strip{display:flex;gap:9mm;padding:10mm;background:var(--paper);align-items:center;width:max-content}
.strip .card{position:relative;box-shadow:2mm 3mm 5mm rgba(30,6,20,.45)}
.strip .card:nth-child(odd){transform:rotate(-2deg)}
.strip .card:nth-child(even){transform:rotate(2deg)}
"""
CSS = SHEET_CSS + C.css()


def slotted(text: str) -> str:
    out, buf, inside = [], "", False
    for ch in text:
        if ch == "{" and not inside:
            out.append(esc(buf)); buf, inside = "", True
        elif ch == "}" and inside:
            out.append(f"<b>{{{esc(buf)}}}</b>"); buf, inside = "", False
        else:
            buf += ch
    out.append(esc(buf))
    return "".join(out)


def front(card: dict, size: str, x: float, y: float, motif: str = "analog") -> str:
    return C.front_html(card, motif, x, y)


def back(size: str, x: float, y: float, motif: str = "analog", set_name: str = "") -> str:
    return C.back_html(motif, x, y, set_name)


def head() -> str:
    """Extra font links and the motif tile, placed first in the body."""
    return C.fonts_extra() + f"<style>{C.tile_css()}</style>"


def cuts(cols: int, rows: int, cw: float, ch: float, mx: float, my: float, pw: float, ph: float) -> str:
    out = []
    for i in range(cols + 1):
        x = mx + i * cw
        out.append(f"<div class='cut v' style='left:{x}mm;top:0;height:{my - 1.5}mm'></div>")
        out.append(f"<div class='cut v' style='left:{x}mm;top:{ph - my + 1.5}mm;height:{my - 1.5}mm'></div>")
        if 0 < i < cols:
            out.append(f"<div class='cut v inline' style='left:{x}mm;top:{my}mm;height:{rows * ch}mm'></div>")
    for j in range(rows + 1):
        y = my + j * ch
        out.append(f"<div class='cut h' style='top:{y}mm;left:0;width:{mx - 1.5}mm'></div>")
        out.append(f"<div class='cut h' style='top:{y}mm;left:{pw - mx + 1.5}mm;width:{mx - 1.5}mm'></div>")
        if 0 < j < rows:
            out.append(f"<div class='cut h inline' style='top:{y}mm;left:{mx}mm;width:{cols * cw}mm'></div>")
    return "".join(out)


def build_html(cards: list[dict], size: str = "tarot", paper: str = "a4", backs: str = "interleave",
               motif: str = "analog", set_name: str = "") -> str:
    cw, ch, cols, rows, s = SIZES[size]
    pw, ph = PAPERS[paper]
    mx, my = (pw - cols * cw) / 2, (ph - rows * ch) / 2
    per = cols * rows
    marks = cuts(cols, rows, cw, ch, mx, my, pw, ph)
    fronts, backs_pages = [], []
    for start in range(0, len(cards), per):
        chunk = cards[start:start + per]
        f_html, b_html = [], []
        for i, card in enumerate(chunk):
            r, c = divmod(i, cols)
            f_html.append(front(card, size, mx + c * cw, my + r * ch, motif))
            b_html.append(back(size, mx + (cols - 1 - c) * cw, my + r * ch, motif, set_name))
        fronts.append(f"<section class='sheet'>{''.join(f_html)}{marks}</section>")
        backs_pages.append(f"<section class='sheet'>{''.join(b_html)}{marks}</section>")
    if backs == "interleave":
        sheets = [p for pair in zip(fronts, backs_pages) for p in pair]
    elif backs == "end":
        sheets = fronts + backs_pages[:1]
    else:
        sheets = fronts
    vars_css = f":root{{--pw:{pw}mm;--ph:{ph}mm;--cw:{cw}mm;--ch:{ch}mm;--s:{s}}}"
    return page(f"HOOK ORACLE {set_name}".strip(), vars_css + CSS, head() + "".join(sheets))


def build_strip(cards: list[dict], size: str = "tarot", motif: str = "analog", set_name: str = "") -> str:
    cw, ch, _, _, s = SIZES[size]
    items = [front(c, size, 0, 0, motif) for c in cards] + [back(size, 0, 0, motif, set_name)]
    vars_css = f":root{{--pw:210mm;--ph:297mm;--cw:{cw}mm;--ch:{ch}mm;--s:{s}}}"
    return page("HOOK ORACLE sample", vars_css + CSS + "body{background:var(--paper)}",
                head() + f"<div class='strip'>{''.join(items)}</div>")


def pick(deck: dict, names: str) -> list[dict]:
    wanted = [n.strip().lower() for n in names.split(",") if n.strip()]
    by_name = {c["name"].lower(): c for c in deck["cards"]}
    missing = [n for n in wanted if n not in by_name]
    if missing:
        raise SystemExit(f"Not in the deck: {', '.join(missing)}")
    return [by_name[n] for n in wanted]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Print the HOOK ORACLE deck.")
    ap.add_argument("--out", default="out", help="folder for the files")
    ap.add_argument("--size", choices=SIZES, default="tarot")
    ap.add_argument("--paper", choices=PAPERS, default="a4")
    ap.add_argument("--backs", choices=("interleave", "end", "none"), default="interleave",
                    help="interleave for double-sided, end for one back page, none to skip")
    ap.add_argument("--only", help="comma-separated card names to print instead of the whole deck")
    ap.add_argument("--strip", help="write a PNG sample strip of the --only cards to this path")
    ap.add_argument("--set", default="core", help="which set to print: core (the 78) or a monthly set "
                    "such as samhain-2026, printed as its own mini deck with its name on face and back")
    ap.add_argument("--style", help="a style.json (default: ./style.json, then ~/.rocha-coded/style.json)")
    ap.add_argument("--motif", choices=M.CHOICES, help="the card look: analog (blush riso stock), cyberpunk (plum stock, pixel chrome) "
                         "or y2k-blog (cream stock, window bar); default from style.json")
    ap.add_argument("--html-only", action="store_true", help="skip Chrome, write HTML only")
    a = ap.parse_args(argv)
    S.use(a.style)
    print(f"Style: {S.current().get('name') or 'unnamed'} ({S.source()})")
    deck = load_deck(sets=[a.set])
    cards = pick(deck, a.only) if a.only else deck["cards"]
    set_name = "" if a.set == "core" else deck["set_names"][a.set]
    stem = "hook-oracle" if a.set == "core" else f"hook-oracle-{a.set}"
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    if a.strip:
        html_path = out / f"{stem}-strip.html"
        html_path.write_text(build_strip(cards, a.size, M.resolve(a.motif), set_name), encoding="utf-8")
        cw, ch = SIZES[a.size][:2]
        w = int(((cw + 9) * (len(cards) + 1) + 11) * 96 / 25.4)
        h = int((ch + 21) * 96 / 25.4)
        ok, err = (False, "skipped") if a.html_only else render.html_to_png(html_path, Path(a.strip), w, h)
        print(f"strip: {a.strip}" if ok else f"strip not rendered ({err}). HTML: {html_path}")
        return 0

    html_path = out / f"{stem}.html"
    html_path.write_text(build_html(cards, a.size, a.paper, a.backs, M.resolve(a.motif), set_name), encoding="utf-8")
    per = SIZES[a.size][2] * SIZES[a.size][3]
    pages = -(-len(cards) // per)
    print(f"HOOK ORACLE {set_name or 'core deck'}: {len(cards)} cards, {a.size} size, {per} per {a.paper.upper()} page, "
          f"{pages} front pages, backs: {a.backs}")
    if a.html_only:
        print(f"HTML: {html_path}")
        return 0
    pdf = out / f"{stem}.pdf"
    ok, err = render.html_to_pdf(html_path, pdf)
    print(f"PDF: {pdf}" if ok else render.fallback_note(html_path) + (f"\n({err})" if err else ""))
    print("Print at 100% (actual size). For backs, print double-sided and flip on the long edge.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
