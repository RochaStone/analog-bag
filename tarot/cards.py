"""One HOOK ORACLE card template in the zine language, for print and for stories.

Every length is in container units (cqw/cqh), so the same markup prints at 70 x 120 mm,
63 x 88 mm (mini) and renders as a 1080 x 1920 story card. Colours and fonts come from
style.json; the motif (analog, cyberpunk, y2k-blog) switches the stock and the chrome.

Front: riso ink on blush (or plum) stock, a gold grimoire border with a moon-phase strip,
the numeral as ransom-note cut letters, the name in the display face with a misregistered
second ink, the structure typed on a taped slip with the blanks in pink marker, the example
on a torn strip, a stub with "pull it when", a barcode and a dotted cut line.
Back: a holographic LORE stamp over a moon strip, two staples, the Rocheverse eye as a
pixel mark, and the scrawl line.
"""
from __future__ import annotations

import base64
import functools
import random
import re
import struct
import zlib
from pathlib import Path

from core import motif as M
from core import style as S
from core.style import esc
from pixels import PIXELS, pixel_sticker

HERE = Path(__file__).resolve().parent
OBJECTS = HERE / "objects"

# Majors with a painted object. The rest get the ransom-note treatment (see docs/MAJORS-TO-PAINT.md).
MAJOR_OBJECT = {
    "major-02": "thermal-printer.png",   # The Receipt
    "major-05": "flip-phone.png",        # The Hotline
    "major-10": "seashell.png",          # The Full Circle
    "major-11": "crystal-ball.png",      # The Fine Print
    "major-12": "incense.png",           # The Pause
    "major-13": "pillar-candle.png",     # The Ending
    "major-14": "cauldron.png",          # The Recipe
    "major-15": "rose.png",              # The Confession (sub rosa)
    "major-17": "gold-star.png",         # The North Star
    "major-18": "crescent-moon.png",     # The Night Shift
    "major-19": "lantern.png",           # The Golden Hour
    "major-21": "shell-map.png",         # The Whole World
}
# Majors still to paint (docs/MAJORS-TO-PAINT.md). When the painted PNG is saved in tarot/objects/
# under this name the card uses it; until then the card keeps its pixel sticker.
PAINT_NEXT = {
    "major-00": "first-day.png",       # The First Day
    "major-01": "spotlight.png",       # The One Woman Show
    "major-03": "guest-check.png",     # The Guest Check
    "major-04": "alarm-clock.png",     # Too Busy
    "major-06": "front-page.png",      # The Front Page
    "major-07": "key.png",             # The Plot Twist
    "major-08": "envelope.png",        # The Permission Slip
    "major-09": "door.png",            # The Quiet Room
    "major-16": "tower.png",           # The Collapse
    "major-20": "scales.png",          # The Verdict
}
GRAIN = f"url('{(OBJECTS / 'grain.png').as_uri()}') 0 0/240px 240px"
# suit: (accent css variable, what it is for, main object, second object)
SUITS = {
    "cups": ("candy", "feeling", "tealight.png", "seashell.png"),
    "wands": ("gold", "bold", "pillar-candle.png", "gold-star.png"),
    "swords": ("cool", "questions", "crystal-cluster.png", "incense.png"),
    "pentacles": ("magenta", "proof", "thermal-printer.png", "guest-check-stamp.png"),
}
RANKS = ("Ace", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten",
         "Page", "Knight", "Queen", "King")
RANK_MARK = {"Ace": "A", "Page": "P", "Knight": "Kn", "Queen": "Q", "King": "K", "Two": "2", "Three": "3",
             "Four": "4", "Five": "5", "Six": "6", "Seven": "7", "Eight": "8", "Nine": "9", "Ten": "10"}
# pip layouts: centres as % of the object area, for one to ten objects
PIPS = {
    1: [(50, 52)], 2: [(32, 40), (68, 62)], 3: [(24, 36), (50, 64), (76, 36)],
    4: [(28, 30), (72, 30), (28, 72), (72, 72)], 5: [(24, 28), (76, 28), (50, 52), (24, 76), (76, 76)],
    6: [(20, 30), (50, 30), (80, 30), (20, 72), (50, 72), (80, 72)],
    7: [(16, 28), (39, 28), (62, 28), (85, 28), (27, 72), (50, 72), (73, 72)],
    8: [(16, 28), (39, 28), (62, 28), (85, 28), (16, 72), (39, 72), (62, 72), (85, 72)],
    9: [(12, 28), (31, 28), (50, 28), (69, 28), (88, 28), (21, 72), (40, 72), (60, 72), (79, 72)],
    10: [(12, 28), (31, 28), (50, 28), (69, 28), (88, 28), (12, 72), (31, 72), (50, 72), (69, 72), (88, 72)],
}
PIP_W = {1: 70, 2: 40, 3: 30, 4: 34, 5: 30, 6: 26, 7: 21, 8: 21, 9: 17, 10: 17}
PIP_SIZE = {1: 90, 2: 58, 3: 52, 4: 44, 5: 42, 6: 40, 7: 38, 8: 38, 9: 34, 10: 34}
MOON_PHASES = (0, .125, .25, .375, .5, .625, .75, .875, 1)
EYE = ("........#####........", ".....###.....###.....", "...##...........##...",
       ".##...............##.", "#...................#", ".##...............##.",
       "...##...........##...", ".....###.....###.....", "........#####........")
