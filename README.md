# seeker-site

The landing page for [Seeker](https://github.com/KristiyanDDimitrov/Seeker),
served at https://seekerapp.dev/. Plain HTML and CSS: no framework, no build
step, no JavaScript, no third-party requests.

- `index.html`, `404.html`, `style.css`, `assets/`: the site.
- `tools/`: dev-only scripts that produced the assets and the checks.
- `verification/`: evidence (screenshots, Lighthouse, link check).
- `HANDOFF.md`: how this was built, and the state of the work.

Colours are Seeker's own theme tokens (`src/seeker/ui/theme.py`); run
`python3 tools/contrast.py` after changing any.

The wordmark is "Seeker" in Barlow Semi Condensed (SIL Open Font License
1.1), outlined to SVG by `tools/wordmark.py`; no font file is served.
