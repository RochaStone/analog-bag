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

    hero = page("analog-bag hero", HERO_CSS, HERO_BODY.format(
        tarot=(EX / "tarot-cards.png").as_uri(), launch=(EX / "launch.png").as_uri(),
        week=(EX / "week.png").as_uri()))
    hero_html = BUILD / "hero.html"
    hero_html.write_text(hero, encoding="utf-8")
    (ROOT / "docs" / "img").mkdir(parents=True, exist_ok=True)
    png(hero_html, ROOT / "docs" / "img" / "hero.png", 1400, 760)
    print("examples and hero rendered")
    return 0


HERO_CSS = """
body{background:var(--hot);width:1400px;height:760px;overflow:hidden}
.desk{position:relative;width:1400px;height:760px;background:var(--hot)}
.desk::before{content:"";position:absolute;inset:0;background:radial-gradient(circle at 30% 20%,rgba(255,255,255,.18),transparent 55%)}
.shot{position:absolute;box-shadow:12px 18px 30px rgba(74,16,51,.45);background:#fff}
.launch{left:70px;top:70px;width:430px;transform:rotate(-5deg)}
.week{left:1000px;top:120px;width:330px;transform:rotate(4deg)}
.tarot{left:430px;top:330px;width:640px;transform:rotate(1.5deg);background:transparent;box-shadow:none}
.title{position:absolute;left:520px;top:58px;color:var(--white);font-family:var(--didone);font-weight:900;font-size:96px;line-height:.9;letter-spacing:-.02em}
.title small{display:block;font-family:var(--tag);font-size:20px;letter-spacing:.2em;font-weight:700;margin-bottom:12px}
.scrawl{position:absolute;left:500px;top:262px;font-family:var(--marker);color:var(--ink);font-size:27px;transform:rotate(-4deg)}
.tape{position:absolute;width:120px;height:34px;background:rgba(255,225,236,.85)}
"""

HERO_BODY = """<div class='desk'>
<img class='shot launch' src='{launch}' alt=''>
<div class='tape' style='left:220px;top:52px;transform:rotate(-8deg)'></div>
<img class='shot week' src='{week}' alt=''>
<div class='tape' style='left:1120px;top:100px;transform:rotate(6deg)'></div>
<div class='title'><small>ROCHA CODED</small>ANALOG<br>BAG</div>
<div class='scrawl'>plan in pen. Claude reads it back.</div>
<img class='shot tarot' src='{tarot}' alt=''>
</div>"""

if __name__ == "__main__":
    raise SystemExit(main())