EYE_IRIS = ("..###..", ".#####.", "##...##", ".#####.", "..###..")
RAYS = ("#...#...#...#...#",)


# ------------------------------------------------------------------ small parts

def ransom(text: str, cls: str = "") -> str:
    """Cut letters, each from a different 'magazine'. Seeded by the text, so it never changes."""
    rnd = random.Random(f"ransom:{text}")
    out, last = [], 0
    for ch in text:
        if ch == " ":
            out.append("<i class='sp'></i>")
            continue
        k = rnd.choice([n for n in range(1, 7) if n != last])
        last = k
        out.append(f"<span class='r{k}' style='transform:translateY({rnd.uniform(-.07, .07):.2f}em) "
                   f"rotate({rnd.uniform(-8, 8):.1f}deg);font-size:{rnd.uniform(.86, 1.08):.2f}em'>{esc(ch)}</span>")
    return f"<span class='ransom {cls}' aria-label='{esc(text)}'>{''.join(out)}</span>"


def _moon(f: float, r: float, cx: float, cy: float) -> str:
    if f < .02 or f > .98:
        return ""
    import math
    rx = abs(math.cos(2 * math.pi * f)) * r
    top, bot = f"{cx:.2f} {cy - r:.2f}", f"{cx:.2f} {cy + r:.2f}"
    if f <= .5:
        outer, sweep = f"M{top} A{r} {r} 0 0 1 {bot}", 0 if f < .25 else 1
    else:
        outer, sweep = f"M{top} A{r} {r} 0 0 0 {bot}", 1 if f > .75 else 0
    return f"{outer} A{rx:.2f} {r} 0 0 {sweep} {top} Z"


def moon_strip(cls: str = "moonstrip") -> str:
    r, step, items = 8.5, 26, []
    for i, f in enumerate(MOON_PHASES):
        cx = 13 + i * step
        lit = _moon(f, r, cx, 13)
        items.append(f"<circle cx='{cx}' cy='13' r='{r}' class='md'/>" + (f"<path d='{lit}' class='ml'/>" if lit else ""))
        if i < 8:
            x = cx + step / 2
            items.append(f"<path d='M{x:.1f} 10 l1 2.4 2.4 1 -2.4 1 -1 2.4 -1 -2.4 -2.4 -1 2.4 -1z' class='ms'/>")
    return (f"<svg class='{cls}' viewBox='0 0 {26 + step * 8} 26' preserveAspectRatio='xMidYMid meet' "
            f"aria-hidden='true'>{''.join(items)}</svg>")


CORNER = ("<svg viewBox='0 0 40 40' aria-hidden='true'><path d='M2 38 V8 Q2 2 8 2 H38' class='c1'/>"
          "<path d='M6 38 V11 Q6 6 11 6 H38' class='c2'/>"
          "<path d='M9 9 l2.2 5.2 5.2 2.2 -5.2 2.2 -2.2 5.2 -2.2 -5.2 -5.2 -2.2 5.2 -2.2z' "
          "transform='translate(5 5) scale(.7)' class='cs'/>"
          "<path d='M14 2 q4 6 10 4 M2 14 q6 4 4 10' class='c3'/>"
          "<circle cx='30' cy='2' r='1.6' class='cs'/><circle cx='2' cy='30' r='1.6' class='cs'/></svg>")


def corners() -> str:
    return "<div class='corners'>" + "".join(f"<i class='k{k}'>{CORNER}</i>" for k in range(4)) + "</div>"


def barcode(seed: str) -> str:
    rnd, x, bars = random.Random(f"bar:{seed}"), 0.0, []
    while x < 94:
        w = rnd.choice([.8, .8, 1.2, 1.6, 2.4])
        bars.append(f"<rect x='{x:.1f}' width='{w}' height='30'/>")
        x += w + rnd.choice([.8, 1.2, 1.6])
    return f"<svg class='bc' viewBox='0 0 96 30' preserveAspectRatio='none' aria-hidden='true'>{''.join(bars)}</svg>"


def torn(name: str, seed: int, n: int = 30) -> str:
    """A clip-path with ripped top and bottom edges."""
    rnd = random.Random(seed)
    top = [f"{i / n * 100:.1f}% {rnd.uniform(.1, 1.3):.2f}cqw" for i in range(n + 1)]
    bot = [f"{100 - i / n * 100:.1f}% calc(100% - {rnd.uniform(.1, 1.3):.2f}cqw)" for i in range(n + 1)]
    return f".{name}{{clip-path:polygon({','.join(top + bot)})}}"


def blanks(text: str) -> str:
    """The structure with every {slot} as a pink marker fill. The braces stay in the text
    (hidden), so the words read exactly as in deck.json."""
    out = []
    for part in re.split(r"(\{[^{}]*\})", text):
        if part.startswith("{") and part.endswith("}"):
            out.append(f"<span class='blank'><i class='br'>{{</i>{esc(part[1:-1])}<i class='br'>}}</i></span>")
        else:
            out.append(esc(part))
    return "".join(out)


