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
from core import style as S  # noqa: E402
from core.moon import moon_age, phases_between  # noqa: E402
from core.style import esc, moon_svg, page  # noqa: E402
from core.when import nice, parse_date, parse_offset  # noqa: E402

CSS = """
@page{size:var(--pw) var(--ph);margin:0}
body{background:#fff}
.paper{display:flex;width:var(--pw);height:var(--ph)}
.cutline{width:0;border-left:.3mm dashed #b9a3ad}
.week{width:148mm;height:210mm;padding:9mm 9mm 7mm 19mm;display:flex;flex-direction:column;overflow:hidden;flex:none}
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


def sheet(start: date, days: list[dict], hemi: str, fill: dict) -> str:
    end = start + timedelta(days=6)
    strip = "".join(
        f"<div class='day'><span class='tag'>{d['day'].strftime('%a')}</span>{moon_svg(d['age'], 7, hemi)}"
        f"<span>{d['day'].day} {d['day'].strftime('%b')}</span><span class='ph'>{esc(d['phase'])}</span></div>"
        for d in days)
    one = fill.get("one_thing")
    one_lines = (f"<div class='line'>{written(one)}</div><div class='line'></div><div class='line'></div>")
    moves = fill.get("moves") or []
    move_rows = "".join(
        f"<div class='move'><span class='n'>{i}</span><span class='box'></span>{written(moves[i - 1] if i <= len(moves) else '')}</div>"
        for i in range(1, 4))
    num = fill.get("number")
    todo = f"<span class='hand todo'>{esc(S.line('todo'))}</span>" if S.line("todo") else ""
    who = S.current().get("handle", "")
    return (f"<section class='week lined grain'>"
            f"<div class='top'><div><div class='kicker tag'>Pocket week</div><h1>THIS<br>WEEK</h1></div>"
            f"<div class='range'>{todo}{esc(nice(start))} to {esc(nice(end))} {end.year}</div></div>"
            f"<div class='moons'>{strip}</div>"
            f"<div class='label tag'>The one thing</div><div class='one'>{one_lines}</div>"
            f"<div class='label tag'>Three moves</div>{move_rows}"
            f"<div class='label tag' style='margin-top:4mm'>One number to watch</div>"
            f"<div class='number'><div class='cell'><span class='tag'>What</span><br>{written(num)}</div>"
            f"<div class='cell'><span class='tag'>Monday</span></div><div class='cell'><span class='tag'>Sunday</span></div></div>"
            f"<div class='letgo'><span class='marker'>let go of:</span>{written(fill.get('let_go'))}</div>"
            f"<div class='label tag' style='margin-top:4mm'>Small wins</div>"
            f"<div class='win'></div><div class='win'></div><div class='win'></div>"
            f"<div class='foot'><span class='tag'><span class='cam'></span>Photograph me when done</span>"
            f"<span class='marker'>Claude reads it back.</span><span class='tag'>{esc(who)}</span></div></section>")


def build_html(start: date, off: timedelta, hemi: str = "north", fill: dict | None = None,
               two_up: bool = False) -> str:
    days = week_days(start, off)
    one = sheet(start, days, hemi, fill or {})
    if two_up:
        body = f"<div class='paper'>{one}<div class='cutline'></div>{one}</div>"
        dims = ":root{--pw:297mm;--ph:210mm}"
    else:
        body = f"<div class='paper'>{one}</div>"
        dims = ":root{--pw:148mm;--ph:210mm}"
    return page(f"This week: {nice(start)}", dims + CSS, body)


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
    html_path.write_text(build_html(start, off, a.hemisphere, fill, a.two_up), encoding="utf-8")
    print(f"Pocket Week: {nice(start)} to {nice(start + timedelta(days=6))}"
          f"{' (two-up on A4)' if a.two_up else ' (A5)'}. HTML: {html_path}")
    if not a.html_only:
        ok, err = render.html_to_pdf(html_path, out / "week.pdf")
        print(f"PDF: {out / 'week.pdf'}" if ok else render.fallback_note(html_path) + (f"\n({err})" if err else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
