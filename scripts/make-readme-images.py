#!/usr/bin/env python3
"""Render every image in the README and examples/ from the tool itself.

    python3 scripts/make-readme-images.py                      # the bundled example style
    python3 scripts/make-readme-images.py --style my-style.json # your own look (and font file)

Needs Chrome. Fixed dates and UTC keep the samples reproducible. Writes:
  docs/img/hero.png          three HOOK ORACLE cards fanned over the pocket week, in the zine look
  docs/img/triptych.png      one card and its week page in analog, cyberpunk and y2k-blog
  docs/img/majors.jpg        a contact sheet of all 22 Major Arcana
  docs/img/step-01..05.svg   pixel step badges for Start here
  docs/img/divider.svg, heart.svg
  examples/                  cards, launch and week pages in each motif, the .ics, a pull
  docs/IMAGES.md             the list of all of the above
"""
from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core import motif as M  # noqa: E402
from core import render  # noqa: E402
from core import style as S  # noqa: E402
from core.style import esc, moon_svg, page  # noqa: E402

EX = ROOT / "examples"
IMG = ROOT / "docs" / "img"
BUILD = ROOT / "out" / "readme-build"
PY = sys.executable
STYLE = str(S.BUNDLED)
WEEK_FILL = ["--one-thing", "Open the retreat waitlist", "--move", "Write the welcome email",
             "--move", "Tell the origin story"]


def run(*args: str) -> str:
    res = subprocess.run([PY, *args, "--style", STYLE], cwd=ROOT, capture_output=True, text=True)
    if res.returncode != 0:
        raise SystemExit(f"failed: {' '.join(args)}\n{res.stderr}")
    return res.stdout


def png(html: Path, out: Path, w: int, h: int, scale: float = 1) -> None:
    ok, err = render.html_to_png(html, out, w, h, scale)
    if not ok:
        raise SystemExit(f"render failed for {out}: {err}")


def suffix(motif: str) -> str:
    return "" if motif == "analog" else f"-{motif}"


def examples() -> None:
    run("tarot/print.py", "--out", str(BUILD), "--only", "The Receipt,The Hotline,Ace of Cups",
        "--strip", str(EX / "tarot-cards.png"))
    (EX / "pull.txt").write_text(run("tarot/pull.py", "--topic", "my spring retreat", "--audience",
                                     "burnt-out founders", "--seed", "7", "--story", str(BUILD / "story")),
                                 encoding="utf-8")
    (EX / "story.png").write_bytes((BUILD / "story" / "story-2-present.png").read_bytes())
    for motif in M.MOTIFS:
        out = BUILD / motif
        run("launch/launch.py", "--offer", "Spring Breath Retreat", "--date", "2026-11-02", "--weeks", "6",
            "--out", str(out), "--utc-offset", "0", "--motif", motif, "--html-only")
        png(out / "launch.html", EX / f"launch{suffix(motif)}.png", 794, 1123)
        run("week/week.py", "--out", str(out), "--start", "2026-11-23", "--utc-offset", "0",
            "--motif", motif, "--html-only", *WEEK_FILL)
        png(out / "week.html", EX / f"week{suffix(motif)}.png", 560, 794)
    for f in ("launch.ics", "launch.md"):
        (EX / f).write_bytes((BUILD / "analog" / f).read_bytes())


def svgs() -> None:
    plum, gold, candy = S.color("plum"), S.color("gold"), S.color("accent")
    for n in range(1, 6):
        digits = f"{n:02d}"
        body = M.rects(M.DIGITS[digits[0]], 2, 4, 3) + M.rects(M.DIGITS[digits[1]], 2, 12, 3)
        (IMG / f"step-{digits}.svg").write_text(
            f"<svg xmlns='http://www.w3.org/2000/svg' width='44' height='32' viewBox='0 0 22 16' "
            f"shape-rendering='crispEdges'><rect width='22' height='16' rx='2' fill='{plum}'/>"
            f"<g fill='{gold}'>{body}</g></svg>", encoding="utf-8")
    (IMG / "divider.svg").write_text(
        f"<svg xmlns='http://www.w3.org/2000/svg' width='720' height='8' shape-rendering='crispEdges'>"
        f"<defs><pattern id='p' width='12' height='8' patternUnits='userSpaceOnUse'>"
        f"<rect x='0' y='3' width='6' height='2' fill='{gold}'/></pattern></defs>"
        f"<rect width='720' height='8' fill='url(#p)'/></svg>", encoding="utf-8")
    (IMG / "heart.svg").write_text(
        f"<svg xmlns='http://www.w3.org/2000/svg' width='21' height='18' viewBox='0 0 7 6' "
        f"shape-rendering='crispEdges'><g fill='{candy}'>{M.rects(M.HEART)}</g></svg>", encoding="utf-8")