def object_for(card: dict) -> list[str]:
    """Paths of the art for a card: the user's override from style.json, else the deck's own.
    Keys checked: card name, card id, suit, 'all'. A value of 'none' means type only."""
    own = S.current().get("tarot", {}).get("objects", {})
    for key in (card["name"].lower(), card["id"].lower(), card.get("suit", "major"), "all"):
        if key in own:
            return [] if own[key] == "none" else [own[key]]
    if card["arcana"] == "major":
        f = MAJOR_OBJECT.get(card["id"]) or card.get("object")
        if f and (OBJECTS / f).is_file():
            return [str(OBJECTS / f)]
        painted = PAINT_NEXT.get(card["id"])
        return [str(OBJECTS / painted)] if painted and (OBJECTS / painted).is_file() else []
    _, _, a, b = SUITS[card["suit"]]
    return [str(OBJECTS / a), str(OBJECTS / b)]


def type_only(card: dict) -> bool:
    """True when the user's style.json says 'none' for this card: the numeral alone."""
    own = S.current().get("tarot", {}).get("objects", {})
    for key in (card["name"].lower(), card["id"].lower(), card.get("suit", "major"), "all"):
        if key in own:
            return own[key] == "none"
    return False


def _src(path: str) -> str:
    return esc(Path(path).as_uri())


# ------------------------------------------------------------------ the card

def hero(card: dict) -> str:
    art = object_for(card)
    rnd = random.Random(card["id"])
    if card["arcana"] == "major":
        if art:
            rot = rnd.uniform(-6, 6)
            return (f"<div class='hero'><i class='disc'></i><img class='obj major' src='{_src(art[0])}' alt='' "
                    f"style='--rot:{rot:.1f}deg'><span class='fig'>fig. {esc(card['numeral'])}</span></div>")
        n = card["numeral"]
        if card["id"] in PIXELS and not type_only(card):
            return (f"<div class='hero type px' style='--rot:{rnd.uniform(-7, 7):.1f}deg'><i class='disc'></i>"
                    f"{pixel_sticker(card['id'])}<span class='pstar a'>{M.star('100%')}</span>"
                    f"<span class='fig'>fig. {esc(n)}</span></div>")
        size = min(26.0, 64.0 / max(1, len(n)))
        return (f"<div class='hero type'><i class='disc'></i>{ransom(n, 'big')}"
                f"<span class='pstar a'>{M.star('100%')}</span><span class='pstar b'>{M.star('100%')}</span>"
                f"<span class='fig'>fig. {esc(n)}</span></div>").replace(
                    "class='ransom big'", f"class='ransom big' style='font-size:{size:.1f}cqw'")
    idx = RANKS.index(card["rank"])
    side = "l" if idx % 2 == 0 else "r"
    if not art:
        return f"<div class='hero type'><i class='disc {side}'></i>{ransom(RANK_MARK[card['rank']], 'big')}</div>"
    if idx >= 10:  # court cards: the object, the second object and the rank as cut letters
        main = f"<img class='obj minor {side}' src='{_src(art[0])}' alt='' style='--rot:{rnd.uniform(-7, 7):.1f}deg'>"
        second = (f"<img class='obj second {side}' src='{_src(art[1])}' alt='' "
                  f"style='--rot:{rnd.uniform(-14, 14):.1f}deg'>" if len(art) > 1 else "")
        return (f"<div class='hero court'><i class='disc {side}'></i>{main}{second}"
                f"{ransom(card['rank'].upper(), 'court ' + side)}</div>")
    n = idx + 1  # pip cards: as many objects as the rank, scattered like a spilled handful
    pips = []
    for x, y in PIPS[n]:
        pips.append(f"<img class='obj pip' src='{_src(art[0])}' alt='' style='left:{x + rnd.uniform(-3, 3):.1f}%;"
                    f"top:{y + rnd.uniform(-4, 4):.1f}%;height:{PIP_SIZE[n]}%;max-width:{PIP_W[n]}cqw;--rot:{rnd.uniform(-16, 16):.1f}deg'>")
    return f"<div class='hero pips'><i class='disc {side}'></i>{''.join(pips)}</div>"


def accent_mark(card: dict) -> str:
    """One seeded extra per card, so the deck reads as a pile of collage, not a template."""
    v = random.Random(f"mark:{card['id']}")
    kind = v.choice(("washi", "hearts", "star", "washi", "none"))
    top = v.uniform(18, 40)
    side = "left" if v.random() < .5 else "right"
    if kind == "washi":
        return f"<i class='mk washi' style='top:{top:.0f}%;{side}:-4cqw;transform:rotate({v.uniform(-40, 40):.0f}deg)'></i>"
    if kind == "hearts":
        h = "".join(M.heart("100%", "var(--candy)") for _ in range(3))
        return f"<span class='mk hearts' style='top:{top:.0f}%;{side}:5cqw'>{h}</span>"
    if kind == "star":
        return f"<span class='mk pstar' style='top:{top:.0f}%;{side}:6cqw'>{M.star('100%')}</span>"
    return ""


