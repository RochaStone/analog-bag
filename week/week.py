#!/usr/bin/env python3
"""Pocket Week: one A5 page for the week, filled in pen.

    python3 week/week.py --out out/                       # the coming week, blank
    python3 week/week.py --out out/ --start 2026-11-02 --two-up
    python3 week/week.py --out out/ --one-thing "Open the retreat waitlist" --move "Write the welcome email"

THIS WEEK masthead, ONE THING, three moves, one number to watch, a let-go line, a
moon strip for the seven days and a "photograph me when done" footer. Writes
week.html and, with Chrome, week.pdf. --two-up puts two copies on one A4 sheet.
"""
from __future__ import annotations

import argparse
import sys
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core import render  # noqa: E402
from core import motif as M  # noqa: E402
from core import style as S  # noqa: E402
from core.moon import moon_age, phases_between  # noqa: E402
from core.style import esc, moon_svg, page  # noqa: E402
from core.when import nice, parse_date, parse_offset  # noqa: E402

PHASE_WORDS = ("new moon", "waxing crescent", "first quarter", "waxing gibbous",
               "full moon", "waning gibbous", "last quarter", "waning crescent")


def phase_word(age: float) -> str:
    return PHASE_WORDS[int(((age % 1) * 8) + 0.5) % 8]

CYBER = """
.week.console .screen{inset:4mm;padding:5mm 5mm 4mm}
.chead{display:flex;justify-content:space-between;align-items:center;position:relative}
.console .top{position:relative;margin-top:2mm;align-items:flex-end}
.console h1.pixel{color:var(--candy);font-size:20pt;line-height:1}
.console .range{color:var(--cream);font-family:var(--mono);font-size:7.4pt}
.console .range .todo{color:var(--candy)}
.keypad{display:grid;grid-template-columns:repeat(7,1fr);gap:1.4mm;margin:3mm 0;position:relative}
.key{background:var(--wine);border:.3mm solid var(--gold);border-radius:2.4mm 2.4mm 3.4mm 3.4mm;display:flex;flex-direction:column;
  align-items:center;gap:.4mm;padding:1.2mm 0 1mm;color:var(--cream)}
.key .pixel{color:var(--gold);font-size:5.6pt}
.key .dn{font-family:var(--mono);font-size:7pt}
.key .ph{color:var(--candy);font-size:4.4pt;height:1.8mm;text-transform:uppercase}
.console .inset{position:relative;flex:1;padding:3mm 4mm;display:flex;flex-direction:column}
.console .label{font-family:var(--pixel);font-weight:400;font-size:7pt}
.console .one{min-height:24mm;margin:1mm 0 3mm;padding:2mm 3mm}
.console .move{height:7.4mm}
.console .number{margin:1mm 0 3mm}
.console .cell{height:11mm;font-family:var(--mono)}
.console .letgo{height:8mm}
.console .win{height:6.4mm}
.console .wins{flex:1;min-height:19mm;background:repeating-linear-gradient(180deg,transparent 0,transparent 6.1mm,var(--candy) 6.1mm,var(--candy) 6.4mm)}
.console .wins .win{display:none}
.console .foot{position:relative;color:var(--cream);margin-top:2.5mm;padding-top:0}
.console .foot .tag{color:var(--gold)}
"""

Y2K = """
.week.desk{padding:6mm 5mm}
.win9{flex:1}
.mainc{flex:1;min-width:0;padding:3mm 4mm;display:flex;flex-direction:column}
.side{width:31mm;flex:none;font-size:6.6pt;padding:2.4mm}
.desk .kicker{display:flex;align-items:center;gap:1mm}
.desk h1{font-size:22pt;line-height:1;margin:.6mm 0 1mm}
.desk .range{text-align:left;font-size:7.6pt;margin-bottom:2.4mm}
.desk .range .todo{transform:none;font-size:7.4pt}
.desk .label{font-family:var(--pixel);font-weight:400;font-size:6.8pt}
.desk .one{min-height:24mm;margin:1mm 0 3mm;padding:2mm 3mm}
.desk .move{height:7.4mm}
.desk .number{grid-template-columns:1.3fr 1fr 1fr;margin:1mm 0 3mm}
.desk .cell{height:11mm}
.desk .letgo{height:8mm}
.desk .win{height:6.4mm}
.desk .mainc .foot{margin-top:2mm}
.desk .wins{flex:1;min-height:19mm;background:repeating-linear-gradient(180deg,transparent 0,transparent 6.1mm,var(--candy) 6.1mm,var(--candy) 6.4mm)}
.desk .wins .win{display:none}
.desk .foot{font-size:6pt}
.desk .foot .marker{font-size:8.4pt}
.mood{display:flex;align-items:center;gap:1.2mm}
.mrow{display:flex;align-items:center;gap:1mm;padding:.3mm 0}
.mrow .ph{margin-left:auto;font-size:4.6pt;color:var(--magenta);text-transform:uppercase}
.side .bottom{margin-top:auto}
.updated{font-family:var(--mono);font-size:5.8pt;color:var(--plum);margin-top:1mm}
.counter{font-size:5.4pt}
"""

