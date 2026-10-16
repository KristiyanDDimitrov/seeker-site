"""Renders Seeker's pages for the site's interactive screenshot, and
records where every control is in each.

    uv run --no-project --with pillow python tools/app_screens.py

Runs ../Seeker's own tools/screenshots.py (real widgets, offscreen,
invented demo data; no personal data) with three changes applied to a
temporary copy, never to the Seeker repo:

- the demo playlists and tracks are the site's (Neurofunk and co.);
- the copy writes into a temporary folder;
- after each page renders it records every visible control's rectangle
  (buttons, checkboxes, fields, list items, tabs, the sidebar, the theme
  toggle) and every table row, so the site can make them clickable.

Each change asserts that the text it replaces is still there, so a
change in Seeker's tool stops this script instead of silently skipping.

Writes, for each page and theme, `assets/screens/<page>[-light]-<w>.webp`
at 2560, 1280 and 640 px wide, and `tools/screen-geometry.json` (one
theme's rectangles: the two themes' layouts are checked to be equal).
Qt's offscreen platform draws the menu bar inside the window; on macOS
it lives in the system menu bar, so that strip is cropped off the
images and the geometry is shifted to match.

Then run tools/build_page.py to rebuild the page from them.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SEEKER = ROOT.parent / "Seeker"
OUT = ROOT / "assets/screens"
GEOMETRY = ROOT / "tools/screen-geometry.json"
PAGES = (
    "dashboard", "library", "search", "downloads", "review", "duplicates",
    "sharing", "history", "help", "support", "settings-general",
    "settings-library", "settings-connections", "settings-matching",
)
THEMES = {"dark": "", "light": "-light"}
WIDTHS = (2560, 1280, 640)
QUALITY = 82  # untuned: visually checked at 1x and 2x, not measured
MENU_BAR = 20  # logical px; 40 px in the 2x images

# The site's demo data. Dashboard rows, in display order, are TRACKS[0],
# [6], [1], [7], [8], [2], [4], [3]; each keeps its row's status.
DEMO = [
    ('_track(1, "Nova Reyes", "Voltage Drop", "Night Shift")', '_track(1, "Zigi SC", "Berserk", "Berserk")'),
    ('_track(7, "Tomas Wren", "Signal Path", "Relay")', '_track(7, "Overtune", "Bass Vibration", "Bass Vibration")'),
    ('_track(2, "Kessler & Vane", "Concrete Bloom", "Concrete Bloom EP")', '_track(2, "HighThere", "Falling For You", "Falling For You")'),
    ('_track(8, "Ana Lindqvist", "Paper Moons (Extended)", "Paper Moons")', '_track(8, "Qo, The Clamps", "Krieg", "Krieg")'),
    ('_track(9, "Juno Halvorsen", "Lowercase", "Lowercase")', '_track(9, "Notequal", "Noises", "Noises")'),
    ('_track(3, "Ilse Marchetti", "Afterimage", "Low Light")', '_track(3, "Pandaemonium (CZ)", "Dust", "Dust")'),
    ('_track(5, "Odile Kessler", "Undertow (Club Mix)", "Undertow")', '_track(5, "Audio, REEBZ", "Tractor Beam", "Tractor Beam")'),
    ('_track(4, "Rutger Solheim", "Static Bloom (Original Mix)", "Static")', '_track(4, "Mob Tactics", "Chugger", "Chugger")'),
    # Names written out in full elsewhere in the dataset.
    ('local_file_path="House/Ilse Marchetti - Afterimage (Edit).mp3"', 'local_file_path="Neurofunk/Pandaemonium (CZ) - Dust (Edit).mp3"'),
    ('tag_artist="Ilse Marchetti", tag_title="Afterimage (Edit)"', 'tag_artist="Pandaemonium (CZ)", tag_title="Dust (Edit)"'),
    ('old_file_path="/Users/demo/Music/Ana Lindqvist - Paper Moons.mp3"', 'old_file_path="/Users/demo/Music/Qo, The Clamps - Krieg.mp3"'),
    ('"Nova Reyes - Voltage Drop.flac"', '"Zigi SC - Berserk.flac"'),
    ('"Nova Reyes - Voltage Drop (1).mp3"', '"Zigi SC - Berserk (1).mp3"'),
    ('"Juno Halvorsen - Lowercase.aiff", 52.4, "House"', '"Notequal - Noises.aiff", 52.4, "Jungle"'),
    ('"Juno Halvorsen - Lowercase.mp3"', '"Notequal - Noises.mp3"'),
    ('"Juno Halvorsen - Lowercase (Radio Edit).mp3"', '"Notequal - Noises (Radio Edit).mp3"'),
    ('"Tomas Wren - Signal Path.flac"', '"Overtune - Bass Vibration.flac"', 2),
    ('"Music\\\\Tomas Wren - Signal Path.flac"', '"Music\\\\Overtune - Bass Vibration.flac"'),
    ('"Rutger Solheim - Static Bloom: no local file"', '"Mob Tactics - Chugger: no local file"'),
    ('"Juno Halvorsen - Lowercase: disk read error"', '"Notequal - Noises: disk read error"'),
    ('folder: str = "Techno"', 'folder: str = "Neurofunk"'),
    # Playlists, renamed in place. Order matters: "Peak Time Techno"
    # becomes Neurofunk before "Warehouse Anthems" takes its name.
    ('"Peak Time Techno"', '"Neurofunk"', 9),
    ('"Deep House Essentials"', '"Jungle"', 4),
    ('"Warehouse Anthems"', '"Peak Time Techno"', 4),
    ('"Sunrise Set"', '"Progressive House"', 2),
    # Downloads and history from other playlists: Jungle, so drum and bass
    # tracks don't sit in techno and house playlists.
    ('track=TRACKS[3], playlist_name="Peak Time Techno"', 'track=TRACKS[3], playlist_name="Jungle"', 2),
    ('track=TRACKS[0], playlist_name="Progressive House"', 'track=TRACKS[0], playlist_name="Jungle"'),
    ('playlist_name="Peak Time Techno", detail="Tags; BPM 124, 8A"', 'playlist_name="Jungle", detail="Tags; BPM 174, 4A"'),
]

RECORDER = '''
def control_geometry(window):
    """Every visible control's rectangle, and every table row's, in the
    window's logical coordinates."""
    from PySide6.QtCore import QRect
    from PySide6.QtWidgets import (
        QAbstractButton, QAbstractSpinBox, QComboBox, QLineEdit, QListView,
        QSlider, QTabBar, QTableView,
    )
    found = []

    def add(kind, label, rect):
        if rect.width() >= 4 and rect.height() >= 4:
            found.append({"kind": kind, "label": label, "x": rect.x(),
                          "y": rect.y(), "w": rect.width(), "h": rect.height()})

    def visible_rect(widget, local=None):
        local = local if local is not None else widget.rect()
        clip = widget.visibleRegion().boundingRect().intersected(local)
        if clip.isEmpty():
            return QRect()
        return QRect(widget.mapTo(window, clip.topLeft()), clip.size())

    for widget in window.findChildren(QWidget):
        if not widget.isVisible() or widget.window() is not window:
            continue
        if isinstance(widget, QTabBar):
            for i in range(widget.count()):
                add("tab", widget.tabText(i), visible_rect(widget, widget.tabRect(i)))
        elif isinstance(widget, QAbstractButton):
            rect = visible_rect(widget)
            if type(widget).__name__ == "ThemeToggleButton":
                add("theme", "", rect)
            elif rect.x() + rect.width() <= 200 and widget.isCheckable():
                add("nav", widget.text().split("  (")[0], rect)
            else:
                add("control", widget.text() or type(widget).__name__, rect)
        elif isinstance(widget, (QComboBox, QLineEdit, QAbstractSpinBox, QSlider)):
            add("control", type(widget).__name__, visible_rect(widget))
        elif isinstance(widget, QListView) and widget.model() is not None:
            for row in range(widget.model().rowCount()):
                r = widget.visualRect(widget.model().index(row, 0))
                add("control", "list item", visible_rect(widget.viewport(), r))
        elif isinstance(widget, QTableView) and widget.model() is not None:
            viewport = widget.viewport()
            for row in range(widget.model().rowCount()):
                r = widget.visualRect(widget.model().index(row, 0))
                add("row", "table row", visible_rect(
                    viewport, QRect(0, r.y(), viewport.width(), r.height())))
    return found


