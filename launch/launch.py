#!/usr/bin/env python3
"""Sacred Launch Calendar: a launch arc laid on the real moon.

    python3 launch/launch.py --offer "Spring Breath Retreat" --date 2026-11-02 --weeks 6 --out out/

Computes the moon phases in the window (offline, no API) and that year's equinoxes and
solstices, then lays six stages (seed, build, open, peak, close, integrate) onto the
phases with two or three plain-language content beats each. Writes launch.ics,
launch.html (one printable page), launch.md and, with Chrome, launch.pdf.
"""
from __future__ import annotations

import argparse
import sys
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core import ics, render  # noqa: E402
from core import style as S  # noqa: E402
from core.moon import moon_age, phases_between, seasons  # noqa: E402
from core.style import PHASE_AGE  # noqa: E402
from core.when import nice, offset_label, parse_date, parse_offset  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from launch_html import to_html  # noqa: E402
from core import motif as M  # noqa: E402

ARC = (
    ("seed", "Seed", "Plant the idea before you sell it.",
     ("tell the origin story", "name the problem out loud")),
    ("build", "Build", "Warm the room. Let them lean in.",
     ("show the receipts", "teach the one thing they get wrong", "open the waitlist")),
    ("open", "Open", "Say it plainly. The doors are open.",
     ("open the doors", "send the letter to the waitlist", "go live and say the price")),
    ("peak", "Peak", "Be everywhere you already are.",
     ("answer the three objections", "share a client's words, with her permission", "show what's inside")),
    ("close", "Close", "Calm, clear, certain.",
     ("say the deadline once, calmly", "close with the one line")),
    ("integrate", "Integrate", "Rest is part of the launch.",
     ("rest and debrief", "welcome the women who said yes")),
)
MOON_NOTE = {
    "new moon": "New moon. Plant it. Say it before it's perfect.",
    "first quarter": "First quarter. Build and decide. Momentum loves a choice.",
    "full moon": "Full moon. Everything is lit. Be seen.",
    "last quarter": "Last quarter. Release what isn't working.",
}
BETWEEN = (
    (0.03, "Dark moon. Rest before the seed."),
    (0.25, "Waxing crescent. Small steps, out loud."),
    (0.50, "Waxing gibbous. Refine and repeat."),
    (0.75, "Waning gibbous. Share what you know."),
    (0.97, "Waning crescent. Clear space. Whisper the idea."),
    (1.01, "Dark moon. Rest before the seed."),
)


def between_note(d: date, off: timedelta) -> tuple[float, str]:
    age = moon_age(datetime.combine(d, time(12), tzinfo=timezone.utc) - off)
    return age, next(text for limit, text in BETWEEN if age < limit)


def window_phases(start: date, end: date, off: timedelta) -> list[tuple[str, date, datetime]]:
    a = datetime.combine(start - timedelta(days=4), time(), tzinfo=timezone.utc)
    b = datetime.combine(end + timedelta(days=4), time(), tzinfo=timezone.utc)
    return [(n, (t + off).date(), t) for n, t in phases_between(a, b)]


def nearest_new_moon(d: date, off: timedelta) -> date:
    news = [p[1] for p in window_phases(d - timedelta(days=16), d + timedelta(days=16), off)
            if p[0] == "new moon"]
    return min(news, key=lambda x: (abs((x - d).days), x))


def plan(offer: str, start: date, weeks: int = 6, off: timedelta = timedelta(0),
         hemisphere: str = "north") -> dict:
    if not 4 <= weeks <= 12:
        raise SystemExit("--weeks must be between 4 and 12.")
    end = start + timedelta(days=weeks * 7)  # exclusive
    phases = window_phases(start, end, off)
    seg = weeks * 7 / len(ARC)
    starts: list[date] = [start]
    anchors: list[str | None] = [next((n for n, d, _ in phases if d == start), None)]
    for i in range(1, len(ARC)):
        nominal = start + timedelta(days=round(i * seg))
        best = None
        for name, d, _ in phases:
            room_before = (d - starts[-1]).days >= 3
            room_after = (end - d).days >= 3 * (len(ARC) - i)
            if abs((d - nominal).days) <= 3 and room_before and room_after:
                if best is None or abs((d - nominal).days) < abs((best[1] - nominal).days):
                    best = (name, d)
        starts.append(best[1] if best else nominal)
        anchors.append(best[0] if best else None)

    stages = []
    for i, (key, label, line, beats) in enumerate(ARC):
        s0 = starts[i]
        s1 = starts[i + 1] if i + 1 < len(ARC) else end
        length = (s1 - s0).days
        moons = [(n, d) for n, d, _ in phases if s0 <= d < s1]
        beat_list = [{"day": s0 + timedelta(days=round(j * length / len(beats))), "text": t}
                     for j, t in enumerate(beats)]
        age, note = between_note(s0, off)
        if anchors[i]:
            age, note = PHASE_AGE[anchors[i]], MOON_NOTE[anchors[i]]
        stages.append({"key": key, "label": label, "line": line, "start": s0,
                       "end": s1 - timedelta(days=1), "anchor": anchors[i], "moons": moons, "age": age,
                       "moon_note": note, "beats": beat_list})

    years = sorted({start.year, (end - timedelta(days=1)).year})
    season_rows = [{"name": n, "feel": f, "day": (t + off).date(), "utc": t,
                    "in_window": start <= (t + off).date() < end}
                   for y in years for n, f, t in seasons(y, hemisphere)]
    return {"offer": offer, "start": start, "end": end - timedelta(days=1), "weeks": weeks,
            "offset": off, "hemisphere": hemisphere,
            "phases": [{"name": n, "day": d, "utc": t} for n, d, t in phases if start <= d < end],
            "seasons": season_rows, "stages": stages,
            "nearest_new_moon": nearest_new_moon(start, off)}


