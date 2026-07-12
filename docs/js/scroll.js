/**
 * Scrollytelling machinery: IntersectionObserver-driven step activation.
 * Ported from taylor-transformer (SPEC §2 eng rule 4).
 *
 * Each .scrolly block has .steps > .step elements and a .sticky panel.
 * The intersecting step closest to the viewport center gets .is-active;
 * the optional callback receives (stepIndex, stepEl).
 */

export function initScrolly(root, onStep = null) {
  const steps = [...root.querySelectorAll('.step')];
  if (!steps.length) return;

  let activeIndex = -1;

  const activate = (index) => {
    if (index === activeIndex) return;
    activeIndex = index;
    steps.forEach((s, i) => s.classList.toggle('is-active', i === index));
    if (onStep) onStep(index, steps[index]);
  };

  const observer = new IntersectionObserver(
    (entries) => {
      const mid = window.innerHeight / 2;
      let best = null;
      let bestDist = Infinity;
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        const r = entry.boundingClientRect;
        const dist = Math.abs(r.top + r.height / 2 - mid);
        if (dist < bestDist) { bestDist = dist; best = entry.target; }
      }
      if (best) activate(steps.indexOf(best));
    },
    { rootMargin: '-30% 0px -30% 0px', threshold: [0, 0.25, 0.5, 0.75, 1] }
  );

  steps.forEach((s) => observer.observe(s));
  activate(0);
  return observer;
}
