/**
 * gpt2.js — zero-shot performance across model size, Figure 1 (four panels).
 * Small-multiples: each task's curve climbs with parameter count toward a
 * dashed supervised-baseline line. Panels reveal one per scroll step.
 */
import { tokens, hidpi } from './_chart.js';

export async function init(panel) {
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let data;
  try { data = await (await fetch('../data/gpt2/figure.json')).json(); }
  catch (e) { throw new Error('could not load gpt2 figure data'); }

  panel.innerHTML = `
    <div class="widget-head">
      <p class="kicker"><span class="cat">zero-shot, no task training</span> · figure 1, redrawn</p>
      <span class="status-chip status-chip--live">live</span>
    </div>
    <canvas class="widget-chart" aria-label="Four panels — reading comprehension, translation, summarization, question answering — each showing zero-shot performance climbing with model size from 117M to 1542M parameters toward a dashed supervised baseline"></canvas>
    <p class="breakit-note" data-cap></p>`;

  const t = tokens(panel);
  const canvas = panel.querySelector('canvas');
  panel.querySelector('[data-cap]').textContent =
    'traced from Figure 1 — approximate; 1542M endpoints exact from the paper; dashed = supervised baseline';

  const params = data.xAxis.values;                 // [117,345,762,1542]
  const xMin = params[0], xMax = params[params.length - 1];
  const panels = data.series.slice(0, 4);

  let shown = reduced ? 4 : 0, target = 4, raf = 0;

  const drawPanel = (ctx, s, px, py, pw, ph, reveal) => {
    const ys = s.points.map((p) => p.y).concat(s.reference ? [s.reference.y] : []);
    const yMax = Math.max(...ys) * 1.1;
    const X = (x) => px + 34 + (x - xMin) / (xMax - xMin) * (pw - 42);
    const Y = (y) => py + 6 + (1 - y / yMax) * (ph - 34);
    ctx.font = `10px ${t.mono}`; ctx.fillStyle = t.muted; ctx.textAlign = 'left';
    ctx.fillText(s.label.split('—')[0].trim().slice(0, 22), px + 4, py + 2);
    // supervised baseline
    if (s.reference) {
      ctx.strokeStyle = t.muted; ctx.setLineDash([4, 3]); ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(X(xMin), Y(s.reference.y)); ctx.lineTo(X(xMax), Y(s.reference.y)); ctx.stroke();
      ctx.setLineDash([]);
    }
    // curve
    const n = Math.max(2, Math.ceil(s.points.length * reveal));
    ctx.strokeStyle = t.base; ctx.lineWidth = 2; ctx.beginPath();
    s.points.slice(0, n).forEach((p, j) => j ? ctx.lineTo(X(p.x), Y(p.y)) : ctx.moveTo(X(p.x), Y(p.y)));
    ctx.stroke();
    if (reveal >= 1) {
      const last = s.points[s.points.length - 1];
      ctx.fillStyle = t.light; ctx.beginPath(); ctx.arc(X(last.x), Y(last.y), 3, 0, 7); ctx.fill();
    }
    // axis foot
    ctx.strokeStyle = t.border; ctx.beginPath();
    ctx.moveTo(X(xMin), py + ph - 24); ctx.lineTo(X(xMax), py + ph - 24); ctx.stroke();
    ctx.fillStyle = t.muted; ctx.font = `9px ${t.mono}`;
    ctx.fillText('117M', X(xMin) - 6, py + ph - 12);
    ctx.textAlign = 'right'; ctx.fillText('1.5B', X(xMax) + 4, py + ph - 12); ctx.textAlign = 'left';
  };

  const draw = () => {
    const w = canvas.clientWidth || 620, h = 320;
    const ctx = hidpi(canvas, w, h);
    ctx.clearRect(0, 0, w, h);
    const cw = w / 2, ch = h / 2;
    panels.forEach((s, i) => {
      const reveal = Math.max(0, Math.min(1, shown - i));
      if (reveal <= 0) return;
      drawPanel(ctx, s, (i % 2) * cw, Math.floor(i / 2) * ch, cw, ch, reveal);
    });
  };
  const animate = () => {
    if (Math.abs(shown - target) < 0.02) { shown = target; draw(); return; }
    shown += (target - shown) * 0.18; draw(); raf = requestAnimationFrame(animate);
  };
  new ResizeObserver(draw).observe(canvas);
  draw();

  return (stepIndex) => {
    target = [0.6, 4, 4, 4][Math.min(3, stepIndex)];
    if (reduced) { shown = target; draw(); }
    else { cancelAnimationFrame(raf); raf = requestAnimationFrame(animate); }
  };
}
