"""Page weight: bytes the browser actually fetched for index.html.

    python3 -m http.server 8765 --bind 127.0.0.1 &   # from the repo root
    uv run --no-project --with playwright==1.56.0 python tools/weight.py

Per viewport and colour scheme: the first load and the total after
scrolling to the bottom. The screenshot's pages all load up front (in
the visitor's theme; the other theme's on its first flip), so the two
are the same. Uncompressed sizes; GitHub Pages gzips the HTML/CSS, so
the wire is smaller.
"""

from pathlib import Path

from playwright.sync_api import sync_playwright

CHROMIUM = (Path.home() / "Library/Caches/ms-playwright/chromium-1194/"
            "chrome-mac/Chromium.app/Contents/MacOS/Chromium")
VIEWPORTS = {"1440 desktop (DPR 1)": (1440, 1), "390 phone (DPR 3)": (390, 3)}

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=str(CHROMIUM))
    for (label, (width, dpr)), scheme in [(v, s) for v in VIEWPORTS.items() for s in ("dark", "light")]:
        context = browser.new_context(viewport={"width": width, "height": 900},
                                      device_scale_factor=dpr, color_scheme=scheme)
        page = context.new_page()
        sizes: dict[str, int] = {}
        page.on("requestfinished", lambda r: sizes.__setitem__(
            r.url.removeprefix("http://127.0.0.1:8765"), len(r.response().body())))
        page.goto("http://127.0.0.1:8765/", wait_until="networkidle")
        first = sum(sizes.values())
        first_n = len(sizes)
        page.evaluate("""async () => {
            for (let y = 0; y < document.body.scrollHeight; y += 300) {
                window.scrollTo(0, y); await new Promise(r => setTimeout(r, 50));
            }}""")
        page.wait_for_load_state("networkidle")
        print(f"== {label}, {scheme}")
        for url, size in sorted(sizes.items(), key=lambda kv: -kv[1]):
            print(f"  {size:>8,} B  {url}")
        print(f"  first load: {first_n} requests, {first:,} B ({first/1024:.1f} KiB)")
        print(f"  after full scroll: {len(sizes)} requests, {sum(sizes.values()):,} B "
              f"({sum(sizes.values())/1024:.1f} KiB)")
        context.close()
    browser.close()
