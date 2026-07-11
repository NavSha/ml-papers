# SPEC — "The Fourteen" (ml-papers site)

**One-line pitch:** Thirteen years of AI, drawn as a single descending loss curve — the 14 papers that matter, explained so an AI-fluent engineer/PM/founder walks away understanding the core ideas *and* believing they can participate in building AI.

**Live URL (target):** https://navsha.github.io/ml-papers/
**Repo:** NavSha/ml-papers (currently private; flipped public at the CP1a deploy).

This spec is the single source of truth. Raw research is committed under `research/` — build agents MUST read the referenced research file before building each piece. Rev 2: incorporates the adversarial review (goal-fit, executability, feasibility critics).

---

## 1. Mission, audience, non-goals

**Audience:** engineers, technical PMs, and founders who use AI tools daily but have never read the papers.

**The two jobs of the site, in order:**
1. **Understanding** — each paper's one key idea, an aha within one screen-scroll of arriving.
2. **Confidence to participate** — every paper page ends with a verified, priced, weekend-scale "build this yourself" coda; the closing page ("2026: you") turns the codas into a participation ladder into open source and AI-adjacent careers. **The participation promise must be visible on the index itself**, not hidden in interior pages (see §4).

**Editorial thesis:** not "what shaped AI history" but "what changes how you build, prioritize, or place bets today."

**Voice rules:**
- Show the ONE real artifact per paper (equation / figure / number) with a plain reading. **The one-equation rule applies to the AHA block, not to widget internals** — widget engines may compute whatever the caveats disclose (see §6a exception).
- Honest analogies, not cute ones. One honest-limits beat per page.
- Correct one common misconception per paper, explicitly.
- **Break-it rule (binding):** every LIVE widget includes one *designed break-it affordance* that demonstrates the page's honest-limits claim interactively. The four affordances are named in §6. Watching everything work builds understanding; breaking something builds confidence.
- No hype words. Numbers make the argument.

**Non-goals (v1):** no live in-browser inference (v2, spike-gated); no comments; no analytics; no per-paper OG images (site og.png only); no search.

---

## 2. Architecture

**Stack: zero-build static.** Plain HTML + one CSS file + native ES modules. No framework, no bundler. Deploy = `git push` (GitHub Pages classic branch deploy, `main` branch `/docs` folder, `.nojekyll`, all internal URLs relative for the `/ml-papers/` subpath). Proven architecture of both sibling sites (`research/taylorTransformer.json`, `research/interactiveExplainers.json`).

### Environment (binding — set up at CP0, verified before anything else)
- **Site-maintenance tools are stdlib-only Python 3** (any local python3): `build_timeline.py`, `build_paper_blocks.py`, `check_links.py`, `inject_meta.py`, `bump_css.py`, `validate_papers.py`.
- **Bakers run in a project venv** created at CP0 and gitignored: `uv venv --python 3.11 .venv && uv pip install --python .venv/bin/python torch transformers numpy pillow` (`uv` is installed at `~/.local/bin/uv`; fallback `python3.11 -m venv`). CP0 AC includes a smoke-run: `.venv/bin/python -c "import torch, transformers, numpy, PIL"`.
- GPT-2 small downloads from HF on first bake (public model, no token; budget 5–15 min).
- webp via Pillow (verified present in sibling venv recipe) or `cwebp`.
- **No metered API key exists in this environment** — nothing may depend on one (see §6b).
- Headless screenshots (posters, og.png) via the gstack `/browse` daemon or chrome-devtools MCP — mechanism and wait conditions specified per checkpoint in CHECKPOINTS.md.

### Routes
```
docs/
  index.html          ← THE primary artifact: the timeline spine
  papers/{slug}.html  ← 14 paper pages
  build.html          ← "2026: you" — the 15th node / participation page
  colophon.html       ← provenance, redrawn-figure policy, licenses, design notes
  404.html            ← "a node that fell off the curve"
```

