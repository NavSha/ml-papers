/**
 * gpt3.js — in-context-learning curves (SPEC §6 scrolly tier).
 * Renders Figure 1.2: accuracy vs number of in-context examples, one curve per
 * model size; the 175B curve climbs steeply while small models stay flat.
 */
import { tokens, hidpi, lineChart } from './_chart.js';

const COLORS = ['muted', 'deep', 'base'];   // 1.3B, 13B, 175B (biggest = brightest)

export async function init(panel) {
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let data;
  try { data = await (await fetch('../data/gpt3/figure.json')).json(); }
  catch (e) { throw new Error('could not load gpt3 figure data'); }

  panel.innerHTML = `
    <div class="widget-head">
      <p class="kicker"><span class="cat">in-context learning</span> · figure 1.2, redrawn</p>
      <span class="status-chip status-chip--live">live</span>
    </div>
    <canvas class="widget-chart" aria-label="In-context learning: Symbol-Insertion accuracy versus number of examples in the prompt, for 1.3B, 13B and 175B parameter models"></canvas>
    <p class="breakit-note" data-cap></p>`;

  const t = tokens(panel);
  const canvas = panel.querySelector('canvas');
  panel.querySelector('[data-cap]').textContent =
    'traced from Figure 1.2 — approximate; K=0/1/100 points are exact (Table H.1)';

  const series = data.series.map((s, i) => ({
    points: s.points,
    color: t[COLORS[i]] || t.base,
    emphasis: i === data.series.length - 1,
    label: s.label.replace(/\s*\(.*\)/, ''),
  }));
  const allY = series.flatMap((s) => s.points.map((p) => p.y));
  const yMax = Math.ceil(Math.max(...allY) + 0.5);

  let target = series.length - 1;   // fully revealed until scroll drives it
  let shown = reduced ? target : 0;
  let raf = 0;

  const draw = () => {
    const w = canvas.clientWidth || 620, h = 300;
    const ctx = hidpi(canvas, w, h);
    lineChart(ctx, t, {
      w, h, series, xDomain: [0, 100], yDomain: [0, yMax],
      xLabel: 'examples in the prompt (K)', yLabel: 'accuracy',
      xTicks: [0, 25, 50, 75, 100],
      yTicks: Array.from({ length: yMax + 1 }, (_, i) => i),
      reveal: (i) => Math.max(0, Math.min(1, shown - i + 1)),
    });
  };
  const animate = () => {
    if (Math.abs(shown - target) < 0.02) { shown = target; draw(); return; }
    shown += (target - shown) * 0.2; draw(); raf = requestAnimationFrame(animate);
  };
  new ResizeObserver(draw).observe(canvas);
  draw();

  return (stepIndex) => {
    // step 0: setup (no curves) · 1: small flat · 2: 175B climbs · 3: all
    target = [0.15, 1, series.length - 1, series.length - 1][Math.min(3, stepIndex)];
    if (reduced) { shown = target; draw(); }
    else { cancelAnimationFrame(raf); raf = requestAnimationFrame(animate); }
  };
}
