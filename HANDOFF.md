# seeker-site: session plan and handoff

A cleared-context agent should read this file first, then continue from
the first task not marked done. Update the task's status and "Notes" as
you go. Keep this file current; it is the only state between sessions.

## The brief (condensed)

Static landing page for Seeker at https://seekerapp.dev/. Plain HTML +
CSS, no framework, no build step, no JS unless an item needs it, **no
third-party requests of any kind** (no CDNs, web fonts, analytics).
System font stack. Files: `index.html`, `404.html`, `style.css`,
`assets/`. Responsive to 360 px with no horizontal scroll. Do **not**
enable GitHub Pages or touch DNS: the user does that.

Content: hero (logo, brows wordmark if clean at size, name, one-line
pitch, "Download" → releases/latest, "View on GitHub", "Latest: v0.1.0 ·
macOS…" line); 2–3 real dark-theme screenshots (WebP, alt text);
features (Spotify playlist sync; multi-drive library scan + matching;
SoulSeek search/download via slskd; tag, art and locally computed
BPM/key); "Runs on your machine" (no account, no telemetry, analysis is
local); requirements (Spotify account, Docker + slskd, SoulSeek
account); footer (GitHub link, hello@seekerapp.dev, one-line note that
users are responsible for what they download). Meta: title,
description, Open Graph + Twitter card with a 1200×630 image, favicon
from the app icon, canonical https://seekerapp.dev/.

Verification evidence required: screenshots at 1440 and 390 wide in
both schemes; raw Lighthouse scores; a link check (incl.
releases/latest); total page weight; WCAG ≥ 4.5:1 for body text using
the app's own contrast logic.

## Decisions already made (do not re-ask)

- Seeker repo: `KristiyanDDimitrov/Seeker`, **public**, default branch
  `main`. Local clone: `../Seeker`.
- Release v0.1.0 ("Seeker 0.1.0", published 2026-10-14, marked Latest):
  assets are exactly `Seeker.dmg` (111,788,167 B) and
  `Seeker.dmg.sha256` (77 B). Platform: **macOS 15 or later on Apple
  silicon only**; ad-hoc signed, not notarized (first launch needs
  Privacy & Security → Open Anyway). Windows/Linux never ran on real
  hardware: do not advertise them.
- Scaffold: the uv/PyCharm Python scaffold was deleted (user's call).
  Site lives at the repo root. Dev-only tooling goes in `tools/`;
  verification evidence in `verification/`. Both, plus this file, are
  excluded from the published site via `_config.yml` `exclude:` (Pages'
  default Jekyll deploy copies plain HTML unchanged).
- GitHub: user wants a **public** repo `KristiyanDDimitrov/seeker-site`
  created and pushed (name confirmed free). Never enable Pages.
- Screenshots: from Seeker's `tools/screenshots.py` (real widgets,
  offscreen, invented demo data; no personal data). Dark theme, one
  fixed window size.
- Dev tools allowed: Playwright Chromium (`npx playwright install
  chromium`), Lighthouse via `npx`, Pillow via `uv run --with pillow`.
  No Chrome, cwebp or ImageMagick on this machine.
- Palette source: `../Seeker/src/seeker/ui/theme.py` `DARK` and `LIGHT`
  (LIGHT is C5's light palette, HISTORY §107, retuned to "Booth violet"
  in S31). Contrast logic: `_relative_luminance` / `contrast_ratio` in
  the same file, copied verbatim into `tools/contrast.py`.
- The user asked to use the available skills; `frontend-design` is
  loaded and its two-pass process applies (plan below).

## Design plan (frontend-design, reviewed)

Subject: Seeker, a Mac app for DJs. Audience: DJs preparing sets,
often in a dark room. Primary job (from Seeker's own
`docs/design/visual-direction.md`): **see what a set is missing, and
get it into the library correctly tagged.** The app's direction is
"Booth": CDJ hardware vocabulary, graphite surfaces, one lit violet
accent, condensed panel lettering for titles.

Color (verbatim from theme.py):

| Token | Dark | Light | Use on the page |
|---|---|---|---|
| BG_APP | #17191C | #E8EAEC | page ground |
| BG_SIDEBAR | #101113 | #DDE0E3 | footer (recessed chrome) |
| BG_SURFACE | #1E2125 | #F9FAFA | screenshot panel, sections that come forward |
| BORDER | #353A40 | #CBD0D5 | hairlines |
| TEXT | #E8EAEC | #15181B | body |
| TEXT_MUTED | #A0A7AE | #4D555D | secondary lines |
| ACCENT | #9A7DFF | #6440E6 | brows, the one primary button, links, focus |
| ON_ACCENT | #120E1F | #FFFFFF | text on the button |
| SUCCESS / CUE / DANGER | #35D07F / #FFB020 / #FF6363 | #11804A / #AD7400 / #C22B2B | lamps only (3:1 role) |

Type: system stacks only. Display = the app's "panel lettering" made
from installed condensed faces: `"Avenir Next Condensed", "SF Pro
Display Condensed", "Arial Narrow", "Roboto Condensed",
sans-serif-condensed, system-ui` at SemiBold/Bold, used for the
wordmark and section titles. Body = `system-ui, -apple-system,
"Segoe UI", Roboto, sans-serif`. Scale ~ 1.25 ratio; body 17–18 px,
measure ≤ 70ch.

Layout: single left-aligned column with a wide image band.

```
[icon] Seeker                                    GitHub
SEEKER  (huge condensed wordmark, violet brows over the "ee")
Find what your sets are missing…          (pitch, ≤ 60ch)
[Download for Mac]  [View on GitHub]
Latest: v0.1.0 · macOS 15+ on Apple silicon
┌──────── dashboard screenshot (BG_SURFACE panel) ────────┐
What it does      | four one-line features, each with a lamp?  (see principle 2)
two screenshots side by side (review, downloads) → stacked on mobile
Runs on your machine | three short lines
What you need        | three items, each a link to where you get it
footer: GitHub · email · responsibility note
```

Principles:
1. Spend the boldness in one place: the wordmark with the brows, big,
   in condensed panel lettering. Everything else quiet.
2. Lamps carry meaning or don't appear. The only lamp use: a small
   legend under the hero screenshot naming the four states the
   screenshot shows (In library / Working / Needs you / Not found),
   because that *is* the product's primary job. No lamps as bullets.
3. Real product first: the screenshot is the hero's second beat, not
   an illustration. No gradients, no card grid, no shadows-as-default.
4. Left aligned. Two-column "label | content" rows on wide screens for
   the three short sections; single column ≤ 720 px.

Review against generic defaults: dark graphite + one bright accent is
close to default trait #2, but it is mandated verbatim by the brief
(theme.py), so it stays; the differentiator is the brows wordmark,
the condensed panel lettering and the lamp legend from the app's own
vocabulary. Dropped: an eyebrow label above the hero, numbered feature
markers (features aren't a sequence), "→" on buttons, a card grid for
features.

## Tasks

Status: `todo` / `doing` / `done`. One commit per task once git has a
remote-free history; push happens in T7.

| # | Task | Status |
|---|---|---|
| T1 | Verify repo/release facts; remove scaffold; git init; this file | done |
| T2 | Assets: icon PNGs from `seeker_icon.icns` (favicon 32, apple-touch 180, 512 for og), brows SVG recoloured to ACCENT; `tools/contrast.py` (verbatim logic) checking every text pair the CSS uses, both schemes | done |
| T3 | Screenshots: run `../Seeker/tools/screenshots.py` (dark, fixed size); pick dashboard + review + one more; PNG→WebP via Pillow into `assets/screens/`; write alt text | done |
| T4 | Build `index.html`, `404.html`, `style.css`, `_config.yml`, `README.md` per design plan | done |
| T5 | og image 1200×630 (render `tools/og.html` with Playwright, save `assets/og.png`); meta tags; favicon links | done |
| T6 | Verify: Playwright screenshots 1440/390 × light/dark into `verification/`; no-horizontal-scroll check at 360; Lighthouse raw JSON+scores; link check incl. releases/latest; third-party request check; page weight total; contrast output | done |
| T7 | `gh repo create KristiyanDDimitrov/seeker-site --public`, push `main`; final report to user with raw evidence. Do NOT enable Pages | done |

## Notes (append as you go)

- T1: `gh release view v0.1.0 -R KristiyanDDimitrov/Seeker` raw output
  was reported to the user in-session; key facts copied above.
- T2: icon PNGs from `iconutil -c iconset` of seeker_icon.icns → assets/icon-32/180/256.png.
  Wordmark: `tools/wordmark.py` outlines "Seeker" in Barlow Semi Condensed
  SemiBold (Seeker's packaging/fonts) with brows placed by wordmark.py's
  constants → assets/wordmark.svg, self-themed via embedded
  prefers-color-scheme style (used as <img>). `python3 tools/contrast.py`:
  34 pairs PASS, tokens == theme.py.
- T3: `QT_SCALE_FACTOR=2 uv run python tools/screenshots.py --theme dark
  --page dashboard --page review --page downloads` in ../Seeker (1280x820 →
  2560x1640). `tools/screens.py` crops the 40 px in-window menu bar (an
  offscreen-Qt artefact; macOS uses the system menu bar) → WebP 2560/1280.
- Copy facts verified in ../Seeker: Spotify needs the user's own Spotify
  app Client ID (README); BPM/key via librosa locally; source is MIT;
  update check optional + off by default; sharing is opt-in (so never
  claim "your library never leaves your Mac").
- Chromium gotcha: `npx playwright@1.56.1 install chromium` downloads the
  zip but its extractor hangs (Node 26). Fix used: unzip the zip from
  $TMPDIR/playwright-download-*/ into ~/Library/Caches/ms-playwright/
  chromium-1194/ and `touch INSTALLATION_COMPLETE`. Done; Chromium.app is
  at chromium-1194/chrome-mac/Chromium.app. Needs dangerouslyDisableSandbox
  for network.
- T4/T5: screenshots link to their 2560 px originals (illegible at phone
  width otherwise). OG card = tools/og.html rendered by tools/og.py; it
  frames the dashboard's Track + Status columns so the lamps show.
  `body { overflow-x: clip }` was removed on purpose: it would hide real
  overflow from the 360 px check.
- Local verification server: `python3 -m http.server 8765 --bind 127.0.0.1`
  from the repo root (needs dangerouslyDisableSandbox for Playwright).
- T6 results (2026-10-14): Lighthouse 12.8.2 mobile + desktop = 100/100/100/100
  (reports in verification/). Layout: no overflow at 1440/390/360, both
  schemes, both pages; 0 off-origin requests. Link check: all OK,
  releases/latest → releases/tag/v0.1.0. MX was missing at first;
  the user then enabled Porkbun forwarding (see below). Page weight: 87.2 KiB desktop / 138.0 KiB 3x phone,
  8 requests. Re-run: tools/shoot.py, linkcheck.py, weight.py, contrast.py.
- T7: repo https://github.com/KristiyanDDimitrov/seeker-site (public,
  main) created and pushed. Pages API → 404 (Pages not enabled, as
  required). All tasks done; open items are the user's: enable Pages,
  point DNS.
- 2026-10-14: MX now `10 fwd1.porkbun.com` / `20 fwd2.porkbun.com` (Porkbun
  email forwarding). SMTP probe (RCPT TO, no DATA): both forwarders
  accept hello@seekerapp.dev with 250 2.1.5 and reject a random address
  with 554, so the forward rule exists. No SPF/TXT record (only matters
  for sending as @seekerapp.dev). linkcheck.py now asks 1.1.1.1.

## Round 2 (2026-10-14 to 2026-10-16): the interactive page

The user asked for the page to "look even cooler without changing it too
much", saw a mockup before each step, and approved the build. Each
decision below is theirs (do not re-ask):

- Mobile bug: the wordmark was an `<img>` of an SVG that picked its own
  colour scheme, which disagreed with the page on the user's phone (dark
  page, light-scheme letters). The wordmark is now inline SVG coloured by
  the page's tokens, on index.html and 404.html.
- "Lit booth": the brows glow (dark theme only, via `--glow`) and power
  on once at load; lamps and the screenshot glow faintly.
- The app icon sits next to the Download button (the thing you get).
- The set strip: the Dashboard's selected playlist as a deck's waveform
  overview, one segment per track with its status lamp. Picking a track
  (its waveform, or its row in the screenshot's track list) shows a
  readout, moves a playhead and outlines the row in the screenshot.
  Until one is picked, "attract mode" steps through the set (hover
  pauses, a pick stops it; reduced motion rests on track 3), with a cue
  line above the strip saying what to do.
- Demo data: playlists Neurofunk, Jungle, Peak Time Techno, Progressive
  House; Neurofunk's eight tracks are real ones the user chose (see
  `tools/app_screens.py`). One invented track remains (Mara Okafor -
  Glasshouse, in Jungle). The Support page's author email
  (kristiyanddimitrov@proton.me) stays in its screenshot: user's call.
- The screenshot is explorable: every sidebar page and Settings' four
  tabs, in both themes, all stacked and painted so switching never
  flashes; picking a waveform from another page jumps back to the
  Dashboard. The app's theme toggle flips the whole page. Every other
  control in the picture scrolls to Download and pops it. Clicking the
  picture never opens the image (the full-size links are gone, by
  request). Phones get a row of page names (and Settings' tabs) above
  the picture instead of the tiny sidebar.
- A Support button (with Revolut and PayPal logos, Simple Icons CC0,
  inlined) scrolls to a Support section built from the app's own Support
  copy; donation links are Seeker's `help_text.SUPPORT_LINKS`.
- JavaScript: about 40 lines, inline, only for scroll-then-pop and the
  jump back to the Dashboard (the brief allows JS where an item needs
  it). Everything else is radios, a checkbox and `:has()`; without JS the
  links still jump and `:target` pops once.

How it is built (see each script's docstring):

1. `uv run --no-project --with pillow python tools/app_screens.py`
   renders every page in both themes with ../Seeker's own screenshot
   tool, patched at run time (never in the Seeker repo) for the demo
   data and a recorder of every control's and table row's rectangle.
   Writes `assets/screens/*.webp` (84 files) and
   `tools/screen-geometry.json`. Each patch asserts its target text, so
   a change in Seeker's tool stops it.
2. `python3 tools/build_page.py` regenerates the marked parts of
   index.html, 404.html and style.css (`build_page.py: NAME` markers):
   wordmark, preload, the figure (strip + screenshot + click targets),
   and the per-track/per-page/attract CSS. Everything outside the
   markers is hand-written. It is idempotent.
3. Re-run the checks (server: `python3 -m http.server 8765 --bind
   127.0.0.1` from the repo root): tools/shoot.py, contrast.py,
   linkcheck.py, weight.py, og.py, and Lighthouse:
   `CHROME_PATH=<Chromium> npx -y lighthouse@12.8.2 http://127.0.0.1:8765/
   --chrome-flags=--headless=new --output=json --output=html
   --output-path=verification/lighthouse-mobile` (add `--preset=desktop`
   and `-desktop` for desktop).

| # | Task | Status |
|---|---|---|
| R1 | Fix the wordmark colour bug (inline SVG) | done |
| R2 | Lit booth, icon by Download, set strip, attract mode | done |
| R3 | New demo data; all 14 pages × 2 themes rendered with geometry | done |
| R4 | Explorable screenshot, theme toggle, download prompts, Support | done |
| R5 | tools/app_screens.py + tools/build_page.py; old tools/screens.py removed | done |
| R6 | Verify (results below), commit, push | done |

Round 2 results (2026-10-16, raw files in `verification/`):
- Layout: no horizontal scroll at 1440/390/360, both schemes, both pages;
  0 off-origin requests (layout-checks.json).
- Lighthouse 12.8.2: desktop 100/100/100/100; mobile 99/100/100/100
  (mobile LCP 2.0 s under simulated throttling; CLS 0, TBT 0).
- Contrast: all pairs pass in both schemes; the toggle's palette copies
  equal the originals (contrast.txt).
- Link check: all OK, incl. revolut.me, paypal.me (-> paypal.com/paypalme)
  and GitHub issues (linkcheck.txt).
- Weight: first load 626.5 KiB (dark) / 641.0 KiB (light), 19 requests,
  was 87 KiB: every page's screenshot preloads so switching never
  flashes; the other theme's load on the first flip (page-weight.txt).
- Behaviour tested in Playwright against the real site: page switching
  and Settings tabs, theme flip both ways (right layer on top, loaded),
  attract mode timing/pause/stop/reduced motion, row = waveform picks,
  Tag button prompts instead of picking, scroll-then-pop (repeatable, no
  URL hash), jump back to the Dashboard (incl. same track, arrow keys),
  Support scroll, and the no-JS fallbacks.

### Direct download (2026-10-16, user's call)

Download (index and 404) is
`https://github.com/KristiyanDDimitrov/Seeker/releases/latest/download/Seeker.dmg`:
GitHub redirects it to the latest release's asset, served as an
attachment, so the file downloads and the visitor stays on the page.
Verified with curl (302 -> v0.1.0's asset, `content-disposition:
attachment; filename=Seeker.dmg`, 111,788,167 B) and in Playwright (a
download event, URL unchanged). After the click, a note (index only,
via the script) gives the first-launch step for the un-notarized app;
"v0.1.0" in the Latest line links to the release (notes, checksum).
linkcheck.py now fetches one byte (`-r 0-0`, 206 = OK) and prints final
URLs without their query (release assets land on signed URLs).

On each new release: keep the asset named exactly `Seeker.dmg` (the
link depends on it), and update by hand the Latest line's version and
tag link, and the note's size ("112 MB") in index.html.