### Slugs, order, and metadata (canonical)
| # | slug | paper | timeline date (arXiv v1) | venue (chip) | category | tier |
|---|------|-------|------|------|----------|------|
| 1 | alexnet | AlexNet | 2012-12 | NeurIPS 2012 | foundations | plate |
| 2 | resnet | ResNet | 2015-12 | CVPR 2016 | foundations | plate |
| 3 | transformer | Attention Is All You Need | 2017-06 | NeurIPS 2017 | foundations | widget |
| 4 | gpt2 | GPT-2 | 2019-02 | OpenAI 2019 | llm-core | scrolly |
| 5 | scaling-laws | Scaling Laws | 2020-01 | arXiv 2020 | llm-core | widget (FLAGSHIP) |
| 6 | gpt3 | GPT-3 | 2020-05 | NeurIPS 2020 | llm-core | scrolly |
| 7 | moe | Switch Transformers / MoE | 2021-01 | JMLR 2022 | llm-core | scrolly |
| 8 | clip | CLIP | 2021-03 | ICML 2021 | beyond-text | plate |
| 9 | lora | LoRA | 2021-06 | ICLR 2022 | for-builders | plate |
| 10 | stable-diffusion | Latent Diffusion | 2021-12 | CVPR 2022 | beyond-text | widget |
| 11 | cot | Chain-of-Thought | 2022-01 | NeurIPS 2022 | making-useful | widget |
| 12 | rlhf | InstructGPT / RLHF | 2022-03 | NeurIPS 2022 | making-useful | scrolly |
| 13 | constitutional-ai | Constitutional AI | 2022-12 | arXiv 2022 | making-useful | scrolly |
| 14 | deepseek-r1 | DeepSeek-R1 | 2025-01 | arXiv 2025 | making-useful | scrolly |

**Timeline position uses the arXiv v1 date; the citation chip cites the publication venue.** Where they differ (resnet, moe, stable-diffusion, lora, cot), the discrepancy is intentional and noted once in colophon.html.

**Acts** (era bands): **I. The bet on scale** (2012–2015: alexnet, resnet) · **II. The architecture** (2017: transformer) · **III. The scaling era** (2019–2021: gpt2, scaling-laws, gpt3, moe) · **IV. Four threads at once** (2021–2022) — the four threads named explicitly: *seeing* (clip), *generating* (stable-diffusion), *customizing* (lora), *aligning* (cot, rlhf, constitutional-ai) · **V. The reasoning era** (2025: deepseek-r1 → the 15th node). The 2023–24 silence between IV and V gets a gap caption ("the frontier went closed — and then it didn't").

### Data flow — `docs/papers.json` is the single source of truth
Top level: `{ "acts": [...], "papers": [...] }`.

Acts entry: `{ "act": 4, "title": "Four threads at once", "years": "2021–2022", "bandCopy": "…", "gapCaptionAfter": "…" | null }` — all five bandCopy strings and gap captions are written at CP0 under the same editorial quality gate as hooks.

Paper entry:
```json
{
  "slug": "transformer", "title": "Attention Is All You Need",
  "nickname": "Transformer", "authorsShort": "Vaswani et al., Google Brain",
  "date": "2017-06",
  "arxiv": "1706.03762",              // nullable (alexnet, gpt2: null)
  "paperUrl": "https://arxiv.org/abs/1706.03762",  // required, canonical link
  "venue": "NeurIPS 2017",            // required
  "act": 2, "category": "foundations",
  "tier": "widget", "status": "plate",
  "minutes": 6,
  "hook": "…", "consequence": "…", "cliffhanger": "…",
  "buildChip": "build it: $0 · one evening",   // cheapest rung, shown on timeline card
  "coda": { "rungs": [ {"tag": "read|run|tweak|train", "text": "…", "href": "…", "time": "2 hrs", "cost": "$0"} ] }
}
```
- Chip link label follows the source: "arXiv 1706.03762" / "NeurIPS 2012" / "openai.com". Copy-citation format (one implementation in components.js): `{authorsShort} ({year}). {title}. {venue}. {paperUrl}`.
- **Coda rung-expansion rule:** `read` = the paper itself (paperUrl); `run` = the verified artifact from research/buildPaths.json with its verified cost/time; `tweak`/`train` = ONLY where buildPaths provides an explicit extension. 2-rung codas are fine. Any agent-added rung must be link-verified live and logged in colophon.html.
- `status`: `"plate"` | `"live"`; timeline cards render an "interactive" chip when live.

