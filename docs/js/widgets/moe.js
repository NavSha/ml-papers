/**
 * moe.js — the router as a load balancer (SPEC §6 scrolly tier).
 * A token flows to exactly ONE of N experts; the rest sit idle. Final step
 * reveals the 7× pre-training speedup vs the dense T5-Base baseline.
 */
export async function init(panel) {
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let data;
  try { data = await (await fetch('../data/moe/figure.json')).json(); } catch { data = null; }
  const speedup = 7;

  panel.innerHTML = `
    <div class="widget-head">
      <p class="kicker"><span class="cat">the router</span> · one expert per token</p>
      <span class="status-chip status-chip--live">live</span>
    </div>
    <svg viewBox="0 0 620 300" role="img" aria-label="A token enters a router that sends it to one of four experts; the other three stay idle. A bar shows the seven-times pre-training speedup over the dense baseline." style="width:100%;height:auto;display:block">
      <text x="20" y="150" font-family="JetBrains Mono, monospace" font-size="13" fill="var(--text)">token</text>
      <line x1="64" y1="146" x2="150" y2="146" stroke="var(--muted)" stroke-width="1.5"/>
      <rect x="150" y="126" width="90" height="40" rx="8" fill="var(--surface-2)" stroke="var(--border)"/>
      <text x="195" y="151" font-family="Inter, sans-serif" font-size="12" fill="var(--text)" text-anchor="middle">router</text>
      <g data-experts></g>
      <g data-speedup opacity="0">
        <text x="20" y="248" font-family="JetBrains Mono, monospace" font-size="12" fill="var(--muted)">pre-training speedup vs dense T5-Base, same compute</text>
        <rect x="20" y="258" width="90" height="24" rx="4" fill="var(--surface-2)"/>
        <text x="115" y="275" font-family="JetBrains Mono, monospace" font-size="12" fill="var(--muted)">dense 1×</text>
        <rect x="20" y="258" width="0" height="24" rx="4" fill="var(--cat-base)" data-bar/>
        <text x="20" y="275" font-family="JetBrains Mono, monospace" font-size="13" fill="var(--ground)" data-barlabel></text>
      </g>
    </svg>
    <p class="breakit-note" data-note>Every token pays every parameter — that's the dense tax.</p>`;

  const svg = panel.querySelector('svg');
  const g = svg.querySelector('[data-experts]');
  const N = 4, active = 1;
  for (let i = 0; i < N; i++) {
    const y = 40 + i * 58;
    const box = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    box.setAttribute('data-expert', i);
    box.innerHTML = `<line x1="240" y1="146" x2="330" y2="${y + 18}" stroke="var(--border)" stroke-width="1" data-wire/>
      <rect x="330" y="${y}" width="120" height="36" rx="8" fill="var(--surface-2)" stroke="var(--border)" data-box/>
      <text x="390" y="${y + 23}" font-family="Inter, sans-serif" font-size="12" fill="var(--muted)" text-anchor="middle" data-lbl>expert ${i + 1}</text>`;
    g.appendChild(box);
  }
  const note = panel.querySelector('[data-note]');
  const bar = panel.querySelector('[data-bar]');
  const barLabel = panel.querySelector('[data-barlabel]');
  const speedupG = panel.querySelector('[data-speedup]');

  const setActive = (on) => {
    g.querySelectorAll('[data-expert]').forEach((e, i) => {
      const lit = on && i === active;
      e.querySelector('[data-box]').setAttribute('stroke', lit ? 'var(--cat-base)' : 'var(--border)');
      e.querySelector('[data-box]').setAttribute('fill', lit ? 'color-mix(in srgb, var(--cat-base) 18%, var(--surface-2))' : 'var(--surface-2)');
      e.querySelector('[data-wire]').setAttribute('stroke', lit ? 'var(--cat-base)' : 'var(--border)');
      e.querySelector('[data-wire]').setAttribute('stroke-width', lit ? '2' : '1');
      e.style.opacity = on ? (lit ? '1' : '0.4') : '1';
    });
  };
  const showSpeedup = (on) => {
    speedupG.setAttribute('opacity', on ? '1' : '0');
    const w = on ? 90 * speedup / 1 * 0.9 : 0;   // scale so 7× fits (~567px cap 540)
    bar.setAttribute('width', String(Math.min(540, w)));
    barLabel.textContent = on ? `Switch ${speedup}×` : '';
  };

  return (stepIndex) => {
    if (stepIndex <= 0) { setActive(false); showSpeedup(false); note.textContent = 'Every token pays every parameter — that’s the dense tax.'; }
    else if (stepIndex === 1) { setActive(true); showSpeedup(false); note.textContent = 'Each token visits ONE expert. Total parameters grow; per-token FLOPs don’t.'; }
    else { setActive(true); showSpeedup(true); note.textContent = `${speedup}× faster pre-training at equal compute (paper, Table 1). Ask about ACTIVE parameters, not headline size.`; }
  };
}
