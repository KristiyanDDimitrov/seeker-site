"""Builds the generated parts of index.html, 404.html and style.css.

    python3 tools/build_page.py

Run it after tools/app_screens.py (new screenshots or geometry), after
tools/wordmark.py, or after editing the data below. Each generated part
sits between a pair of markers, `<!-- build_page.py: NAME -->` and
`<!-- /build_page.py: NAME -->` (`/* ... */` in the CSS); everything
outside them is edited by hand. The parts:

- wordmark (index.html, 404.html): assets/wordmark.svg inlined, so it
  takes the page's colours (an <img> picks its own scheme, which can
  disagree with the page's), with a second, blurred copy of the brows
  for their glow.
- preload (index.html): the system theme's dashboard image.
- figure (index.html): the deck (the playlist's waveform strip) and the
  explorable screenshot: every page in both themes, stacked, and the
  click targets over them, from tools/screen-geometry.json.
- generated (style.css): the per-track and per-page rules, and attract
  mode (the strip stepping through the set until a track is picked).

All of it is radio buttons, a checkbox and :has(); the page's small
script only adds the scroll-and-pop and the jump back to the Dashboard.
"""

import json
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GEOMETRY = json.loads((ROOT / "tools/screen-geometry.json").read_text())
IMAGE_W, IMAGE_H = 1280, 800  # the screenshots' 1x size, after the crop

# The Dashboard's selected playlist, Neurofunk, in its rows' order, as in
# tools/app_screens.py's demo data: (artist, title, status, lamp, length
# in minutes, downloaded fraction or None). Lengths only set the strip's
# proportions.
TRACKS = [
    ("Zigi SC", "Berserk", "In library", "play", 5.2, None),
    ("Overtune", "Bass Vibration", "In library", "play", 4.8, None),
    ("HighThere", "Falling For You", "Downloading 66%", "cue", 5.6, 0.66),
    ("Qo, The Clamps", "Krieg", "Awaiting review", "wait", 5.0, None),
    ("Notequal", "Noises", "Retrying", "cue", 4.6, 0.0),
    ("Pandaemonium (CZ)", "Dust", "Needs review", "wait", 5.4, None),
    ("Audio, REEBZ", "Tractor Beam", "Candidate to review", "wait", 5.9, None),
    ("Mob Tactics", "Chugger", "Not found", "off", 4.9, None),
]
RESTING_TRACK = 3  # shown still, with reduced motion, until one is picked

