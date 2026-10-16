"""Checks every colour pair the page uses against WCAG, with Seeker's
own contrast logic.

    python3 tools/contrast.py

Reads the tokens from style.css (the dark `:root` block and the
`prefers-color-scheme: light` block), confirms each equals theme.py's
DARK/LIGHT value, then checks every pair below in both schemes. The
palettes repeat for the theme toggle (`:root:has(#theme:checked)`, one
copy per direction); each copy must equal its original. Exits non-zero
on any failure.

`_relative_luminance` and `contrast_ratio` are copied verbatim from
../Seeker/src/seeker/ui/theme.py (importing it would pull in PySide6).
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEME_PY = ROOT.parent / "Seeker/src/seeker/ui/theme.py"


# --- verbatim from theme.py ------------------------------------------------

def _relative_luminance(hex_color: str) -> float:
    """Real WCAG 2.x relative luminance, so contrast is a test, not a
    claim. No third-party dependency; the formula is short enough to own
    directly and verify against known reference values in tests (pure
    black/white)."""
    hex_color = hex_color.lstrip("#")
    r, g, b = (
        int(hex_color[i:i + 2], 16) / 255 for i in (0, 2, 4)
    )

    def channel(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def contrast_ratio(hex_a: str, hex_b: str) -> float:
    """WCAG contrast ratio between two colors, always >= 1.0
    regardless of argument order (lighter over darker)."""
    l_a = _relative_luminance(hex_a)
    l_b = _relative_luminance(hex_b)
    lighter, darker = max(l_a, l_b), min(l_a, l_b)
    return (lighter + 0.05) / (darker + 0.05)

# ---------------------------------------------------------------------------

TEXT_AA = 4.5
NON_TEXT = 3.0

# (foreground, background, floor, where on the page)
PAIRS = [
    ("text", "bg-app", TEXT_AA, "body text, headings"),
    ("text-muted", "bg-app", TEXT_AA, "'Latest' line, captions, notes, lamp legend, cue line, readout status, page row"),
    ("accent", "bg-app", TEXT_AA, "links in sections, readout track number"),
    ("accent-hover", "bg-app", TEXT_AA, "hovered links"),
    ("text", "bg-surface-2", TEXT_AA, "secondary button, hovered; picked page in the page row"),
    ("text", "bg-surface", TEXT_AA, "first-launch note after Download"),
    ("on-accent", "accent", TEXT_AA, "primary button"),
    ("on-accent", "accent-hover", TEXT_AA, "primary button, hovered"),
    ("on-accent", "accent-pressed", TEXT_AA, "primary button, pressed"),
    ("on-accent", "accent", TEXT_AA, "skip link"),
    ("text-muted", "bg-sidebar", TEXT_AA, "footer text"),
    ("accent", "bg-sidebar", TEXT_AA, "footer links"),
    ("accent-hover", "bg-sidebar", TEXT_AA, "footer links, hovered"),
    ("text-muted", "bg-app", NON_TEXT, "secondary button border"),
    ("accent", "bg-app", NON_TEXT, "focus ring"),
    ("success", "bg-app", NON_TEXT, "lamp: in library"),
    ("cue", "bg-app", NON_TEXT, "lamp: downloading / waiting"),
    ("danger", "bg-app", NON_TEXT, "lamp: not found"),
]

# CSS token -> theme.py field
FIELDS = {
    name: name.upper().replace("-", "_")
    for name in (
        "bg-app", "bg-sidebar", "bg-surface", "bg-surface-2", "border",
        "border-strong", "text", "text-muted", "accent", "accent-hover",
        "accent-pressed", "on-accent", "success", "cue", "danger",
    )
}


def tokens(block: str) -> dict[str, str]:
    return {m[1]: m[2].upper() for m in re.finditer(r"--([a-z0-9-]+):\s*(#[0-9A-Fa-f]{6})", block)}


def css_palettes() -> tuple[dict[str, str], dict[str, str]]:
    css = (ROOT / "style.css").read_text()
    dark = re.search(r"^:root \{(.*?)^\}", css, re.S | re.M)
    light = re.search(r"prefers-color-scheme: light\)\s*\{\s*:root \{(.*?)\}", css, re.S)
    assert dark and light, "style.css token blocks not found"
    return tokens(dark[1]), tokens(light[1])


def theme_palette(name: str) -> dict[str, str]:
    source = THEME_PY.read_text()
    block = re.search(rf"^{name} = Palette\((.*?)^\)", source, re.S | re.M)
    assert block, f"{name} not found in theme.py"
    return {m[1]: m[2].upper() for m in re.finditer(r'(\w+)="(#[0-9A-Fa-f]{6})"', block[1])}


def flipped_copies() -> list[tuple[str, dict[str, str], dict[str, str]]]:
    """The toggle's copies: (which, copy, original)."""
    css = (ROOT / "style.css").read_text()
    dark, light = css_palettes()
    to_dark = re.search(r"prefers-color-scheme: light\)\s*\{.*?:root:has\(#theme:checked\) \{(.*?)\}", css, re.S)
    to_light = re.search(r"not all and \(prefers-color-scheme: light\)\s*\{\s*:root:has\(#theme:checked\) \{(.*?)\}", css, re.S)
    assert to_dark and to_light, "style.css toggle blocks not found"
    return [("flipped to dark", tokens(to_dark[1]), dark), ("flipped to light", tokens(to_light[1]), light)]


def main() -> int:
    failures = 0
    for which, copy, original in flipped_copies():
        same = copy == original
        failures += not same
        print(f"{'PASS' if same else 'FAIL'} {which}: {len(copy)} tokens "
              f"{'equal' if same else 'differ from'} the original palette")
    for scheme, css in zip(("dark", "light"), css_palettes()):
        theme = theme_palette(scheme.upper())
        print(f"\n== {scheme} ==")
        for token, field in FIELDS.items():
            if css.get(token) != theme[field]:
                failures += 1
                print(f"  MISMATCH --{token} {css.get(token)} != theme.py {field} {theme[field]}")
        print(f"  {len(FIELDS)} tokens checked against theme.py {scheme.upper()}")
        for fg, bg, floor, where in PAIRS:
            ratio = contrast_ratio(css[fg], css[bg])
            ok = ratio >= floor
            failures += not ok
            print(f"  {'PASS' if ok else 'FAIL'} {ratio:5.2f}:1 (>= {floor}) "
                  f"{fg} {css[fg]} on {bg} {css[bg]}  [{where}]")
    print(f"\n{'OK' if not failures else f'{failures} FAILURE(S)'}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
