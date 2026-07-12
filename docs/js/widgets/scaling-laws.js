/**
 * scaling-laws.js — THE flagship widget (SPEC §6a; research/scalingMath.json).
 *
 * Mode A "Spend the budget": one log-slider for C → compute-optimal N, D,
 * loss, $, capability vintage, verdict.
 * Mode B "Allocate it yourself": sliders for N and D → your loss vs the
 * optimal loss at the same compute; the "GPT-3's mistake" preset is the
 * page's designed break-it affordance.
 *
 * Engine: Chinchilla parametric loss L(N,D) = E + A/N^α + B/D^β with the
 * 20:1 frontier N_opt = √(C/120). The Hoffmann↔Epoch toggle swaps ALL
 * constants including the asymptote. Loss values are nats/token.
 * Sanity asserts run at init (Hoffmann constants) — a failure is a console
 * error and fails the no-console-errors AC.
 */

const HOFFMANN = { E: 1.69, A: 406.4, B: 410.7, alpha: 0.34, beta: 0.28, name: 'Hoffmann 2022' };
const EPOCH    = { E: 1.82, A: 482.01, B: 2085.43, alpha: 0.3478, beta: 0.3658, name: 'Epoch AI 2024 re-fit' };

const ANCHORS = [
  { name: 'GPT-2',  year: 2019, N: 1.5e9,  D: 1.667e11, C: 1.5e21,  note: 'coherent paragraphs, no reliable task-following' },
  { name: 'GPT-3',  year: 2020, N: 175e9,  D: 300e9,   C: 3.14e23, note: 'few-shot learning — prompting becomes an interface', off: 'undertrained: 1.7 tokens/param' },
  { name: 'Chinchilla', year: 2022, N: 70e9, D: 1.4e12, C: 5.76e23, note: 'beat a 4× bigger model on equal compute' },
  { name: 'GPT-4 (est.)', year: 2023, N: 280e9, D: 13e12, C: 2.1e25, note: 'passes the bar exam — "wait for the next model" pays off', est: true },
  { name: 'Llama 3.1 405B', year: 2024, N: 405e9, D: 15.6e12, C: 3.8e25, note: 'GPT-4-class in the open', off: 'overtrained on purpose: ~38 tokens/param for cheaper inference' },
];

const VERDICTS = [
  { below: 1e-4, text: 'Weekend territory — nanoGPT scale. Perfect for learning; nobody trains products here.' },
  { below: 1,    text: "A frontier lab has already passed this point. 'Wait for the next model' beats building this yourself — unless your edge is proprietary data or post-training." },
  { below: Infinity, text: "You're at the frontier. Nobody is ahead of you to wait for — differentiation here is data, post-training, and product." },
];

const FRONTIER_NEWEST_C = 3.8e25;

let K = HOFFMANN;
const loss = (N, D) => K.E + K.A / Math.pow(N, K.alpha) + K.B / Math.pow(D, K.beta);
const nOpt = (C) => Math.sqrt(C / 120);
const lossOptAtC = (C) => { const n = nOpt(C); return loss(n, 20 * n); };
const usd = (C, price, mfu) => C * price / (989e12 * mfu * 3600);

/* engineering-suffix formatting (DESIGN §0: numbers in mono with suffixes) */
export function fmt(n, unit = '') {
  if (!isFinite(n)) return '—';
  const abs = Math.abs(n);
  const steps = [[1e12, 'T'], [1e9, 'B'], [1e6, 'M'], [1e3, 'k']];
  for (const [v, s] of steps) if (abs >= v) return trim(n / v) + s + unit;
  return trim(n) + unit;
}
const trim = (x) => (x >= 100 ? Math.round(x) : x >= 10 ? x.toFixed(1) : x.toFixed(2)).toString().replace(/\.0+$/, '');
const fmtUsd = (n) => n >= 1e9 ? '$' + trim(n / 1e9) + 'B' : n >= 1e6 ? '$' + trim(n / 1e6) + 'M' : n >= 1e3 ? '$' + trim(n / 1e3) + 'k' : '$' + trim(n);
/* compute in FLOPs spans 1e17–1e27 — engineering suffixes stop at T, so use
   the field's own notation (matches the chart's 1eNN axis labels). */
const fmtC = (c) => {
  let e = Math.floor(Math.log10(c));
  let m = c / 10 ** e;
  if (m >= 9.95) { m = 1; e += 1; }
  return (m >= 1.05 ? m.toFixed(1) + '×' : '') + '1e' + e;
};

