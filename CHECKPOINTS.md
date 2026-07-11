# CHECKPOINTS — build plan for "The Fourteen"

## Execution contract (binding)
1. Checkpoints run in order; a checkpoint is done only when every AC passes. The site must be complete-feeling at every boundary.
2. **Every checkpoint closes with `git commit` + `git push`** (auto-deploys once Pages is live). Within CP1b and CP6, commit+push after EACH page — pages are independently landable units.
3. **Go-live happens at CP1a, not the end**: secrets scan → push → repo public → Pages enabled → live smoke test. Everything after CP1a ships incrementally to a live site.
4. **Parallelization mandate:** CP1b pages and CP6 upgrades are built by parallel subagents in batches of 3–4, each given DESIGN.md + the relevant template + its paperFacts/buildPaths entries; the orchestrator reviews for voice consistency before landing.
5. **Schedule governor:** at T−3h before expected wake-up (~08:00 local), stop starting new CP3–CP6 units; jump to CP7+CP8 with whatever has landed. **Pre-authorized cuts, in order:** (1) Polo Club iframe facades → attribution link-out cards (removes the screenshot pipeline); (2) CP6 pages beyond rlhf + deepseek-r1 stay at plate grade; (3) CP3 CoT widget → plate page with the 17.9%→56.9% headline as a static figure. Shedding these is spec-compliant.
6. SPEC.md governs all content/engineering decisions; `research/*.json` governs all facts.

---

## CP0 — Environment, scaffold, design system, data spine
- [ ] **Environment first:** `uv venv --python 3.11 .venv && uv pip install --python .venv/bin/python torch transformers numpy pillow`; smoke-run `import torch, transformers, numpy, PIL` passes; `.venv` gitignored.
- [ ] `DESIGN.md` per SPEC §3 (graphite ground, 5 category accent quads with AA-verified hexes, 3 named font families, paper-chip recipe, components, motion + reduced-motion, mobile inversion). CLAUDE.md rule: read DESIGN.md before visual work.
- [ ] `docs/css/site.css` v=1: tokens → skeleton → components (paper-chip, node card, act band, scrolly grid, widget panel, coda rungs, minimap). Zero hardcoded colors outside tokens.
- [ ] `docs/papers.json`: `acts` array (5 bandCopy + gap captions, incl. the 2023–24 caption) AND all 14 papers complete per SPEC §2 schema — hook, consequence, cliffhanger, minutes, buildChip, venue, paperUrl, full codas under the rung-expansion rule.
- [ ] `docs/prices.json` per SPEC §2 schema (gpu section from research; api section placeholder until CP3).
- [ ] `tools/`: validate_papers.py, build_timeline.py, **build_paper_blocks.py**, check_links.py + inject_meta.py (ported), bump_css.py; baker stubs with deps documented in-file (bake_attention.py, bake_cot.py, bake_diffusion_strip.py, **bake_paper_figures.py**).
- [ ] `templates/paper-plate.html`, `paper-scrolly.html`, `paper-widget.html` with full SPEC §5 anatomy incl. marked HOOK/CODA/HANDOFF blocks and static nav fallbacks.
- [ ] Skeleton `docs/index.html` (hero with BOTH deck lines + acts + empty NODES block), `.nojekyll`, `robots.txt`, check_links GitHub Action.
- **AC:** venv smoke-run passes; validate_papers.py passes; build_timeline.py AND build_paper_blocks.py idempotent; check_links passes; commit+push.
- **V:** local render at 3 widths: act bands, fonts, tokens correct.

## CP1a — Deployable core + GO LIVE
- [ ] index.html complete: 14 node cards (with buildChips) + act bands + gap captions baked; hero; footer (sibling banner, **build.html**, GitHub, colophon); 15th node with "2026: you" reveal-on-approach.
- [ ] All js modules: main.js, scroll.js (verbatim port), components.js (chrome only, static fallbacks), spine.js (curve + `renderMinimap` + static fallback), timeline.js (act progress, fast-path toggle, ladder checkmarks).
- [ ] The 4 FINAL plate pages: alexnet, resnet, clip, lora (bake_paper_figures.py data where data-driven; full anatomy incl. codas).
- [ ] colophon.html + 404.html; inject_meta.py run; sitemap.xml (17 URLs).
- [ ] **Deploy:** `git log`/tree secrets scan → commit+push → `gh repo edit NavSha/ml-papers --visibility public --accept-visibility-change-consequences` → enable Pages (`gh api -X POST repos/NavSha/ml-papers/pages -f "source[branch]=main" -f "source[path]=/docs"`) → poll `gh api repos/NavSha/ml-papers/pages/builds/latest` every 30s until `status=built` (timeout 15 min) → curl live index + one paper page for HTTP 200.
- **AC:** SPEC §9 full 17-page check for the pages that exist (index, 4 plates, build placeholder OK to be CP1b, colophon, 404); JS-off readable; zero console errors; **live URL serves the site**.
- **V:** full-width screenshot record (1440/768/390) from the LIVE url.

## CP1b — The remaining 10 pages at plate grade + build.html
- [ ] 10 paper pages at plate grade (parallel batches of 3–4; commit+push per page): transformer, gpt2, scaling-laws, gpt3, moe, stable-diffusion, cot, rlhf, constitutional-ai, deepseek-r1. deepseek-r1's handoff → build.html (closing-argument copy).
- [ ] build.html complete per SPEC §7 (ladder with localStorage contract, contribute/communities/jobs, "checked July 2026" stamp).
- **AC:** every page's aha within one scroll at 1440px; codas verified against buildPaths.json; check_links passes; JS-off readable.
- **V:** screenshot review of changed pages at 3 widths; live spot-check.

