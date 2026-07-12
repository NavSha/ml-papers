/**
 * deepseek-r1.js — pinned scrolly visual (SPEC §5 scrolly tier; CHECKPOINTS CP6).
 *
 * The reward loop (generate → rule-based check → reward → update) opens the
 * story; the R1-Zero training curve (AIME 2024 pass@1) then draws itself
 * progressively as the reader scrolls; the R1-vs-o1 anchors land last.
 *
 * Data: ../data/deepseek-r1/figure.json — interior curve points are traced
 * from the paper's Figure 2 ("traced, approximate"; caption rendered in the
 * panel per the colophon rule); the endpoints (15.6 → 71.0) and the
 * 79.8 / 79.2 anchors are exact values stated in the paper. Nothing invented.
 *
 * No libraries; hand-rolled canvas; update-in-place; one rAF write per frame;
 * generation-counter cancellation; reduced motion = final state instantly.
 */

const DATA = '../data/deepseek-r1/figure.json';
const YMAX = 90; // chart headroom above the 79.8 anchor

export async function init(panel) {
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const fig = await (await fetch(DATA)).json();
  const curve = fig.series.find((s) => s.id === 'r1-zero-aime-training');
  const anchors = fig.series.find((s) => s.id === 'aime-anchors').points;
  const pts = curve.points;
  const XMAX = pts[pts.length - 1].x;
  const anchor = (label, fb) => anchors.find((p) => p.label === label)?.y ?? fb;
  const R1 = anchor('DeepSeek-R1 (pass@1)', 79.8);
  const O1 = anchor('OpenAI-o1-1217 (pass@1)', 79.2);
  console.assert(pts[0].y === 15.6 && pts[pts.length - 1].y === 71.0,
    'deepseek-r1: curve endpoints drifted from the paper', pts[0], pts[pts.length - 1]);

  panel.innerHTML = `
    <div class="widget-head">
      <p class="kicker"><span class="cat">the training run</span> · figure 2, redrawn</p>
      <span class="status-chip">scroll to train</span>
    </div>

    <svg data-loop viewBox="0 0 640 126" role="img"
         aria-label="The training loop: generate answer, rule-based check (correct? formatted?), reward, update the model — repeat; the only training signal is the check"
         style="width:100%;height:auto;display:block;margin-bottom:12px">
      <defs>
        <marker id="r1arr" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto">
          <path d="M0 0 L8 4 L0 8 z" fill="var(--muted)"/>
        </marker>
        <marker id="r1arrc" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto">
          <path d="M0 0 L8 4 L0 8 z" fill="var(--cat-base)"/>
        </marker>
      </defs>
      <rect x="24" y="8" width="122" height="52" rx="8" fill="var(--surface-2)" stroke="var(--border)"/>
      <text x="85" y="39" font-family="Inter, sans-serif" font-size="13" fill="var(--text)" text-anchor="middle">generate answer</text>
      <line x1="150" y1="34" x2="172" y2="34" stroke="var(--muted)" stroke-width="1.5" marker-end="url(#r1arr)"/>
      <rect x="178" y="8" width="136" height="52" rx="8" fill="var(--cat-deep)"/>
      <text x="246" y="30" font-family="Inter, sans-serif" font-size="13" fill="var(--cat-light)" text-anchor="middle">rule-based check</text>
      <text x="246" y="48" font-family="Inter, sans-serif" font-size="11" fill="var(--cat-light)" text-anchor="middle">correct? formatted?</text>
      <line x1="318" y1="34" x2="340" y2="34" stroke="var(--muted)" stroke-width="1.5" marker-end="url(#r1arr)"/>
      <rect x="346" y="8" width="84" height="52" rx="8" fill="var(--surface-2)" stroke="var(--border)"/>
      <text x="388" y="39" font-family="Inter, sans-serif" font-size="13" fill="var(--text)" text-anchor="middle">reward</text>
      <line x1="434" y1="34" x2="456" y2="34" stroke="var(--muted)" stroke-width="1.5" marker-end="url(#r1arr)"/>
      <rect x="462" y="8" width="130" height="52" rx="8" fill="var(--surface-2)" stroke="var(--border)"/>
      <text x="527" y="39" font-family="Inter, sans-serif" font-size="13" fill="var(--text)" text-anchor="middle">update the model</text>
      <path d="M 527 60 L 527 90 L 85 90 L 85 66" fill="none" stroke="var(--cat-base)" stroke-width="2" marker-end="url(#r1arrc)"/>
      <text x="306" y="112" font-family="Inter, sans-serif" font-size="12" fill="var(--cat-base)" text-anchor="middle">repeat — the only training signal is the check</text>
    </svg>

    <canvas class="widget-chart" style="height:300px"
            aria-label="AIME 2024 pass@1 versus RL steps: DeepSeek-R1-Zero climbs from 15.6% at step 0 to 71.0% at the end of training; the polished R1 lands at 79.8%, just past OpenAI o1-1217's dashed line at 79.2%"></canvas>

    <div aria-live="polite">
      <p class="widget-verdict" data-out="moral" hidden>if your domain has an automatic checker,
        it is RL-able — and the moat held for months, not years.</p>
    </div>
    <p class="chart-note">curve traced from the paper’s figure — approximate ·
      15.6 / 71.0 / 79.8 / 79.2 are exact values from the paper</p>`;

  const $ = (sel) => panel.querySelector(sel);
  const loopEl = $('[data-loop]');
  const cv = $('canvas');
  const out = {}; panel.querySelectorAll('[data-out]').forEach((e) => { out[e.dataset.out] = e; });
  loopEl.style.transition = reduced ? 'none' : 'opacity 400ms ease';

  /* one reveal scalar drives everything: 0–1 curve draw, 1–2 anchors, 2–3 moral */
  let t = 0;
  let target = 0;
  let gen = 0;   // cancels an in-flight animation when the step changes
  let rafId = 0; // coalesce redraws: one rAF write per frame

  const drawChart = () => {
    const dpr = window.devicePixelRatio || 1;
    const w = cv.clientWidth || 560, h = 300;
    cv.width = w * dpr; cv.height = h * dpr;
    const ctx = cv.getContext('2d');
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    const css = getComputedStyle(panel);
    const col = (v, fb) => css.getPropertyValue(v).trim() || fb;
    const PADL = 46, PADR = 20, PADT = 18, PADB = 36;
    const X = (x) => PADL + x / XMAX * (w - PADL - PADR);
    const Y = (v) => PADT + (YMAX - v) / YMAX * (h - PADT - PADB);
    ctx.clearRect(0, 0, w, h);

    const curveP = Math.max(0, Math.min(1, t));
    const anchorA = Math.max(0, Math.min(1, t - 1));

    /* grid + axis labels — border/muted per the design tokens */
    ctx.strokeStyle = col('--border', '#262A31'); ctx.lineWidth = 1;
    ctx.fillStyle = col('--muted', '#9BA1A9');
    ctx.font = '11px "JetBrains Mono", monospace';
    ctx.textAlign = 'right';
    for (const v of [0, 20, 40, 60, 80]) {
      ctx.beginPath(); ctx.moveTo(PADL, Y(v)); ctx.lineTo(w - PADR, Y(v)); ctx.stroke();
      ctx.fillText(v + '%', PADL - 8, Y(v) + 4);
    }
    ctx.textAlign = 'center';
    for (let s = 0; s <= XMAX; s += 2000) {
      ctx.beginPath(); ctx.moveTo(X(s), PADT); ctx.lineTo(X(s), h - PADB); ctx.stroke();
      ctx.fillText(s === 0 ? '0' : s / 1000 + 'k', X(s), h - PADB + 16);
    }
    ctx.fillText(`${curve.xAxis.label} (axis approximate)`, PADL + (w - PADL - PADR) / 2, h - 6);
    ctx.textAlign = 'left';
    ctx.fillText(`${curve.yAxis.label} (%)`, PADL, 10);

    /* the starting point is always on the chart: base model, 15.6% */
    ctx.beginPath(); ctx.arc(X(0), Y(pts[0].y), 4.5, 0, 7);
    ctx.fillStyle = col('--text', '#E8EAED'); ctx.fill();
    ctx.strokeStyle = col('--ground', '#0C0D0F'); ctx.lineWidth = 2; ctx.stroke();
    ctx.font = '12px "JetBrains Mono", monospace';
    ctx.fillStyle = col('--muted', '#9BA1A9');
    ctx.fillText('base 15.6%', X(0) + 10, Y(pts[0].y) - 10);

    /* the RL training curve, drawn up to the reveal fraction */
    if (curveP > 0) {
      const px = curveP * XMAX;
      let hx = pts[0].x, hy = pts[0].y;
      ctx.strokeStyle = col('--cat-base', '#7BC9A3'); ctx.lineWidth = 2.5;
      ctx.beginPath();
      ctx.moveTo(X(pts[0].x), Y(pts[0].y));
      for (let i = 1; i < pts.length; i++) {
        if (pts[i].x <= px) { hx = pts[i].x; hy = pts[i].y; ctx.lineTo(X(hx), Y(hy)); continue; }
        const a = pts[i - 1], b = pts[i];
        const f = (px - a.x) / (b.x - a.x);
        hx = px; hy = a.y + (b.y - a.y) * f;
        ctx.lineTo(X(hx), Y(hy));
        break;
      }
      ctx.stroke();
      /* the moving head while training; the R1-Zero dot once done */
      ctx.beginPath(); ctx.arc(X(hx), Y(hy), curveP < 1 ? 4 : 5, 0, 7);
      ctx.fillStyle = col(curveP < 1 ? '--cat-light' : '--cat-base', '#7BC9A3'); ctx.fill();
      ctx.strokeStyle = col('--ground', '#0C0D0F'); ctx.lineWidth = 2; ctx.stroke();
      if (curveP < 1) {
        ctx.fillStyle = col('--cat-light', '#B9E6CF');
        ctx.textAlign = hx > XMAX * 0.75 ? 'right' : 'left';
        ctx.fillText(hy.toFixed(1) + '%', X(hx) + (hx > XMAX * 0.75 ? -10 : 10), Y(hy) - 10);
      } else {
        ctx.fillStyle = col('--cat-base', '#7BC9A3');
        ctx.textAlign = 'right';
        ctx.fillText('R1-Zero 71.0%', X(XMAX) - 10, Y(71) + 18);
      }
    }

    /* the anchors: o1's closed bar, and the shipped R1 a hair past it */
    if (anchorA > 0) {
      ctx.globalAlpha = anchorA;
      ctx.strokeStyle = col('--text', '#E8EAED'); ctx.lineWidth = 1.5; ctx.setLineDash([3, 4]);
      ctx.beginPath(); ctx.moveTo(PADL, Y(O1)); ctx.lineTo(w - PADR, Y(O1)); ctx.stroke();
      ctx.setLineDash([]);
      ctx.fillStyle = col('--text', '#E8EAED');
      ctx.textAlign = 'left';
      ctx.fillText(`o1-1217 ${O1.toFixed(1)}%`, PADL + 6, Y(O1) + 16);
      ctx.beginPath(); ctx.arc(X(XMAX), Y(R1), 5.5, 0, 7);
      ctx.fillStyle = col('--cat-light', '#B9E6CF'); ctx.fill();
      ctx.strokeStyle = col('--ground', '#0C0D0F'); ctx.lineWidth = 2; ctx.stroke();
      ctx.fillStyle = col('--cat-light', '#B9E6CF');
      ctx.textAlign = 'right';
      ctx.fillText(`R1 ${R1.toFixed(1)}%`, X(XMAX) - 10, Y(R1) - 10);
      ctx.globalAlpha = 1;
    }
  };

  const render = () => {
    rafId = 0;
    drawChart();
    out.moral.hidden = t < 2.9;
  };
  const schedule = () => { if (!rafId) rafId = requestAnimationFrame(render); };

  /* the climb (t 0→1) is slow enough to watch; later beats snap; rewinds are quick */
  const animateTo = () => {
    gen++;
    if (reduced || t === target) { t = target; schedule(); return; }
    const g = gen;
    let last = performance.now();
    const tick = (now) => {
      if (g !== gen) return;
      const dt = Math.min(0.1, (now - last) / 1000); last = now;
      const dir = Math.sign(target - t);
      const speed = dir < 0 ? 4 : t < 1 ? 0.55 : 3.5;
      t += dir * speed * dt;
      if ((dir > 0 && t >= target) || (dir < 0 && t <= target)) t = target;
      render();
      if (t !== target) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  };

  new ResizeObserver(schedule).observe(cv);
  render();

  /* scroll-driven story beats (scrolly-tier contract) */
  return (stepIndex) => {
    target = Math.max(0, Math.min(3, stepIndex));
    loopEl.style.opacity = target === 0 ? '1' : '0.45';
    animateTo();
  };
}
