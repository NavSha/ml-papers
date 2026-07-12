# The Fourteen — ml-papers

**Live site: https://navsha.github.io/ml-papers/**

Thirteen years of AI, drawn as a single descending loss curve — the 14 papers every
engineer, technical PM, and founder should know, each explained to one aha and each
ending with a verified, priced "build this yourself" path. The timeline ends at the
15th node: [2026: you](https://navsha.github.io/ml-papers/build.html) — the
participation ladder into open-source AI and AI-adjacent careers.

The curation lens (see [PAPERS.md](PAPERS.md)): not "what shaped AI history," but
*what changes how you build, prioritize, or place bets today.*

## The fourteen

| year | paper | the hook |
|------|-------|----------|
| 2012 | **AlexNet** | Two gaming GPUs beat a decade of hand-built vision — by ten points, in a contest where progress was measured in one. |
| 2015 | **ResNet** | A 56-layer network was losing to its own 20-layer version — until two characters of algebra, `+ x`, made 152 layers trainable. |
| 2017 | **Transformer** | Eight GPUs, 3.5 days, one equation — and the record fell to an architecture that deleted reading-in-order. |
| 2019 | **GPT-2** | One dumb objective on 40GB of web text — and translation, summarization, and QA emerged unasked. |
| 2020 | **Scaling Laws** | Loss falls as a ruler-straight power law for eight orders of magnitude — capability became purchasable. *(the flagship interactive)* |
| 2020 | **GPT-3** | At 175B parameters, examples in the prompt started working like training — with zero weight updates. |
| 2021 | **MoE / Switch** | A router sends each token to one expert — parameters grow 100×, cost per token doesn't. |
| 2021 | **CLIP** | 400M image–caption pairs, one shared space — classification became retrieval, and vector search was born. |
| 2021 | **LoRA** | Fine-tuning GPT-3: a 350GB checkpoint per task — or a 35MB file that matches it. |
| 2021 | **Stable Diffusion** | Denoise in a space 48× smaller and generative imagery lands on consumer GPUs — then the weights shipped open. |
| 2022 | **Chain-of-Thought** | Same model, same weights: 17.9% → 56.9% on math — the only thing that changed was the prompt. |
| 2022 | **InstructGPT / RLHF** | Human labelers preferred a 1.3B model over 175B GPT-3 — quality as you experience it is post-training. |
| 2022 | **Constitutional AI** | 16 plain-English principles replaced tens of thousands of human labels — and the model got less harmful without refusing more. |
| 2025 | **DeepSeek-R1** | Reward only "the answer is correct" and reasoning emerges — then the weights shipped, and the moat was months. |

## Architecture

Zero-build static site: plain HTML + one CSS file + native ES modules. No framework,
no bundler — `git push` to `main` deploys `docs/` via GitHub Pages.

- `docs/papers.json` — single source of truth for all editorial prose (hooks,
  cliffhangers, codas, act copy). Baked into HTML at edit time by stdlib tools —
  every page is fully readable with JS disabled.
- `docs/js/spine.js` — the descending loss curve, drawn from measured DOM positions.
- `docs/js/widgets/` — one module per interactive paper (scaling-laws, transformer
  attention, chain-of-thought, stable-diffusion, plus the scrolly charts). All data
  is baked offline; no live inference, no external JS.
- `docs/data/` — baked widget data with provenance (`manifest.json` / `figure.json`
  per paper; "traced, approximate" flagged where values were read off a printed
  figure — see the [colophon](https://navsha.github.io/ml-papers/colophon.html)).
- `DESIGN.md` — the design system (dark graphite, five category accent quads, cream
  "paper-chips" whenever the paper itself speaks). Read it before any visual change.
- `SPEC.md` / `CHECKPOINTS.md` — the build contract this site was constructed from.

## Rebuilding assets

```bash
# editorial rebake (stdlib python)
python3 tools/build_timeline.py       # index node cards from papers.json
python3 tools/build_paper_blocks.py   # hooks/codas/handoffs into paper pages
python3 tools/build_ladder.py         # the build.html ladder
python3 tools/inject_meta.py          # OG/Twitter meta
python3 tools/check_links.py          # internal link check (also runs in CI)

# widget data (project venv: uv venv --python 3.11 .venv && uv pip install
#   --python .venv/bin/python torch transformers numpy pillow)
.venv/bin/python tools/bake_attention.py        # GPT-2 attention for the arcs widget
.venv/bin/python tools/bake_cot.py              # CoT cases verbatim from the paper
.venv/bin/python tools/bake_diffusion_strip.py  # forward-diffusion webp strips
.venv/bin/python tools/bake_paper_figures.py    # scrolly chart data + provenance
```

## Siblings

- [taylor-transformer](https://navsha.github.io/taylor-transformer/) — how a language model writes
- [dogs-vs-cats](https://navsha.github.io/dogs-vs-cats/) — how a machine learns to see
- [interactive-explainers](https://navsha.github.io/interactive-explainers/) — AI for PMs: the practice, not the history
  *(TODO: add a reciprocal ml-papers card on the explainers homepage — tracked, other repo)*

Curated and built in Claude Code sessions, June–July 2026. Figure provenance,
licenses, and the keep/drop record: [colophon](https://navsha.github.io/ml-papers/colophon.html) · [PAPERS.md](PAPERS.md).