CSS = """
@page{size:var(--pw) var(--ph);margin:0}
body{background:#fff}
.paper{display:flex;width:var(--pw);height:var(--ph)}
.cutline{width:0;border-left:.3mm dashed #b9a3ad}
.week{width:148mm;height:210mm;display:flex;flex-direction:column;overflow:hidden;flex:none}
.week.lined{padding:9mm 9mm 7mm 19mm}
@media screen and (max-width:480px){.paper{width:auto;height:auto;flex-direction:column}.week{zoom:.66}}
.top{display:flex;justify-content:space-between;align-items:flex-end}
.kicker{color:var(--wine);font-size:7pt}
h1{font-family:var(--didone);font-weight:900;color:var(--wine);font-size:31pt;line-height:.95;letter-spacing:-.01em}
.range{font-size:8.6pt;text-align:right}
.range .todo{font-size:8.4pt;display:block;white-space:nowrap;transform:rotate(-3deg);margin-bottom:1mm}
.moons{display:grid;grid-template-columns:repeat(7,1fr);gap:1mm;margin:3.5mm 0 3mm;padding:2mm 1.5mm;background:var(--plum);border-radius:1.6mm}
.day{display:flex;flex-direction:column;align-items:center;color:var(--cream);font-size:6.4pt;gap:.6mm}
.day .tag{color:var(--gold);font-size:5.6pt}
.day .ph{color:var(--candy);font-size:5pt;height:2.2mm;text-transform:uppercase;letter-spacing:.06em}
.label{color:var(--wine);font-size:8pt;margin-bottom:1mm}
.one{position:relative;background:#fff;border:.35mm solid var(--candy);border-radius:1.6mm;padding:4mm 4mm 3mm;min-height:31mm;
  box-shadow:.6mm 1mm 2mm rgba(30,6,20,.18);margin:2mm 0 4mm}
.one .line{border-bottom:.3mm solid var(--candy);height:7.2mm}
.write{font-family:var(--marker);color:var(--ink);font-size:12pt;line-height:7.2mm}
.move{display:flex;align-items:center;gap:2.4mm;border-bottom:.3mm solid var(--candy);height:8.2mm}
.move .n{font-family:var(--didone);font-weight:900;color:var(--wine);font-size:11pt;width:5mm;flex:none;text-align:left;line-height:1}
.number{display:grid;grid-template-columns:1.6fr 1fr 1fr;gap:2mm;margin:1mm 0 4mm}
.cell{background:rgba(255,255,255,.75);border:.3mm solid var(--candy);border-radius:1.2mm;padding:1.2mm 2mm;height:13mm}
.cell .tag{font-size:5.8pt;color:var(--plum)}
.letgo{display:flex;align-items:flex-end;gap:2mm;border-bottom:.3mm solid var(--candy);height:9mm}
.letgo .marker{font-size:12pt;transform:rotate(-2deg);white-space:nowrap}
.win{border-bottom:.3mm solid var(--candy);height:7.4mm}
.foot{margin-top:auto;display:flex;justify-content:space-between;align-items:center;font-size:6.6pt;padding-top:2mm}
.foot .marker{font-size:9.5pt}
.cam{display:inline-block;border:.4mm solid var(--ink);border-radius:1mm;width:6mm;height:4.2mm;position:relative;margin-right:1.5mm;vertical-align:middle}
.cam::after{content:"";position:absolute;width:2mm;height:2mm;border:.4mm solid var(--ink);border-radius:50%;left:1.6mm;top:.7mm}
"""