### Prose ownership (the central content contract)
**Hard rule: editorial prose lives in HTML at edit time, never injected from JS at runtime.** Two stdlib tools enforce single-sourcing from papers.json:
- `tools/build_timeline.py` — idempotently rewrites ONE marked block `<!-- BEGIN:NODES -->…<!-- END:NODES -->` in index.html containing, in chronological order: act bands, node cards, and gap captions (all from papers.json).
- `tools/build_paper_blocks.py` — idempotently rewrites marked blocks `<!-- BEGIN:HOOK -->`, `<!-- BEGIN:CODA -->`, `<!-- BEGIN:HANDOFF -->` in each `papers/{slug}.html` from papers.json.
- `components.js` handles NON-editorial chrome only: minimap shell injection, copy-citation button wiring, fast-path href swapping. Every JS-touched placeholder has a hard-coded static fallback in HTML (minimum: a "← timeline" anchor).
- Editorial facts come from `research/paperFacts.json` (ideas/artifacts/takeaways/misconceptions/analogies) and `research/buildPaths.json` (codas, build.html). Do not invent facts absent from research or the papers; added claims get cited in colophon.html.

### File structure
```
ml-papers/
  SPEC.md  CHECKPOINTS.md  DESIGN.md  README.md  PAPERS.md  VISUALIZATIONS.md
  research/*.json           ← committed research (content source of truth)
  templates/                ← paper-page templates, NEVER deployed
  spikes/                   ← any live-inference experiment lands here first
  tools/                    ← build_timeline.py, build_paper_blocks.py, check_links.py,
                              inject_meta.py, bump_css.py, validate_papers.py (stdlib);
                              bake_attention.py, bake_cot.py, bake_diffusion_strip.py,
                              bake_paper_figures.py (venv; deps documented in-file)
  .venv/                    ← baker venv (gitignored)
  docs/                     ← THE DEPLOYED SITE
    .nojekyll  index.html  build.html  colophon.html  404.html
    papers.json  prices.json  sitemap.xml  robots.txt  og.png
    css/site.css            ← one stylesheet, ?v=N
    js/  main.js  scroll.js  spine.js  timeline.js  components.js  widgets/{slug}.js
    papers/{slug}.html × 14
    data/{slug}/…           ← baked JSON/webp, ≤3MB per paper dir
    assets/                 ← poster screenshots, committed webp
```

### `docs/prices.json` schema (date-stamped, single source for all $ figures)
```json
{
  "asOf": "2026-07",
  "gpu": { "usdPerHour": 2.50, "range": [1.50, 7.00], "peakFlops": 989e12, "mfu": 0.40,
           "source": "see research/scalingMath.json price anchors" },
  "api": { "model": "<model used for CoT cost estimates>", "inputPerMTok": 0, "outputPerMTok": 0,
           "sourceUrl": "<provider pricing page>", "note": "fetched at CP3; if unreachable, labeled estimates" }
}
```

