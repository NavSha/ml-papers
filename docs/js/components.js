/**
 * components.js — paper-page chrome ONLY (SPEC §2 prose ownership: no
 * editorial text here, ever). Owns:
 *  - minimap shell injection + spine.renderMinimap (eng rule 10)
 *  - copy-citation button wiring (format fixed by SPEC §2, baked in data-cite)
 *  - fast-path handoff href swapping (SPEC §4 terminals)
 * Every placeholder keeps its hard-coded static fallback in HTML.
 */

import { renderMinimap } from './spine.js';

/* SPEC §4: transformer prev → index; rlhf next → build.html. */
const FASTPATH_ROUTES = {
  'transformer':  { prev: '../index.html',        next: 'scaling-laws.html' },
  'scaling-laws': { prev: 'transformer.html',     next: 'rlhf.html' },
  'rlhf':         { prev: 'scaling-laws.html',    next: '../build.html' },
};

async function initMinimap(slug) {
  const el = document.querySelector('[data-minimap]');
  if (!el) return;
  try {
    const res = await fetch('../papers.json');
    const data = await res.json();
    renderMinimap(el, data.papers, slug);
  } catch (err) {
    console.error('minimap could not load', err); // static "← timeline" fallback remains
  }
}

function initCopyCitation() {
  const btn = document.querySelector('.chip-copy[data-cite]');
  if (!btn || !navigator.clipboard) return;
  btn.hidden = false;
  btn.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(btn.dataset.cite);
      const label = btn.textContent;
      btn.textContent = 'copied ✓';
      setTimeout(() => { btn.textContent = label; }, 1600);
    } catch { /* clipboard denied — the link fallback remains */ }
  });
}

function initFastPathHandoff(slug) {
  if (localStorage.getItem('mlp.fastpath') !== '1') return;
  const routes = FASTPATH_ROUTES[slug];
  if (!routes) return;
  const prev = document.querySelector('[data-handoff="prev"]');
  const next = document.querySelector('[data-handoff="next"]');
  if (prev) prev.href = routes.prev;
  if (next) next.href = routes.next;
  const handoff = document.querySelector('.handoff-nav') || next?.closest('.handoff');
  if (handoff && !handoff.querySelector('.chip-fastpath')) {
    const chip = document.createElement('span');
    chip.className = 'chip chip-fastpath';
    chip.textContent = 'fast path on';
    handoff.append(chip);
  }
}

export function initComponents(slug) {
  initMinimap(slug);
  initCopyCitation();
  initFastPathHandoff(slug);
}
