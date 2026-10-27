"""The printable launch page. One data model, three motif skins:
analog (pink lined paper), cyberpunk (a plum launch console), y2k-blog (launch.exe)."""
from __future__ import annotations

from datetime import date

from core import motif as M
from core import style as S
from core.style import PHASE_AGE, esc, moon_svg, page
from core.when import nice, offset_label

PHASE_WORDS = ("new moon", "waxing crescent", "first quarter", "waxing gibbous",
               "full moon", "waning gibbous", "last quarter", "waning crescent")


def phase_word(age: float) -> str:
    return PHASE_WORDS[int(((age % 1) * 8) + 0.5) % 8]


def model(p: dict) -> dict:
    hemi = p["hemisphere"]
    return {
        "offer": p["offer"], "weeks": p["weeks"], "offset": offset_label(p["offset"]),
        "range": f"{nice(p['start'])} to {nice(p['end'])} {p['end'].year}",
        "open_day": nice(p["stages"][2]["start"]),
        "phases": [{"svg": moon_svg(PHASE_AGE[ph["name"]], 8, hemi), "small": moon_svg(PHASE_AGE[ph["name"]], 4, hemi),
                    "name": ph["name"], "day": nice(ph["day"])} for ph in p["phases"]],
        "seasons": [{"text": f"{s['feel']} {nice(s['day'])}", "in": s["in_window"]}
                    for s in p["seasons"] if s["day"].year == p["start"].year],
        "stages": [{"n": i, "label": st["label"], "dates": f"{nice(st['start'])} to {nice(st['end'])}",
                    "line": st["line"], "note": st["moon_note"], "icon": moon_svg(st["age"], 4.2, hemi),
                    "beats": [(nice(b["day"]), b["text"]) for b in st["beats"]], "pens": 5 - len(st["beats"])}
                   for i, st in enumerate(p["stages"], 1)],
        "mood": phase_word(p["stages"][0]["age"]), "mood_svg": moon_svg(p["stages"][0]["age"], 5, hemi),
        "scrawl": S.line("scrawl"), "handle": S.current().get("handle", ""),
    }


def _seasons(m: dict, sep: str = " &middot; ") -> str:
    return sep.join(f"<b>{esc(s['text'])}</b>" if s["in"] else esc(s["text"]) for s in m["seasons"])


def _beats(st: dict, mono_box: bool = False) -> str:
    box = "<span class='box'></span>"
    rows = "".join(f"<div class='beat'>{box}<span class='d'>{esc(d)}</span><span>{esc(t)}</span></div>"
                   for d, t in st["beats"])
    return rows + f"<div class='beat pen'>{box}<span class='d'></span><span></span></div>" * st["pens"]


def _strip(m: dict) -> str:
    return "".join(f"<div class='ph'>{ph['svg']}<span class='tag'>{esc(ph['name'])}</span>"
                   f"<span>{esc(ph['day'])}</span></div>" for ph in m["phases"])


def _handle(m: dict) -> str:
    return f" <span class='tag handle'>{esc(m['handle'])}</span>" if m["handle"] else ""


def analog(m: dict) -> str:
    cards = "".join(
        f"<div class='stage'><div class='num'>{st['n']:02d}</div><div class='tag'>{esc(st['label'])}</div>"
        f"<div class='dates'>{esc(st['dates'])}</div><div class='line'>{esc(st['line'])}</div>"
        f"<div class='note'>{st['icon']}<span>{esc(st['note'])}</span></div>{_beats(st)}</div>"
        for st in m["stages"])
    return (f"<main class='sheet lined grain'><div class='kicker tag'>Sacred launch calendar &middot; {m['weeks']} weeks"
            f" &middot; {esc(m['offset'])}</div><h1>{esc(m['offer'])}</h1>"
            f"<div class='sub'><span>{esc(m['range'])}</span>"
            f"<span class='scrawl'>doors open {esc(m['open_day'])}!</span></div>"
            f"<div class='strip'>{_strip(m)}</div><div class='seasons'>This year: {_seasons(m)}</div>"
            f"<div class='grid'>{cards}</div>"
            f"<div class='foot'><span class='tag'>Tick in pen. Photograph me. Claude reads it back.</span>"
            f"<span><span class='marker'>{esc(m['scrawl'])}</span>{_handle(m)}</span></div></main>")