def monday_on_or_after(d: date) -> date:
    return d + timedelta(days=(7 - d.weekday()) % 7)


def week_days(start: date, off: timedelta) -> list[dict]:
    a = datetime.combine(start, time(), tzinfo=timezone.utc) - off
    phases = {(t + off).date(): n for n, t in phases_between(a, a + timedelta(days=7))}
    days = []
    for i in range(7):
        d = start + timedelta(days=i)
        noon = datetime.combine(d, time(12), tzinfo=timezone.utc) - off
        days.append({"day": d, "age": moon_age(noon), "phase": phases.get(d, "")})
    return days


def written(text: str | None) -> str:
    return f"<span class='write'>{esc(text)}</span>" if text else ""


def blocks(fill: dict) -> dict:
    """The shared pieces of the page, the same in every motif."""
    moves = fill.get("moves") or []
    return {
        "one": (f"<div class='line'>{written(fill.get('one_thing'))}</div><div class='line'></div><div class='line'></div>"),
        "moves": "".join(
            f"<div class='move'><span class='n'>{i}</span><span class='box'></span>"
            f"{written(moves[i - 1] if i <= len(moves) else '')}</div>" for i in range(1, 4)),
        "number": (f"<div class='number'><div class='cell'><span class='tag'>What</span><br>{written(fill.get('number'))}</div>"
                   f"<div class='cell'><span class='tag'>Monday</span></div><div class='cell'><span class='tag'>Sunday</span></div></div>"),
        "letgo": f"<div class='letgo'><span class='marker'>let go of:</span>{written(fill.get('let_go'))}</div>",
        "wins": "<div class='wins'><div class='win'></div><div class='win'></div><div class='win'></div></div>",
    }


def body(b: dict) -> str:
    return (f"<div class='label tag'>The one thing</div><div class='one'>{b['one']}</div>"
            f"<div class='label tag'>Three moves</div>{b['moves']}"
            f"<div class='label tag' style='margin-top:4mm'>One number to watch</div>{b['number']}{b['letgo']}"
            f"<div class='label tag' style='margin-top:4mm'>Small wins</div>{b['wins']}")


def sheet(start: date, days: list[dict], hemi: str, fill: dict, motif: str = "analog") -> str:
    end = start + timedelta(days=6)
    rng = f"{nice(start)} to {nice(end)} {end.year}"
    todo = f"<span class='hand todo'>{esc(S.line('todo'))}</span>" if S.line("todo") else ""
    who = esc(S.current().get("handle", ""))
    b = blocks(fill)
    if motif == "cyberpunk":
        keys = "".join(
            f"<div class='key'><span class='pixel'>{d['day'].strftime('%a')}</span>{moon_svg(d['age'], 5, hemi)}"
            f"<span class='dn'>{d['day'].day}</span><span class='ph'>{esc(d['phase'])}</span></div>" for d in days)
        return (f"<section class='week console'>{M.screws()}<div class='screen'>"
                f"<div class='chead'>{M.prompt('thisweek --start ' + start.isoformat())}{M.leds()}</div>"
                f"<div class='top'><h1 class='pixel'>THIS WEEK</h1><div class='range'>{todo}{esc(rng)}</div></div>"
                f"<div class='keypad'>{keys}</div><div class='inset'>{body(b)}</div>"
                f"<div class='foot'>{M.prompt('photograph me when done')}<span class='tag'>{who}</span></div></div></section>")
    if motif == "y2k-blog":
        today = days[0]
        rows = "".join(f"<div class='mrow'>{moon_svg(d['age'], 3.6, hemi)}<span>{d['day'].strftime('%a')} {d['day'].day}</span>"
                       f"<span class='ph'>{esc(d['phase'])}</span></div>" for d in days)
        side = (f"<aside class='side'><div><h4>mood</h4><div class='mood'>{moon_svg(today['age'], 5, hemi)} "
                f"{esc(phase_word(today['age']))}</div></div><div><h4>the moon</h4>{rows}</div>"
                f"<div><h4>guestbook</h4><div class='guest'><div class='ln'></div><div class='ln'></div></div></div>"
                f"<div class='bottom'>{M.hit_counter()}<div class='updated'>{who}</div></div></aside>")
        main = (f"<div class='mainc'><div class='kicker tag'>{M.star('2.4mm')} Pocket week</div><h1>THIS WEEK</h1>"
                f"<div class='range'>{todo}{esc(rng)}</div>{body(b)}"
                f"<div class='foot'><span class='tag'><span class='cam'></span>Photograph me when done</span>"
                f"<span class='marker'>Claude reads it back.</span></div></div>")
        return f"<section class='week desk'>{M.window('thisweek.exe', main + side)}</section>"
    strip = "".join(
        f"<div class='day'><span class='tag'>{d['day'].strftime('%a')}</span>{moon_svg(d['age'], 7, hemi)}"
        f"<span>{d['day'].day} {d['day'].strftime('%b')}</span><span class='ph'>{esc(d['phase'])}</span></div>"
        for d in days)
    return (f"<section class='week lined grain'>"
            f"<div class='top'><div><div class='kicker tag'>Pocket week</div><h1>THIS<br>WEEK</h1></div>"
            f"<div class='range'>{todo}{esc(rng)}</div></div>"
            f"<div class='moons'>{strip}</div>{body(b)}"
            f"<div class='foot'><span class='tag'><span class='cam'></span>Photograph me when done</span>"
            f"<span class='marker'>Claude reads it back.</span><span class='tag'>{who}</span></div></section>")


