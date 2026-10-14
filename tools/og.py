"""Renders tools/og.html to assets/og.png at exactly 1200x630.

    python3 -m http.server 8765 --bind 127.0.0.1 &   # from the repo root
    uv run --no-project --with playwright==1.56.0 python tools/og.py
"""

from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
CHROMIUM = (Path.home() / "Library/Caches/ms-playwright/chromium-1194/"
            "chrome-mac/Chromium.app/Contents/MacOS/Chromium")

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=str(CHROMIUM))
    page = browser.new_page(viewport={"width": 1200, "height": 630},
                            color_scheme="dark")
    page.goto("http://127.0.0.1:8765/tools/og.html", wait_until="networkidle")
    page.screenshot(path=str(ROOT / "assets/og.png"))
    browser.close()
print("wrote assets/og.png")
