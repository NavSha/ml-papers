/**
 * main.js — entry point for every page (SPEC §2 eng rules 1–4).
 * Detects page type and boots the right modules:
 *  - index (has #timeline): spine curve + timeline enhancements
 *  - paper page (body[data-slug]): chrome, scrollytelling, lazy widget boot
 * Widgets follow the contract: async init(panel) → optional (stepIndex)=>{}.
 */

import { initScrolly } from './scroll.js';

const timeline = document.getElementById('timeline');
const slug = document.body.dataset.slug;

if (timeline) {
  import('./spine.js').then((m) => m.initSpine(timeline)).catch((e) => console.error('spine failed', e));
  import('./timeline.js').then((m) => m.initTimeline(timeline)).catch((e) => console.error('timeline failed', e));
}

if (slug) {
  import('./components.js').then((m) => m.initComponents(slug)).catch((e) => console.error('components failed', e));
}

/* Scrollytelling + lazy widget boot (one widget per paper page at most). */
const scrollies = [...document.querySelectorAll('.scrolly')];
const widgetPanel = document.querySelector('.widget-panel[data-widget]');

let stepCallback = null;
let pendingStep;
let booted = false;

const bootWidget = async () => {
  if (booted || !widgetPanel) return;
  booted = true;
  const name = widgetPanel.dataset.widget;
  try {
    const mod = await import(`./widgets/${name}.js`);
    stepCallback = await mod.init(widgetPanel);
    if (stepCallback && pendingStep !== undefined) stepCallback(pendingStep);
  } catch (err) {
    widgetPanel.querySelector('.placeholder')?.replaceChildren(
      document.createTextNode('this demo could not load — ' + err.message));
    console.error(`widget ${name} failed to boot`, err);
  }
};

if (widgetPanel) {
  new IntersectionObserver((entries, obs) => {
    if (entries.some((e) => e.isIntersecting)) { bootWidget(); obs.disconnect(); }
  }, { rootMargin: '600px 0px' }).observe(widgetPanel);
}

for (const el of scrollies) {
  initScrolly(el, (stepIndex) => {
    pendingStep = stepIndex;
    if (stepCallback) stepCallback(stepIndex);
  });
}
