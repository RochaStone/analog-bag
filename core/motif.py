"""Three motif families, one set of tokens.

Motifs are STRUCTURE (paper, a girly terminal, a 2003 blog window); the style tokens
are COLOUR AND TYPE. Every page renders its one data model through any of the three.
"""
from __future__ import annotations

from . import style as S
from .style import esc

MOTIFS = ("analog", "cyberpunk", "y2k-blog")
ALIASES = {
    "guest-check": "analog", "front-page": "analog", "magazine-scrawl": "analog",
    "pink-paper": "analog", "leopard": "analog", "neutral": "analog", "": "analog",
    "rotary": "cyberpunk", "retro-tv": "cyberpunk", "terminal": "cyberpunk",
    "sticker-collage": "y2k-blog", "y2k": "y2k-blog", "blog": "y2k-blog",
}
CHOICES = MOTIFS + tuple(k for k in ALIASES if k)


def resolve(cli: str | None = None) -> str:
    """--motif wins, then style.json motif, then analog. Old names map to a family."""
    raw = (cli or S.current().get("motif") or "analog").strip().lower()
    if raw in MOTIFS:
        return raw
    if raw in ALIASES:
        return ALIASES[raw]
    raise SystemExit(f"Unknown motif '{raw}'. Pick one of: {', '.join(MOTIFS)}.")


# ---- pixel bitmaps (drawn as merged SVG rects, so they stay tiny and crisp) ----
STAR = ("...#...", "...#...", "..###..", "#######", "..###..", "...#...", "...#...")
HEART = (".##.##.", "#######", "#######", ".#####.", "..###..", "...#...")
DIGITS = {
    "0": ("###", "#.#", "#.#", "#.#", "###"), "1": (".#.", "##.", ".#.", ".#.", "###"),
    "2": ("###", "..#", "###", "#..", "###"), "3": ("###", "..#", "###", "..#", "###"),
    "4": ("#.#", "#.#", "###", "..#", "..#"), "5": ("###", "#..", "###", "..#", "###"),
    "6": ("###", "#..", "###", "#.#", "###"), "7": ("###", "..#", "..#", ".#.", ".#."),
    "8": ("###", "#.#", "###", "#.#", "###"), "9": ("###", "#.#", "###", "..#", "###"),
}


def rects(bitmap: tuple[str, ...], cell: float = 1, dx: float = 0, dy: float = 0) -> str:
    out = []
    for y, row in enumerate(bitmap):
        x = 0
        while x < len(row):
            if row[x] == "#":
                run = x
                while run < len(row) and row[run] == "#":
                    run += 1
                out.append(f"<rect x='{dx + x * cell:g}' y='{dy + y * cell:g}' "
                           f"width='{(run - x) * cell:g}' height='{cell:g}'/>")
                x = run
            else:
                x += 1
    return "".join(out)


def pixel_svg(bitmap: tuple[str, ...], size: str, color: str) -> str:
    w, h = len(bitmap[0]), len(bitmap)
    return (f"<svg viewBox='0 0 {w} {h}' width='{size}' height='{size}' shape-rendering='crispEdges' "
            f"aria-hidden='true'><g fill='{color}'>{rects(bitmap)}</g></svg>")


def star(size: str = "3mm", color: str | None = None) -> str:
    return pixel_svg(STAR, size, color or S.color("gold"))


def heart(size: str = "3mm", color: str | None = None) -> str:
    return pixel_svg(HEART, size, color or S.color("gold"))


def blocks(filled: int, total: int = 6) -> str:
    """A progress bar made of blocks (no glow)."""
    return ("<span class='blocks' aria-label='stage " + str(filled) + " of " + str(total) + "'>"
            + "".join(f"<i class='{'on' if i < filled else 'off'}'></i>" for i in range(total)) + "</span>")


def hit_counter(number: str = "000,777") -> str:
    return f"<div class='counter'>you are visitor no. <b>{esc(number)}</b></div>"


def window(title: str, body: str, cls: str = "") -> str:
    """Mac OS 9 style window chrome: cream window, plum title bar, three gold buttons."""
    return (f"<div class='win9 {cls}'><div class='bar'><span class='btns'><i></i><i></i><i></i></span>"
            f"<span class='wtitle'>{esc(title)}</span></div><div class='pane'>{body}</div></div>")


def prompt(command: str) -> str:
    return (f"<div class='prompt'><span class='ps'>rocheverse:~$</span> {esc(command)}"
            f"<span class='cursor'></span></div>")


def leds() -> str:
    return "<span class='leds'><i class='c'></i><i class='g'></i><i class='c'></i></span>"


def screws() -> str:
    return "".join(f"<i class='screw {p}'></i>" for p in ("tl", "tr", "bl", "br"))


