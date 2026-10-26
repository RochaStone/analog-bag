#!/usr/bin/env python3
"""Print the whole Hook Tarot deck: fronts and backs, ready to cut.

    python3 tarot/print.py --out out/                 # tarot size 70 x 120 mm, 4 per page
    python3 tarot/print.py --out out/ --size mini     # 63 x 88 mm, 9 per page
    python3 tarot/print.py --out out/ --only "The Receipt,Ace of Cups" --strip cards.png

Fronts and backs alternate page by page so a double-sided print (flip on long edge)
lines the backs up behind the fronts. Writes hook-tarot.html, and hook-tarot.pdf when
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
from core import style as S  # noqa: E402
from core.style import esc, moon_svg, page  # noqa: E402
from glyphs import glyph_svg  # noqa: E402
from pull import load_deck  # noqa: E402

SIZES = {"tarot": (70.0, 120.0, 2, 2, 1.0), "mini": (63.0, 88.0, 3, 3, 0.8)}
PAPERS = {"a4": (210.0, 297.0), "letter": (215.9, 279.4)}
SUIT_SYMBOL = {"cups": "Cups", "wands": "Wands", "swords": "Swords", "pentacles": "Pentacles"}

CSS = """
@page{size:var(--pw) var(--ph);margin:0}
body{background:#fff}
.sheet{position:relative;width:var(--pw);height:var(--ph);overflow:hidden;page-break-after:always;break-after:page;background:#fff}
.card{position:absolute;width:var(--cw);height:var(--ch);background:var(--plum);color:var(--cream);overflow:hidden;
  font-size:calc(11.6pt*var(--s))}
.frame{position:absolute;inset:calc(3mm*var(--s));border:.35mm solid var(--gold);border-radius:1.6mm}
.frame::after{content:"";position:absolute;inset:.9mm;border:.2mm solid var(--gold);border-radius:1.1mm;opacity:.7}
.inner{position:absolute;inset:calc(5.5mm*var(--s));display:flex;flex-direction:column;align-items:center;text-align:center}
.top{color:var(--gold);font-size:.66em;display:flex;justify-content:space-between;width:100%}
.glyph{margin:calc(1.6mm*var(--s)) 0 calc(.8mm*var(--s))}
.name{font-family:var(--didone);font-weight:700;color:var(--candy);font-size:1.5em;line-height:1.02;text-transform:uppercase;letter-spacing:.02em}
.title{font-family:var(--didone);font-style:italic;color:var(--candy);font-size:.95em;margin-top:.4mm}
.rule{width:40%;height:0;border-top:.25mm solid var(--gold);margin:calc(1.6mm*var(--s)) auto}
.structure{font-size:.92em;line-height:1.3}
.structure b{color:var(--gold);font-weight:600}
.example{font-style:italic;font-size:.74em;line-height:1.3;opacity:.82;margin-top:calc(3mm*var(--s))}
.stars{margin-top:auto;color:var(--gold);font-size:.7em;letter-spacing:.6em;opacity:.8}
.when{margin-top:calc(2mm*var(--s));font-size:.58em;color:var(--gold);line-height:1.25}
.when .tag{display:block;font-size:.95em;margin-bottom:.4mm}
.back{display:flex;align-items:center;justify-content:center}
.back .inner{justify-content:center;gap:calc(3mm*var(--s))}
.back .word{font-family:var(--didone);color:var(--candy);font-size:1.7em;letter-spacing:.12em;text-transform:uppercase}
.back .moons{display:flex;gap:1.2mm}
.back .sub{color:var(--gold);font-size:.62em}
.back .lore{font-family:var(--marker);color:var(--candy);font-size:3.2em;line-height:1;transform:rotate(-4deg)}
.back .under{font-family:var(--didone);font-style:italic;color:var(--cream);font-size:.8em;margin-top:-1mm}
.cut{position:absolute;border-color:#9b8a93;border-style:dashed;border-width:0}
.cut.v{border-left-width:.2mm;width:0}
.cut.h{border-top-width:.2mm;height:0}
.inline{border-color:rgba(246,239,228,.35)}
.strip{display:flex;gap:9mm;padding:10mm;background:var(--paper);align-items:center;width:max-content}
.strip .card{position:relative;box-shadow:2mm 3mm 5mm rgba(74,16,51,.35)}
.strip .card:nth-child(odd){transform:rotate(-2deg)}
.strip .card:nth-child(even){transform:rotate(2deg)}
"""


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


def front(card: dict, size: str, x: float, y: float) -> str:
    s = SIZES[size][4]
    if card["arcana"] == "major":
        left, right, glyph, title = card["numeral"], "Major Arcana", card["glyph"], ""
    else:
        left, right, glyph = card["rank"], SUIT_SYMBOL[card["suit"]], card["suit"]
        title = f"<div class='title'>{esc(card['title'])}</div>"
    example = "" if size == "mini" else f"<div class='example'>{esc(card['example'])}</div>"
    return (f"<div class='card' style='left:{x}mm;top:{y}mm'><div class='frame'></div><div class='inner'>"
            f"<div class='top tag'><span>{esc(left)}</span><span>{esc(right)}</span></div>"
            f"<div class='glyph'>{glyph_svg(glyph, round(30 * s, 1), S.color('gold'))}</div>"
            f"<div class='name'>{esc(card['name'])}</div>{title}<div class='rule'></div>"
            f"<div class='structure'>{slotted(card['structure'])}</div>{example}"
            f"<div class='stars'>&#10022; &#10022; &#10022;</div><div class='when'><span class='tag'>Pull it when</span>{esc(card['when_to_pull'])}</div>"
            f"</div></div>")


def back(size: str, x: float, y: float) -> str:
    s = SIZES[size][4]
    st = S.current()
    stamp = (f"<div class='lore'>{esc(S.line('stamp'))}</div>" if S.line("stamp") else "") + (
        f"<div class='under'>{esc(S.line('scrawl'))}</div>" if S.line("scrawl") else "")
    handle = f" &middot; {esc(st['handle'])}" if st.get("handle") else ""
    moons = "".join(moon_svg(a, round(6 * s, 1)) for a in (0.12, 0.25, 0.5, 0.75, 0.88))
    return (f"<div class='card back' style='left:{x}mm;top:{y}mm'><div class='frame'></div><div class='inner'>"
            f"<div class='moons'>{moons}</div>{glyph_svg('eye', round(30 * s, 1), S.color('gold'))}"
            f"{stamp}<div class='sub tag'>Hook Tarot{handle}</div>"
            f"<div class='moons'>{moons}</div></div></div>")


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


def build_html(cards: list[dict], size: str = "tarot", paper: str = "a4", backs: str = "interleave") -> str:
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
            f_html.append(front(card, size, mx + c * cw, my + r * ch))
            b_html.append(back(size, mx + (cols - 1 - c) * cw, my + r * ch))
        fronts.append(f"<section class='sheet'>{''.join(f_html)}{marks}</section>")
        backs_pages.append(f"<section class='sheet'>{''.join(b_html)}{marks}</section>")
    if backs == "interleave":
        sheets = [p for pair in zip(fronts, backs_pages) for p in pair]
    elif backs == "end":
        sheets = fronts + backs_pages[:1]
    else:
        sheets = fronts
    vars_css = f":root{{--pw:{pw}mm;--ph:{ph}mm;--cw:{cw}mm;--ch:{ch}mm;--s:{s}}}"
    return page("Hook Tarot", vars_css + CSS, "".join(sheets))


def build_strip(cards: list[dict], size: str = "tarot") -> str:
    cw, ch, _, _, s = SIZES[size]
    items = [front(c, size, 0, 0) for c in cards] + [back(size, 0, 0)]
    vars_css = f":root{{--pw:210mm;--ph:297mm;--cw:{cw}mm;--ch:{ch}mm;--s:{s}}}"
    return page("Hook Tarot sample", vars_css + CSS + "body{background:var(--paper)}",
                f"<div class='strip'>{''.join(items)}</div>")


def pick(deck: dict, names: str) -> list[dict]:
    wanted = [n.strip().lower() for n in names.split(",") if n.strip()]
    by_name = {c["name"].lower(): c for c in deck["cards"]}
    missing = [n for n in wanted if n not in by_name]
    if missing:
        raise SystemExit(f"Not in the deck: {', '.join(missing)}")
    return [by_name[n] for n in wanted]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Print the Hook Tarot deck.")
    ap.add_argument("--out", default="out", help="folder for the files")
    ap.add_argument("--size", choices=SIZES, default="tarot")
    ap.add_argument("--paper", choices=PAPERS, default="a4")
    ap.add_argument("--backs", choices=("interleave", "end", "none"), default="interleave",
                    help="interleave for double-sided, end for one back page, none to skip")
    ap.add_argument("--only", help="comma-separated card names to print instead of the whole deck")
    ap.add_argument("--strip", help="write a PNG sample strip of the --only cards to this path")
    ap.add_argument("--style", help="a style.json (default: ./style.json, then ~/.rocha-coded/style.json)")
    ap.add_argument("--html-only", action="store_true", help="skip Chrome, write HTML only")
    a = ap.parse_args(argv)
    S.use(a.style)
    print(f"Style: {S.current().get('name') or 'unnamed'} ({S.source()})")
    deck = load_deck()
    cards = pick(deck, a.only) if a.only else deck["cards"]
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    if a.strip:
        html_path = out / "hook-tarot-strip.html"
        html_path.write_text(build_strip(cards, a.size), encoding="utf-8")
        cw, ch = SIZES[a.size][:2]
        w = int(((cw + 9) * (len(cards) + 1) + 11) * 96 / 25.4)
        h = int((ch + 21) * 96 / 25.4)
        ok, err = (False, "skipped") if a.html_only else render.html_to_png(html_path, Path(a.strip), w, h)
        print(f"strip: {a.strip}" if ok else f"strip not rendered ({err}). HTML: {html_path}")
        return 0

    html_path = out / "hook-tarot.html"
    html_path.write_text(build_html(cards, a.size, a.paper, a.backs), encoding="utf-8")
    per = SIZES[a.size][2] * SIZES[a.size][3]
    pages = -(-len(cards) // per)
    print(f"Hook Tarot: {len(cards)} cards, {a.size} size, {per} per {a.paper.upper()} page, "
          f"{pages} front pages, backs: {a.backs}")
    if a.html_only:
        print(f"HTML: {html_path}")
        return 0
    pdf = out / "hook-tarot.pdf"
    ok, err = render.html_to_pdf(html_path, pdf)
    print(f"PDF: {pdf}" if ok else render.fallback_note(html_path) + (f"\n({err})" if err else ""))
    print("Print at 100% (actual size). For backs, print double-sided and flip on the long edge.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
