"""The printable look, read from one shared style.json.

Fallback order (the same in every Rocha Coded tool):
    an explicit --style path -> ./style.json -> ~/.rocha-coded/style.json
    -> the bundled examples/style.rocha-coded.json
Any key the user's file leaves out or leaves blank falls back to the bundled example.
See STYLE.md for the keys.
"""
from __future__ import annotations

import html
import json
import math
import re
from pathlib import Path
from urllib.parse import quote_plus

ROOT = Path(__file__).resolve().parent.parent
BUNDLED = ROOT / "examples" / "style.rocha-coded.json"
HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")
FONT_RE = re.compile(r"^[A-Za-z0-9 ]{1,60}$")

FALLBACK_STACKS = {
    "masthead": "'Didot','Bodoni 72',Georgia,'Times New Roman',serif",
    "label": "'Arial Narrow','Helvetica Neue',Arial,sans-serif",
    "body": "Georgia,'Times New Roman',serif",
    "scrawl": "'Marker Felt','Chalkboard SE','Comic Sans MS',cursive",
    "mono": "'Courier New',monospace",
}
# css variable <- palette key
PALETTE_VARS = {"hot": "hero", "candy": "accent", "paper": "paper_pink", "cream": "paper",
                "ink": "ink", "red": "marker", "plum": "plum", "gold": "gold", "blue": "cool"}

_active: dict | None = None
_source: str = ""


def _read(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Could not read the style file {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"The style file {path} must hold one JSON object.")
    return data


def find_style(explicit: str | None = None) -> Path:
    if explicit:
        p = Path(explicit).expanduser()
        if not p.exists():
            raise SystemExit(f"No style file at {p}")
        return p
    for p in (Path.cwd() / "style.json", Path.home() / ".rocha-coded" / "style.json"):
        if p.exists():
            return p
    return BUNDLED


def _merge(base: dict, user: dict) -> tuple[dict, list[str]]:
    """User values over the bundled example. Blank values fall back. Bad colours and
    font names are dropped with a warning instead of reaching the page."""
    out, warnings = json.loads(json.dumps(base)), []
    for key, val in user.items():
        if key in ("palette", "fonts", "lines") and isinstance(val, dict):
            for k, v in val.items():
                if not isinstance(v, str) or not v.strip():
                    continue
                v = v.strip()
                if key == "palette" and not HEX_RE.match(v):
                    warnings.append(f"palette.{k} '{v}' is not a #RRGGBB colour, using the example's")
                    continue
                if key == "fonts" and not FONT_RE.match(v):
                    warnings.append(f"fonts.{k} '{v}' is not a plain font name, using the example's")
                    continue
                out.setdefault(key, {})[k] = v
        elif isinstance(val, str) and val.strip():
            out[key] = val.strip()
        elif isinstance(val, list):
            out[key] = val
    return out, warnings


def use(explicit: str | None = None) -> dict:
    """Load and activate the style. Prints where it came from and any warnings."""
    global _active, _source
    path = find_style(explicit)
    base = _read(BUNDLED)
    style, warnings = (base, []) if path == BUNDLED else _merge(base, _read(path))
    _active, _source = style, str(path)
    for w in warnings:
        print(f"style: {w}")
    return style


def current() -> dict:
    return _active if _active is not None else use()


def source() -> str:
    current()
    return _source


def color(key: str) -> str:
    return current()["palette"][key]


def line(key: str) -> str:
    return current().get("lines", {}).get(key, "")


def fonts_link(style: dict) -> str:
    links = ['<link rel="preconnect" href="https://fonts.googleapis.com">',
             '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>']
    for role, name in style["fonts"].items():
        fam = quote_plus(name)
        links.append(f'<link href="https://fonts.googleapis.com/css2?family={fam}&display=swap" rel="stylesheet">')
        if role in ("masthead", "body", "label"):  # extra weights; a 400 reply is harmless
            links.append(f'<link href="https://fonts.googleapis.com/css2?family={fam}:ital,wght@0,700;1,400'
                         f'&display=swap" rel="stylesheet">')
        if role == "masthead":
            links.append(f'<link href="https://fonts.googleapis.com/css2?family={fam}:wght@900'
                         f'&display=swap" rel="stylesheet">')
    return "".join(links)


def root_css(style: dict) -> str:
    pal, f = style["palette"], style["fonts"]
    colours = " ".join(f"--{var}:{pal[key]};" for var, key in PALETTE_VARS.items())

    def stack(role: str) -> str:
        return f"'{f[role]}',{FALLBACK_STACKS[role]}"

    return (":root{" + colours + " --white:#FFFFFF;"
            f" --didone:{stack('masthead')}; --tag:{stack('label')}; --body:{stack('body')};"
            f" --marker:{stack('scrawl')}; --mono:{stack('mono')};}}" + BASE_CSS)


BASE_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:var(--cream);color:var(--ink);font-family:var(--body);
  -webkit-print-color-adjust:exact;print-color-adjust:exact}
.tag{font-family:var(--tag);text-transform:uppercase;letter-spacing:.14em;font-weight:700}
.didone{font-family:var(--didone)}
.marker{font-family:var(--marker);color:var(--red)}
.lined{background-color:var(--paper);
  background-image:linear-gradient(90deg,transparent 15mm,color-mix(in srgb,var(--red) 55%,transparent) 15mm,color-mix(in srgb,var(--red) 55%,transparent) 15.4mm,transparent 15.4mm),
  repeating-linear-gradient(180deg,transparent 0,transparent 6.6mm,var(--candy) 6.6mm,var(--candy) 7mm);}
.grain{position:relative}
.grain::after{content:"";position:absolute;inset:0;pointer-events:none;opacity:.22;mix-blend-mode:multiply;
  background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='160' height='160'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 .3  0 0 0 0 .1  0 0 0 0 .2  0 0 0 .35 0'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>");}
.box{width:3.6mm;height:3.6mm;border:.45mm solid var(--ink);border-radius:.6mm;display:inline-block;flex:none}
"""


def esc(text: str) -> str:
    return html.escape(str(text), quote=True)


def page(title: str, css: str, body: str) -> str:
    style = current()
    return (f"<!doctype html><html lang='en'><head><meta charset='utf-8'>"
            f"<meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<title>{esc(title)}</title>{fonts_link(style)}<style>{root_css(style)}{css}</style></head>"
            f"<body>{body}</body></html>")


def moon_svg(age: float, size_mm: float, hemisphere: str = "north",
             lit: str | None = None, dark: str | None = None, rim: str | None = None) -> str:
    """A drawn moon for a lunation age (0 new, .5 full). Northern sky shows the
    waxing light on the right; the southern sky mirrors it."""
    lit = lit or color("gold")
    dark = dark or color("plum")
    rim = rim or lit
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
