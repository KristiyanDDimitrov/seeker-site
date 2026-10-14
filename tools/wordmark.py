"""Outlines the app's wordmark to an SVG: "Seeker" in Barlow Semi
Condensed SemiBold (the face the app's sidebar wordmark uses), with the
icon's two brows over the "ee".

    uv run --with fonttools --with uharfbuzz python tools/wordmark.py

The brow geometry is Seeker's own (src/seeker/ui/wordmark.py and
packaging/icons/seeker_brows.svg), so the page and the app draw the same
mark. The word is outlined, not set in a web font, so the page makes no
font request and the mark looks the same on every system. Barlow is OFL
1.1; outlining glyphs into a logo is permitted use.

Writes assets/wordmark.svg, coloured TEXT/ACCENT for each scheme by
its own embedded style, so it works as a plain <img>.
"""

from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont

SEEKER = Path(__file__).resolve().parents[2] / "Seeker"
FONT = SEEKER / "packaging/fonts/BarlowSemiCondensed-SemiBold.ttf"
OUT = Path(__file__).resolve().parents[1] / "assets/wordmark.svg"

# From src/seeker/ui/wordmark.py, unchanged.
LEFT_BROW = ((0.0, 0.0), (167 / 483, 1.0))
RIGHT_BROW = ((316 / 483, 1.0), (1.0, 0.0))
BROW_ASPECT = 123.4 / 483
SPAN_OF_EE = 0.9
PEN_PER_X_HEIGHT = 0.15
GAP_PER_X_HEIGHT = 0.3

TEXT = "Seeker"


def main() -> None:
    font = TTFont(FONT)
    glyph_set = font.getGlyphSet()
    x_height = font["OS/2"].sxHeight
    cap_height = font["OS/2"].sCapHeight

    blob = hb.Blob.from_file_path(str(FONT))
    hb_font = hb.Font(hb.Face(blob))
    buf = hb.Buffer()
    buf.add_str(TEXT)
    buf.guess_segment_properties()
    hb.shape(hb_font, buf, {"kern": True, "liga": True})

    order = font.getGlyphOrder()
    paths: list[str] = []
    ee_bounds: list[tuple[float, float, float, float]] = []
    ink_left = ink_right = None
    pen_x = 0
    for index, (info, pos) in enumerate(zip(buf.glyph_infos, buf.glyph_positions)):
        name = order[info.codepoint]
        x = pen_x + pos.x_offset
        svg_pen = SVGPathPen(glyph_set)
        glyph_set[name].draw(svg_pen)
        # Font units are y-up; flip into SVG's y-down with the baseline at 0.
        paths.append(f'<path transform="translate({x} 0) scale(1 -1)" d="{svg_pen.getCommands()}"/>')
        bounds_pen = BoundsPen(glyph_set)
        glyph_set[name].draw(bounds_pen)
        if bounds_pen.bounds:
            x0, y0, x1, y1 = bounds_pen.bounds
            ink_left = x + x0 if ink_left is None else min(ink_left, x + x0)
            ink_right = x + x1 if ink_right is None else max(ink_right, x + x1)
            if index in (1, 2):  # the "ee"
                ee_bounds.append((x + x0, y0, x + x1, y1))
        pen_x += pos.x_advance

    ee_left = min(b[0] for b in ee_bounds)
    ee_right = max(b[2] for b in ee_bounds)
    ee_top = max(b[3] for b in ee_bounds)  # ink top, overshoot included
    span = (ee_right - ee_left) * SPAN_OF_EE
    centre = (ee_left + ee_right) / 2
    pen = x_height * PEN_PER_X_HEIGHT
    height = span * BROW_ASPECT + pen
    bottom = -ee_top - x_height * GAP_PER_X_HEIGHT  # y-down
    box_left = centre - (span + pen) / 2
    box_top = bottom - height
    inset = pen / 2
    inner_w = span
    inner_h = height - pen

    def point(p: tuple[float, float]) -> str:
        return f"{box_left + inset + p[0] * inner_w:.1f} {box_top + inset + p[1] * inner_h:.1f}"

    brows = "".join(
        f'<path d="M{point(a)} L{point(b)}"/>' for a, b in (LEFT_BROW, RIGHT_BROW)
    )

    # Tight to the ink: the brows (or the cap height) on top, the
    # baseline below ("Seeker" has no descenders), 10 units of air.
    top = min(box_top, -cap_height) - 10
    left = ink_left - 10
    width = ink_right - ink_left + 20
    view_h = 10 - top
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{left:.0f} {top:.0f} {width:.0f} {view_h:.0f}" '
        f'role="img" aria-label="Seeker">'
        # TEXT and ACCENT from theme.py, dark then light, so the mark
        # follows the scheme even when loaded as an <img>.
        "<style>.w{fill:#E8EAEC}.b{stroke:#9A7DFF}"
        "@media (prefers-color-scheme:light){.w{fill:#15181B}.b{stroke:#6440E6}}</style>"
        f'<g class="w">{"".join(paths)}</g>'
        f'<g class="b" fill="none" stroke-width="{pen:.1f}" stroke-linecap="butt">{brows}</g>'
        f"</svg>\n"
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(svg)
    print(f"wrote {OUT} ({len(svg)} bytes); viewBox {left:.0f} {top:.0f} {width:.0f} {view_h:.0f}")
    print(f"x_height={x_height} pen={pen:.1f} span={span:.1f} ee_top={ee_top}")


if __name__ == "__main__":
    main()
