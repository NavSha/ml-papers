# CLAUDE.md — ml-papers ("The Fourteen")

Static site (zero-build, GitHub Pages from `docs/` on `main`). SPEC.md is the binding contract; CHECKPOINTS.md is the build plan; `research/*.json` governs all facts.

## Rules

1. **Read DESIGN.md before ANY visual work** (CSS, components, widgets, figures). Zero hardcoded colors outside the token block in `docs/css/site.css`.
2. **Read SPEC.md before ANY content work** (prose, papers.json, codas, widget copy). Do not invent facts absent from `research/*.json` or the papers.
3. **`docs/papers.json` is the ONLY home of editorial prose** (hooks, consequences, cliffhangers, bandCopy, gap captions, codas). Never put prose in `components.js` or duplicate it by hand in HTML.
4. After editing papers.json, run in order: `python3 tools/validate_papers.py`, then `python3 tools/build_timeline.py` and `python3 tools/build_paper_blocks.py` (both idempotent — run twice, expect no diff).
5. **Bakers run in the project venv:** `.venv/bin/python tools/bake_*.py` (torch/transformers/numpy/pillow live there; `.venv` is gitignored). Site-maintenance tools (`validate_papers`, `build_*`, `check_links`, `inject_meta`, `bump_css`) are stdlib-only — any `python3`.
6. **Cache-bust after every `docs/css/site.css` edit:** `python3 tools/bump_css.py` (rewrites `?v=N` everywhere). Never hand-edit version query strings.
7. Run `python3 tools/check_links.py` before any push. All internal URLs relative (site lives under `/ml-papers/`).
