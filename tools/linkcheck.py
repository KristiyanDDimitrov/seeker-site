"""Checks that every link and asset reference in the site resolves.

    python3 -m http.server 8765 --bind 127.0.0.1 &   # from the repo root
    python3 tools/linkcheck.py

Internal references (href, src, srcset, imagesrcset, content="/...")
are fetched from the local server. External http(s) links are fetched
for real, following redirects, and the final URL is printed (so
releases/latest shows which tag it lands on). mailto: addresses get an
MX lookup of their domain via `dig` at 1.1.1.1 (a local resolver can
hold a stale negative answer). URLs on seekerapp.dev itself
(canonical, og:url, og:image) can only resolve once the user points DNS
at Pages, so they are checked as their local equivalent and listed
separately. Exits non-zero if anything else fails.
"""

import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parents[1]
LOCAL = "http://127.0.0.1:8765"
SITE = "https://seekerapp.dev"
PAGES = {"index.html": "/", "404.html": "/404.html"}
UA = "Mozilla/5.0 (Macintosh; Apple silicon Mac OS X) seeker-site linkcheck"


class Refs(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if not value:
                continue
            if name in ("href", "src"):
                self.refs.append(value)
            elif name in ("srcset", "imagesrcset"):
                self.refs += [part.split()[0] for part in value.split(",")]
            elif name == "content" and value.startswith(("http://", "https://")):
                self.refs.append(value)


def fetch(url: str) -> tuple[int, str]:
    """GET with redirects followed, via curl (it uses the system trust
    store; python.org's Python ships without CA certificates)."""
    out = subprocess.run(
        ["curl", "-sS", "-L", "-o", "/dev/null", "--max-time", "30", "-A", UA,
         "-w", "%{http_code} %{url_effective}", url],
        capture_output=True, text=True,
    ).stdout.split()
    return (int(out[0]), out[1]) if out else (0, url)


def main() -> int:
    failures = 0
    seen: set = set()
    for file_name, served_at in PAGES.items():
        parser = Refs()
        parser.feed((ROOT / file_name).read_text())
        for ref in parser.refs:
            if ref.startswith("#"):
                if (file_name, ref) in seen:
                    continue
                seen.add((file_name, ref))
                ok = f'id="{ref[1:]}"' in (ROOT / file_name).read_text()
                print(f"{'OK  ' if ok else 'FAIL'} {file_name}: {ref} (in-page anchor)")
                failures += not ok
                continue
            if ref.startswith("mailto:"):
                domain = ref.split("@", 1)[1]
                mx = subprocess.run(["dig", "+short", "MX", domain, "@1.1.1.1"],
                                    capture_output=True, text=True).stdout.split()
                ok = bool(mx)
                print(f"{'OK  ' if ok else 'FAIL'} {file_name}: {ref} -> MX {' '.join(mx) or '(none)'}")
                failures += not ok
                continue
            if ref.startswith(SITE):
                if ref in seen:
                    continue
                seen.add(ref)
                url = LOCAL + ref[len(SITE):]
                status, _ = fetch(url)
                print(f"{'PEND' if status == 200 else 'FAIL'} {file_name}: {ref} "
                      f"-> local {url} {status} (live once DNS + Pages are on)")
                failures += status != 200
                continue
            url = ref if ref.startswith(("http://", "https://")) else urljoin(LOCAL + served_at, ref)
            if url in seen:
                continue
            seen.add(url)
            status, final = fetch(url)
            ok = status == 200
            failures += not ok
            hop = f" -> {final}" if final != url else ""
            print(f"{'OK  ' if ok else 'FAIL'} {file_name}: {ref} [{status}]{hop}")
    print("\nOK" if not failures else f"\n{failures} FAILURE(S)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