## CP2 — Scaling Laws flagship (`plate → live`)
- [ ] widgets/scaling-laws.js per SPEC §6a: Modes A+B, verdict-line logic verbatim, plot spec (log-x, LINEAR-y, asymptote, frontier, 5 anchors with GPT-2 D_effective rule, shaded extrapolation), "GPT-3's mistake" break-it preset, advanced panel (price/MFU, Hoffmann↔Epoch toggle swapping constants everywhere incl. asymptote), $ odometer, caveats drawer (all 10), prices stamp, init-time sanity asserts.
- **AC:** asserts pass (Hoffmann constants); anchors placed per research (GPT-3 visibly above frontier); break-it preset present; keyboard + reduced-motion OK; status flipped; commit+push.

## CP3 — Chain-of-Thought (`→ live`)
- [ ] Env-var check for an API key at start: none expected → **primary path: hand-authored from the paper's exemplars/appendix** (SPEC §6b), token counts via GPT-2 tokenizer in venv; fetch provider public pricing page for prices.json api section (record sourceUrl + date; unreachable → labeled estimates).
- [ ] widgets/cot.js: two panes + meters + headline + **"try it on a small model" break-it pane** (paper-appendix sub-threshold examples, honestly labeled) + provenance footer.
- **AC:** costs recompute from prices.json; direct pane shows no hidden chain-of-thought; gap direction matches the headline or framing copy explains honestly; break-it pane present; mobile stacked; status flipped; commit+push.

## CP4 — Transformer/Attention (`→ live`)
- [ ] bake_attention.py in venv (GPT-2 small; 8 curated sentences incl. **1–2 designed failure sentences**; quantized; ≤3MB). Fallback variant per SPEC §6c only if the bake fails.
- [ ] widgets/transformer.js: chips + arcs, layer/head selector, heatmap toggle, per-sentence notes incl. "why this breaks".
- [ ] Polo Club facade: poster captured headless (gstack /browse or chrome-devtools; wait for the visualization canvas selector, allow 3–5 min model stream; verify non-blank; cwebp/Pillow compress) — fallback poster: MIT-licensed screenshot from the poloclub README. bbycroft teaser: headless capture with WebGL paint wait; blank → typographic link-out card (no image).
- **AC:** arcs match baked data (coreference sentence spot-check — or fallback AC per SPEC §6c); failure sentence demonstrates diffusion; facade loads nothing until click; status flipped; commit+push.

## CP5 — Stable Diffusion (`→ live`)
- [ ] bake_diffusion_strip.py in venv: Blue Marble source (or author-owned fallback), linear β 1e-4→0.02, T=1000, ~12 frames, **2 seeds**, ≤3MB webp.
- [ ] widgets/stable-diffusion.js: scrubber (keyboard/touch), latent-vs-pixel toggle with the arithmetic, **"shuffle the noise" break-it button**, Diffusion Explainer facade (≥1200px gate, poster as CP4).
- **AC:** scrubber operable; both seeds swap; lazy load; credits in colophon; status flipped; commit+push.

## CP6 — Tier-2 scrolly upgrades (order = cut-line priority: rlhf, deepseek-r1, gpt2, gpt3, moe, constitutional-ai)
Each page: upgrade → verify → flip status → **commit+push before starting the next**. Partial close is spec-compliant (remaining pages stay plate-grade).
- [ ] Pinned visuals (baked/static via bake_paper_figures.py, provenance recorded): rlhf = 3-step pipeline + 1.3B-beats-175B bar; deepseek-r1 = AIME curve (15.6→71.0→79.8) stepwise + reward-loop diagram; gpt2 = Figure-1 four-panel redraw; gpt3 = Figure-1.2 ICL curves redraw; moe = router animation + 7× callout; constitutional-ai = two-phase pipeline + **2–3 principles quoted EXACTLY from the arXiv 2212.08073 appendix (fetch ar5iv HTML; cite appendix section in colophon)** in paper-chips.
- **AC per page:** steps drive visual via scroll.js contract; mobile inversion; JS-off shows prose + static final-state figure; figure.json provenance exists; status flipped.

## CP7 — Connective tissue
- [ ] Fast-path end-to-end per SPEC §4 terminals (transformer prev → index; **rlhf next → build.html**).
- [ ] Ladder ↔ timeline checkmarks via the localStorage contract.
- [ ] Cross-links: sibling banner (ml-papers side; other repo = TODO note in README), coda own-repo links verified.
- [ ] README.md: hero screenshot, live URL, the 14 with hooks, architecture, asset-rebuild commands (venv + bakers).
- **AC:** **both reading paths (full chronological and fast-path) terminate at build.html — verified by click-through** in a fresh profile; localStorage flows work; commit+push.

## CP8 — Final QA + polish + live re-verification
- [ ] Multi-agent QA sweep: (a) content accuracy vs research/*.json + papers; (b) interaction testing every widget/toggle/scrubber incl. all four break-it affordances; (c) design consistency vs DESIGN.md; (d) a11y (contrast, keyboard, aria, reduced-motion); (e) 390px mobile; (f) performance (no page >1.5MB initial payload; site <15MB). Fix everything; re-verify.
- [ ] og.png: headless screenshot of the index hero at 1200×630; OG description carries both deck lines; inject_meta re-run; bump_css final.
- [ ] Final commit+push; poll Pages build; **full 17-page live sweep** (SPEC §9) from https://navsha.github.io/ml-papers/ — case-sensitive paths, OG tags, zero console errors.
- **V:** live screenshot record at 3 widths attached to the wake-up report.
