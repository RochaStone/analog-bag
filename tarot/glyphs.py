"""Gold line-art emblems for the Hook Tarot. Each is SVG drawn in a 100 x 100 box."""
from __future__ import annotations

import math


def _star(cx: float, cy: float, points: int, outer: float, inner: float) -> str:
    pts = []
    for i in range(points * 2):
        r = outer if i % 2 == 0 else inner
        a = math.pi * i / points - math.pi / 2
        pts.append(f"{cx + r * math.cos(a):.1f},{cy + r * math.sin(a):.1f}")
    return f"<polygon points='{' '.join(pts)}'/>"


def _rays(cx: float, cy: float, n: int, r1: float, r2: float) -> str:
    d = ""
    for i in range(n):
        a = 2 * math.pi * i / n
        d += (f"M{cx + r1 * math.cos(a):.1f} {cy + r1 * math.sin(a):.1f} "
              f"L{cx + r2 * math.cos(a):.1f} {cy + r2 * math.sin(a):.1f} ")
    return f"<path d='{d}'/>"


def _spiral() -> str:
    pts = []
    for i in range(0, 420):
        t = i / 40
        r = 2 + 3.2 * t
        pts.append(f"{50 + r * math.cos(t):.1f},{50 + r * math.sin(t):.1f}")
    return f"<polyline points='{' '.join(pts)}'/>"


GLYPHS = {
    "seedling": "<path d='M50 86 V44 M50 58 Q30 56 27 36 Q47 36 50 56 M50 50 Q70 46 74 26 Q53 27 50 48'/>"
                "<path d='M30 86 H70'/>",
    "spotlight": "<path d='M42 14 H58 L80 78 H20 Z' opacity='.55'/><circle cx='50' cy='12' r='5'/>"
                 "<path d='M14 86 H86'/>" + _star(50, 62, 4, 8, 2.5),
    "receipt": "<path d='M30 14 H70 V80 L65 86 L60 80 L55 86 L50 80 L45 86 L40 80 L35 86 L30 80 Z'/>"
               "<path d='M37 28 H63 M37 38 H57 M37 48 H63 M37 58 H52 M45 70 H63'/>",
    "plate": "<circle cx='50' cy='52' r='24'/><circle cx='50' cy='52' r='16'/>"
             "<path d='M17 30 V74 M13 30 V42 Q17 47 21 42 V30 M83 30 Q76 46 83 54 V74'/>",
    "clock": "<circle cx='50' cy='52' r='30'/><path d='M50 52 V32 M50 52 L64 60'/>"
             + _rays(50, 52, 12, 25, 28) + "<path d='M38 18 L32 12 M62 18 L68 12'/>",
    "phone": "<path d='M24 78 L31 52 H69 L76 78 Z'/><circle cx='50' cy='65' r='9'/><circle cx='50' cy='65' r='3'/>"
             "<path d='M20 44 Q50 22 80 44 L73 50 Q50 34 27 50 Z'/>",
    "newspaper": "<rect x='18' y='20' width='64' height='62'/><path d='M24 30 H76' stroke-width='4'/>"
                 "<path d='M24 40 H48 M24 47 H48 M24 54 H48 M24 61 H48 M24 68 H48 M54 40 H76 M54 47 H76 "
                 "M54 54 H76 M54 61 H76 M54 68 H70'/>",
    "key": "<circle cx='32' cy='50' r='13'/><circle cx='32' cy='50' r='5'/>"
           "<path d='M45 50 H84 M74 50 V61 M82 50 V58'/>",
    "envelope": "<rect x='16' y='28' width='68' height='46'/><path d='M16 28 L50 56 L84 28'/>"
                "<path d='M50 48 C44 40 36 46 50 56 C64 46 56 40 50 48 Z'/>",
    "door": "<path d='M30 86 V28 Q50 8 70 28 V86 Z'/><path d='M36 86 V32 Q50 16 64 32 V86'/>"
            "<circle cx='59' cy='60' r='2'/><path d='M22 86 H78'/>",
    "spiral": _spiral(),
    "eye": "<path d='M12 50 Q50 18 88 50 Q50 82 12 50 Z'/><circle cx='50' cy='50' r='14'/>"
           "<circle cx='50' cy='50' r='6'/>" + _rays(50, 50, 16, 42, 46),
    "hourglass": "<path d='M30 14 H70 M30 86 H70 M35 14 Q35 40 50 50 Q65 40 65 14 "
                 "M35 86 Q35 60 50 50 Q65 60 65 86 M42 80 Q50 70 58 80'/>",
    "candle": "<rect x='40' y='42' width='20' height='40'/><path d='M50 42 V34'/>"
              "<path d='M50 32 C44 24 48 16 50 10 C52 16 56 24 50 32 Z'/><path d='M30 86 H70'/>",
    "bowl": "<path d='M20 48 H80 Q78 78 50 80 Q22 78 20 48 Z'/><path d='M56 44 L78 16'/>"
            "<path d='M36 86 H64 M42 80 V86 M58 80 V86'/>",
    "lips": "<path d='M14 50 Q32 30 50 41 Q68 30 86 50 Q68 74 50 72 Q32 74 14 50 Z'/>"
            "<path d='M14 50 Q50 58 86 50'/>",
    "lightning": "<path d='M57 10 L30 54 H49 L40 90 L72 40 H52 Z'/>",
    "star": _star(50, 50, 8, 36, 12) + _star(50, 50, 4, 14, 4),
    "moon": "<path d='M60 16 A34 34 0 1 0 60 84 A27 27 0 1 1 60 16 Z'/>" + _star(70, 34, 4, 7, 2),
    "sun": "<circle cx='50' cy='50' r='17'/>" + _rays(50, 50, 16, 23, 36),
    "scales": "<path d='M50 14 V84 M36 84 H64 M20 28 H80 M20 28 L10 54 H30 Z M80 28 L70 54 H90 Z'/>"
              "<circle cx='50' cy='14' r='3'/>",
    "globe": "<circle cx='50' cy='50' r='32'/><ellipse cx='50' cy='50' rx='13' ry='32'/>"
             "<path d='M18 50 H82 M22 34 H78 M22 66 H78'/>",
    "cups": "<path d='M28 18 H72 Q72 54 50 60 Q28 54 28 18 Z'/><path d='M50 60 V78 M34 82 H66'/>"
            "<path d='M34 26 Q50 32 66 26'/>",
    "wands": "<path d='M34 88 L66 12'/><path d='M60 26 Q70 22 72 12 M54 40 Q44 40 40 32 M48 54 Q58 56 64 50'/>"
             + _star(66, 12, 4, 6, 2),
    "swords": "<path d='M50 8 L56 20 V64 H44 V20 Z'/><path d='M32 64 H68 M50 64 V84'/><circle cx='50' cy='88' r='4'/>",
    "pentacles": "<circle cx='50' cy='50' r='34'/>" + _star(50, 50, 5, 30, 12),
}


def glyph_svg(name: str, size_mm: float, color: str = "#E9B949", width: float = 2.2) -> str:
    inner = GLYPHS.get(name, GLYPHS["star"])
    return (f"<svg viewBox='0 0 100 100' width='{size_mm}mm' height='{size_mm}mm' aria-hidden='true'>"
            f"<g fill='none' stroke='{color}' stroke-width='{width}' stroke-linejoin='round' "
            f"stroke-linecap='round'>{inner}</g></svg>")
