"""Pixel stickers for the Major Arcana that are still waiting for a painted object.

Each is a 16 x 16 bitmap: '#' ink, 'o' accent, '*' gold, 'w' paper, '.' empty. They render as
crisp SVG rects in the style.json colours, so they re-tone with the rest of the card.
"""
from __future__ import annotations

PIXELS = {
    "major-00": (  # The First Day: a sprout in a pot
        "................", ".....##.........", "....#oo#..##....", "....#ooo##oo#...",
        ".....#ooo#oo#...", "......##o#o#....", ".......##.#.....", "........#.......",
        "........#.......", "...##########...", "...#********#...", "....#******#....",
        "....#******#....", ".....#****#.....", ".....######.....", "................"),
    "major-01": (  # The One Woman Show: a stage microphone
        ".....######.....", "....#oooooo#....", "....########....", "....#oooooo#....",
        "....########....", "....#oooooo#....", ".....######.....", "......#**#......",
        "......#**#......", ".......##.......", ".......##.......", ".......##.......",
        ".......##.......", ".....######.....", "....#******#....", "....########...."),
    "major-03": (  # The Guest Check: a check with a jagged tear
        "...##########...", "...#oooooooo#...", "...#wwwwwwww#...", "...#w**w****#...",
        "...#wwwwwwww#...", "...#w###w##w#...", "...#wwwwwwww#...", "...#w####www#...",
        "...#wwwwwwww#...", "...#w##w###w#...", "...#wwwwwwww#...", "...#wwww*ooo#...",
        "...#wwwwwwww#...", "...#w#w#w#w##...", "...##.#.#.#.#...", "................"),
    "major-04": (  # Too Busy: a twin-bell alarm clock
        "..##........##..", ".#**#......#**#.", ".#***######***#.", "..#.#oooooo#.#..",
        "...#oooooooo#...", "..#oooo#ooooo#..", "..#oooo#ooooo#..", "..#oooo#ooooo#..",
        "..#oooo####oo#..", "..#oooooooooo#..", "..#oooooooooo#..", "...#oooooooo#...",
        "....#oooooo#....", ".....######.....", "....#......#....", "...##......##..."),
    "major-06": (  # The Front Page: a folded newspaper
        "................", ".##############.", ".#wwwwwwwwwwww#.", ".#w##########w#.",
        ".#wwwwwwwwwwww#.", ".#w*****w####w#.", ".#w*****wwwwww#.", ".#w*****w####w#.",
        ".#w*****wwwwww#.", ".#wwwwwww####w#.", ".#w####wwwwwww#.", ".#wwwwwww####w#.",
        ".#w####wwwwwww#.", ".#wwwwwwwwwwww#.", ".##############.", "................"),
    "major-07": (  # The Plot Twist: a key
        "................", "................", "..####..........", ".#****#.........",
        "#**##**#........", "#*#..#*########.", "#*#..#*********#", "#**##**###*#*##.",
        ".#****#...#*#*#.", "..####....###.#.", "................", "................",
        "................", "................", "................", "................"),
    "major-08": (  # The Permission Slip: an envelope with a heart seal
        "................", "................", ".##############.", ".##wwwwwwwwww##.",
        ".#w##wwwwww##w#.", ".#www##ww##www#.", ".#wwwww##wwwww#.", ".#wwww#oo#wwww#.",
        ".#wwww#oo#wwww#.", ".#wwwww##wwwww#.", ".#wwwwwwwwwwww#.", ".##############.",
        "................", "................", "................", "................"),
    "major-09": (  # The Quiet Room: an arched door, open a crack
        ".....######.....", "....#oooooo#....", "...#oo####oo#...", "..#oo#wwww#oo#..",
        "..#o#wwwwww#o#..", "..#o#wwwwww#o#..", "..#o#wwwwww#o#..", "..#o#wwww*w#o#..",
        "..#o#wwwwww#o#..", "..#o#wwwwww#o#..", "..#o#wwwwww#o#..", "..#o#wwwwww#o#..",
        ".##############.", ".#************#.", ".##############.", "................"),
    "major-16": (  # The Collapse: a lightning bolt
        ".........#####..", "........#****#..", ".......#****#...", "......#****#....",
        ".....#****#.....", "....#****######.", "...#*********#..", "...######***#...",
        ".......#***#....", "......#***#.....", ".....#**#.......", "....#*#.........",
        "...##...........", "................", "................", "................"),
    "major-20": (  # The Verdict: balance scales
        ".......**.......", ".......**.......", "..************..", "..#....**....#..",
        ".#o#...**...#o#.", "#ooo#..**..#ooo#", "#####..**..#####", ".......**.......",
        ".......**.......", ".......**.......", ".......**.......", ".....******.....",
        "....********....", "................", "................", "................"),
}
COLOURS = {"#": "var(--ink)", "o": "var(--candy)", "*": "var(--gold)", "w": "#FFFBF8"}


def _trim(rows: tuple[str, ...]) -> tuple[str, ...]:
    """Drop empty rows at the bottom so the sticker sits on its base line."""
    rows = list(rows)
    while rows and not rows[-1].strip("."):
        rows.pop()
    return tuple(rows)


def pixel_sticker(card_id: str) -> str:
    rows = _trim(PIXELS[card_id])
    w, h = len(rows[0]), len(rows)
    rects = []
    for y, row in enumerate(rows):
        x = 0
        while x < w:
            ch = row[x]
            if ch == ".":
                x += 1
                continue
            run = x
            while run < w and row[run] == ch:
                run += 1
            rects.append(f"<rect x='{x}' y='{y}' width='{run - x}' height='1' fill='{COLOURS[ch]}'/>")
            x = run
    return (f"<svg class='pix' viewBox='-.5 -.5 {w + 1} {h + 1}' shape-rendering='crispEdges' "
            f"aria-hidden='true'>{''.join(rects)}</svg>")
