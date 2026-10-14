"""Screenshots and layout checks against a local copy of the site.

    python3 -m http.server 8765 --bind 127.0.0.1 &   # from the repo root
    uv run --no-project --with playwright==1.56.0 python tools/shoot.py

For each page, width (1440, 390, 360) and colour scheme: a full-page
screenshot into verification/ (360 is checked, not saved), the
document's scrollWidth against the viewport (no horizontal scroll), and
every request the page made, which must all be to the local origin.
Exits non-zero on any overflow or off-origin request.
"""

import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "verification"
BASE = "http://127.0.0.1:8765"
CHROMIUM = (Path.home() / "Library/Caches/ms-playwright/chromium-1194/"
            "chrome-mac/Chromium.app/Contents/MacOS/Chromium")
PAGES = {"index": "/", "404": "/no-such-page"}
WIDTHS = (1440, 390, 360)
SAVED_WIDTHS = (1440, 390)
SCHEMES = ("dark", "light")


def main() -> int:
    OUT.mkdir(exist_ok=True)
    problems: list[str] = []
    report = []
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=str(CHROMIUM))
        for page_name, path in PAGES.items():
            for width in WIDTHS:
                for scheme in SCHEMES:
                    context = browser.new_context(
                        viewport={"width": width, "height": 900},
                        device_scale_factor=2 if width < 800 else 1,
                        color_scheme=scheme,
                    )
                    page = context.new_page()
                    requests: list[str] = []
                    page.on("request", lambda r: requests.append(r.url))
                    # python -m http.server has no 404.html fallback, so
                    # the 404 page is loaded directly to see its layout.
                    url = BASE + ("/404.html" if page_name == "404" else path)
                    page.goto(url, wait_until="networkidle")
                    # Lazy images: scroll through so they load and show.
                    page.evaluate("""async () => {
                        for (let y = 0; y < document.body.scrollHeight; y += 400) {
                            window.scrollTo(0, y); await new Promise(r => setTimeout(r, 40));
                        }
                        window.scrollTo(0, 0);
                    }""")
                    page.wait_for_load_state("networkidle")
                    scroll_w = page.evaluate("document.documentElement.scrollWidth")
                    off_origin = [u for u in requests if not u.startswith(BASE)]
                    entry = {
                        "page": page_name, "width": width, "scheme": scheme,
                        "scrollWidth": scroll_w,
                        "requests": len(requests), "off_origin": off_origin,
                    }
                    report.append(entry)
                    if scroll_w > width:
                        problems.append(f"{page_name} {width} {scheme}: scrollWidth {scroll_w}")
                    if off_origin:
                        problems.append(f"{page_name} {width} {scheme}: off-origin {off_origin}")
                    if width in SAVED_WIDTHS:
                        shot = OUT / f"{page_name}-{width}-{scheme}.png"
                        page.screenshot(path=str(shot), full_page=True)
                    print(json.dumps(entry))
                    context.close()
        browser.close()
    (OUT / "layout-checks.json").write_text(json.dumps(report, indent=2) + "\n")
    print("OK" if not problems else "\n".join(problems))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
