/**
 * constitutional-ai.js — the two-phase RLAIF pipeline (SPEC §6 scrolly tier).
 * Phase 1 (critique → revise → SFT) and Phase 2 (AI comparisons → preference
 * model → RL) light stage by stage. Verbatim constitution principles from the
 * paper's appendix (2212.08073 App. C.1/C.2) surface as paper-chips.
 * No figure.json — the diagram is rendered from static structure.
 */
export async function init(panel) {
  const P1 = [
    ['critique', 'the model flags what is harmful in its own answer'],
    ['revise', 'it rewrites the answer to remove the harm'],
    ['SFT', 'fine-tune on the revised answers'],
  ];
  const P2 = [
    ['AI compares', 'an AI ranks response pairs against the principles'],
    ['preference model', 'trained on those AI judgments'],
    ['RL', 'optimise against the preference model'],
  ];

  panel.innerHTML = `
    <div class="widget-head">
      <p class="kicker"><span class="cat">governance as a config file</span> · two phases</p>
      <span class="status-chip status-chip--live">live</span>
    </div>
    <svg viewBox="0 0 620 210" role="img" aria-label="Two phases. Phase one: critique, revise, supervised fine-tuning. Phase two: AI comparisons, preference model, reinforcement learning." style="width:100%;height:auto;display:block">
      <text x="12" y="24" font-family="JetBrains Mono, monospace" font-size="11" fill="var(--muted)">phase 1 — self-revision</text>
      ${P1.map((s, i) => stage(i, 0, s)).join('')}
      <text x="12" y="130" font-family="JetBrains Mono, monospace" font-size="11" fill="var(--muted)">phase 2 — RLAIF</text>
      ${P2.map((s, i) => stage(i, 1, s)).join('')}
    </svg>
    <div class="paper-chip cai-principle" data-principle hidden>
      <span class="chip-tab">arXiv 2212.08073 · App. C</span>
      <p class="chip-quote"></p>
      <p class="chip-meta" data-pmeta></p>
    </div>
    <p class="breakit-note" data-note>Tens of thousands of human harmlessness labels — slow, opaque, inconsistent.</p>`;

  function stage(i, row, s) {
    const x = 30 + i * 200, y = 34 + row * 106;
    return `<g data-stage="${row}-${i}" opacity="0.4">
      <rect x="${x}" y="${y}" width="160" height="58" rx="10" fill="var(--surface-2)" stroke="var(--border)" data-box/>
      <text x="${x + 80}" y="${y + 26}" font-family="Inter, sans-serif" font-size="13" fill="var(--text)" text-anchor="middle">${s[0]}</text>
      <text x="${x + 80}" y="${y + 44}" font-family="Inter, sans-serif" font-size="10" fill="var(--muted)" text-anchor="middle">${s[1].slice(0, 42)}</text>
    </g>${i < 2 ? `<line x1="${x + 160}" y1="${y + 29}" x2="${x + 200}" y2="${y + 29}" stroke="var(--muted)" stroke-width="1.5"/>` : ''}`;
  }

  const lightRow = (row, on) => panel.querySelectorAll(`[data-stage^="${row}-"]`).forEach((g) => {
    g.style.opacity = on ? '1' : '0.4';
    g.querySelector('[data-box]').setAttribute('stroke', on ? 'var(--cat-base)' : 'var(--border)');
    g.querySelector('[data-box]').setAttribute('fill', on ? 'color-mix(in srgb, var(--cat-base) 16%, var(--surface-2))' : 'var(--surface-2)');
  });

  const chip = panel.querySelector('[data-principle]');
  const quote = chip.querySelector('.chip-quote');
  const pmeta = chip.querySelector('[data-pmeta]');
  const note = panel.querySelector('[data-note]');
  const showPrinciple = (text, ref) => { chip.hidden = false; quote.textContent = '“' + text + '”'; pmeta.textContent = ref; };

  return (stepIndex) => {
    if (stepIndex <= 0) {
      lightRow(0, false); lightRow(1, false); chip.hidden = true;
      note.textContent = 'Tens of thousands of human harmlessness labels — slow, opaque, inconsistent.';
    } else if (stepIndex === 1) {
      lightRow(0, true); lightRow(1, false);
      note.textContent = 'The model critiques and revises itself against written principles:';
      showPrinciple("Identify specific ways in which the assistant's last response is harmful, unethical, racist, sexist, toxic, dangerous, or illegal.", 'critique principle · Appendix C.1');
    } else if (stepIndex === 2) {
      lightRow(0, true); lightRow(1, true);
      note.textContent = 'An AI ranks responses against the constitution — humans still write it and all the helpfulness labels:';
      showPrinciple('Please choose the response that is as harmless and ethical as possible. Do NOT choose responses that are toxic, racist, or sexist.', 'comparison principle · Appendix C.2');
    } else {
      lightRow(0, true); lightRow(1, true);
      note.textContent = 'The result: less harmful without refusing more. Write your agent guardrails as testable principles — auditable, diffable.';
    }
  };
}