def set_label(card: dict) -> str:
    """The set name shown on a card from a monthly set; empty for the core deck."""
    return card.get("set_name", "") if card.get("set", "core") != "core" else ""


def front_html(card: dict, motif: str, x: float | None = 0, y: float | None = 0, kicker: str = "") -> str:
    major = card["arcana"] == "major"
    accent, meaning = ("candy", "") if major else (SUITS[card["suit"]][0], SUITS[card["suit"]][1])
    if major:
        right = f"<span class='kick set'>{esc(set_label(card))}</span>" if set_label(card) else \
            "<span class='kick'>major arcana</span>"
        left = ransom(card["numeral"], "num")
        title = ""
    else:
        left = f"<span class='kick'>{esc(card['suit'])} &middot; {esc(meaning)}</span>"
        right = ransom(RANK_MARK[card["rank"]], "num")
        title = f"<div class='ttl'>{esc(card['title'])}</div>"
    if kicker:
        if not major:
            left = ransom(RANK_MARK[card["rank"]], "num")
        right = f"<span class='kick pos'>{esc(kicker)}</span>"
    chrome = ""
    if motif == "y2k-blog":
        slug = re.sub(r"[^a-z0-9]+", "-", card["name"].lower()).strip("-")
        chrome = f"<div class='wbar'><span class='btns'><i></i><i></i><i></i></span>{esc(slug)}.txt</div>"
    elif motif == "cyberpunk":
        chrome = "<div class='prompt'><span class='ps'>rocheverse:~$</span> cat hook<span class='cur'></span></div>"
    pos = "" if x is None else f" style='left:{x}mm;top:{y}mm'"
    v = random.Random(f"vary:{card['id']}")
    sign = 1 if v.random() < .5 else -1
    vary = (f"--sa:var(--{accent});--slr:{sign * v.uniform(.5, 1.5):.2f}deg;--exr:{-sign * v.uniform(.5, 1.6):.2f}deg;"
            f"--disc:var(--disc-{accent});--tx:{v.uniform(18, 62):.0f}%;--tr:{v.uniform(-6, 6):.1f}deg")
    return (f"<div class='card' data-m='{esc(motif)}'{pos}><div class='face fr m-{esc(motif)}' "
            f"style='{vary}'>{accent_mark(card)}<div class='stock'></div><div class='frame'></div>{corners()}"
            f"{moon_strip()}<div class='head'>{left}{right}</div>{hero(card)}"
            f"<div class='nm'><div class='name' data-r='{esc(card['name'])}'>{esc(card['name'])}</div>{title}</div>"
            f"<div class='slip'><i class='tape'></i>{chrome}<div class='structure'>{blanks(card['structure'])}</div></div>"
            f"<div class='ex torn-ex'>{esc(card['example'])}</div>"
            f"<div class='stub'><span class='sc'>&#9986;</span><div class='when'><b>pull it when</b>"
            f"{esc(card['when_to_pull'])}</div><div class='code'>{barcode(card['id'])}"
            f"<span class='no'>No. {esc(card['id'])}</span></div></div></div></div>")


def eye_svg() -> str:
    """The Rocheverse eye as a pixel mark: gold lids, a candy iris, rays above and below."""
    return ("<svg class='eye' viewBox='-1 -1 23 15' shape-rendering='crispEdges' aria-hidden='true'>"
            f"<g class='eo'>{M.rects(EYE, 1, 0, 2)}</g><g class='ei'>{M.rects(EYE_IRIS, 1, 7, 4)}</g>"
            "<rect x='10' y='6' width='1' height='1' class='ep'/>"
            f"<g class='er'>{M.rects(RAYS, 1, 2, 0)}{M.rects(RAYS, 1, 2, 12)}</g></svg>")


def back_html(motif: str, x: float | None = 0, y: float | None = 0, set_name: str = "") -> str:
    st = S.current()
    stamp, scrawl = S.line("stamp"), S.line("scrawl")
    lore_cls = "lore pixel" if motif == "cyberpunk" else "lore holo"
    handle = f" &middot; {esc(st['handle'])}" if st.get("handle") else ""
    if set_name:
        handle = f" &middot; {esc(set_name)}" + handle
    pos = "" if x is None else f" style='left:{x}mm;top:{y}mm'"
    return (f"<div class='card back' data-m='{esc(motif)}'{pos}><div class='face bk m-{esc(motif)}'>"
            f"<div class='stock'></div><div class='frame'></div>{corners()}"
            f"<i class='staple s1'></i><i class='staple s2'></i>"
            f"{moon_strip('moonstrip top')}<div class='eyebox'>{eye_svg()}<i class='xer'></i></div>"
            f"{moon_strip('moonstrip mid')}"
            + (f"<div class='{lore_cls}'><span>{esc(stamp)}</span></div>" if stamp else "")
            + (f"<div class='scrawl'>{esc(scrawl)}</div>" if scrawl else "")
            + f"<div class='sub'>HOOK ORACLE{handle}</div>{barcode('back')}</div></div>")