def load_tarot():
    spec = importlib.util.spec_from_file_location("tarot_print_readme", ROOT / "tarot" / "print.py")
    tp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tp)
    return tp


def desk_css(w: int, h: int, ground: str = "var(--plum)") -> str:
    """A zine desk: the ground, a riso dot screen and paper grain."""
    return (f"html,body{{width:{w}px;height:{h}px;overflow:hidden;background:{ground}}}"
            ".desk{position:relative;width:100%;height:100%;overflow:hidden}"
            ".desk::before{content:'';position:absolute;inset:0;background-image:radial-gradient(circle,"
            "color-mix(in srgb,var(--candy) 22%,transparent) 0 1.6px,transparent 2.3px);background-size:11px 11px}"
            ".desk::after{content:'';position:absolute;inset:0;pointer-events:none;mix-blend-mode:multiply;opacity:.8;"
            f"background:{tp_cards().GRAIN}}}"
            ".lay{position:absolute;transform-origin:50% 50%}"
            ".lay .card{position:relative;box-shadow:10px 16px 26px rgba(12,2,8,.5)}"
            ".page{position:absolute;box-shadow:14px 20px 30px rgba(12,2,8,.45)}"
            ".tape2{position:absolute;width:150px;height:40px;background:color-mix(in srgb,var(--candy) 75%,transparent);"
            "clip-path:polygon(0 8%,4% 0,9% 10%,14% 0,100% 0,96% 12%,100% 24%,95% 38%,100% 52%,96% 66%,100% 80%,"
            "95% 92%,100% 100%,0 100%,4% 86%,0 72%,5% 58%,0 44%,4% 30%,0 18%)}")


def tp_cards():
    sys.path.insert(0, str(ROOT / "tarot"))
    import cards
    return cards


def card_page(title: str, css: str, body: str) -> str:
    c = tp_cards()
    return page(title, c.css() + css, c.fonts_extra() + f"<style>{c.tile_css()}</style>" + body)


def lay(html: str, x: int, y: int, w: int, rot: float, z: int = 1) -> str:
    h = round(w * 120 / 70)
    return (f"<div class='lay' style='left:{x}px;top:{y}px;width:{w}px;height:{h}px;"
            f"transform:rotate({rot}deg);z-index:{z};--cw:{w}px;--ch:{h}px'>{html}</div>")


def hero() -> None:
    c = tp_cards()
    deck = {d["name"]: d for d in load_tarot().load_deck()["cards"]}
    one = lambda n: c.front_html(deck[n], "analog", None, None)  # noqa: E731
    word = c.ransom("HOOK ORACLE", "word")
    body = (f"<div class='desk'>"
            f"<img class='page' src='{(EX / 'week.png').as_uri()}' alt='' "
            f"style='left:96px;top:118px;width:520px;transform:rotate(-6deg)'>"
            f"<i class='tape2' style='left:250px;top:96px;transform:rotate(-9deg)'></i>"
            + lay(c.back_html("analog", None, None), 1290, 170, 280, 13, 1)
            + lay(one("The Receipt"), 470, 190, 320, -10, 2)
            + lay(one("Ace of Cups"), 1040, 150, 320, 9, 3)
            + lay(one("The Hotline"), 750, 110, 340, -1, 4)
            + f"<div class='mark'>{word}</div>"
            f"<div class='line'>pull three cards {M.star('22px')} print the deck {M.star('22px')} "
            f"plan your week in pen</div></div>")
    css = desk_css(1600, 900) + """
.mark{position:absolute;left:70px;top:740px;font-size:62px;z-index:6;transform:rotate(-3deg)}
.mark .ransom span{box-shadow:3px 5px 8px rgba(12,2,8,.45)}
.line{position:absolute;right:56px;bottom:38px;z-index:6;font-family:var(--mono);font-size:20px;letter-spacing:.12em;
  color:var(--cream);display:flex;align-items:center;gap:12px;text-transform:uppercase}
"""
    path = BUILD / "hero.html"
    path.write_text(card_page("analog-bag hero", css, body), encoding="utf-8")
    png(path, IMG / "hero.png", 1600, 900)


