/**
 * rlhf.js — the three-step InstructGPT pipeline (SPEC §6 scrolly tier).
 * SFT → reward model → PPO lights up stage by stage; the final step reveals
 * the human-preference win rates from the paper's tabulated results.
 */
export async function init(panel) {
  let data;
  try { data = await (await fetch('../data/rlhf/figure.json')).json(); } catch { data = null; }
  const wins = (data?.series?.find((s) => s.id === 'headline-win-rates')?.points || [
    { label: 'vs 175B GPT-3', value: 85 },
    { label: 'vs few-shot GPT-3', value: 71 },
  ]).map((p) => ({ label: p.label.replace(/^175B InstructGPT /, '').replace('few-shot 175B GPT-3', 'few-shot GPT-3'), value: p.value }));

  const stages = [
    ['1', 'SFT', 'fine-tune on human demonstrations'],
    ['2', 'reward model', 'learn from ranked comparisons'],
    ['3', 'PPO', 'optimise against the reward'],
  ];

  panel.innerHTML = `
    <div class="widget-head">
      <p class="kicker"><span class="cat">alignment as a product layer</span> · the 3-step pipeline</p>
      <span class="status-chip status-chip--live">live</span>
    </div>
    <svg viewBox="0 0 620 170" role="img" aria-label="Three-stage pipeline: supervised fine-tuning, then a reward model trained on human rankings, then PPO reinforcement learning against that reward." style="width:100%;height:auto;display:block">
      ${stages.map((s, i) => {
        const x = 30 + i * 200;
        return `<g data-stage="${i}" opacity="0.4">
          <rect x="${x}" y="40" width="160" height="66" rx="10" fill="var(--surface-2)" stroke="var(--border)" data-box/>
          <text x="${x + 80}" y="66" font-family="JetBrains Mono, monospace" font-size="11" fill="var(--muted)" text-anchor="middle">step ${s[0]}</text>
          <text x="${x + 80}" y="86" font-family="Inter, sans-serif" font-size="14" fill="var(--text)" text-anchor="middle">${s[1]}</text>
          <text x="${x + 80}" y="122" font-family="Inter, sans-serif" font-size="10.5" fill="var(--muted)" text-anchor="middle">${s[2]}</text>
        </g>${i < 2 ? `<line x1="${x + 160}" y1="73" x2="${x + 200}" y2="73" stroke="var(--muted)" stroke-width="1.5"/>` : ''}`;
      }).join('')}
    </svg>
    <div data-wins hidden>
      <p class="breakit-note" data-winnote></p>
      <div data-bars></div>
    </div>
    <p class="breakit-note" data-note>A raw language model predicts text. It does not try to help you.</p>`;

  const setStage = (n) => panel.querySelectorAll('[data-stage]').forEach((g, i) => {
    const on = i < n;
    g.style.opacity = on ? '1' : '0.4';
    g.querySelector('[data-box]').setAttribute('stroke', on ? 'var(--cat-base)' : 'var(--border)');
    g.querySelector('[data-box]').setAttribute('fill', on ? 'color-mix(in srgb, var(--cat-base) 16%, var(--surface-2))' : 'var(--surface-2)');
  });

  const barsEl = panel.querySelector('[data-bars]');
  barsEl.innerHTML = wins.map((wv) => `
    <div class="rlhf-bar"><span class="rlhf-bar-lbl">${wv.label}</span>
      <span class="rlhf-bar-track"><span class="rlhf-bar-fill" style="width:0%" data-w="${wv.value}"></span></span>
      <span class="rlhf-bar-val num">${wv.value}%</span></div>`).join('');

  const note = panel.querySelector('[data-note]');
  const winsBox = panel.querySelector('[data-wins]');

  return (stepIndex) => {
    if (stepIndex <= 0) { setStage(0); winsBox.hidden = true; note.textContent = 'A raw language model predicts text. It does not try to help you.'; }
    else if (stepIndex === 1) { setStage(3); winsBox.hidden = true; note.textContent = 'Demonstrations → ranked comparisons → RL against the learned reward.'; }
    else if (stepIndex === 2) {
      setStage(3); winsBox.hidden = false; note.textContent = '';
      panel.querySelector('[data-winnote]').textContent = 'Labelers preferred the 1.3B instruct model over 175B GPT-3 — 100× fewer parameters. And on the API distribution:';
      requestAnimationFrame(() => barsEl.querySelectorAll('[data-w]').forEach((b) => { b.style.width = b.dataset.w + '%'; }));
    } else {
      setStage(3); winsBox.hidden = false;
      note.textContent = 'When vendors "feel" different, you are feeling the reward model — sycophancy, hedging, refusal style are its artifacts. Eval for them.';
    }
  };
}
