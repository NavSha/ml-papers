/**
 * transformer.js — attention, running for real (SPEC §6c).
 * Draws the actual attention weights of GPT-2 small (baked offline) as arcs
 * over the token chips: hover/focus any token to see what it attends to.
 * A heatmap toggle shows the full T×T grid. One sentence is a genuine
 * failure case (Winograd coreference the small model can't resolve).
 */
const SVG = 'http://www.w3.org/2000/svg';

export async function init(panel) {
  let data;
  try { data = await (await fetch('../data/transformer/attention.json')).json(); }
  catch { throw new Error('could not load attention data'); }

  const sents = data.sentences;
  panel.innerHTML = `
    <div class="widget-head">
      <p class="kicker"><span class="cat">attention, for real</span> · GPT-2 small</p>
      <span class="status-chip status-chip--live">live</span>
    </div>
    <div class="attn-chips" data-sel role="tablist" aria-label="Example sentences"></div>
    <div class="attn-stage">
      <svg class="attn-arcs" data-arcs role="img" aria-label="Attention arcs from the focused token to the tokens it attends to"></svg>
      <div class="attn-tokens" data-tokens></div>
      <table class="attn-heat" data-heat hidden></table>
    </div>
    <div class="attn-controls">
      <button class="chip" data-heattoggle type="button" aria-pressed="false">show the grid</button>
      <span class="attn-foot num" data-foot></span>
    </div>
    <p class="breakit-note" data-note></p>`;

  const selEl = panel.querySelector('[data-sel]');
  const arcs = panel.querySelector('[data-arcs]');
  const tokensEl = panel.querySelector('[data-tokens]');
  const heatEl = panel.querySelector('[data-heat]');
  const note = panel.querySelector('[data-note]');
  const foot = panel.querySelector('[data-foot]');
  const heatToggle = panel.querySelector('[data-heattoggle]');

  let cur = 0, focusTok = 0, heat = false;

  sents.forEach((s, i) => {
    const b = document.createElement('button');
    b.className = 'chip attn-pick' + (s.holds === false || s.fail ? ' attn-pick--breaks' : '');
    b.type = 'button';
    b.textContent = (s.holds === false || s.fail ? '⚠ ' : '') + shortLabel(s);
    b.setAttribute('role', 'tab');
    b.addEventListener('click', () => selectSentence(i));
    selEl.appendChild(b);
  });

  function shortLabel(s) {
    return (s.why || s.text).split(/[:—]/)[0].trim().slice(0, 22);
  }

  function selectSentence(i) {
    cur = i;
    const s = sents[i];
    focusTok = s.expect?.from ?? 0;
    [...selEl.children].forEach((c, j) => c.setAttribute('aria-selected', String(j === i)));
    renderTokens();
    renderHeat();
    draw();
    note.textContent = (s.holds === false || s.fail)
      ? 'Why this breaks: ' + (s.note || 'the small model can’t resolve this dependency — its best head spreads its attention instead of committing.')
      : (s.why || '');
    foot.textContent = `layer ${s.layer} · head ${s.head}`;
  }

  function renderTokens() {
    const s = sents[cur];
    tokensEl.replaceChildren(...s.tokens.map((tk, j) => {
      const el = document.createElement('button');
      el.className = 'attn-tok';
      el.type = 'button';
      el.textContent = tk.replace(/^ /, ' ');
      el.setAttribute('aria-label', `token ${tk.trim()}`);
      const focus = () => { focusTok = j; draw(); };
      el.addEventListener('mouseenter', focus);
      el.addEventListener('focus', focus);
      el.addEventListener('click', focus);
      return el;
    }));
  }

  function weightsFor(row) {
    return sents[cur].weights[row].map((v) => v / 255);
  }

  function draw() {
    const s = sents[cur];
    const toks = [...tokensEl.children];
    if (!toks.length) return;
    // mark focus + target
    toks.forEach((el, j) => {
      el.classList.toggle('is-focus', j === focusTok);
      el.classList.toggle('is-target', j === s.expect?.to && focusTok === s.expect?.from);
    });
    // arcs from focusTok to each attended token
    const stageBox = arcs.getBoundingClientRect();
    const w = arcs.clientWidth || 600, h = 70;
    arcs.setAttribute('viewBox', `0 0 ${w} ${h}`);
    arcs.setAttribute('height', h);
    const centers = toks.map((el) => {
      const r = el.getBoundingClientRect();
      return r.left - stageBox.left + r.width / 2;
    });
    const wts = weightsFor(focusTok);
    const frag = document.createDocumentFragment();
    wts.forEach((wt, j) => {
      if (j > focusTok || wt < 0.04) return;   // causal: only attends backwards
      const x1 = centers[focusTok], x2 = centers[j];
      const path = document.createElementNS(SVG, 'path');
      const midY = h - 6 - Math.min(56, Math.abs(x1 - x2) * 0.32);
      path.setAttribute('d', `M ${x1} ${h - 4} Q ${(x1 + x2) / 2} ${midY} ${x2} ${h - 4}`);
      path.setAttribute('fill', 'none');
      path.setAttribute('stroke', 'var(--cat-base)');
      path.setAttribute('stroke-width', String(0.5 + wt * 4));
      path.setAttribute('stroke-opacity', String(0.15 + wt * 0.75));
      path.setAttribute('stroke-linecap', 'round');
      frag.appendChild(path);
    });
    arcs.replaceChildren(frag);
  }

  function renderHeat() {
    const s = sents[cur];
    const n = s.tokens.length;
    const rows = [];
    rows.push('<tr><td></td>' + s.tokens.map((t) => `<th scope="col">${esc(t.trim())}</th>`).join('') + '</tr>');
    for (let i = 0; i < n; i++) {
      const cells = s.weights[i].map((v, j) => {
        const a = j <= i ? (v / 255) : 0;
        return `<td style="background:color-mix(in srgb, var(--cat-base) ${Math.round(a * 100)}%, var(--surface-2))" title="${a.toFixed(2)}"></td>`;
      }).join('');
      rows.push(`<tr><th scope="row">${esc(s.tokens[i].trim())}</th>${cells}</tr>`);
    }
    heatEl.innerHTML = rows.join('');
  }

  heatToggle.addEventListener('click', () => {
    heat = !heat;
    heatToggle.setAttribute('aria-pressed', String(heat));
    heatToggle.textContent = heat ? 'show the arcs' : 'show the grid';
    heatEl.hidden = !heat;
    arcs.hidden = heat;
    tokensEl.hidden = heat;
    if (!heat) draw();
  });

  const esc = (t) => t.replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));

  new ResizeObserver(() => { if (!heat) draw(); }).observe(arcs);
  selectSentence(0);

  return (stepIndex) => {
    if (stepIndex === 0) { if (heat) heatToggle.click(); selectSentence(coref()); }
    else if (stepIndex === 1) { if (!heat) heatToggle.click(); }
    else { if (heat) heatToggle.click(); selectSentence(firstFail()); }
  };
  function coref() { const i = sents.findIndex((s) => /coreference|binding|agreement/i.test(s.why || '')); return i < 0 ? 0 : i; }
  function firstFail() { const i = sents.findIndex((s) => s.holds === false || s.fail); return i < 0 ? sents.length - 1 : i; }
}