def story_html(card: dict, motif: str, kicker: str = "") -> str:
    """One card as a full 1080 x 1920 story page."""
    css_ = (":root{--cw:1080px;--ch:1920px}html,body{width:1080px;height:1920px;overflow:hidden}"
            + css() + ".card{position:relative}")
    body = fonts_extra() + f"<style>{tile_css()}</style>" + front_html(card, motif, None, None, kicker)
    return S.page(f"HOOK ORACLE {card['name']}", css_, body)


# ------------------------------------------------------------------ styles

HOLO = ("linear-gradient(118deg,var(--cool) 8%,#8FD8B4 24%,#fff 38%,var(--accent-c) 52%,var(--gold) 68%,"
        "var(--cool) 84%,#fff 96%)")


def css() -> str:
    return CSS.replace("%STAMP%", ink_tile()).replace("%HOLO%", HOLO) + torn("torn-ex", 5)


CSS = """
.card{position:absolute;width:var(--cw);height:var(--ch);overflow:hidden;container-type:size}
.face{position:absolute;inset:0;display:flex;flex-direction:column;padding:4.4cqw 7.2cqw 4.6cqw;isolation:isolate;
  --accent-c:var(--candy);--fg:var(--ink);--st:var(--paper);--dot:color-mix(in srgb,var(--candy) 55%,transparent);
  --md:var(--plum);--ml:var(--cream);--exb:var(--plum);--exf:var(--cream);color:var(--fg);--dots:var(--dots-a)}
.m-cyberpunk{--dots:var(--dots-c);--fg:var(--cream);--st:var(--plum);--dot:color-mix(in srgb,var(--candy) 22%,transparent);--md:var(--wine);
  --ml:var(--candy);--exb:var(--candy);--exf:var(--ink)}
.m-y2k-blog{--dots:var(--dots-y);--st:var(--cream);--dot:color-mix(in srgb,var(--magenta) 16%,transparent);--exb:var(--wine)}
.stock{position:absolute;inset:0;z-index:-3;background-color:var(--st);
  background-image:var(--dots);background-size:1.7cqw 1.7cqw}
.stock::after{content:"";position:absolute;inset:0;background:var(--grain) 0 0/24cqw 24cqw;opacity:.9}
.m-cyberpunk .stock::before{content:"";position:absolute;inset:0;
  background:repeating-linear-gradient(180deg,rgba(255,247,244,.05) 0 .35cqw,transparent .35cqw .9cqw)}
.m-y2k-blog .stock{background-image:var(--tile),var(--dots);
  background-size:9cqw 9cqw,1.7cqw 1.7cqw}
.frame{position:absolute;inset:2.4cqw;border:.45cqw solid var(--gold);outline:.22cqw solid var(--gold);
  outline-offset:-1.5cqw;z-index:-2;pointer-events:none}
.corners i{position:absolute;width:10cqw;height:10cqw;z-index:-1}
.corners svg{width:100%;height:100%;display:block}
.corners .c1{fill:none;stroke:var(--gold);stroke-width:1.6}.corners .c2{fill:none;stroke:var(--gold);stroke-width:.8}
.corners .c3{fill:none;stroke:var(--gold);stroke-width:1}.corners .cs{fill:var(--gold)}
.corners .k0{left:1.1cqw;top:1.1cqw}.corners .k1{right:1.1cqw;top:1.1cqw;transform:scaleX(-1)}
.corners .k2{left:1.1cqw;bottom:1.1cqw;transform:scaleY(-1)}.corners .k3{right:1.1cqw;bottom:1.1cqw;transform:scale(-1,-1)}
.moonstrip{display:block;flex:none;width:54cqw;height:5.4cqw;margin:0 auto}
.moonstrip .md{fill:var(--md);stroke:var(--gold);stroke-width:1.4}.moonstrip .ml{fill:var(--ml)}.moonstrip .ms{fill:var(--gold)}
.head{flex:none;display:flex;justify-content:space-between;align-items:center;height:8.6cqw;margin-top:1.4cqw}
.kick{font-family:var(--mono);font-size:2.45cqw;letter-spacing:.2em;text-transform:uppercase;color:var(--magenta);
  border:.32cqw solid var(--magenta);border-radius:.5cqw;padding:.5cqw 1.3cqw;transform:rotate(-2deg);
  -webkit-mask-image:%STAMP%;mask-image:%STAMP%;-webkit-mask-size:30cqw;mask-size:30cqw}
.m-cyberpunk .kick{font-family:var(--pixel);letter-spacing:.08em;color:var(--candy);border-color:var(--candy)}
.ransom{display:inline-flex;align-items:center;gap:.5cqw;line-height:1;white-space:nowrap}
.ransom span{display:inline-block;padding:.1em .13em .06em;box-shadow:.25cqw .35cqw .5cqw rgba(30,6,24,.32);
  clip-path:polygon(2% 4%,30% 0,62% 3%,98% 0,100% 40%,97% 96%,64% 100%,30% 97%,0 100%,3% 52%)}
.ransom .sp{display:inline-block;width:.35em}
.ransom.num{font-size:7.4cqw}
.ransom .r1{font-family:var(--didone);font-weight:900;background:var(--cream);color:var(--ink)}
.ransom .r2{font-family:var(--tag);font-weight:800;background:var(--plum);color:var(--cream)}
.ransom .r3{font-family:var(--pixel);font-weight:700;background:var(--candy);color:var(--ink)}
.ransom .r4{font-family:var(--mono);font-weight:500;background:var(--gold);color:var(--ink)}
.ransom .r5{font-family:var(--didone);font-style:italic;font-weight:900;background:var(--wine);color:var(--candy)}
.ransom .r6{font-family:var(--tag);font-weight:800;background:#fff;color:transparent;-webkit-text-stroke:.09em var(--ink)}
.hero{flex:1 1 auto;min-height:0;position:relative;margin:.6cqw -3cqw 0}
.hero .disc{position:absolute;width:44cqw;height:44cqw;border-radius:50%;left:6cqw;top:50%;transform:translateY(-50%);
  background:var(--disc) 0 0/2.2cqw 2.2cqw;opacity:.75}
.m-cyberpunk .hero .disc{opacity:.45}
.hero .disc.r{left:auto;right:6cqw}
.obj{position:absolute;display:block;object-fit:contain;transform:rotate(var(--rot));
  filter:drop-shadow(.5cqw 0 0 #fff) drop-shadow(-.5cqw 0 0 #fff) drop-shadow(0 .5cqw 0 #fff) drop-shadow(0 -.5cqw 0 #fff)
  drop-shadow(.4cqw 1.4cqw 1.2cqw rgba(30,6,24,.42))}
.obj.major{right:-2cqw;top:0;height:100%;max-width:78cqw}
.obj.minor{top:4%;height:88%;max-width:56cqw}
.obj.minor.l{left:5cqw}.obj.minor.r{right:5cqw}
.obj.second{top:2%;height:38%;max-width:30cqw}
.obj.second.l{right:6cqw}.obj.second.r{left:6cqw}
.obj.pip{transform:translate(-50%,-50%) rotate(var(--rot));max-width:30cqw;width:auto}
.hero.pips .disc{left:50%;transform:translate(-50%,-50%)}
.ransom.court{position:absolute;top:46%;z-index:3;font-size:8.6cqw;transform:rotate(-4deg)}
.ransom.court.l{right:5cqw}.ransom.court.r{left:5cqw}
.hero.type{display:flex;align-items:center;justify-content:center}
.hero.type .disc{left:50%;transform:translate(-50%,-50%);width:52cqw;height:52cqw}
.ransom.big{position:relative;z-index:2;transform:rotate(-3deg);font-size:22cqw}
.ransom.big span{box-shadow:.5cqw .8cqw 1cqw rgba(30,6,24,.35)}
.pix{position:relative;z-index:2;height:88%;width:auto;max-width:66cqw;transform:rotate(var(--rot));
  filter:drop-shadow(.7cqw 0 0 #fff) drop-shadow(-.7cqw 0 0 #fff) drop-shadow(0 .7cqw 0 #fff) drop-shadow(0 -.7cqw 0 #fff)
  drop-shadow(.4cqw 1.4cqw 1.2cqw rgba(30,6,24,.42))}
.pstar{position:absolute;width:7cqw;height:7cqw;z-index:3}.pstar.a{left:9cqw;top:8%}.pstar.b{right:10cqw;bottom:22%;width:4.6cqw;height:4.6cqw}
.fig{position:absolute;left:2.4cqw;bottom:24%;font-family:var(--mono);font-size:2.1cqw;letter-spacing:.14em;
  color:var(--fg);opacity:.75;transform:rotate(-90deg);transform-origin:left bottom;white-space:nowrap}
.nm{flex:none;position:relative;z-index:3;margin-top:-7cqw}
.name{position:relative;font-family:var(--didone);font-weight:900;font-size:9.4cqw;line-height:.94;letter-spacing:-.025em;
  color:var(--fg);font-variation-settings:'opsz' 144;text-wrap:balance}
.name::after{content:attr(data-r);position:absolute;inset:0;transform:translate(.85cqw,.7cqw);color:var(--sa);z-index:-1;
  text-wrap:balance}
.m-cyberpunk .name::after{mix-blend-mode:normal}
.ttl{font-family:var(--marker);color:var(--magenta);font-size:5cqw;line-height:1.1;margin-top:.6cqw;transform:rotate(-2deg);
  transform-origin:left center;white-space:nowrap}
.m-cyberpunk .ttl{color:var(--candy)}
.slip{flex:none;position:relative;background:#FFFBF8;color:var(--ink);margin:3cqw -1cqw 0;padding:3.2cqw 3.6cqw 3cqw;
  transform:rotate(var(--slr,-.7deg));box-shadow:0 .5cqw 0 rgba(59,18,48,.08),0 1.4cqw 2.4cqw rgba(30,6,24,.3)}
.slip .tape{position:absolute;top:-2.3cqw;left:var(--tx,50%);width:21cqw;height:4.8cqw;margin-left:-10.5cqw;transform:rotate(var(--tr,-3deg));
  background:color-mix(in srgb,var(--sa) 78%,transparent);
  clip-path:polygon(0 8%,4% 0,9% 10%,14% 0,100% 0,96% 12%,100% 24%,95% 38%,100% 52%,96% 66%,100% 80%,95% 92%,100% 100%,0 100%,4% 86%,0 72%,5% 58%,0 44%,4% 30%,0 18%)}
.m-cyberpunk .slip .tape{mix-blend-mode:normal}
.structure{font-family:var(--mono);font-size:3.42cqw;line-height:1.5;letter-spacing:-.01em}
.blank{background:color-mix(in srgb,var(--candy) 82%,transparent);padding:.04em .18em;margin:0;border-radius:.35em .6em .4em .55em;
  -webkit-box-decoration-break:clone;box-decoration-break:clone;font-weight:500}
.br{display:none}
.wbar{display:flex;align-items:center;gap:1.4cqw;margin:-3.2cqw -3.6cqw 2.2cqw;padding:1cqw 2cqw;background:var(--plum);
  color:var(--cream);font-family:var(--pixel);font-size:2.5cqw;letter-spacing:.06em}
.wbar .btns i{display:inline-block;width:1.8cqw;height:1.8cqw;background:var(--gold);margin-right:.6cqw}
.prompt{font-family:var(--mono);font-size:2.5cqw;color:var(--magenta);margin-bottom:1.2cqw}
.prompt .cur{display:inline-block;width:1.4cqw;height:2.6cqw;background:var(--candy);vertical-align:-.4cqw;margin-left:.8cqw}
.ex{flex:none;margin:2.8cqw -2.4cqw 0;padding:3.1cqw 5cqw 3.1cqw;background:var(--exb);color:var(--exf);font-family:var(--body);
  font-style:italic;font-size:3.12cqw;line-height:1.34;transform:rotate(var(--exr,.9deg))}
.stub{flex:none;position:relative;display:grid;grid-template-columns:1fr 18cqw;gap:2.4cqw;align-items:end;
  margin-top:2.6cqw;padding-top:2.2cqw;border-top:.32cqw dashed var(--fg)}
.stub .sc{position:absolute;left:-1.6cqw;top:-3cqw;font-size:4.2cqw;line-height:1;color:var(--fg);
  font-family:'Apple Symbols','Segoe UI Symbol','DejaVu Sans',sans-serif;background:var(--st);padding:0 .6cqw}
.when{font-family:var(--mono);font-size:2.42cqw;line-height:1.38}
.when b{display:inline-block;font-weight:500;letter-spacing:.18em;text-transform:uppercase;color:var(--magenta);
  border:.28cqw solid var(--magenta);padding:.2cqw .9cqw;margin-right:1.2cqw;transform:rotate(-1.5deg);
  -webkit-mask-image:%STAMP%;mask-image:%STAMP%;-webkit-mask-size:24cqw;mask-size:24cqw}
.m-cyberpunk .when b{color:var(--candy);border-color:var(--candy)}
.code{display:flex;flex-direction:column;align-items:stretch;gap:.6cqw}
.bc{display:block;width:100%;height:6.4cqw;fill:var(--fg)}
.no{font-family:var(--mono);font-size:2cqw;letter-spacing:.1em;text-align:center;white-space:nowrap}
.mk{position:absolute;z-index:4;pointer-events:none}
.mk.washi{width:24cqw;height:5cqw;opacity:.92;
  background:var(--washi) 0 .1cqw/2.4cqw 2.4cqw,color-mix(in srgb,var(--plum) 85%,transparent);
  clip-path:polygon(0 0,100% 0,97% 20%,100% 40%,97% 60%,100% 80%,98% 100%,0 100%,3% 80%,0 60%,3% 40%,0 20%)}
.mk.hearts{display:flex;gap:1cqw;width:20cqw;height:5cqw}.mk.hearts svg{width:5cqw;height:5cqw}
.mk.pstar{width:6cqw;height:6cqw}
/* short cards (mini) lose the example; the stub stays */
@container (min-aspect-ratio: 2/3){.ex{display:none}.face{padding-top:3.6cqw}.nm{margin-top:-5cqw}}
/* back */
.bk{--dots:var(--dots-c);--st:var(--plum);--fg:var(--cream);--dot:color-mix(in srgb,var(--candy) 20%,transparent);--md:var(--wine);--ml:var(--cream)}
.bk.m-y2k-blog{--st:var(--plum)}
.bk .moonstrip{position:absolute;left:50%;transform:translateX(-50%);width:66cqw;height:6.6cqw}
.bk .moonstrip.top{top:7%}.bk .moonstrip.mid{top:58%}
.staple{position:absolute;top:1.6cqw;width:13cqw;height:2cqw;border-radius:.5cqw;z-index:6;
  background:linear-gradient(180deg,#8d8a92,#f2f0f4 45%,#a9a5ad);box-shadow:.3cqw .4cqw .4cqw rgba(0,0,0,.45)}
.staple.s1{left:22cqw;transform:rotate(-4deg)}.staple.s2{right:22cqw;transform:rotate(3deg)}
.eyebox{position:absolute;left:50%;top:21%;width:58cqw;transform:translateX(-50%)}
.eye{display:block;width:100%;height:auto}
.eye .eo{fill:var(--gold)}.eye .ei{fill:var(--candy)}.eye .ep{fill:var(--cream)}.eye .er{fill:var(--gold);opacity:.7}
.xer{position:absolute;inset:-4cqw;background-image:var(--xdots);
  background-size:1.3cqw 1.3cqw;opacity:.5}
.lore{position:absolute;left:50%;top:50%;transform:translate(-50%,0) rotate(-7deg);z-index:4;padding:1.6cqw 5cqw;
  border:1cqw solid transparent;border-image:%HOLO% 1;background:color-mix(in srgb,var(--plum) 72%,transparent);
  -webkit-mask-image:%STAMP%;mask-image:%STAMP%;-webkit-mask-size:50cqw;mask-size:50cqw}
.lore span{display:block;font-family:var(--didone);font-weight:900;font-size:21cqw;line-height:.95;letter-spacing:.06em;
  font-variation-settings:'opsz' 144;background:%HOLO%;-webkit-background-clip:text;background-clip:text;color:transparent}
.lore.pixel{border:1cqw solid var(--candy);border-image:none;-webkit-mask-image:none;mask-image:none;background:var(--plum);box-shadow:1cqw 1cqw 0 var(--candy)}
.lore.pixel span{font-family:var(--pixel);font-weight:700;font-size:16cqw;letter-spacing:.04em;background:none;color:var(--candy);-webkit-text-fill-color:var(--candy)}
.bk .scrawl{position:absolute;left:12cqw;right:12cqw;top:73%;text-align:center;font-family:var(--marker);color:var(--candy);
  font-size:6.6cqw;line-height:1.05;transform:rotate(-3deg);text-wrap:balance}
.bk .sub{position:absolute;left:0;right:0;bottom:11%;text-align:center;font-family:var(--mono);font-size:2.6cqw;
  letter-spacing:.2em;text-transform:uppercase;color:var(--gold)}
.bk .bc{position:absolute;left:50%;bottom:5%;width:22cqw;height:4.4cqw;margin-left:-11cqw;fill:var(--cream);opacity:.85}
"""