# (page, its name in the phone's page row, alt text, caption). The first
# eleven are the sidebar's; Settings' other tabs follow.
PAGES = [
    ("dashboard", "Dashboard",
     "Seeker's dashboard. The playlist Neurofunk is selected, with 2 of its 8 tracks missing. Each track has a status: in library, downloading at 66 percent, awaiting review, retrying, needs review, candidate to review, or not found. A banner offers to download the 2 missing tracks.",
     "Pick a playlist and every track shows where it stands."),
    ("library", "Library",
     "The Library page acting on the playlist Neurofunk. Zigi SC - Berserk is tagged with its cover art embedded; Overtune - Bass Vibration is not tagged yet and has no cover art. A banner reports 6 tracks tagged, 1 without cover art and 1 failed. Panels on the right tag the playlist, repair cover art and rename files.",
     "Library: tag a playlist's tracks with Spotify's details and cover art, and rename the files to match."),
    ("search", "Search",
     "The Search page. A search for Glasshouse by Mara Okafor found 4 files on SoulSeek, each listed with its peer, quality, size and score, and a Download button. One file is locked.",
     "Search: find a track that isn't in any of your playlists and download it from SoulSeek."),
    ("downloads", "Downloads",
     "The Downloads page listing nine SoulSeek transfers across playlists: two downloading with progress meters, two queued, one retrying because the file is locked by the peer, one upgrade ready for review, one completed, and two failed with their reasons and a Retry button.",
     "Downloads: every transfer, with backups queued in case a peer drops out."),
    ("review", "Review",
     "The Review page in three sections: SoulSeek candidates to confirm, with match scores of 72.6 and 58.9; a downloaded upgrade from MP3 192 kbps to FLAC; and a local file match to confirm. Each row has buttons to accept or turn it down.",
     "Review: confirm the matches Seeker wasn't sure enough to accept alone."),
    ("duplicates", "Duplicates",
     "The Duplicates page found 3 groups of duplicate files, such as a FLAC and an MP3 of Zigi SC - Berserk at 97 percent similarity. The best copy in each group is picked to keep, and nothing is deleted until you confirm.",
     "Duplicates: find copies of the same track by how they sound, not by file name, and keep the best one."),
    ("sharing", "Sharing",
     "The Sharing page. The Music location is shared on SoulSeek with 3,180 files and the Archive location is not; one peer is downloading Overtune - Bass Vibration from you.",
     "Sharing: what you share back to SoulSeek, and who is downloading from you."),
    ("history", "History",
     "The History page listing four recent events, downloads and tag runs, each with its time, track, playlist and detail.",
     "History: what was downloaded and tagged recently."),
    ("help", "Help",
     "The Help page: how Seeker works in five steps, from syncing playlists to reviewing and tagging, then troubleshooting tips and where Seeker keeps its data.",
     "Help: how Seeker works, and what to check when something doesn't."),
    ("support", "Support",
     "The Support page: ways to support the artists whose music you play, optional donations, and how to report a bug.",
     "Support: Seeker is free; this page is about backing the artists you play."),
    ("settings-general", "Settings",
     "Settings, on the General tab: appearance, starting at login, a daily search for missing tracks, notifications and update checks.",
     "Settings: appearance, startup, a daily search for missing tracks, notifications and updates."),
    ("settings-library", "Library",
     "Settings, on the Library tab: three library locations, one available and two on an unplugged drive, with a warning that one folder sits inside another; where downloads go by default; and a destination per playlist.",
     "Settings: the folders Seeker scans, and where each playlist's downloads go."),
    ("settings-connections", "Connections",
     "Settings, on the Connections tab: the Spotify Client ID, the SoulSeek login slskd uses, and starting slskd in Docker with a folder to share.",
     "Settings: your Spotify app and your SoulSeek login."),
    ("settings-matching", "Matching",
     "Settings, on the Matching tab: the auto-match threshold, 90, and the needs-review threshold, 70.",
     "Settings: how closely a file must match a track to be accepted, or sent to Review."),
]
NAV_PAGE = {"Settings": "settings-general"}  # else the sidebar label, lowercased
TAB_PAGE = {"General": "settings-general", "Library": "settings-library",
            "Connections": "settings-connections", "Matching": "settings-matching"}
THEMES = {"dark": "", "light": "-light"}
SIZES = "(min-width: 1264px) 1200px, calc(100vw - 32px)"

# The strip: a 1200x64 waveform, one bar per 4 units, 10 between tracks.
STRIP_W, STRIP_H, GAP, BAR = 1200, 64, 10, 4
# Attract mode: seconds per track, and when it starts (after the brows
# power on and the strip draws in).
SLOT, START = 2.2, 1.9


def box(rect: dict) -> str:
    return (f"left:{rect['x'] / IMAGE_W * 100:.3f}%;top:{rect['y'] / IMAGE_H * 100:.3f}%;"
            f"width:{rect['w'] / IMAGE_W * 100:.3f}%;height:{rect['h'] / IMAGE_H * 100:.3f}%")


def of_kind(page: str, kind: str) -> list[dict]:
    return [rect for rect in GEOMETRY[page] if rect["kind"] == kind]


def wordmark(label: str) -> str:
    svg = (ROOT / "assets/wordmark.svg").read_text()
    view = re.search(r'viewBox="([^"]+)"', svg)[1]
    glyphs = re.search(r'<g class="w">(.*?)</g>', svg, re.S)[1]
    brows = re.search(r'<g class="b"[^>]*>(.*?)</g>', svg, re.S)[1]
    return (f'<svg class="wordmark" viewBox="{view}" role="img" aria-label="{label}">'
            '<defs><filter id="lit" x="-60%" y="-120%" width="220%" height="340%">'
            '<feGaussianBlur stdDeviation="34"/></filter></defs>'
            f'<g class="wordmark-type">{glyphs}</g>'
            f'<g class="brows brows-glow" filter="url(#lit)">{brows}</g>'
            f'<g class="brows">{brows}</g></svg>')