def cyberpunk(m: dict) -> str:
    panels = "".join(
        f"<div class='panel'><div class='phead'><span class='pixel'>[{st['n']:02d}] {esc(st['label'])}</span>"
        f"{M.blocks(st['n'])}</div><div class='inset'><div class='dates'>{esc(st['dates'])}</div>"
        f"<div class='note'>{st['icon']}<span>{esc(st['note'])}</span></div>{_beats(st)}</div></div>"
        for st in m["stages"])
    command = f'launch --offer "{m["offer"]}" --weeks {m["weeks"]}'
    return (f"<main class='sheet console'>{M.screws()}<div class='screen'>"
            f"<div class='chead'>{M.prompt(command)}"
            f"{M.leds()}</div><h1 class='pixel'>{esc(m['offer'])}</h1>"
            f"<div class='sub'><span>{esc(m['range'])} &middot; {esc(m['offset'])}</span>"
            f"<span class='doors pixel'>doors open {esc(m['open_day'])}</span></div>"
            f"<div class='strip'>{_strip(m)}</div><div class='seasons'>{_seasons(m, ' / ')}</div>"
            f"<div class='grid'>{panels}</div>"
            f"<div class='foot'>{M.prompt('tick in pen, photograph me, claude reads it back')}"
            f"<span><span class='marker'>{esc(m['scrawl'])}</span>{_handle(m)}</span></div></div></main>")


def y2k_blog(m: dict) -> str:
    star = M.star("2.6mm")
    cards = "".join(
        f"<div class='stage'><div class='tag'>{star} {esc(st['label'])} <span class='n'>{st['n']:02d}</span></div>"
        f"<div class='dates'>{esc(st['dates'])}</div><div class='line'>{esc(st['line'])}</div>"
        f"<div class='note'>{st['icon']}<span>{esc(st['note'])}</span></div>{_beats(st)}</div>"
        for st in m["stages"])
    moons = "".join(f"<div class='mrow'>{ph['small']}<span>{esc(ph['name'])}</span><span class='d'>{esc(ph['day'])}</span></div>"
                    for ph in m["phases"])
    marquee = f" {star} ".join([f"doors open {esc(m['open_day'])}"] +
                               [f"{esc(ph['name'])} {esc(ph['day'])}" for ph in m["phases"][:4]])
    about = esc(m["offer"]) + (f"<br>by {esc(m['handle'])}" if m["handle"] else "")
    side = (f"<aside class='side'><div><h4>about me</h4>{about}</div>"
            f"<div><h4>mood</h4><div class='mood'>{m['mood_svg']} {esc(m['mood'])}</div></div>"
            f"<div><h4>the moon</h4>{moons}</div><div><h4>this year</h4>{_seasons(m, '<br>')}</div>"
            f"<div><h4>guestbook</h4><div class='guest'><div class='ln'></div><div class='ln'></div><div class='ln'></div></div></div>"
            f"<div><h4>currently</h4>launching {esc(m['offer'])}<br>doors open {esc(m['open_day'])}</div>"
            f"<div class='bottom'>{M.hit_counter()}<div class='updated'>last updated {esc(date.today().isoformat())}</div></div></aside>")
    main = (f"<div class='mainc'><div class='marquee'>{star} {marquee} {star}</div>"
            f"<div class='kicker tag'>Sacred launch calendar &middot; {m['weeks']} weeks &middot; {esc(m['offset'])}</div>"
            f"<h1>{esc(m['offer'])}</h1><div class='sub'><span>{esc(m['range'])}</span>"
            f"<span class='scrawl'>{esc(m['scrawl'])}</span></div><div class='grid'>{cards}</div>"
            f"<div class='foot'><span class='tag'>Tick in pen. Photograph me. Claude reads it back.</span>{_handle(m)}</div></div>")
    return f"<main class='sheet desk'>{M.window('launch.exe', main + side)}</main>"


SKINS = {"analog": analog, "cyberpunk": cyberpunk, "y2k-blog": y2k_blog}


def to_html(p: dict, motif: str = "analog") -> str:
    motif = M.resolve(motif)
    m = model(p)
    css = BASE + M.css() + {"analog": ANALOG, "cyberpunk": CYBER, "y2k-blog": Y2K}[motif]
    if motif == "y2k-blog":
        css += f".desk{{background-image:{M.tiled_bg()}}}"
    return page(f"Launch: {p['offer']}", css, SKINS[motif](m))


BASE = """
@page{size:A4;margin:0}
body{background:var(--cream)}
.sheet{width:210mm;height:297mm;display:flex;flex-direction:column;overflow:hidden}
@media screen and (max-width:600px){.sheet{zoom:.46}}
.beat{display:flex;gap:2mm;align-items:center;font-size:9.4pt;padding:1.6mm 0;border-bottom:.3mm solid var(--candy)}
.beat .d{font-family:var(--mono);font-size:7.4pt;color:var(--magenta);min-width:19mm;white-space:nowrap}
.beat.pen{height:7.6mm}
.beat.pen .box{border-color:var(--candy)}
.strip{display:flex;justify-content:space-around;gap:2.4mm;flex-wrap:wrap;margin:4mm 0 2mm;padding:2.5mm 3mm;background:var(--plum);border-radius:2mm}
.ph{display:flex;flex-direction:column;align-items:center;color:var(--cream);font-size:6.6pt;min-width:12mm}
.ph .tag{color:var(--gold);font-size:5.8pt;margin-top:.8mm;letter-spacing:.08em}
.note{font-size:7.4pt;display:flex;gap:1.5mm;align-items:center}
.foot{margin-top:3mm;display:flex;justify-content:space-between;align-items:center;font-size:8pt}
.foot .marker{font-size:11pt}
.handle{font-size:7pt;margin-left:2mm}
"""