def to_ics(p: dict, stamp: datetime | None = None) -> str:
    events = []
    for st in p["stages"]:
        for b in st["beats"]:
            events.append({"day": b["day"], "summary": f"{st['label']}: {b['text']} ({p['offer']})",
                           "description": f"{st['line']} {st['moon_note']}", "category": "Launch"})
    for ph in p["phases"]:
        events.append({"day": ph["day"], "summary": ph["name"].capitalize(),
                       "description": f"Exact time {ph['utc'].strftime('%Y-%m-%d %H:%M')} UTC. "
                                      f"{MOON_NOTE[ph['name']]}", "category": "Moon"})
    for s in p["seasons"]:
        if s["in_window"]:
            events.append({"day": s["day"], "summary": f"{s['name'].capitalize()} ({s['feel']})",
                           "description": f"Exact time {s['utc'].strftime('%Y-%m-%d %H:%M')} UTC.",
                           "category": "Season"})
    events.sort(key=lambda e: e["day"])
    return ics.calendar(f"Launch: {p['offer']}", events, stamp)


def to_md(p: dict) -> str:
    out = [f"# Sacred Launch: {p['offer']}", "",
           f"{nice(p['start'])} to {nice(p['end'])} {p['end'].year}. {p['weeks']} weeks. "
           f"Dates in {offset_label(p['offset'])}.", "", "## Moon", ""]
    out += [f"- {nice(ph['day'])}: {ph['name']}" for ph in p["phases"]]
    out += ["", "## Equinoxes and solstices", ""]
    out += [f"- {nice(s['day'])} {s['day'].year}: {s['name']} ({s['feel']})"
            + (" **in your launch**" if s["in_window"] else "") for s in p["seasons"]]
    for st in p["stages"]:
        out += ["", f"## {st['label']}: {nice(st['start'])} to {nice(st['end'])}", "",
                f"> {st['line']} {st['moon_note']}", ""]
        out += [f"- [ ] {b['text']} {{due: {b['day'].isoformat()}}}" for b in st["beats"]]
    return "\n".join(out) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Lay a launch arc on the moon.")
    ap.add_argument("--offer", required=True, help="the name of what you're launching")
    ap.add_argument("--date", help="first day of the launch window (default: today)")
    ap.add_argument("--weeks", type=int, default=6, help="length of the window, 4 to 12 (default 6)")
    ap.add_argument("--out", default="out", help="folder for the files")
    ap.add_argument("--utc-offset", help="your clock, like +08:00 or -5 (default: this computer)")
    ap.add_argument("--hemisphere", choices=("north", "south"), default="north")
    ap.add_argument("--align", action="store_true", help="move the start to the nearest new moon")
    ap.add_argument("--style", help="a style.json (default: ./style.json, then ~/.rocha-coded/style.json)")
    ap.add_argument("--motif", choices=M.CHOICES, help="analog, cyberpunk or y2k-blog (default: your style.json)")
    ap.add_argument("--html-only", action="store_true", help="skip Chrome, no PDF")
    a = ap.parse_args(argv)
    S.use(a.style)
    print(f"Style: {S.current().get('name') or 'unnamed'} ({S.source()})")
    off = parse_offset(a.utc_offset)
    start = parse_date(a.date) if a.date else (datetime.now(timezone.utc) + off).date()
    if a.align:
        moved = nearest_new_moon(start, off)
        print(f"Aligned: start moved from {start} to the new moon on {moved}.")
        start = moved
    p = plan(a.offer.strip(), start, a.weeks, off, a.hemisphere)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "launch.ics").write_text(to_ics(p), encoding="utf-8", newline="")
    (out / "launch.md").write_text(to_md(p), encoding="utf-8")
    html_path = out / "launch.html"
    motif = M.resolve(a.motif)
    html_path.write_text(to_html(p, motif), encoding="utf-8")

    print(f"Sacred Launch: {p['offer']}, {nice(p['start'])} to {nice(p['end'])} {p['end'].year} ({motif})")
    for st in p["stages"]:
        moon = f" on the {st['anchor']}" if st["anchor"] else ""
        print(f"  {st['label']:<9} {nice(st['start'])}{moon}: " + "; ".join(b["text"] for b in st["beats"]))
    print("Moon: " + ", ".join(f"{ph['name']} {nice(ph['day'])}" for ph in p["phases"]))
    if not a.align and p["nearest_new_moon"] != start:
        print(f"Tip: the nearest new moon is {p['nearest_new_moon']}. Add --align to start on it.")
    print(f"Wrote {out / 'launch.ics'}, {out / 'launch.md'}, {html_path}")
    if not a.html_only:
        ok, err = render.html_to_pdf(html_path, out / "launch.pdf")
        print(f"PDF: {out / 'launch.pdf'}" if ok else render.fallback_note(html_path) + (f"\n({err})" if err else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
