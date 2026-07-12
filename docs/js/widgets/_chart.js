/**
 * _chart.js — shared, dependency-free canvas helpers for the scrolly widgets
 * (SPEC §2 rule 9: hand-rolled charts, no libraries). Reads DESIGN tokens off
 * the panel's computed style so charts retheme with the page category.
 */

export function tokens(panel) {
  const cs = getComputedStyle(panel);
  const g = (v, fb) => cs.getPropertyValue(v).trim() || fb;
  return {
    base: g('--cat-base', '#A48FFF'), deep: g('--cat-deep', '#6A55C2'),
    light: g('--cat-light', '#C9BCFF'), text: g('--text', '#E8EAED'),
    muted: g('--muted', '#9BA1A9'), border: g('--border', '#262A31'),
    surface2: g('--surface-2', '#1B1D23'), ground: g('--ground', '#0C0D0F'),
    warn: g('--warn', '#E2B93B'), mono: 'JetBrains Mono, monospace',
  };
}

export function hidpi(canvas, w, h) {
  const dpr = window.devicePixelRatio || 1;
  canvas.width = w * dpr; canvas.height = h * dpr;
  canvas.style.width = w + 'px'; canvas.style.height = h + 'px';
  const ctx = canvas.getContext('2d');
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  return ctx;
}

/** Generic multi-series line chart with progressive reveal (0..1 per series). */
export function lineChart(ctx, t, opts) {
  const { w, h, series, xDomain, yDomain, xLabel, yLabel, xTicks, yTicks, reveal } = opts;
  const PADL = 48, PADR = 16, PADT = 16, PADB = 40;
  const X = (x) => PADL + (x - xDomain[0]) / (xDomain[1] - xDomain[0]) * (w - PADL - PADR);
  const Y = (y) => PADT + (yDomain[1] - y) / (yDomain[1] - yDomain[0]) * (h - PADT - PADB);
  ctx.clearRect(0, 0, w, h);
  ctx.font = `11px ${t.mono}`;
  ctx.fillStyle = t.muted; ctx.strokeStyle = t.border; ctx.lineWidth = 1;

  for (const yt of (yTicks || [])) {
    ctx.beginPath(); ctx.moveTo(PADL, Y(yt)); ctx.lineTo(w - PADR, Y(yt)); ctx.stroke();
    ctx.textAlign = 'right'; ctx.fillText(String(yt), PADL - 6, Y(yt) + 4);
  }
  ctx.textAlign = 'center';
  for (const xt of (xTicks || [])) ctx.fillText(String(xt), X(xt), h - PADB + 16);
  if (xLabel) ctx.fillText(xLabel, w / 2, h - 8);
  ctx.save(); ctx.translate(12, h / 2); ctx.rotate(-Math.PI / 2);
  if (yLabel) { ctx.textAlign = 'center'; ctx.fillText(yLabel, 0, 0); } ctx.restore();

  series.forEach((s, i) => {
    const r = reveal ? reveal(i) : 1;
    if (r <= 0) return;
    const pts = s.points;
    const n = Math.max(2, Math.ceil(pts.length * r));
    ctx.strokeStyle = s.color; ctx.lineWidth = s.emphasis ? 3 : 1.8;
    ctx.globalAlpha = s.emphasis ? 1 : 0.85;
    if (s.dashed) ctx.setLineDash([5, 4]); else ctx.setLineDash([]);
    ctx.beginPath();
    pts.slice(0, n).forEach((p, j) => j ? ctx.lineTo(X(p.x), Y(p.y)) : ctx.moveTo(X(p.x), Y(p.y)));
    ctx.stroke();
    ctx.setLineDash([]); ctx.globalAlpha = 1;
    if (s.label && r >= 1) {
      const last = pts[pts.length - 1];
      ctx.fillStyle = s.color; ctx.textAlign = 'left';
      ctx.fillText(s.label, Math.min(X(last.x) + 6, w - PADR - 60), Y(last.y) + 3);
    }
  });
}

/** Horizontal bar chart. bars: [{label, value, color, note}], max = axis top. */
export function barChart(ctx, t, opts) {
  const { w, h, bars, max, reveal } = opts;
  const PADL = 8, PADR = 60, PADT = 12, PADB = 12;
  const bh = Math.min(40, (h - PADT - PADB) / bars.length - 12);
  ctx.clearRect(0, 0, w, h);
  ctx.font = `12px ${t.mono}`;
  bars.forEach((b, i) => {
    const r = reveal ? Math.max(0, Math.min(1, reveal(i))) : 1;
    const y = PADT + i * ((h - PADT - PADB) / bars.length);
    const full = (w - PADL - PADR) * (b.value / max);
    ctx.fillStyle = t.surface2;
    ctx.fillRect(PADL, y, w - PADL - PADR, bh);
    ctx.fillStyle = b.color || t.base;
    ctx.fillRect(PADL, y, full * r, bh);
    ctx.fillStyle = t.text; ctx.textAlign = 'left';
    ctx.fillText(b.label, PADL + 8, y + bh / 2 + 4);
    ctx.fillStyle = t.light; ctx.textAlign = 'right';
    ctx.fillText(b.display ?? String(b.value), w - 6, y + bh / 2 + 4);
  });
}

export const easeReveal = (target, idx, per = 1) =>
  Math.max(0, Math.min(1, (target - idx) / per + 1));
