# seeker-site

The landing page for [Seeker](https://github.com/KristiyanDDimitrov/Seeker),
served at https://seekerapp.dev/. Plain HTML and CSS, a few lines of inline
JavaScript, no framework, no third-party requests. The interactive screenshot
is generated: `tools/app_screens.py` renders Seeker's pages and records where
their controls are, and `tools/build_page.py` rebuilds the marked parts of the
pages from that (see HANDOFF.md, "Round 2").

- `index.html`, `404.html`, `style.css`, `assets/`: the site.
- `tools/`: dev-only scripts that produced the assets and the checks.
- `verification/`: evidence (screenshots, Lighthouse, link check).
- `HANDOFF.md`: how this was built, and the state of the work.

Colours are Seeker's own theme tokens (`src/seeker/ui/theme.py`); run
`python3 tools/contrast.py` after changing any.

The wordmark is "Seeker" in Barlow Semi Condensed (SIL Open Font License
1.1), outlined to SVG by `tools/wordmark.py`; no font file is served.