def tiled_bg() -> str:
    """A tiled blush pattern of tiny gold pixel stars, as a CSS background value."""
    g = S.color("gold").replace("#", "%23")
    svg = (f"<svg xmlns='http://www.w3.org/2000/svg' width='28' height='28' shape-rendering='crispEdges'>"
           f"<g fill='{g}' opacity='.35'>{rects(STAR, 1, 3, 3)}{rects(STAR, 1, 17, 17)}</g></svg>")
    return f'url("data:image/svg+xml;utf8,{svg}")'


def css() -> str:
    """Shared chrome for the cyberpunk and y2k-blog skins."""
    return """
:root{--pixel:'Silkscreen','Pixelify Sans','Courier New',monospace}
.pixel{font-family:var(--pixel);font-weight:400;letter-spacing:.02em;text-transform:uppercase}
/* cyberpunk: a plum console, soft scanlines, no glow */
.console{background:var(--wine);position:relative}
.console .screen{position:absolute;inset:5mm;background:var(--plum);border-radius:3mm;overflow:hidden;
  display:flex;flex-direction:column;color:var(--cream)}
.console .screen::before{content:"";position:absolute;inset:0;pointer-events:none;
  background:repeating-linear-gradient(180deg,rgba(255,247,244,.035) 0,rgba(255,247,244,.035) .5mm,transparent .5mm,transparent 1.2mm)}
.screw{position:absolute;width:2.4mm;height:2.4mm;border-radius:50%;background:var(--gold);border:.3mm solid var(--plum)}
.screw.tl{left:1.3mm;top:1.3mm}.screw.tr{right:1.3mm;top:1.3mm}.screw.bl{left:1.3mm;bottom:1.3mm}.screw.br{right:1.3mm;bottom:1.3mm}
.prompt{font-family:var(--mono);font-size:8pt;color:var(--cream)}
.prompt .ps{color:var(--candy)}
.cursor{display:inline-block;width:1.6mm;height:3mm;background:var(--candy);vertical-align:-.5mm;margin-left:1mm;
  animation:blink 1.1s steps(1) infinite}
@keyframes blink{50%{opacity:0}}
@media print{.cursor{animation:none}}
.leds i{display:inline-block;width:1.8mm;height:1.8mm;border-radius:50%;margin-left:1mm}
.leds .c{background:var(--candy)}.leds .g{background:var(--gold)}
.blocks{display:inline-flex;gap:.6mm}
.blocks i{display:inline-block;width:2.6mm;height:2.6mm}
.blocks .on{background:var(--candy)}.blocks .off{border:.3mm solid var(--candy);opacity:.6}
.inset{background:var(--cream);color:var(--ink);border-radius:1.4mm}
/* y2k-blog: an OS 9 window on tiled blush */
.desk{background-color:var(--paper)}
.win9{background:var(--cream);border:.4mm solid var(--plum);border-radius:1.6mm;box-shadow:1mm 1.4mm 0 rgba(30,6,20,.25);overflow:hidden;
  display:flex;flex-direction:column}
.win9 .bar{background:var(--plum);color:var(--cream);display:flex;align-items:center;gap:2mm;padding:1.2mm 2mm;flex:none}
.win9 .btns i{display:inline-block;width:2.4mm;height:2.4mm;border-radius:50%;background:var(--gold);margin-right:.8mm}
.win9 .wtitle{font-family:var(--pixel);font-size:8pt;letter-spacing:.06em;margin:0 auto;padding-right:8mm}
.win9 .pane{flex:1;display:flex;min-height:0}
.side{background:var(--paper);border-left:.3mm dashed var(--plum);padding:3mm;font-size:7.4pt;display:flex;flex-direction:column;gap:2.2mm}
.side h4{font-family:var(--pixel);font-weight:400;font-size:6.6pt;color:var(--wine);letter-spacing:.06em;
  border-bottom:.3mm solid var(--candy);padding-bottom:.6mm;margin-bottom:.8mm}
.counter{font-family:var(--mono);font-size:6.4pt;background:var(--plum);color:var(--gold);padding:1mm 1.4mm;border-radius:.8mm}
.counter b,.side .counter b{color:var(--cream);font-weight:400;letter-spacing:.1em}
.marquee{font-family:var(--mono);font-size:7pt;color:var(--wine);border-bottom:.3mm dashed var(--plum);padding:1mm 0;white-space:nowrap;overflow:hidden}
.guest{border:.3mm solid var(--candy);border-radius:1mm;background:#fff;padding:1.2mm;min-height:14mm}
.guest .ln{border-bottom:.3mm solid var(--candy);height:4.6mm}
"""