def build_html(start: date, off: timedelta, hemi: str = "north", fill: dict | None = None,
               two_up: bool = False, motif: str | None = None) -> str:
    motif = M.resolve(motif)
    days = week_days(start, off)
    one = sheet(start, days, hemi, fill or {}, motif)
    if two_up:
        html = f"<div class='paper'>{one}<div class='cutline'></div>{one}</div>"
        dims = ":root{--pw:297mm;--ph:210mm}"
    else:
        html = f"<div class='paper'>{one}</div>"
        dims = ":root{--pw:148mm;--ph:210mm}"
    css = dims + CSS + M.css() + {"analog": "", "cyberpunk": CYBER, "y2k-blog": Y2K}[motif]
    if motif == "y2k-blog":
        css += f".desk{{background-image:{M.tiled_bg()}}}"
    return page(f"This week: {nice(start)}", css, html)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Render the Pocket Week printable.")
    ap.add_argument("--out", default="out", help="folder for the files")
    ap.add_argument("--start", help="first day of the week (default: the coming Monday)")
    ap.add_argument("--utc-offset", help="your clock, like +08:00 or -5 (default: this computer)")
    ap.add_argument("--hemisphere", choices=("north", "south"), default="north")
    ap.add_argument("--one-thing", help="prefill the one thing")
    ap.add_argument("--move", action="append", default=[], help="prefill a move (up to three)")
    ap.add_argument("--number", help="prefill the number to watch")
    ap.add_argument("--let-go", help="prefill the let-go line")
    ap.add_argument("--two-up", action="store_true", help="two A5 copies on one A4 landscape sheet")
    ap.add_argument("--motif", choices=M.CHOICES, help="analog, cyberpunk or y2k-blog (default: your style.json)")
    ap.add_argument("--style", help="a style.json (default: ./style.json, then ~/.rocha-coded/style.json)")
    ap.add_argument("--html-only", action="store_true", help="skip Chrome, no PDF")
    a = ap.parse_args(argv)
    S.use(a.style)
    print(f"Style: {S.current().get('name') or 'unnamed'} ({S.source()})")
    if len(a.move) > 3:
        raise SystemExit("Three moves, no more. That's the point.")
    off = parse_offset(a.utc_offset)
    today = (datetime.now(timezone.utc) + off).date()
    start = parse_date(a.start) if a.start else monday_on_or_after(today)
    fill = {"one_thing": a.one_thing, "moves": a.move, "number": a.number, "let_go": a.let_go}
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    html_path = out / "week.html"
    html_path.write_text(build_html(start, off, a.hemisphere, fill, a.two_up, a.motif), encoding="utf-8")
    print(f"Pocket Week: {nice(start)} to {nice(start + timedelta(days=6))}"
          f"{' (two-up on A4)' if a.two_up else ' (A5)'}. HTML: {html_path}")
    if not a.html_only:
        ok, err = render.html_to_pdf(html_path, out / "week.pdf")
        print(f"PDF: {out / 'week.pdf'}" if ok else render.fallback_note(html_path) + (f"\n({err})" if err else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
