#!/usr/bin/env python3
"""Maintainer script: re-render examples/ and the README hero from the real tools.

    python3 scripts/make_examples.py

Needs Chrome. Uses fixed dates and UTC so the samples are reproducible.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core import render  # noqa: E402
from core import style as S  # noqa: E402
from core.style import page  # noqa: E402

EX = ROOT / "examples"
BUILD = ROOT / "out" / "examples-build"
PY = sys.executable


def run(*args: str) -> None:
    res = subprocess.run([PY, *args], cwd=ROOT, capture_output=True, text=True)
    if res.returncode != 0:
        raise SystemExit(f"failed: {' '.join(args)}\n{res.stderr}")
    print(res.stdout.strip())


def png(html: Path, out: Path, w: int, h: int, scale: float = 1) -> None:
    ok, err = render.html_to_png(html, out, w, h, scale)
    if not ok:
        raise SystemExit(f"render failed for {out}: {err}")


def main() -> int:
    if not render.find_chrome():
        raise SystemExit("Chrome is needed to render the examples.")
    EX.mkdir(exist_ok=True)
    BUILD.mkdir(parents=True, exist_ok=True)

    run("tarot/print.py", "--out", str(BUILD), "--only",
        "The Receipt,The Hotline,Ace of Cups", "--strip", str(EX / "tarot-cards.png"))
    pull = subprocess.run([PY, "tarot/pull.py", "--topic", "my spring retreat",
                           "--audience", "burnt-out founders", "--seed", "7"],
                          cwd=ROOT, capture_output=True, text=True, check=True).stdout
    (EX / "pull.txt").write_text(pull, encoding="utf-8")

    run("launch/launch.py", "--offer", "Spring Breath Retreat", "--date", "2026-11-02",
        "--weeks", "6", "--out", str(BUILD), "--utc-offset", "0", "--html-only")
    for f in ("launch.ics", "launch.md"):
        (EX / f).write_bytes((BUILD / f).read_bytes())
    png(BUILD / "launch.html", EX / "launch.png", 794, 1123)

    run("week/week.py", "--out", str(BUILD), "--start", "2026-11-23", "--utc-offset", "0",
        "--one-thing", "Open the retreat waitlist", "--move", "Write the welcome email",
        "--move", "Tell the origin story", "--html-only")
    png(BUILD / "week.html", EX / "week.png", 560, 794)

    ok, err = render.html_to_png(BUILD / "launch.html", BUILD / "launch-top.png", 794, 250, 2)
    if not ok:
        raise SystemExit(f"render failed: {err}")
    hero_html = BUILD / "hero.html"
    hero_html.write_text(hero_page(), encoding="utf-8")
    (ROOT / "docs" / "img").mkdir(parents=True, exist_ok=True)
    png(hero_html, ROOT / "docs" / "img" / "hero.png", 1600, 900)
    print("examples and hero rendered")
    return 0


def hero_page() -> str:
    """The README hero: real card HTML fanned in the centre, the week page on the
    right, the launch page cropped to its title and moon strip, bottom left."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("tarot_print_hero", ROOT / "tarot" / "print.py")
    tp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tp)
    deck = {c["name"]: c for c in tp.load_deck()["cards"]}
    cards = [tp.front(deck[n], "tarot", 0, 0) for n in ("The Receipt", "The Hotline", "Ace of Cups")]
    fan = (f"<div class='slot back'>{tp.back('tarot', 0, 0)}</div>"
           f"<div class='slot left'>{cards[0]}</div><div class='slot right'>{cards[2]}</div>"
           f"<div class='slot mid'>{cards[1]}</div>")
    body = HERO_BODY.format(fan=fan, week=(EX / "week.png").as_uri(),
                            launch=(BUILD / "launch-top.png").as_uri(), scrawl=S.line("scrawl"))
    return page("analog-bag hero", ":root{--cw:70mm;--ch:120mm;--s:1}" + tp.CSS + HERO_CSS, body)


HERO_CSS = """
html,body{width:1600px;height:900px;overflow:hidden;background:var(--ground)}
.desk{position:relative;width:1600px;height:900px;background:var(--ground);overflow:hidden}
.desk::before{content:"";position:absolute;inset:0;background:radial-gradient(ellipse at 60% 45%,var(--wine),transparent 70%);opacity:.75}
.label{position:absolute;left:84px;top:70px;color:var(--gold);font-family:var(--tag);font-weight:700;font-size:22px;letter-spacing:.24em}
.word{position:absolute;left:78px;top:104px;color:var(--cream);font-family:var(--didone);font-weight:900;font-size:116px;line-height:.88;letter-spacing:-.02em}
.scrawl{position:absolute;left:88px;top:306px;font-family:var(--marker);color:var(--candy);font-size:28px;transform:rotate(-4deg)}
.fan{position:absolute;left:790px;top:500px;width:0;height:0}
.slot{position:absolute;left:0;top:0;transform-origin:50% 100%}
.slot .card{position:relative;transform:translate(-50%,-50%) scale(1.04);transform-origin:50% 50%;box-shadow:3mm 5mm 8mm rgba(12,2,8,.55)}
.slot.back{transform:translate(240px,-95px) rotate(24deg)}
.slot.left{transform:translate(-190px,34px) rotate(-12deg)}
.slot.right{transform:translate(190px,34px) rotate(12deg)}
.slot.mid{transform:translate(0,-14px)}
.shot{position:absolute;box-shadow:14px 22px 36px rgba(12,2,8,.55);background:#fff}
.week{left:1328px;top:300px;width:236px;transform:rotate(4deg)}
.launch{left:66px;top:640px;width:450px;transform:rotate(-3deg)}
"""

HERO_BODY = """<div class='desk grain'>
<img class='shot launch' src='{launch}' alt=''>
<div class='label'>ROCHA CODED</div>
<div class='word'>ANALOG<br>BAG</div>
<div class='scrawl'>{scrawl}</div>
<div class='fan'>{fan}</div>
<img class='shot week' src='{week}' alt=''>
</div>"""

if __name__ == "__main__":
    raise SystemExit(main())