def triptych() -> None:
    c = tp_cards()
    card = {d["name"]: d for d in load_tarot().load_deck()["cards"]}["The Receipt"]
    cols = []
    for i, m in enumerate(M.MOTIFS):
        x = 60 + i * 520
        cols.append(f"<img class='page' src='{(EX / f'week{suffix(m)}.png').as_uri()}' alt='' "
                    f"style='left:{x}px;top:60px;width:300px;transform:rotate(-4deg)'>"
                    + lay(c.front_html(card, m, None, None), x + 190, 120, 270, 5, 2)
                    + f"<div class='cap' style='left:{x + 20}px'>{M.star('20px')} {esc(m)}</div>")
    css = desk_css(1600, 780) + """
.cap{position:absolute;top:700px;font-family:var(--pixel);font-size:24px;color:var(--candy);display:flex;gap:10px;align-items:center}
"""
    path = BUILD / "triptych.html"
    path.write_text(card_page("analog-bag triptych", css, f"<div class='desk'>{''.join(cols)}</div>"), encoding="utf-8")
    png(path, IMG / "triptych.png", 1600, 780)


def sheet(names: list[dict], out: Path, motif: str = "analog", cols: int = 6) -> None:
    """A contact sheet: every card in a grid on the plum desk."""
    c = tp_cards()
    w, gap, pad = 300, 30, 60
    h = round(w * 120 / 70)
    rows = -(-len(names) // cols)
    W, H = pad * 2 + cols * w + (cols - 1) * gap, pad * 2 + rows * h + (rows - 1) * gap
    cells = "".join(
        f"<div class='lay' style='left:{pad + (i % cols) * (w + gap)}px;top:{pad + (i // cols) * (h + gap)}px;"
        f"width:{w}px;height:{h}px;--cw:{w}px;--ch:{h}px'>{c.front_html(d, motif, None, None)}</div>"
        for i, d in enumerate(names))
    path = BUILD / f"{out.stem}.html"
    path.write_text(card_page(out.stem, desk_css(W, H), f"<div class='desk'>{cells}</div>"), encoding="utf-8")
    png(path, out, W, H)


def majors() -> None:
    """The sheet is large, so it ships as a JPEG (macOS sips does the conversion)."""
    raw = BUILD / "majors.png"
    sheet(load_tarot().load_deck()["cards"][:22], raw)
    res = subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "60", str(raw),
                          "--out", str(IMG / "majors.jpg")], capture_output=True, text=True)
    if res.returncode != 0:
        raise SystemExit(f"could not convert the majors sheet to JPEG: {res.stderr.strip()}")


IMAGES_MD = """# Images

Every image here is generated by `scripts/make-readme-images.py` from the tool itself. No photos.

| File | What it is |
|---|---|
| `docs/img/hero.png` | The README hero: three HOOK ORACLE cards and the LORE back fanned over the pocket week, in the zine look |
| `docs/img/triptych.png` | The Receipt card and the pocket week in analog, cyberpunk and y2k-blog |
| `docs/img/majors.jpg` | All 22 Major Arcana on one sheet |
| `examples/story.png` | One card as a 1080 x 1920 story, from a three-card pull |
| `docs/img/step-01.svg` to `step-05.svg` | Pixel step badges for Start here |
| `docs/img/divider.svg` | A gold pixel hairline between README sections |
| `docs/img/heart.svg` | A pixel heart for If it goes wrong |
| `examples/tarot-cards.png` | Three card fronts and a card back |
| `examples/launch.png`, `launch-cyberpunk.png`, `launch-y2k-blog.png` | The launch page in each motif |
| `examples/week.png`, `week-cyberpunk.png`, `week-y2k-blog.png` | The pocket week in each motif |

The painted objects on the cards live in `tarot/objects/`. All 22 Major Arcana are painted (see `docs/MAJORS-TO-PAINT.md`).
"""


def main() -> int:
    global STYLE
    ap = argparse.ArgumentParser(description="Render the README images from the tool itself.")
    ap.add_argument("--style", help="a style.json for every image (default: the bundled example)")
    a = ap.parse_args()
    if not render.find_chrome():
        raise SystemExit("Chrome is needed to render the README images.")
    STYLE = str(Path(a.style).resolve()) if a.style else str(S.BUNDLED)
    S.use(STYLE)
    for d in (EX, IMG, BUILD):
        d.mkdir(parents=True, exist_ok=True)
    examples()
    svgs()
    hero()
    triptych()
    majors()
    (ROOT / "docs" / "IMAGES.md").write_text(IMAGES_MD, encoding="utf-8")
    print("README images and examples rendered")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
