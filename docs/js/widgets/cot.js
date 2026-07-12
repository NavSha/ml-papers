/**
 * cot.js — Chain-of-Thought side-by-side with a cost meter (SPEC §6b).
 *
 * Two panes over the same question: "answer directly" (the paper's standard
 * prompting condition) vs "think step by step" (few-shot CoT). Every response
 * text is reproduced verbatim from Wei et al. arXiv 2201.11903 (baked by
 * tools/bake_cot.py, GPT-2 token counts computed offline); costs are
 * ESTIMATES computed from docs/prices.json at 2026 API prices.
 *
 * Break-it affordance (binding): "try it on a small model" — PaLM 62B's
 * fluent-but-wrong chains from the paper's Appendix A.1, making the ~100B
 * emergence threshold interactive.
 */

let gen = 0; // generation counter — cancels stale async inits

const fmtUsd = (n) => (n >= 100 ? '$' + Math.round(n) : n >= 1 ? '$' + n.toFixed(2) : '$' + n.toFixed(3));

export async function init(panel) {
  const g = ++gen;
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  let prices = { asOf: '2026-07', api: { model: 'Claude Opus 4.8', inputPerMTok: 5, outputPerMTok: 25, note: 'estimates' } };
  try {
    const p = await (await fetch('../prices.json')).json();
    if (p && p.api && p.api.outputPerMTok) prices = p;
  } catch { /* defaults hold — clearly labeled estimates either way */ }
  const data = await (await fetch('../data/cot/cases.json')).json();
  if (g !== gen) return; // a newer init owns the panel

  const api = prices.api;
  const perKCalls = (tokens) => tokens * api.outputPerMTok / 1000; // $ per 1,000 calls, output tokens
  const maxTok = Math.max(...data.cases.map((c) => Math.max(c.direct.tokens, c.cot.tokens)));

  panel.innerHTML = `
    <div class="widget-head">
      <p class="kicker"><span class="cat">chain-of-thought</span> · same weights, two prompts</p>
      <span class="status-chip">est. at 2026 api prices</span>
    </div>

    <p class="cot-headline" aria-label="GSM8K accuracy ${data.headline.before} percent with standard prompting, ${data.headline.after} percent with chain-of-thought">
      <span class="num cot-before">${data.headline.before}%</span><span class="cot-arrow">→</span><span class="num cot-after">${data.headline.after}%</span>
    </p>
    <p class="cot-headline-sub">${data.headline.model} on ${data.headline.bench} — same weights, only the prompt changed.</p>

    <figure class="paper-chip cot-exemplar">
      <blockquote class="chip-quote">Q: ${data.exemplar.q}<br>A: ${data.exemplar.cot.text}</blockquote>
      <figcaption class="chip-caption">${data.exemplar.src} — this worked example IS the entire intervention: paste it above the question and the model imitates the scratch work.</figcaption>
    </figure>

    <div class="widget-tabs" role="group" aria-label="pick a problem" data-cases></div>

    <p class="widget-readouts" style="margin-bottom:0" data-question aria-live="polite"></p>

    <div class="cot-panes">
      <article class="cot-pane" data-pane="direct">
        <div class="cot-pane-head">
          <span class="readout-label">answer directly</span>
          <span data-badge="direct"></span>
        </div>
        <p class="cot-response" data-text="direct"></p>
        <div class="bar cot-meter" aria-hidden="true"><div class="bar-fill" data-fill="direct" style="width:0%"></div></div>
        <p class="readout-label" data-meter="direct" aria-live="polite"></p>
      </article>
      <article class="cot-pane" data-pane="cot">
        <div class="cot-pane-head">
          <span class="readout-label">think step by step</span>
          <span data-badge="cot"></span>
        </div>
        <p class="cot-response" data-text="cot"></p>
        <div class="bar cot-meter" aria-hidden="true"><div class="bar-fill" data-fill="cot" style="width:0%"></div></div>
        <p class="readout-label" data-meter="cot" aria-live="polite"></p>
      </article>
    </div>
    <p class="cot-framing" data-framing></p>
    <p class="breakit-note">costs are estimates at 2026 API prices (${api.model}, $${api.outputPerMTok}/MTok output${api.note === 'estimates' ? ', estimated rates' : ''}) — response tokens only, counted with the GPT-2 tokenizer.</p>

    <div class="breakit">
      <p class="kicker breakit-kicker">break it</p>
      <button class="btn-primary" type="button" data-breakit-btn aria-expanded="false">try it on a small model</button>
      <div data-breakit-body hidden></div>
    </div>

    <p class="provenance-line">${data.provenance} — Wei et al. (2022), NeurIPS 2022. Exemplar: Figure 1; problems: Figure 1 + Table 20 (Appendix G); small-model failures: Figure 10 (Appendix A.1). Direct-condition text follows the paper's standard-prompting format (final answer only).</p>`;

  const $ = (sel) => panel.querySelector(sel);
  const els = {
    tabs: $('[data-cases]'),
    question: $('[data-question]'),
    panes: { direct: $('[data-pane="direct"]'), cot: $('[data-pane="cot"]') },
    text: { direct: $('[data-text="direct"]'), cot: $('[data-text="cot"]') },
    fill: { direct: $('[data-fill="direct"]'), cot: $('[data-fill="cot"]') },
    meter: { direct: $('[data-meter="direct"]'), cot: $('[data-meter="cot"]') },
    badge: { direct: $('[data-badge="direct"]'), cot: $('[data-badge="cot"]') },
    framing: $('[data-framing]'),
    breakBtn: $('[data-breakit-btn]'),
    breakBody: $('[data-breakit-body]'),
  };

  /* case selector chips — native buttons, keyboard operable */
  const label = (c) => c.q.split(/[.,?]/)[0].split(' ').slice(0, 4).join(' ').toLowerCase();
  data.cases.forEach((c, i) => {
    const b = document.createElement('button');
    b.className = 'chip';
    b.type = 'button';
    b.textContent = label(c);
    b.setAttribute('aria-pressed', String(i === 0));
    b.addEventListener('click', () => { current = i; syncTabs(); render(); });
    els.tabs.appendChild(b);
  });
  const syncTabs = () => [...els.tabs.children].forEach((b, i) => b.setAttribute('aria-pressed', String(i === current)));

  let current = 0;
  let raf = 0;

  const paneUpdate = (side, c) => {
    const d = c[side];
    els.text[side].textContent = d.text;
    els.fill[side].style.width = Math.round(100 * d.tokens / maxTok) + '%';
    els.meter[side].textContent = `${d.tokens} tokens · ${fmtUsd(perKCalls(d.tokens))} per 1k calls`;
    els.badge[side].className = d.correct ? 'badge-ok' : 'badge-err';
    els.badge[side].textContent = d.correct ? '✓ correct' : '✗ wrong';
  };

  const render = () => {
    cancelAnimationFrame(raf);
    raf = requestAnimationFrame(() => { // one rAF write per frame
      const c = data.cases[current];
      els.question.textContent = 'Q: ' + c.q;
      paneUpdate('direct', c);
      paneUpdate('cot', c);
      const x = (c.cot.tokens / c.direct.tokens).toFixed(1);
      els.framing.textContent = c.direct.correct
        ? `one of the paper's own prompt exemplars — both correct as written; the chain costs ~${x}× the output tokens, and the payoff shows up on held-out problems: ${data.headline.before}% → ${data.headline.after}%.`
        : `same model, same question: the bare answer is wrong; the ~${x}×-longer worked chain is right. That trade is the whole paper.`;
    });
  };

  /* break-it pane — PaLM 62B's fluent-but-wrong chains, honestly labeled */
  let breakBuilt = false;
  const buildBreakit = () => {
    if (breakBuilt) return;
    breakBuilt = true;
    els.breakBody.innerHTML = data.breakit.map((b) => `
      <div class="cot-breakit-case">
        <p class="readout-label">${b.model} · same CoT prompt</p>
        <p class="widget-readouts" style="margin:6px 0">Q: ${b.q}</p>
        <p class="cot-response">${b.text}</p>
        <p class="readout-label">${b.tokens} tokens of fluent scratch work · ${fmtUsd(perKCalls(b.tokens))} per 1k calls — spent on a wrong answer</p>
        <p class="breakit-verdict">${b.error}</p>
      </div>`).join('') + `
      <p class="breakit-note">Below ~100B parameters, chain-of-thought can HURT accuracy: scratch paper only
        helps someone who already knows how to multiply. (${data.breakit[0].src})</p>`;
  };
  const openBreakit = (open) => {
    buildBreakit();
    els.breakBody.hidden = !open;
    els.breakBtn.setAttribute('aria-expanded', String(open));
    els.breakBtn.textContent = open ? 'hide the small model' : 'try it on a small model';
  };
  els.breakBtn.addEventListener('click', () => openBreakit(els.breakBody.hidden));

  const emphasize = (side) => {
    for (const s of ['direct', 'cot']) {
      els.panes[s].classList.toggle('is-hot', s === side);
      els.panes[s].classList.toggle('is-dim', side !== null && s !== side);
    }
  };

  render();

  /* scroll-driven story beats (widget-tier scrolly contract) */
  return (stepIndex) => {
    if (stepIndex === 0) emphasize('direct');
    if (stepIndex === 1) emphasize('cot');
    if (stepIndex === 2) {
      emphasize(null);
      if (!reduced) { // replay the meter fill so the cost gap reads; reduced-motion keeps final state
        for (const s of ['direct', 'cot']) {
          const w = els.fill[s].style.width;
          els.fill[s].style.width = '0%';
          requestAnimationFrame(() => requestAnimationFrame(() => { els.fill[s].style.width = w; }));
        }
      }
    }
    if (stepIndex >= 3) openBreakit(true);
  };
}