GEOMETRY = {}


def capture_window('''


def patched_tool(out_dir: Path) -> str:
    source = (SEEKER / "tools/screenshots.py").read_text()

    def sub(old: str, new: str, count: int = 1) -> None:
        nonlocal source
        found = source.count(old)
        if found != count:
            sys.exit(f"tools/screenshots.py changed: expected {count} of {old!r}, found {found}")
        source = source.replace(old, new)

    sub("REPO_ROOT = Path(__file__).resolve().parent.parent", f"REPO_ROOT = Path({str(SEEKER)!r})")
    sub('SCREENS_DIR = REPO_ROOT / "tools" / ".screens"', f"SCREENS_DIR = Path({str(out_dir)!r})")
    for old, new, *count in DEMO:
        sub(old, new, *count)
    sub("\ndef capture_window(", RECORDER)
    sub("""                window.grab().save(str(path))
                written.append(path)""", """                window.grab().save(str(path))
                written.append(path)
                if size == (1280, 820):
                    GEOMETRY.setdefault(theme_name, {})[screen.name] = control_geometry(window)""")
    sub("""    finally:
        close(app, window)
    return written


def capture_wizard(""", """    finally:
        close(app, window)
    import json
    (SCREENS_DIR / f"geometry-{theme_name}.json").write_text(
        json.dumps(GEOMETRY.get(theme_name, {})))
    return written


def capture_wizard(""")
    return source


def menu_bar_height(image: Image.Image) -> int:
    """The first row, scanning down the window's right edge, whose
    colour differs from row 0's: there the in-window menu bar ends."""
    rgb = image.convert("RGB")
    x = rgb.width - 4
    top = rgb.getpixel((x, 0))
    for y in range(1, rgb.height // 10):
        if rgb.getpixel((x, y)) != top:
            return y
    sys.exit("no menu bar edge found; check the source image")


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        raw = Path(tmp)
        tool = raw / "screenshots_site.py"
        tool.write_text(patched_tool(raw))
        env = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}
        env["QT_SCALE_FACTOR"] = "2"
        pages = [arg for page in PAGES for arg in ("--page", page)]
        for theme in THEMES:
            subprocess.run(["uv", "run", "python", str(tool), "--theme", theme, *pages],
                           cwd=SEEKER, env=env, check=True)

        geometry = {}
        for theme in THEMES:
            found = json.loads((raw / f"geometry-{theme}.json").read_text())
            for rects in found.values():
                for rect in rects:
                    rect["y"] -= MENU_BAR
            geometry[theme] = {page: found[page] for page in PAGES}
        if geometry["dark"] != geometry["light"]:
            sys.exit("the dark and light layouts differ; one geometry can't serve both")
        GEOMETRY.write_text(json.dumps(geometry["dark"], indent=1) + "\n")
        print(f"{GEOMETRY.relative_to(ROOT)}: {sum(map(len, geometry['dark'].values()))} rectangles")

        OUT.mkdir(parents=True, exist_ok=True)
        for theme, suffix in THEMES.items():
            for page in PAGES:
                source = Image.open(raw / f"{page}-{theme}-1280x820.png")
                cut = menu_bar_height(source)
                if cut != 2 * MENU_BAR:
                    sys.exit(f"{page} {theme}: menu bar is {cut} px, expected {2 * MENU_BAR}")
                cropped = source.crop((0, cut, source.width, source.height))
                for width in WIDTHS:
                    height = round(cropped.height * width / cropped.width)
                    image = cropped if width == cropped.width else cropped.resize(
                        (width, height), Image.Resampling.LANCZOS)
                    path = OUT / f"{page}{suffix}-{width}.webp"
                    image.save(path, "WEBP", quality=QUALITY, method=6)
                print(f"{page}{suffix}: {cropped.width}x{cropped.height} at {WIDTHS}")


if __name__ == "__main__":
    main()
