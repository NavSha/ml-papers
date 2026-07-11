# Best Existing Visualizations & Explainers — the bar to beat

Research from June 20, 2026 session: what's out there, what makes the best ones work, and the format plan for making our 14 papers accessible to technical PMs, founders, and engineers.

## The gold standard

**The all-time greats:**
- [The Illustrated Transformer](https://jalammar.github.io/illustrated-transformer/) (Jay Alammar) — the single most influential explainer ever made; taught at Stanford, MIT, Harvard, CMU. Also his [Illustrated GPT-2](https://jalammar.github.io/illustrated-gpt2/) and [seq2seq with attention](https://jalammar.github.io/visualizing-neural-machine-translation-mechanics-of-seq2seq-models-with-attention/). *Lesson: progressive disclosure — one concept per diagram, build up slowly.*
- [3Blue1Brown — Attention in transformers, visually explained](https://www.3blue1brown.com/lessons/attention/) (Grant Sanderson) — the clearest video explanation of attention anywhere. *Lesson: animate the actual math, with a strong narrative spine.*
- [Distill.pub](https://distill.pub/) — proved interactive, reactive diagrams (hover to change the model's behavior) teach better than static text. Archived, but still the design north star.

**Interactive, run-it-yourself tools (closest to what we'd build):**
- [Transformer Explainer](https://poloclub.github.io/transformer-explainer/) (Georgia Tech Polo Club) — live GPT-2 in the browser; type text, watch attention weights and next-token probabilities update, temperature slider. Svelte + D3 + ONNX. Open source.
- [Diffusion Explainer](https://poloclub.github.io/diffusion-explainer/) (same lab) — step through how a prompt becomes an image, timestep by timestep. Open source.
- [LLM Visualization](https://bbycroft.net/llm) (Brendan Bycroft) — stunning 3D walkthrough of every matrix multiply in a GPT, scrollable end to end.

**The mainstream-media benchmark:**
- [FT: "Generative AI exists because of the transformer"](https://ig.ft.com/generative-ai/) — proof this can reach a completely non-technical audience via scrollytelling. Closest reference for the PM/founder audience specifically.

## What the best ones have in common

1. **One idea per screen**, revealed progressively — never the whole architecture at once.
2. **A concrete running example** the reader can change ("type your sentence," "drag this slider").
3. **A strong analogy** that's honest, not cute (attention = "looking back at relevant words while writing the next one").
4. **"Why it matters" framing up front**, mechanics second.
5. **Scrollytelling** — the visual is pinned, the text scrolls and drives it.

## Format plan for our 14 — tiered

**Tier 1 — Build interactive widgets** (where interactivity unlocks real intuition):
- **Transformer / Attention** → "watch attention light up": type a sentence, hover a word, see what it attends to. (Or embed Transformer Explainer.)
- **Scaling Laws** → slider toy: drag compute/data/params, watch the loss curve drop on a log-log plot, with live "$ cost" and "capability" readouts. *The one that lands hardest with founders.*
- **Chain-of-Thought** → side-by-side: same hard question, "answer directly" vs. "think step by step," with a token-count + cost meter. Makes "buy quality with tokens" visceral.
- **Stable Diffusion** → denoising scrubber: drag the timestep, watch noise resolve into an image. (Or embed Diffusion Explainer.)

**Tier 2 — Scrollytelling explainers** (strategy stories, not mechanisms):
- GPT-2, GPT-3, RLHF, Constitutional AI, Mixture-of-Experts, DeepSeek-R1 — pinned diagram + scrolling narrative + a "why this changed the industry" callout.

**Tier 3 — Card / timeline format** (the foundations):
- AlexNet, ResNet, CLIP, LoRA — one rich card each: the problem, the one key idea (single diagram), the lesson that outlived it.

**The unifying frame:** a scrollable **timeline from 2012 → 2025** where each paper is a node; clicking a node opens its card/widget. The spine makes the reader *feel* the arc: vision breakthrough → architecture → scale → alignment → reasoning.

## Recommended build order

1. **Flagship interactive first: the Scaling Laws slider** — highest "aha per pixel" for a PM/founder audience; nobody has done a great founder-framed version.
2. **Timeline shell** as the navigation spine.
3. **Tier 2/3 as scroll + cards**, embedding the open-source Polo Club tools rather than rebuilding Transformer/Diffusion explainers.
