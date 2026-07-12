/**
 * timeline.js — index-only enhancement (SPEC §4). Owns:
 *  - time-proportional node spacing (DESIGN §7; static spacing is the JS-off fallback)
 *  - the fast-path toggle (localStorage contract: mlp.fastpath = "1")
 *  - ladder checkmarks on node cards (mlp.ladder.{slug} — SPEC §2 contract)
 * Editorial prose is never touched here (SPEC §2 prose ownership).
 */

const FASTPATH = ['transformer', 'scaling-laws', 'rlhf'];

function applySpacing(section) {
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const desktop = window.matchMedia('(min-width: 780px)').matches;
  const perYear = desktop ? 220 : 110;   // --time-scale
  const MIN = 96, MAXPERYEAR = 480;
  const cards = [...section.querySelectorAll('.node-card')];
  let prevDate = null;
  for (const card of cards) {
    const [y, m] = card.dataset.date.split('-').map(Number);
    const t = y + (m - 1) / 12;
    if (prevDate !== null) {
      const years = Math.max(0, t - prevDate);
      const gap = Math.min(Math.max(years * perYear, MIN), MAXPERYEAR * Math.max(years, 1));
      card.style.marginTop = `${Math.round(gap)}px`;
    }
    prevDate = t;
  }
  void reduced; // spacing applies regardless; only motion is gated elsewhere
}

function initFastPath() {
  const btn = document.querySelector('[data-fastpath]');
  if (!btn) return;
  btn.hidden = false;

  const apply = (on) => {
    btn.setAttribute('aria-pressed', String(on));
    document.body.classList.toggle('fastpath-on', on);
    for (const slug of FASTPATH) {
      document.querySelector(`.node-card[data-slug="${slug}"]`)?.classList.toggle('is-fastpath', on);
    }
  };

  let on = localStorage.getItem('mlp.fastpath') === '1';
  apply(on);
  btn.addEventListener('click', () => {
    on = !on;
    if (on) localStorage.setItem('mlp.fastpath', '1');
    else localStorage.removeItem('mlp.fastpath');
    apply(on);
  });
}

function initCheckmarks(section) {
  for (const check of section.querySelectorAll('.node-check[data-check]')) {
    const slug = check.dataset.check;
    let arr = [];
    try { arr = JSON.parse(localStorage.getItem(`mlp.ladder.${slug}`) || '[]'); } catch { /* ignore */ }
    if (Array.isArray(arr) && arr.length) {
      check.hidden = false;
      check.removeAttribute('aria-hidden');
      check.setAttribute('aria-label', 'built on this device');
    }
  }
}

export function initTimeline(section) {
  applySpacing(section);
  window.matchMedia('(min-width: 780px)').addEventListener('change', () => applySpacing(section));
  initFastPath();
  initCheckmarks(section);
}
