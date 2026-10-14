"""Converts Seeker's own screenshots into the page's WebP images.

    # 1. In ../Seeker: real widgets, offscreen, invented demo data, dark
    #    theme, 1280x820 window rendered at 2x:
    QT_SCALE_FACTOR=2 uv run python tools/screenshots.py --theme dark \
        --page dashboard --page review --page downloads
    # 2. Here:
    uv run --no-project --with pillow python tools/screens.py

Qt's offscreen platform draws the menu bar inside the window; on macOS
it lives in the system menu bar, so that strip is cropped off. Nothing
else is touched. Each screen is written at 2560 and 1280 px wide for
`srcset`.
"""

from pathlib import Path

from PIL import Image

SOURCE = Path(__file__).resolve().parents[2] / "Seeker/tools/.screens"
OUT = Path(__file__).resolve().parents[1] / "assets/screens"
SCREENS = ("dashboard", "review", "downloads")
WIDTHS = (2560, 1280)
QUALITY = 82  # untuned: visually checked at 1x and 2x, not measured


def menu_bar_height(image: Image.Image) -> int:
    """The first row, scanning down the window's right edge, whose
    colour differs from row 0's: there the in-window menu bar ends."""
    rgb = image.convert("RGB")
    x = rgb.width - 4
    top = rgb.getpixel((x, 0))
    for y in range(1, rgb.height // 10):
        if rgb.getpixel((x, y)) != top:
            return y
    raise SystemExit("no menu bar edge found; check the source image")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name in SCREENS:
        source = Image.open(SOURCE / f"{name}-dark-1280x820.png")
        cut = menu_bar_height(source)
        cropped = source.crop((0, cut, source.width, source.height))
        for width in WIDTHS:
            height = round(cropped.height * width / cropped.width)
            image = cropped if width == cropped.width else cropped.resize(
                (width, height), Image.Resampling.LANCZOS,
            )
            path = OUT / f"{name}-{width}.webp"
            image.save(path, "WEBP", quality=QUALITY, method=6)
            print(f"{path.name}: {image.width}x{image.height}, "
                  f"{path.stat().st_size} B (menu bar cut: {cut} px)")


if __name__ == "__main__":
    main()
