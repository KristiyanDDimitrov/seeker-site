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
| T2 | (done) Assets: icon PNGs from `seeker_icon.icns` (favicon 32, apple-touch 180, 512 for og), brows SVG recoloured to ACCENT; `tools/contrast.py` (verbatim logic) checking every text pair the CSS uses, both schemes | todo |
| T3 | (done) Screenshots: run `../Seeker/tools/screenshots.py` (dark, fixed size); pick dashboard + review + one more; PNG→WebP via Pillow into `assets/screens/`; write alt text | todo |
| T4 | (done) Build `index.html`, `404.html`, `style.css`, `_config.yml`, `README.md` per design plan | todo |
| T5 | (done) og image 1200×630 (render `tools/og.html` with Playwright, save `assets/og.png`); meta tags; favicon links | todo |
| T6 | (done) Verify: Playwright screenshots 1440/390 × light/dark into `verification/`; no-horizontal-scroll check at 360; Lighthouse raw JSON+scores; link check incl. releases/latest; third-party request check; page weight total; contrast output | todo |
| T7 | `gh repo create KristiyanDDimitrov/seeker-site --public`, push `main`; final report to user with raw evidence. Do NOT enable Pages | todo |

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
  releases/latest → releases/tag/v0.1.0. **FAIL: seekerapp.dev has no MX
  record** (Porkbun NS, parked A records), so hello@ bounces until the
  user sets up mail. Page weight: 87.2 KiB desktop / 138.0 KiB 3x phone,
  8 requests. Re-run: tools/shoot.py, linkcheck.py, weight.py, contrast.py.