def srcset(page: str, suffix: str) -> str:
    return ", ".join(f"assets/screens/{page}{suffix}-{w}.webp {w}w" for w in (640, 1280, 2560))


def preload() -> str:
    links = []
    for theme, media in (("dark", "not all and (prefers-color-scheme: light)"),
                         ("light", "(prefers-color-scheme: light)")):
        suffix = THEMES[theme]
        links.append(
            f'<link rel="preload" media="{media}" as="image" type="image/webp" fetchpriority="high"\n'
            f'        href="assets/screens/dashboard{suffix}-1280.webp"\n'
            f'        imagesrcset="{srcset("dashboard", suffix)}"\n'
            f'        imagesizes="{SIZES}">')
    return "\n  ".join(links)


def strip() -> tuple[str, list[float]]:
    """The waveform overview and the tracks' left edges, in % of it.

    A club track's shape: intro, build, a breakdown at 55-65%, the drop,
    outro. Tracks you have are drawn; one downloading is drawn as far as
    it got; ones waiting on you are dimmed; the rest are flat."""
    random.seed(7)
    total = sum(t[4] for t in TRACKS)
    usable = STRIP_W - GAP * (len(TRACKS) - 1)
    x, lefts, groups = 0.0, [], []
    for i, (_, _, _, lamp, minutes, done) in enumerate(TRACKS, 1):
        width = usable * minutes / total
        lefts.append(x / STRIP_W * 100)
        paths = {"have": [], "dim": [], "flat": []}
        bars = int(width // BAR)
        for b in range(bars):
            t = b / bars
            env = min(1, t / 0.12) * min(1, (1 - t) / 0.1)
            env *= 0.95 if t < 0.5 else (0.35 if t < 0.6 else 1.0)
            a = env * (0.55 + 0.45 * random.random())
            bx = x + b * BAR + 1
            h = max(2, a * (STRIP_H - 4))
            bar = f"M{bx:.1f} {STRIP_H / 2 - h / 2:.1f}h2v{h:.1f}h-2z"
            flat = f"M{bx:.1f} {STRIP_H / 2 - 1}h2v2h-2z"
            if lamp == "play" or (done is not None and t < done):
                paths["have"].append(bar)
            elif lamp == "off" or done is not None:
                paths["flat"].append(flat)
            else:
                paths["dim"].append(bar)
        groups.append(f'<g class="w{i}">' + "".join(
            f'<path class="wave-{kind}" d="{"".join(d)}"/>' for kind, d in paths.items() if d) + "</g>")
        x += width + GAP
    svg = (f'<svg class="strip-wave" viewBox="0 0 {STRIP_W} {STRIP_H}" preserveAspectRatio="none" '
           f'aria-hidden="true">{"".join(groups)}</svg>')
    return svg, lefts


def figure() -> str:
    wave, lefts = strip()
    widths = [b - a for a, b in zip(lefts, lefts[1:] + [100 + GAP / STRIP_W * 100])]
    n = len(TRACKS)
    readouts, tracks = [], []
    for i, (artist, title, status, lamp, _, _) in enumerate(TRACKS, 1):
        name = f"{artist} - {title}"
        readouts.append(
            f'<p class="ro ro-{i}"><span class="ro-n">{i:02d}<span>/{n:02d}</span></span>'
            f'<span class="ro-t">{name}</span><span class="ro-s lamp-{lamp}">{status}</span></p>')
        width = widths[i - 1] - GAP / STRIP_W * 100
        tracks.append(
            f'<input class="sr" type="radio" name="track" id="t{i}">'
            f'<label class="seg lamp-{lamp}" for="t{i}" style="left:{lefts[i - 1]:.2f}%;width:{width:.2f}%">'
            f'<span class="sr">{name}: {status.lower()}</span></label>')

    radios, tabs, descs, layers, caps, dzs = [], [], [], {t: [] for t in THEMES}, [], []
    for page, tab, alt, caption in PAGES:
        first = page == "dashboard"
        sub_tab = page.startswith("settings-") and page != "settings-general"
        # Each radio carries its own name: its labels are the picture's
        # sidebar (hidden on phones), the phone's page row (hidden from
        # screen readers, which have the radios) and Settings' tabs.
        name = f"Settings: {tab}" if sub_tab else tab
        radios.append(f'<input class="sr" type="radio" name="page" id="pg-{page}" aria-label="{name}"{" checked" if first else ""}>')
        tabs.append(f'<label class="tab tab-{page}{" tab-sub" if sub_tab else ""}" for="pg-{page}">{tab}</label>')
        descs.append(f'<p class="sr desc desc-{page}">{alt}</p>')
        caps.append(f'<span class="cap cap-{page}">{caption}</span>')
        for theme, suffix in THEMES.items():
            # The dashboards load at once; the rest lazily, which for the
            # layer on show is at once too, and for the other layer is on
            # the first flip of the theme.
            load = 'fetchpriority="high"' if first else 'loading="lazy" fetchpriority="low"'
            layers[theme].append(
                f'<img class="scr scr-{page}" srcset="{srcset(page, suffix)}" sizes="{SIZES}" '
                f'src="assets/screens/{page}{suffix}-1280.webp" width="{IMAGE_W}" height="{IMAGE_H}" {load} alt="">')
        dzs.append(f'<div class="dzs dzs-{page}">' + "".join(
            f'<a class="dz" href="#download" tabindex="-1" style="{box(r)}"></a>'
            for r in of_kind(page, "control")) + "</div>")
    # The dashboard last, so a page still loading shows it underneath.
    for theme in layers:
        layers[theme] = layers[theme][1:] + layers[theme][:1]

    spots = []
    for r in of_kind("dashboard", "nav"):
        page = NAV_PAGE.get(r["label"], r["label"].lower())
        spots.append(f'<label class="hs hs-{page}" for="pg-{page}" style="{box(r)}"><span class="sr">{r["label"]}</span></label>')
    for r in of_kind("dashboard", "theme"):
        spots.append(f'<label class="hs hs-theme" for="theme" style="{box(r)}"><span class="sr">Switch between dark and light</span></label>')
    for r in of_kind("settings-general", "tab"):
        page = TAB_PAGE[r["label"]]
        spots.append(f'<label class="hs hs-tab hs-{page}" for="pg-{page}" style="{box(r)}"><span class="sr">Settings: {r["label"]}</span></label>')

    rows = of_kind("dashboard", "row")
    assert len(rows) == n, f"expected {n} dashboard rows, found {len(rows)}"
    table = {"x": rows[0]["x"], "w": rows[0]["w"]}
    across = f"left:{table['x'] / IMAGE_W * 100:.3f}%;width:{table['w'] / IMAGE_W * 100:.3f}%"
    rowspots = "".join(
        f'<label class="rs" for="t{i}" style="top:{r["y"] / IMAGE_H * 100:.3f}%;height:{r["h"] / IMAGE_H * 100:.3f}%"></label>'
        for i, r in enumerate(rows, 1))

    return f'''<figure class="shot shot-hero">
        <div class="deck">
          <p class="cue-line" aria-hidden="true"><span class="when-attract"><span class="cue-dot"></span><span class="moving">Seeker is stepping through the playlist. Pick a track, here or in the app's list, to stop on it.</span><span class="still">Pick a track, here or in the app's list, to find it in both.</span></span><span class="when-picked"><span class="cue-dot"></span><span class="wide">Now click the sidebar in the picture to look around the app, and the <span class="to-light">moon to switch to light.</span><span class="to-dark">sun to switch to dark.</span></span><span class="narrow">Now pick a page below to look around the app.</span></span></p>
          <div class="readout" aria-hidden="true">{"".join(readouts)}</div>
          <fieldset class="strip">
            <legend class="sr">Tracks in the playlist Neurofunk. Pick one to find it in the screenshot.</legend>
            {wave}
            <span class="playhead" aria-hidden="true"></span>
            {"".join(tracks)}
          </fieldset>
        </div>
        <fieldset class="pages">
          <legend class="sr">Seeker's pages. Pick one to see it.</legend>
          {"".join(radios)}
          <input class="sr" type="checkbox" id="theme" aria-label="Switch between dark and light">
          <div class="tabs" aria-hidden="true"><label class="tab tab-theme" for="theme"><span class="to-light">Light mode</span><span class="to-dark">Dark mode</span></label>{"".join(tabs)}</div>
          {"".join(descs)}
          <div class="screen">
            <div class="set set-dark">{"".join(layers["dark"])}</div>
            <div class="set set-light">{"".join(layers["light"])}</div>
            <span class="row-hl" style="{across}" aria-hidden="true"></span>
            <div class="rowspots" style="{across}" aria-hidden="true">{rowspots}</div>
            <div class="dz-layer" aria-hidden="true">{"".join(dzs)}</div>
            <div class="hotspots">{"".join(spots)}</div>
          </div>
        </fieldset>
        <figcaption>
          {"".join(caps)}
          <ul class="lamps">
            <li class="lamp-play">In your library</li>
            <li class="lamp-cue">Downloading</li>
            <li class="lamp-wait">Waiting for you to review</li>
            <li class="lamp-off">Not found</li>
          </ul>
        </figcaption>
      </figure>'''


def css() -> str:
    _, lefts = strip()
    rows = of_kind("dashboard", "row")
    tops = [r["y"] / IMAGE_H * 100 for r in rows]
    heights = [r["h"] / IMAGE_H * 100 for r in rows]
    n = len(TRACKS)
    out = ["/* A picked track: the playhead, the row outline, its readout, its",
           "   waveform brighter. */"]
    for i in range(1, n + 1):
        out.append(
            f".shot-hero:has(#t{i}:checked) {{ --ph: {lefts[i - 1]:.2f}%; --row-top: {tops[i - 1]:.3f}%; --row-h: {heights[i - 1]:.3f}%; }}\n"
            f".shot-hero:has(#t{i}:checked) .ro-{i} {{ display: flex; }}\n"
            f".shot-hero:has(#t{i}:checked) .w{i} {{ --wave-have: var(--text); --wave-dim: var(--text-muted); }}")
    out.append("\n/* A picked page: its image on top, its description, caption and\n   controls; its tab in the phone's row. */")
    for page, *_ in PAGES:
        out.append(
            f".shot-hero:has(#pg-{page}:checked) .scr-{page} {{ z-index: 1; }}\n"
            f".shot-hero:has(#pg-{page}:checked) :is(.desc-{page}, .cap-{page}, .dzs-{page}) {{ display: block; }}\n"
            f".shot-hero:has(#pg-{page}:checked) .tab-{page} {{ color: var(--text); border-color: var(--accent); background: var(--bg-surface-2); }}\n"
            f".shot-hero:has(#pg-{page}:focus-visible) :is(.hs-{page}, .tab-{page}) {{ outline: 2px solid var(--accent); outline-offset: 1px; }}")

    # Attract mode: until a track is picked (no radio checked), the strip
    # steps through the set, as idle decks do, so it shows what picking
    # does; hovering pauses it and the first pick stops it. Still (reduced
    # motion, or before it starts) it rests on RESTING_TRACK.
    idle = ".shot-hero:not(:has(input[name=track]:checked))"
    rest = RESTING_TRACK - 1
    cycle = n * SLOT
    glide = 0.45 / cycle * 100  # % of the cycle the playhead takes to move
    slot = 100 / n
    animated = f"{idle} :is(.playhead, .row-hl, .ro, .strip-wave g)"
    paused = ".shot-hero:has(.strip:hover, .rowspots:hover) :is(.playhead, .row-hl, .ro, .strip-wave g)"

    def glide_frames(prop: str, values: list[float]) -> str:
        frames = []
        for i, v in enumerate(values):
            frames.append(f"    {i * slot:.3f}% {{ {prop}: {v:.3f}%; }}")
            frames.append(f"    {(i + 1) * slot - glide:.3f}% {{ {prop}: {v:.3f}%; }}")
        frames.append(f"    100% {{ {prop}: {values[0]:.3f}%; }}")
        return "\n".join(frames)

    out.append(f"""
/* Attract mode: the strip steps through the set until a track is picked.
   Still, it rests on track {RESTING_TRACK}. */
{idle} .cue-line .when-attract {{ display: inline-flex; }}
.shot-hero:has(input[name=track]:checked) .cue-line .when-picked {{ display: inline-flex; }}
{idle} .ro-{RESTING_TRACK} {{ display: flex; }}
{idle} {{ --ph: {lefts[rest]:.2f}%; --row-top: {tops[rest]:.3f}%; --row-h: {heights[rest]:.3f}%; }}
{idle} .w{RESTING_TRACK} {{ --wave-have: var(--text); --wave-dim: var(--text-muted); }}
@media (prefers-reduced-motion: no-preference) {{
  {idle} .cue-line .moving {{ display: inline; }}
  {idle} .cue-line .still {{ display: none; }}
  {idle} .cue-dot {{ animation: cue-blink 1s steps(1) infinite; }}
  {idle} .ro {{ display: flex; opacity: 0; }}
  {idle} .w{RESTING_TRACK} {{ --wave-have: initial; --wave-dim: initial; }}
  {animated} {{ animation-duration: {cycle:.1f}s; animation-delay: {START}s; animation-iteration-count: infinite; animation-fill-mode: both; }}
  {idle} .playhead {{ animation-name: attract-ph, appear; animation-duration: {cycle:.1f}s, 0.3s; animation-iteration-count: infinite, 1; animation-timing-function: ease-in-out; }}
  {idle} .row-hl {{ animation-name: attract-row; animation-timing-function: ease-in-out; height: {sum(heights) / n:.3f}%; }}
  {paused} {{ animation-play-state: paused; }}
  @keyframes attract-ph {{
{glide_frames("left", lefts)}
  }}
  @keyframes attract-row {{
{glide_frames("top", tops)}
  }}""")
    # Each track is lit for its slot: its readout shows, its waveform is
    # at full strength (the others dim to half).
    for i in range(n):
        for kind, floor, selector in (("ro", 0, f".ro-{i + 1}"), ("w", 0.5, f".strip-wave .w{i + 1}")):
            frames = [f"0% {{ opacity: {1 if i == 0 else floor}; }}"]
            if i:
                frames.append(f"{i * slot:.3f}% {{ opacity: 1; }}")
            if i < n - 1:
                frames.append(f"{(i + 1) * slot:.3f}% {{ opacity: {floor}; }}")
            frames.append(f"100% {{ opacity: {floor}; }}")
            out.append(f"  {idle} {selector} {{ animation-name: attract-{kind}{i + 1}; animation-timing-function: step-end; }}")
            out.append(f"  @keyframes attract-{kind}{i + 1} {{ {' '.join(frames)} }}")
    out.append("}")
    return "\n".join(out)


def fill(path: Path, name: str, content: str, comment: tuple[str, str] = ("<!--", "-->")) -> None:
    start, end = comment
    open_marker = f"{start} build_page.py: {name} {end}"
    close_marker = f"{start} /build_page.py: {name} {end}"
    text = path.read_text()
    a, b = text.index(open_marker) + len(open_marker), text.index(close_marker)
    indent = re.search(r"[ \t]*$", text[:text.index(open_marker)])[0]
    path.write_text(text[:a] + "\n" + indent + content + "\n" + indent + text[b:])


def main() -> None:
    fill(ROOT / "index.html", "wordmark", wordmark("Seeker"))
    fill(ROOT / "404.html", "wordmark", wordmark("Seeker home"))
    fill(ROOT / "index.html", "preload", preload())
    fill(ROOT / "index.html", "figure", figure())
    fill(ROOT / "style.css", "generated", css(), ("/*", "*/"))
    for name in ("index.html", "404.html", "style.css"):
        print(f"{name}: {(ROOT / name).stat().st_size:,} B")


if __name__ == "__main__":
    main()