ANALOG = """
.sheet.lined{padding:11mm 11mm 9mm 20mm}
.kicker{color:var(--wine);font-size:8.5pt}
h1{font-family:var(--didone);font-weight:900;color:var(--wine);font-size:30pt;line-height:1;margin:1.5mm 0 1mm;letter-spacing:-.01em}
.sub{display:flex;justify-content:space-between;align-items:baseline;font-size:9.5pt}
.scrawl{font-family:var(--marker);color:var(--magenta);font-size:13pt;transform:rotate(-2deg);display:inline-block}
.seasons{font-size:7.6pt;margin:1mm 0 3mm;color:var(--ink)}
.seasons b{color:var(--wine)}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:4mm;flex:1}
.stage{background:rgba(255,255,255,.78);border:.35mm solid var(--candy);border-radius:2mm;padding:3mm 3.5mm;position:relative;
  box-shadow:.6mm 1mm 2mm rgba(30,6,20,.16)}
.stage .num{position:absolute;right:3mm;top:2mm;font-family:var(--didone);font-size:20pt;color:var(--candy);font-weight:900}
.stage .tag{color:var(--wine);font-size:9pt}
.stage .dates{font-size:8pt;color:var(--ink)}
.stage .line{font-family:var(--didone);font-style:italic;font-size:10pt;margin:1.2mm 0 .6mm}
.stage .note{color:var(--plum)}
.handle{color:var(--plum)}
"""

CYBER = """
.console .screen{padding:7mm 7mm 5mm}
.chead{display:flex;justify-content:space-between;align-items:center;position:relative}
h1.pixel{color:var(--candy);font-size:24pt;line-height:1.05;margin:3mm 0 1.5mm;position:relative}
.sub{display:flex;justify-content:space-between;align-items:baseline;font-family:var(--mono);font-size:8.4pt;position:relative}
.doors{color:var(--gold);font-size:8pt}
.strip{border:.3mm solid var(--gold);position:relative}
.seasons{font-family:var(--mono);font-size:6.8pt;margin:1mm 0 3mm;opacity:.85;position:relative}
.seasons b{color:var(--gold);font-weight:400}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:3.5mm;flex:1;position:relative}
.panel{display:flex;flex-direction:column;border:.3mm solid var(--candy);border-radius:1.6mm;overflow:hidden}
.phead{display:flex;justify-content:space-between;align-items:center;padding:1.4mm 2.4mm;font-size:8pt;color:var(--cream)}
.panel .inset{flex:1;padding:2mm 3mm;border-radius:0}
.panel .dates{font-family:var(--mono);font-size:7.4pt;color:var(--wine)}
.panel .note{color:var(--plum);margin:.6mm 0}
.panel .beat{font-family:var(--mono);font-size:8pt}
.foot{position:relative;color:var(--cream)}
.foot .marker{color:var(--candy)}
.handle{color:var(--gold)}
"""

Y2K = """
.sheet.desk{padding:9mm}
.win9{flex:1}
.mainc{flex:1;padding:4mm 5mm;display:flex;flex-direction:column;min-width:0}
.side{width:47mm;flex:none}
.kicker{color:var(--wine);font-size:7.6pt;margin-top:2mm}
h1{font-family:var(--didone);font-weight:900;color:var(--wine);font-size:24pt;line-height:1;margin:1mm 0 1mm}
.sub{display:flex;justify-content:space-between;align-items:baseline;font-size:8.6pt;margin-bottom:3mm}
.scrawl{font-family:var(--marker);color:var(--magenta);font-size:11pt;transform:rotate(-2deg);display:inline-block}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:3mm;flex:1}
.stage{background:#fff;border:.3mm solid var(--candy);border-radius:1.2mm;padding:2.4mm 2.8mm}
.stage .tag{font-family:var(--pixel);font-weight:400;color:var(--wine);font-size:8pt;display:flex;align-items:center;gap:1mm}
.stage .tag .n{margin-left:auto;color:var(--candy)}
.stage .dates{font-family:var(--mono);font-size:7pt}
.stage .line{font-family:var(--didone);font-style:italic;font-size:9pt;margin:.8mm 0 .4mm}
.stage .note{color:var(--plum);font-size:6.8pt}
.stage .beat{font-size:8.4pt;padding:1.2mm 0}
.stage .beat .d{min-width:16mm;font-size:6.8pt}
.stage .beat.pen{height:6.4mm}
.mood{display:flex;align-items:center;gap:1.2mm}
.mrow{display:flex;align-items:center;gap:1.2mm;font-size:6.8pt;padding:.4mm 0}
.mrow .d{margin-left:auto;font-family:var(--mono);font-size:6.2pt}
.side b{color:var(--wine)}
.updated{font-family:var(--mono);font-size:6pt;color:var(--plum);margin-top:1.2mm}
.side .bottom{margin-top:auto}
.handle{color:var(--plum)}
"""
