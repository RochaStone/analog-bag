#!/usr/bin/env python3
"""Render every image in the README and examples/ from the tool itself.

    python3 scripts/make-readme-images.py

Needs Chrome. Fixed dates and UTC keep the samples reproducible. Writes:
  docs/img/hero.png          the y2k-blog window (analog-bag.exe) with the kit inside
  docs/img/triptych.png      the same week in analog, cyberpunk and y2k-blog
  docs/img/step-01..05.svg   pixel step badges for Start here
  docs/img/divider.svg, heart.svg
  examples/                  cards, launch and week pages in each motif, the .ics, a pull
  docs/IMAGES.md             the list of all of the above
"""
from __future__ import annotations

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
WEEK_FILL = ["--one-thing", "Open the retreat waitlist", "--move", "Write the welcome email",
             "--move", "Tell the origin story"]


def run(*args: str) -> str:
    res = subprocess.run([PY, *args], cwd=ROOT, capture_output=True, text=True)
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
                                     "burnt-out founders", "--seed", "7"), encoding="utf-8")
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


def hero() -> None:
    tp = load_tarot()
    deck = {c["name"]: c for c in tp.load_deck()["cards"]}
    cards = [tp.front(deck[n], "tarot", 0, 0) for n in ("The Receipt", "The Hotline", "Ace of Cups")]
    fan = (f"<div class='slot back'>{tp.back('tarot', 0, 0)}</div><div class='slot left'>{cards[0]}</div>"
           f"<div class='slot right'>{cards[2]}</div><div class='slot mid'>{cards[1]}</div>")
    star = M.star("16px")
    marquee = f" {star} ".join(["pull three cards", "lay your launch on the moon", "plan your week in pen",
                                "photograph it, Claude reads it back"])
    side = (f"<aside class='side'><div><h4>about me</h4>a printable founder kit for your bag</div>"
            f"<div><h4>mood</h4><div class='mood'>{moon_svg(0.48, 7)} full moon</div></div>"
            f"<div><h4>currently reading</h4>the hook tarot, 78 cards</div>"
            f"<div><h4>guestbook</h4>sign it on GitHub {M.heart('16px', S.color('accent'))}</div>"
            f"<div class='bottom'>{M.hit_counter()}</div></aside>")
    main = (f"<div class='mainc'><div class='marquee'>{star} {marquee} {star}</div>"
            f"<div class='fan'>{fan}</div><img class='week' src='{(EX / 'week.png').as_uri()}' alt=''></div>")
    body = f"<div class='desk hero'>{M.window('analog-bag.exe', main + side)}</div>"
    css = (":root{--cw:70mm;--ch:120mm;--s:1}" + tp.CSS + M.css() + HERO_CSS
           + f".desk{{background-image:{M.tiled_bg()}}}")
    path = BUILD / "hero.html"
    path.write_text(page("analog-bag hero", css, body), encoding="utf-8")
    png(path, IMG / "hero.png", 1600, 900)


HERO_CSS = """
html,body{width:1600px;height:900px;overflow:hidden;background:var(--paper)}
.desk.hero{width:1600px;height:900px;padding:40px 44px;display:flex}
.hero .win9{flex:1;border-width:3px;border-radius:12px;box-shadow:10px 14px 0 rgba(30,6,20,.25)}
.hero .win9 .bar{padding:10px 16px}
.hero .win9 .btns i{width:16px;height:16px;margin-right:6px}
.hero .win9 .wtitle{font-size:20px}
.hero .mainc{flex:1;position:relative;overflow:hidden}
.hero .marquee{font-size:16px;padding:12px 22px;border-bottom:2px dashed var(--plum);display:flex;gap:10px;align-items:center}
.hero .side{width:320px;font-size:18px;gap:18px;padding:22px;border-left:2px dashed var(--plum)}
.hero .side h4{font-size:14px;border-bottom-width:2px;padding-bottom:4px;margin-bottom:8px}
.hero .mood{display:flex;align-items:center;gap:10px}
.hero .side .bottom{margin-top:auto}
.hero .counter{font-size:15px;padding:8px 10px;border-radius:6px}
.fan{position:absolute;left:440px;top:440px;width:0;height:0}
.slot{position:absolute;left:0;top:0;transform-origin:50% 100%}
.slot .card{position:relative;transform:translate(-50%,-50%) scale(.92);box-shadow:3mm 5mm 7mm rgba(12,2,8,.45)}
.slot.back{transform:translate(215px,-80px) rotate(22deg)}
.slot.left{transform:translate(-185px,30px) rotate(-12deg)}
.slot.right{transform:translate(185px,30px) rotate(12deg)}
.slot.mid{transform:translate(0,-12px)}
.hero img.week{position:absolute;right:46px;top:150px;width:290px;transform:rotate(3deg);box-shadow:10px 14px 24px rgba(12,2,8,.35)}
"""


def triptych() -> None:
    cells = "".join(
        f"<figure><img src='{(EX / f'week{suffix(m)}.png').as_uri()}' alt=''><figcaption class='pixel'>"
        f"{M.star('18px')} {esc(m)}</figcaption></figure>" for m in M.MOTIFS)
    css = """
html,body{width:1600px;height:780px;overflow:hidden;background:var(--plum)}
.row{display:flex;justify-content:center;gap:60px;padding:44px 0}
figure{display:flex;flex-direction:column;align-items:center;gap:18px}
figure img{width:430px;box-shadow:10px 14px 24px rgba(12,2,8,.5)}
figcaption{color:var(--candy);font-size:24px;display:flex;align-items:center;gap:10px}
"""
    path = BUILD / "triptych.html"
    path.write_text(page("analog-bag triptych", M.css() + css, f"<div class='row'>{cells}</div>"), encoding="utf-8")
    png(path, IMG / "triptych.png", 1600, 780)


IMAGES_MD = """# Images

Every image here is generated by `scripts/make-readme-images.py` from the tool itself. No photos.

| File | What it is |
|---|---|
| `docs/img/hero.png` | The README hero: a y2k-blog window, analog-bag.exe, with three Hook Tarot cards, the LORE back and a pocket week |
| `docs/img/triptych.png` | The same pocket week in analog, cyberpunk and y2k-blog |
| `docs/img/step-01.svg` to `step-05.svg` | Pixel step badges for Start here |
| `docs/img/divider.svg` | A gold pixel hairline between README sections |
| `docs/img/heart.svg` | A pixel heart for If it goes wrong |
| `examples/tarot-cards.png` | Three card fronts and a card back |
| `examples/launch.png`, `launch-cyberpunk.png`, `launch-y2k-blog.png` | The launch page in each motif |
| `examples/week.png`, `week-cyberpunk.png`, `week-y2k-blog.png` | The pocket week in each motif |
"""


def main() -> int:
    if not render.find_chrome():
        raise SystemExit("Chrome is needed to render the README images.")
    S.use(str(S.BUNDLED))
    for d in (EX, IMG, BUILD):
        d.mkdir(parents=True, exist_ok=True)
    examples()
    svgs()
    hero()
    triptych()
    (ROOT / "docs" / "IMAGES.md").write_text(IMAGES_MD, encoding="utf-8")
    print("README images and examples rendered")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