function assertSanity() {
  const close = (a, b, tol) => Math.abs(a - b) <= tol;
  console.assert(close(loss(70e9, 1.4e12), 1.937, 0.01), 'scaling-laws: Chinchilla loss check failed', loss(70e9, 1.4e12));
  console.assert(close(loss(175e9, 300e9), 2.002, 0.01), 'scaling-laws: GPT-3 loss check failed', loss(175e9, 300e9));
  console.assert(close(nOpt(5.76e23), 69.3e9, 1e9), 'scaling-laws: N_opt check failed', nOpt(5.76e23));
}

export async function init(panel) {
  assertSanity();
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let prices = { gpu: { usdPerHour: 2.5, mfu: 0.4 }, asOf: '2026-07' };
  try { prices = await (await fetch('../prices.json')).json(); } catch { /* defaults hold */ }

  panel.innerHTML = `
    <div class="widget-head">
      <p class="kicker"><span class="cat">the scaling laws</span> · run them yourself</p>
      <span class="chip" data-prices-stamp>prices as of ${prices.asOf}</span>
    </div>
    <div class="widget-tabs" role="tablist">
      <button class="chip" role="tab" aria-pressed="true" data-mode="a">spend the budget</button>
      <button class="chip" role="tab" aria-pressed="false" data-mode="b">allocate it yourself</button>
    </div>

    <div data-pane="a">
      <label class="widget-label">training compute
        <input type="range" data-in="c" min="18" max="27" step="0.05" value="23">
        <span class="num" data-out="c" aria-live="off"></span></label>
      <div class="widget-readouts" aria-live="polite">
        <p>optimal model <strong class="num" data-out="n"></strong> ·
           optimal data <strong class="num" data-out="d"></strong> ·
           loss <strong class="num" data-out="l"></strong></p>
        <p class="odometer num" data-out="usd"></p>
        <p data-out="vintage" class="widget-vintage"></p>
        <p data-out="verdict" class="widget-verdict"></p>
      </div>
    </div>

    <div data-pane="b" hidden>
      <label class="widget-label">model size N
        <input type="range" data-in="n" min="7" max="13" step="0.05" value="11.24">
        <span class="num" data-out="bn"></span></label>
      <label class="widget-label">training tokens D
        <input type="range" data-in="d" min="9" max="15" step="0.05" value="11.48">
        <span class="num" data-out="bd"></span></label>
      <button class="btn-primary" data-preset-gpt3 type="button">GPT-3's mistake</button>
      <div class="widget-readouts" aria-live="polite">
        <p>that costs <strong class="num" data-out="bc"></strong> of compute
           (<strong class="num" data-out="busd"></strong>)</p>
        <p>your loss <strong class="num" data-out="bl"></strong> ·
           optimal at the same spend <strong class="num" data-out="blopt"></strong></p>
        <p data-out="bratio" class="widget-verdict"></p>
      </div>
    </div>

    <canvas class="widget-chart" height="380" aria-label="Loss versus training compute, log x axis: the compute-optimal frontier with five real models placed on it"></canvas>
    <p class="breakit-note" data-out="chartnote"></p>

    <details class="widget-advanced">
      <summary>advanced: prices, utilization, whose constants</summary>
      <label class="widget-label">GPU price $/hr
        <input type="range" data-in="price" min="1.5" max="7" step="0.25" value="${prices.gpu.usdPerHour}">
        <span class="num" data-out="price"></span></label>
      <label class="widget-label">utilization (MFU)
        <input type="range" data-in="mfu" min="0.2" max="0.5" step="0.01" value="${prices.gpu.mfu}">
        <span class="num" data-out="mfu"></span></label>
      <button class="chip" data-constants type="button" aria-pressed="false">constants: Hoffmann 2022 — tap for the Epoch 2024 re-fit</button>
      <p class="breakit-note">The 2022 paper's own Approach-3 constants are internally inconsistent
        (Epoch AI 2024, arXiv:2404.10102). Both fits are shown; the frontier stays 20 tokens/param either way.</p>
    </details>`;

  const $ = (sel) => panel.querySelector(sel);
  const els = {
    panes: { a: $('[data-pane="a"]'), b: $('[data-pane="b"]') },
    tabs: [...panel.querySelectorAll('[data-mode]')],
    c: $('[data-in="c"]'), n: $('[data-in="n"]'), d: $('[data-in="d"]'),
    price: $('[data-in="price"]'), mfu: $('[data-in="mfu"]'),
    canvas: $('canvas'),
  };
  const out = {}; panel.querySelectorAll('[data-out]').forEach((e) => { out[e.dataset.out] = e; });

  let mode = 'a';
  let shownUsd = 0;

  const state = () => ({
    C: Math.pow(10, +els.c.value),
    N: Math.pow(10, +els.n.value),
    D: Math.pow(10, +els.d.value),
    price: +els.price.value,
    mfu: +els.mfu.value,
  });

  const vintage = (l) => {
    let best = null;
    for (const a of ANCHORS) {
      const al = loss(a.N, a.D);
      if (!best || Math.abs(al - l) < Math.abs(loss(best.N, best.D) - l)) best = a;
    }
    return best;
  };

  const rollOdometer = (target) => {
    if (reduced) { out.usd.textContent = fmtUsd(target); shownUsd = target; return; }
    const start = shownUsd, t0 = performance.now();
    const step = (t) => {
      const p = Math.min(1, (t - t0) / 250);
      shownUsd = start + (target - start) * p;
      out.usd.textContent = fmtUsd(shownUsd);
      if (p < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  };

  const render = () => {
    const s = state();
    out.price.textContent = '$' + s.price.toFixed(2);
    out.mfu.textContent = Math.round(s.mfu * 100) + '%';
    if (mode === 'a') {
      const n = nOpt(s.C), d = 20 * n, l = loss(n, d);
      out.c.textContent = fmt(s.C) + ' FLOPs';
      out.n.textContent = fmt(n) + ' params';
      out.d.textContent = fmt(d) + ' tokens';
      out.l.textContent = l.toFixed(3) + ' nats';
      rollOdometer(usd(s.C, s.price, s.mfu));
      const v = vintage(l);
      out.vintage.textContent = `≈ ${v.name}, ${v.year} — ${v.note}`;
      const R = s.C / FRONTIER_NEWEST_C;
      out.verdict.textContent = VERDICTS.find((x) => R < x.below).text;
    } else {
      const C = 6 * s.N * s.D, l = loss(s.N, s.D), lo = lossOptAtC(C);
      const tpp = s.D / s.N;
      out.bn.textContent = fmt(s.N) + ' params';
      out.bd.textContent = fmt(s.D) + ' tokens';
      out.bc.textContent = fmt(C) + ' FLOPs';
      out.busd.textContent = fmtUsd(usd(C, s.price, s.mfu));
      out.bl.textContent = l.toFixed(3) + ' nats';
      out.blopt.textContent = lo.toFixed(3) + ' nats';
      out.bratio.textContent = tpp < 14
        ? `you are undertrained: ${trim(tpp)} tokens/param vs ~20 — GPT-3's exact mistake`
        : tpp > 30
          ? `you are overtrained: ${trim(tpp)} tokens/param vs ~20 — rational only if inference cost rules you`
          : `near the frontier: ${trim(tpp)} tokens/param ≈ the 20:1 rule`;
    }
    drawChart();
  };

  /* ——— chart: log-x (C 1e17–1e27), LINEAR y (loss 1.6–4.0) ——— */
  const drawChart = () => {
    const cv = els.canvas, dpr = window.devicePixelRatio || 1;
    const w = cv.clientWidth || 640, h = 380;
    cv.width = w * dpr; cv.height = h * dpr;
    const ctx = cv.getContext('2d');
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    const css = getComputedStyle(panel);
    const col = (v, fb) => css.getPropertyValue(v).trim() || fb;
    const PADL = 46, PADR = 16, PADT = 14, PADB = 34;
    const X = (C) => PADL + (Math.log10(C) - 17) / 10 * (w - PADL - PADR);
    const Y = (l) => PADT + (4.0 - Math.min(4, Math.max(1.6, l))) / 2.4 * (h - PADT - PADB);
    ctx.clearRect(0, 0, w, h);

    /* extrapolation shading beyond 1e24 */
    ctx.fillStyle = 'rgba(255,255,255,.03)';
    ctx.fillRect(X(1e24), PADT, w - PADR - X(1e24), h - PADT - PADB);

    /* grid + labels */
    ctx.strokeStyle = col('--border', '#262A31'); ctx.lineWidth = 1;
    ctx.fillStyle = col('--muted', '#9BA1A9');
    ctx.font = '11px "JetBrains Mono", monospace';
    for (let e = 17; e <= 27; e += 2) {
      ctx.beginPath(); ctx.moveTo(X(10 ** e), PADT); ctx.lineTo(X(10 ** e), h - PADB); ctx.stroke();
      ctx.fillText('1e' + e, X(10 ** e) - 12, h - PADB + 14);
      const dollars = usd(10 ** e, state().price, state().mfu);
      ctx.fillText(fmtUsd(dollars), X(10 ** e) - 12, h - PADB + 27);
    }
    for (const l of [2.0, 2.5, 3.0, 3.5, 4.0]) {
      ctx.beginPath(); ctx.moveTo(PADL, Y(l)); ctx.lineTo(w - PADR, Y(l)); ctx.stroke();
      ctx.fillText(l.toFixed(1), 8, Y(l) + 4);
    }

    /* irreducible-entropy asymptote */
    ctx.strokeStyle = col('--warn', '#E2B93B'); ctx.setLineDash([5, 5]);
    ctx.beginPath(); ctx.moveTo(PADL, Y(K.E)); ctx.lineTo(w - PADR, Y(K.E)); ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = col('--warn', '#E2B93B');
    ctx.fillText(`E = ${K.E} — irreducible entropy of text`, PADL + 6, Y(K.E) - 6);

    /* compute-optimal frontier */
    ctx.strokeStyle = col('--cat-base', '#A48FFF'); ctx.lineWidth = 2;
    ctx.beginPath();
    for (let e = 17; e <= 27; e += 0.1) {
      const C = 10 ** e, l = lossOptAtC(C);
      e === 17 ? ctx.moveTo(X(C), Y(l)) : ctx.lineTo(X(C), Y(l));
    }
    ctx.stroke();

    /* anchors */
    for (const a of ANCHORS) {
      const l = loss(a.N, a.D);
      ctx.beginPath(); ctx.arc(X(a.C), Y(l), 5, 0, 7);
      ctx.fillStyle = col('--text', '#E8EAED'); ctx.fill();
      ctx.strokeStyle = col('--ground', '#0C0D0F'); ctx.lineWidth = 2; ctx.stroke();
      ctx.fillStyle = col('--muted', '#9BA1A9');
      ctx.fillText(a.name + (a.est ? ' *' : ''), X(a.C) - 20, Y(l) - 10);
    }

    /* your point */
    const s = state();
    const yc = mode === 'a' ? s.C : 6 * s.N * s.D;
    const yl = mode === 'a' ? lossOptAtC(yc) : loss(s.N, s.D);
    ctx.beginPath(); ctx.arc(X(yc), Y(yl), 7, 0, 7);
    ctx.fillStyle = col('--cat-light', '#C9BCFF'); ctx.fill();
    ctx.strokeStyle = col('--ground', '#0C0D0F'); ctx.lineWidth = 2; ctx.stroke();

    out.chartnote.textContent = (mode === 'b' && yl > lossOptAtC(yc) + 0.005)
      ? 'your dot sits above the frontier — same money, worse model. That gap is the Chinchilla paper.'
      : 'the shaded region extrapolates the fit beyond its largest fitted models. * = reported/leaked figures.';
  };

  /* ——— wiring ——— */
  els.tabs.forEach((t) => t.addEventListener('click', () => {
    mode = t.dataset.mode;
    els.tabs.forEach((x) => x.setAttribute('aria-pressed', String(x === t)));
    els.panes.a.hidden = mode !== 'a';
    els.panes.b.hidden = mode !== 'b';
    render();
  }));
  panel.querySelectorAll('input[type="range"]').forEach((r) => r.addEventListener('input', render));
  $('[data-preset-gpt3]').addEventListener('click', () => {
    if (mode !== 'b') els.tabs[1].click();
    /* exact paper coordinates — 'any' stops the 0.05 grid from snapping the
       preset off the published 2.002-vs-1.937 comparison (SPEC §6a AC);
       keyboard arrows still move ~1% of range. */
    els.n.step = els.d.step = 'any';
    els.n.value = Math.log10(175e9);
    els.d.value = Math.log10(300e9);
    render();
  });
  $('[data-constants]').addEventListener('click', (e) => {
    K = K === HOFFMANN ? EPOCH : HOFFMANN;
    e.target.setAttribute('aria-pressed', String(K === EPOCH));
    e.target.textContent = K === HOFFMANN
      ? 'constants: Hoffmann 2022 — tap for the Epoch 2024 re-fit'
      : 'constants: Epoch AI 2024 re-fit — tap for the paper’s originals';
    render();
  });
  new ResizeObserver(drawChart).observe(els.canvas);
  render();

  /* scroll-driven story beats (widget-tier scrolly contract) */
  return (stepIndex) => {
    if (stepIndex === 1 && mode !== 'a') els.tabs[0].click();
    if (stepIndex >= 2 && mode !== 'b') els.tabs[1].click();
    if (stepIndex === 3) $('[data-preset-gpt3]').click();
  };
}