### `tools/bake_paper_figures.py` (venv)
Produces `docs/data/{slug}/figure.json` for every redrawn data figure (CP1 plates + CP6 scrollies): extracts values from ar5iv HTML/paper tables where tabulated; where only a figure exists (e.g. R1's training curve), traces approximate points and emits `"provenance": "traced, approximate"` — colophon.html surfaces provenance verbatim per figure.

### localStorage contract (binding for build.html, timeline.js, components.js)
- `mlp.ladder.{slug}` = JSON array of checked rung indices. build.html renders one checkbox per rung; a timeline node shows its checkmark when the array is non-empty.
- `mlp.fastpath` = `"1"` when on, absent otherwise.
- No other keys.

### Engineering rules
1. **Widget contract:** each widget exports `async init(panel)` → optionally returns `(stepIndex) => {}`. Lazy boot via IntersectionObserver (`rootMargin: '600px 0px'`) + dynamic `import()`; pre-boot step events buffered; boot failure shows graceful message.
2. **Generation-counter cancellation** in every async widget.
3. **Update-in-place charts**; one rAF write per frame.
4. **Scrollytelling:** `.scrolly > .steps + .sticky`, IntersectionObserver `rootMargin: '-30% 0px -30% 0px'`, activate intersecting step closest to viewport center. Mobile inversion <780px: sticky docks top (≤48svh), tap targets ≥44px.
5. **A11y floor:** WCAG AA; keyboard-operable widgets; `aria-pressed`/`aria-live`; `prefers-reduced-motion` handled in CSS AND JS.
6. **Asset budget:** ≤3MB per `data/{slug}/`; site total <15MB; webp only.
7. **Cache busting:** `site.css?v=N` via `tools/bump_css.py`.
8. **CI:** one GitHub Action running check_links.py on push.
9. **No external JS dependencies.** Hand-rolled canvas/SVG charts (port dogs-vs-cats `draw()`). Google Fonts with preconnect.
10. **Minimap ownership:** components.js injects the placeholder shell (static fallback: "← timeline" link), then calls spine.js's exported `renderMinimap(el, currentSlug)`.

---

## 3. Design system (locked at CP0 in DESIGN.md; constraints binding)

Third sibling: taylor-transformer = warm amber "learns to write"; dogs-vs-cats = cool cyan "learns to see"; **ml-papers = dark graphite "how we got here"** — same structural DNA (dark scrollytelling, sticky panels, mono kickers, panel recipe, feTurbulence grain, footer cross-links).

- **Color logic:** chronology owns position; **category owns color** — five accent quads (base/deep/light/gradient) via `body[data-cat]` remap (interactive-explainers pattern). Acts own only era bands + gap captions. Every accent-on-ground pair passes WCAG AA.
- **Type: exactly three families** — one display serif, Inter (narration/UI), one mono (data/labels/kickers).
- **Paper chips (signature device):** cream light-on-dark inverted card whenever *the paper speaks* — citation headers, attributed quotes, redrawn-figure captions. System serif stack (Charter/Georgia). Mono arXiv-ID tab.
- Numbers get engineering suffixes everywhere (91M, 1.4T, $2.6k).

---

## 4. index.html — the timeline spine

A reader who only scrolls index.html gets the full 13-year story in ~6 minutes — **both jobs, not just job #1**:
- **Hero:** the hook line ("Thirteen years of AI, drawn as a single descending loss curve") PLUS the participation deck sentence: *"Every one of these is reproducible this weekend for under $30 — each page shows you how."* Both carry into the OG description.
- **The loss-curve conceit:** the rail is one continuous descending SVG curve — history as a training run — 2012 high → 2025 low, past deepseek-r1 to the **15th node**, which is unlabeled at rest but reveals its caption **"2026: you"** on approach (scroll-reach) and links to build.html. Footer also links build.html explicitly.
- **spine.js:** path generated from measured node DOM positions (ResizeObserver + `document.fonts.ready`), never hardcoded; scroll drives `stroke-dashoffset`; one rAF write/frame; `prefers-reduced-motion`/perf fallback renders the curve fully drawn and static; heights reserved pre-boot (no layout shift). <780px: curve moves to a left rail (git-graph idiom), `--time-scale` halved.
- **Time-proportional node spacing** (capped) — the 2021–22 pileup and 2023–24 gap are physically felt.
- **Node cards** (static, baked): year + nickname + hook + consequence + minutes chip + **buildChip** ("build it: $0 · one evening") + category accent + "interactive" chip when live + ladder checkmark (via timeline.js from `mlp.ladder.*`).
- **Fast-path toggle** ("Only have 20 minutes?"): highlights transformer → scaling-laws → rlhf; sets `mlp.fastpath`. Re-routing: transformer prev → index; transformer next → scaling-laws; scaling-laws next → rlhf; **rlhf next → build.html**. All other pages unchanged.
- Footer: sibling banner ("want the practice, not the history?" → interactive-explainers), **build.html**, GitHub, colophon.

---

## 5. Paper page anatomy (rigid, identical on all 14)

```
minimap (spine.renderMinimap, current node lit; static fallback "← timeline")
→ paper-chip citation header (title, authorsShort, venue, source-labeled link, copy-citation)
→ HOOK block (baked from papers.json)
→ THE AHA (within one scroll): the ONE artifact, redrawn from data (bake_paper_figures.py
   where data-driven), with its plain reading
→ what-it-changed (builder takeaway, present tense)
→ honest-limits (misconception corrected + where the idea breaks)
→ BUILD CODA (baked from papers.json; cites own repos where flagged in buildPaths.json:
   alexnet→dogs-vs-cats, transformer→tiny-llm-pipeline + taylor-transformer,
   gpt2→tiny-llm-pipeline, rlhf→tiny-llm-pipeline SFT/DPO, lora→taylor-lstm callback)
→ cliffhanger handoff (baked; static HTML; fast-path aware via components.js).
   deepseek-r1's next handoff ALWAYS points to build.html with closing-argument copy
   ("the moat is shallow → 2026: you") — there is no next paper; never wrap to alexnet.
```
Tiers: **plate** = anatomy above with static redrawn artifact (FINAL for alexnet, resnet, clip, lora). **scrolly** = AHA + what-it-changed become a 3–6 step pinned-visual sequence. **widget** = scrolly with an interactive widget as the pinned visual.

---

## 6. Widget specs (Tier 1) — each names its break-it affordance

### 6a. scaling-laws — THE FLAGSHIP. Build exactly to `research/scalingMath.json`.
**One-equation exception:** the displayed AHA artifact is Kaplan's Figure-1 straight lines (L(N)=(Nc/N)^0.076 as the caption); the Chinchilla parametric form is the widget's *engine*, surfaced in the advanced panel/caveats with one bridging sentence in prose: "the widget runs the 2022-corrected constants — the caveats drawer explains why."
- **Mode A "Spend the budget"** (default): log-slider C (1e18–1e27 FLOPs) + linked $ readout. `Nopt=√(C/120)`, `Dopt=20·Nopt`, `loss=1.69+406.4/Nopt^0.34+410.7/Dopt^0.28`, `usd=C·price/(989e12·MFU·3600)`. Readouts: N_opt, D_opt, loss, $, capability-vintage ("≈ GPT-2, 2019"), $ odometer, verdict line.
- **Verdict line (exact logic + strings):** R = C / 3.8e25 (newest anchor, Llama 3.1 405B).
  - R < 1e-4 → "Weekend territory — nanoGPT scale. Perfect for learning; nobody trains products here."
  - 1e-4 ≤ R < 1 → "A frontier lab has already passed this point. 'Wait for the next model' beats building this yourself — unless your edge is proprietary data or post-training."
  - R ≥ 1 → "You're at the frontier. Nobody is ahead of you to wait for — differentiation here is data, post-training, and product."
- **Mode B "Allocate it yourself":** sliders N (1e7–1e13), D (1e9–1e15); shows C=6ND, your loss vs optimal at same C, tokens/param vs ~20. **Break-it affordance: the "GPT-3's mistake" preset** (N=175e9, D=300e9 → 2.002 vs Chinchilla 70B/1.4T → 1.937 at equal compute) — the reader personally makes OpenAI's 2020 allocation error and watches a smaller model beat it.
- **Plot:** log-scaled x (C, 1e17–1e27) with secondary $ axis, **LINEAR y** (loss 1.6–4.0), dashed asymptote at E=1.69 "irreducible entropy of text". Chinchilla-optimal frontier; 5 anchors (GPT-2, GPT-3 above frontier, Chinchilla on it, GPT-4 est., Llama 3.1 405B slightly above, annotated). **GPT-2 anchor: C=1.5e21 with D_effective=C/(6N)≈167B tokens for the loss coordinate** (epochs = effective tokens; note in caveats). Shade extrapolation beyond ~1e24.
- **Advanced panel:** price slider $1.50–$7 (default $2.50), MFU 20–50% (default 40%), **Hoffmann↔Epoch-refit toggle** — swaps A/B/E/α/β EVERYWHERE (readouts, Mode B deltas, frontier loss values, asymptote line+label moves to 1.82); frontier allocation stays Nopt=√(C/120) in both modes. "Prices as of" stamp from prices.json.
- **Caveats drawer:** all 10 caveats from research, verbatim-adapted.
- **Sanity asserts** (`console.assert`, run unconditionally at widget init, evaluated with Hoffmann constants): L(70e9,1.4e12)≈1.937 ±0.01, L(175e9,300e9)≈2.002 ±0.01, C=5.76e23→N_opt≈69.3e9 ±1e9. A failed assert = console error = caught by the no-console-errors AC.

### 6b. cot — side-by-side with a cost meter
**Primary content path (no API key exists — binding):** hand-authored from the paper's own published exemplars and appendix outputs (Wei et al. arXiv 2201.11903 appendix has full problem/response pairs for both conditions). Token counts computed offline with the GPT-2 tokenizer in the CP0 venv. Provenance labeled in the widget UI footer + colophon: "responses reproduced from the paper; costs are estimates at 2026 API prices." An API bake is an optional enhancement ONLY behind an env-var check at CP3 start, named model, ~$1 cap.
- Two panes: "answer directly" vs few-shot CoT (Roger's tennis balls exemplar verbatim). Token + cost meters recompute from prices.json (API prices fetched from the provider's public pricing page at CP3; source URL + date recorded; if unreachable, labeled estimates).
- Headline: PaLM 540B GSM8K **17.9% → 56.9%**, same weights, only the prompt changed.
- **Break-it affordance: a third pane/toggle — "try it on a small model"** — fluent-but-wrong reasoning reproduced from the paper's appendix sub-threshold examples, honestly labeled, making the ~100B emergence threshold interactive ("scratch paper only helps someone who already knows how to multiply").
- Honest-limits: below threshold CoT can hurt; printed reasoning ≠ faithful introspection.

### 6c. transformer — attention arcs
- Primary: SVG arcs over token chips; heatmap toggle; ~8 curated sentences each with a "why this sentence" note. Data baked by `tools/bake_attention.py` (venv: GPT-2 small via HF transformers; curated sentences only; quantized weights; ≤3MB).
- **Break-it affordance: 1–2 of the 8 sentences are designed failure cases** (e.g. a long-range dependency where GPT-2-small's attention visibly diffuses), with "why this breaks" notes.
- **Fallback variant** (last resort, only if the venv bake fails): bake from the local taylor-transformer char-level ONNX model; the widget becomes "attention over characters" with adjusted examples (previous-token heads, word-boundary attention, repeated-motif lookback), adjusted notes, and a paper-chip note explaining the substitution. Fallback AC: a designated character-level pattern (word-boundary head) is visibly correct.
- Below the widget: click-to-activate iframe facade of **Polo Club Transformer Explainer** (MIT; ≥1200px gate; attribution; committed poster) + screenshot-teaser link-out card to **bbycroft.net/llm** (NO iframe, NO fork — unlicensed).

### 6d. stable-diffusion — forward-process scrubber + embed
- **Scrubber:** timestep slider over baked webp strips — `tools/bake_diffusion_strip.py` (venv: numpy+Pillow), forward-noising with linear β schedule 1e-4→0.02, T=1000, ~12 evenly-spaced frames, ≤3MB total, **2 seeds baked**. Source image: NASA "Blue Marble" (Apollo 17 Earth photo, public domain, https://commons.wikimedia.org/wiki/File:The_Earth_seen_from_Apollo_17.jpg), credited in colophon; fallback: a frame the author owns from video-editing-experiment/, credited "author's own."
- Latent-vs-pixel toggle: 64×64×4 = 16,384 numbers vs 512×512×3 = 786,432 — "~48× less work on every one of ~50 denoising steps."
- **Break-it affordance: "shuffle the noise" button** — swaps to the second baked seed: same image, completely different noise at every t — the information is *destroyed*, not hidden; generation starts from exactly this. Kills the collage myth interactively.
- Reverse process: click-to-activate **Polo Club Diffusion Explainer** iframe (MIT; ≥1200px gate; link-out on mobile).

### Embed policy (binding, from research/embeds.json)
Polo Club: iframe with click-to-activate poster facade (committed webp screenshot), visible attribution + source link, `title`/`allow="fullscreen"`/`referrerpolicy`, ≥1200px gate, link-out fallback. bbycroft: teaser card + link out ONLY. Poster capture mechanism: CHECKPOINTS CP4/CP5 (headless browser, wait conditions, README-asset fallback).

---

## 7. build.html — "2026: you" + the participation ladder

Content from `research/buildPaths.json`. Visible section stamp: **"checked July 2026"** (like prices.json — decay is honest, not silent).
- **The ladder** — all 14 codas as one ascending ladder, checkbox per rung (localStorage contract §2), grouped by layer of the stack (full mapping, binding): **see it** (alexnet, resnet, clip) → **build it** (transformer, moe) → **scale it** (gpt2, scaling-laws, gpt3) → **shape it** (rlhf, constitutional-ai, lora, cot) → **generate & reason** (stable-diffusion, deepseek-r1). Checkmarks surface on timeline nodes.
- **Where to contribute now:** vLLM, llama.cpp, lm-evaluation-harness (flagged most accessible), diffusers, open-r1, Axolotl — with what contributions look like.
- **Communities:** EleutherAI + SOAR presented as a recurring program WITHOUT cohort dates ("runs mentored cohorts for people with no research experience — watch eleuther.ai/soar"), GPU MODE, HF, Cohere Labs, LAION, ARENA/mech-interp, r/LocalLLaMA.
- **The jobs reality** (Epoch AI, Mar 2026, cited): research = 12%/7% of Anthropic/OpenAI openings; customer-adoption engineering doubled; FDE/Solutions/Applied-AI roles need exactly what the ladder teaches. Closing line: *"The scarce skill isn't inventing the next transformer — it's having actually trained, aligned, evaluated, and served a model at any scale."*

## 8. colophon.html + 404
Colophon: redrawn-figure policy + per-figure provenance (incl. "traced, approximate" flags), baked-JSON provenance (which baker, which model, when), embed attributions/licenses, prices.json + build.html date stamps, CC0/PD image credits, design system in brief, curation story (link PAPERS.md cut list). 404: "a node that fell off the curve."

---

## 9. Verification requirements
- `check_links.py` passes; papers.json passes validate_papers.py; **build_timeline.py AND build_paper_blocks.py idempotent** (run twice → no diff).
- Local server + screenshot review at 1440/768/390px — **scoped to pages changed in the checkpoint**; full 17-page sweep only at CP1a-deploy and CP8.
- Scaling-law sanity asserts pass (§6a; Hoffmann constants).
- JS disabled: index and every paper page fully readable, nav works.
- Zero console errors on any page.

## 10. Cut lines / v2 (parked)
Live ONNX inference (spike-gated); per-paper OG cards; spine temperature ramp; theme toggle; search; wiki/lint layer. **Pre-authorized schedule cuts are in CHECKPOINTS.md (execution contract) — shedding them is spec-compliant, not failure.**

## 11. Risks & mitigations
- **Spine SVG jank:** measure-from-DOM only, static fallback, svh units, reduced-motion path; if it fights, ship the static-drawn curve.
- **Attention bake >3MB:** curated sentences only, hand-picked layer×head selection, quantized uint8 weights.
- **Editorial drift:** papers.json is the only home of hooks/cliffhangers/codas; build_timeline.py + build_paper_blocks.py are the only writers; components.js never carries prose.
- **Embed upstream changes:** committed posters + link-out fallbacks.
- **Toolchain walls:** environment section (§2) front-loads every dependency to CP0 with a smoke-test AC.
