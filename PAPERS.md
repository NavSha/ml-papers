# The Final 14 — what every engineer, technical PM, and founder should know

The lens: not "what shaped AI history," but "what changes how you build, prioritize, or place bets *today*."

## The foundations

1. **AlexNet** — "ImageNet Classification with Deep Convolutional Neural Networks" (Krizhevsky, Sutskever & Hinton, 2012) — [paper](https://papers.nips.cc/paper/4824-imagenet-classification-with-deep-convolutional-neural-networks)
   Origin story; the durable lesson: general methods + compute beat clever engineering.
2. **ResNet** — "Deep Residual Learning for Image Recognition" (He et al., 2015) — [arXiv:1512.03385](https://arxiv.org/abs/1512.03385)
   Residual connections; why we can train very deep nets — skip connections sit in every Transformer block.
3. **Transformer** — "Attention Is All You Need" (Vaswani et al., 2017) — [arXiv:1706.03762](https://arxiv.org/abs/1706.03762)
   The architecture under everything; what a context window is.

## The LLM core

4. **GPT-2** — "Language Models are Unsupervised Multitask Learners" (Radford et al., 2019) — [paper](https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf)
   The core bet: next-token prediction → general capability.
5. **Scaling Laws** — "Scaling Laws for Neural Language Models" (Kaplan et al., 2020) — [arXiv:2001.08361](https://arxiv.org/abs/2001.08361)
   Why billion-dollar runs are rational; "wait for the next model" as strategy.
6. **GPT-3** — "Language Models are Few-Shot Learners" (Brown et al., 2020) — [arXiv:2005.14165](https://arxiv.org/abs/2005.14165)
   In-context learning; why prompting is a real interface.
7. **Mixture-of-Experts** — "Switch Transformers" (Fedus et al., 2021) — [arXiv:2101.03961](https://arxiv.org/abs/2101.03961)
   How frontier models scale affordably; the cost story PMs reason about.

## Making models useful

8. **InstructGPT / RLHF** — "Training language models to follow instructions with human feedback" (Ouyang et al., 2022) — [arXiv:2203.02155](https://arxiv.org/abs/2203.02155)
   Raw model → usable assistant; alignment as a product layer.
9. **Constitutional AI** — "Constitutional AI: Harmlessness from AI Feedback" (Anthropic, 2022) — [arXiv:2212.08073](https://arxiv.org/abs/2212.08073)
   Alignment via explicit principles; why models behave/refuse as they do.
10. **Chain-of-Thought** — "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models" (Wei et al., 2022) — [arXiv:2201.11903](https://arxiv.org/abs/2201.11903)
    Reasoning, inference-time compute, "buy quality with tokens."
11. **DeepSeek-R1** — "Incentivizing Reasoning Capability in LLMs via Reinforcement Learning" (DeepSeek, 2025) — [arXiv:2501.12948](https://arxiv.org/abs/2501.12948)
    Post-training matters as much as pretraining; capability moats are shallower than they look.

## Beyond text

12. **CLIP** — "Learning Transferable Visual Models From Natural Language Supervision" (Radford et al., 2021) — [arXiv:2103.00020](https://arxiv.org/abs/2103.00020)
    Embeddings/shared-space idea; foundation of vector search and RAG.
13. **Stable Diffusion** — "High-Resolution Image Synthesis with Latent Diffusion Models" (Rombach et al., 2022) — [arXiv:2112.10752](https://arxiv.org/abs/2112.10752)
    How generative media works + the open-vs-closed playbook.

## For builders

14. **LoRA** — "LoRA: Low-Rank Adaptation of Large Language Models" (Hu et al., 2021) — [arXiv:2106.09685](https://arxiv.org/abs/2106.09685)
    Cheap, modular customization; bread-and-butter for fine-tuning.

---

The arc the 14 tell: **vision breakthrough → architecture → scale → alignment → reasoning.**

If someone only has time for three: **Transformer, Scaling Laws, RLHF** — architecture, economics, and product. Those three explain ~80% of every strategic AI decision being made right now.

## Consider later (parked, not dropped)

- **PPO** (Schulman et al., 2017) — the RL engine inside RLHF; dropped as plumbing since RLHF represents the idea
- **AdamW** — "Decoupled Weight Decay Regularization" (Loshchilov & Hutter, 2017) — the optimizer that actually trains today's LLMs
- **LayerNorm** (Ba, Kiros & Hinton, 2016) / **RMSNorm** (Zhang & Sennrich, 2019) — the normalization actually in use
- Possible future companion: a five-question "how training happens" primer for engineers (loss → AdamW → norms/residuals → regularization → scaling)

## Cut and why (from the fuller 20-keeper list)

Kept during the paper-by-paper pass but cut by the engineer/PM/founder lens — real history, lesson absorbed elsewhere:

- **ImageNet** (2009) — "data is the benchmark" lesson is history, not working knowledge
- **word2vec** (2013) — embeddings idea lives on via CLIP
- **GANs** (2014) — displaced by diffusion
- **seq2seq** (2014) — absorbed into the Transformer story
- **Adam** (2014), **BatchNorm/Dropout** (2014–15) — training plumbing; see "consider later"
- **ViT** (2020) — unification story covered by CLIP
- **DDPM** (2020) — the invention, but Stable Diffusion carries both the idea and the business lesson

Dropped outright during the pass: VAEs, Bahdanau attention, VGG, DQN, AlphaGo, Hestness scaling, BERT, AlphaFold, Chinchilla, FlashAttention, Llama 2/3.
