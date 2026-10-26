"""The Rocha Coded printable look: palette, type, pink lined paper and drawn moons."""
from __future__ import annotations

import html
import math

FONTS_LINK = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,wght@0,500;0,700;0,900;1,500'
    '&family=Archivo+Narrow:wght@500;700&family=Newsreader:ital,wght@0,400;0,600;1,400'
    '&family=Permanent+Marker&family=Courier+Prime&display=swap" rel="stylesheet">'
)

ROOT_CSS = """
:root{
  --hot:#FF2D8A; --candy:#FFB3D1; --paper:#FFE1EC; --cream:#F6EFE4; --ink:#111111;
  --red:#E0202E; --plum:#4A1033; --gold:#D4A64A; --blue:#BFD4EA; --white:#FFFFFF;
  --didone:'Bodoni Moda','Didot','Bodoni 72','Playfair Display',Georgia,serif;
  --tag:'Archivo Narrow','Arial Narrow','Helvetica Neue',Arial,sans-serif;
  --body:'Newsreader',Georgia,'Times New Roman',serif;
  --marker:'Permanent Marker','Marker Felt','Chalkboard SE','Comic Sans MS',cursive;
  --mono:'Courier Prime','Courier New',monospace;
}
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:var(--cream);color:var(--ink);font-family:var(--body);
  -webkit-print-color-adjust:exact;print-color-adjust:exact}
.tag{font-family:var(--tag);text-transform:uppercase;letter-spacing:.14em;font-weight:700}
.didone{font-family:var(--didone)}
.marker{font-family:var(--marker);color:var(--red)}
.lined{background-color:var(--paper);
  background-image:linear-gradient(90deg,transparent 15mm,rgba(224,32,46,.55) 15mm,
    rgba(224,32,46,.55) 15.4mm,transparent 15.4mm),
  repeating-linear-gradient(180deg,transparent 0,transparent 6.6mm,var(--candy) 6.6mm,var(--candy) 7mm);}
.grain{position:relative}
.grain::after{content:"";position:absolute;inset:0;pointer-events:none;opacity:.22;mix-blend-mode:multiply;
  background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='160' height='160'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 .3  0 0 0 0 .1  0 0 0 0 .2  0 0 0 .35 0'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>");}
.box{width:3.6mm;height:3.6mm;border:.45mm solid var(--ink);border-radius:.6mm;display:inline-block;flex:none}
"""


def esc(text: str) -> str:
    return html.escape(str(text), quote=True)


def page(title: str, css: str, body: str) -> str:
    return (f"<!doctype html><html lang='en'><head><meta charset='utf-8'>"
            f"<meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<title>{esc(title)}</title>{FONTS_LINK}<style>{ROOT_CSS}{css}</style></head>"
            f"<body>{body}</body></html>")


def moon_svg(age: float, size_mm: float, hemisphere: str = "north",
             lit: str = "#D4A64A", dark: str = "#4A1033", rim: str = "#D4A64A") -> str:
    """A drawn moon for a lunation age (0 new, .5 full). Northern sky shows the
    waxing light on the right; the southern sky mirrors it."""
    r = 10.0
    a = age % 1.0
    waxing = a <= 0.5
    a2 = a if waxing else 1 - a
    cos_t = math.cos(2 * math.pi * a2)
    rx = abs(cos_t) * r
    sweep = 0 if cos_t > 0 else 1
    path = (f"M0,{-r} A{r},{r} 0 0 1 0,{r} "
            f"A{rx:.3f},{r} 0 0 {sweep} 0,{-r} Z")
    mirror = (not waxing) != (hemisphere == "south")
    flip = " transform='scale(-1,1)'" if mirror else ""
    return (f"<svg class='moon' viewBox='-11 -11 22 22' width='{size_mm}mm' height='{size_mm}mm' "
            f"aria-hidden='true'><circle r='{r}' fill='{dark}'/>"
            f"<path d='{path}' fill='{lit}'{flip}/>"
            f"<circle r='{r}' fill='none' stroke='{rim}' stroke-width='.8'/></svg>")


PHASE_AGE = {"new moon": 0.0, "first quarter": 0.25, "full moon": 0.5, "last quarter": 0.75}