def fonts_extra() -> str:
    """The display face with its optical-size axis, when the display face is Fraunces."""
    if S.current()["fonts"].get("masthead", "").strip().lower() != "fraunces":
        return ""
    return ('<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,900;'
            '1,9..144,400&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">')


def _png(px: int, pixel) -> str:
    """A tiny RGBA PNG as a data URI, written with the standard library only."""
    rows = []
    for y in range(px):
        row = bytearray([0])
        for x in range(px):
            row += bytes(pixel(x, y))
        rows.append(bytes(row))

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", px, px, 8, 6, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(b"".join(rows), 9)) + chunk(b"IEND", b""))
    return f"url('data:image/png;base64,{base64.b64encode(png).decode()}')"


def dot_tile(hex_colour: str, opacity: float, r: float = 2.2, px: int = 40) -> str:
    """A dot screen as a small PNG tile (r is the radius on a 10-unit cell). An image tile is
    stored once in the PDF and repeated, where a gradient or vector dots repeat on every card."""
    rr, gg, bb = (int(hex_colour[i:i + 2], 16) for i in (1, 3, 5))
    rad, c = r / 10 * px, px / 2

    def pixel(x: int, y: int) -> tuple[int, int, int, int]:
        cover = sum(((x + (i + .5) / 4 - c) ** 2 + (y + (j + .5) / 4 - c) ** 2) <= rad * rad
                    for i in range(4) for j in range(4)) / 16
        return rr, gg, bb, round(255 * opacity * cover)
    return _png(px, pixel)


@functools.lru_cache(maxsize=1)
def ink_tile(px: int = 96) -> str:
    """Uneven stamp ink: a mask that is mostly solid with seeded speckles and thin patches."""
    rnd = random.Random(11)
    blots = [(rnd.uniform(0, px), rnd.uniform(0, px), rnd.uniform(3, 9)) for _ in range(14)]

    def pixel(x: int, y: int) -> tuple[int, int, int, int]:
        a = 255 if rnd.random() > .1 else rnd.randint(40, 160)
        for bx, by, br in blots:
            if (x - bx) ** 2 + (y - by) ** 2 < br * br:
                a = min(a, 110)
        return 0, 0, 0, a
    return _png(px, pixel)


def tile_css() -> str:
    """Pattern tiles, coloured from style.json at build time (so they re-tone and stay vector)."""
    col = S.color
    discs = {"candy": col("accent"), "gold": col("gold"), "cool": col("cool"), "magenta": col("marker")}
    parts = [f"--tile:{M.tiled_bg()}", f"--grain:url('{(OBJECTS / 'grain.png').as_uri()}')",
             f"--dots-a:{dot_tile(col('accent'), .55)}", f"--dots-c:{dot_tile(col('accent'), .22)}",
             f"--dots-y:{dot_tile(col('marker'), .16)}", f"--xdots:{dot_tile(col('plum'), 1, 2.7)}",
             f"--washi:{dot_tile(col('gold'), 1, 1.6)}"]
    parts += [f"--disc-{k}:{dot_tile(v, 1, 2.5)}" for k, v in discs.items()]
    return ":root{" + ";".join(parts) + "}"
