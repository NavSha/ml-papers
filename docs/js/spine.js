/**
 * spine.js — the descending loss curve (DESIGN §7).
 *
 * initSpine(section): draws the index curve inside .spine-rail from MEASURED
 * node-card positions (ResizeObserver + document.fonts.ready — never
 * hardcoded), scroll-drives stroke-dashoffset with one rAF write per frame,
 * and handles the 15th-node reveal. prefers-reduced-motion renders the curve
 * fully drawn and reveals the 15th node immediately.
 *
 * renderMinimap(el, papers, currentSlug): the horizontal mini-spine used on
 * paper pages (DESIGN §8), called by components.js.
 */

const SVG_NS = 'http://www.w3.org/2000/svg';
const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');

/* x-position encodes loss: high/right at 2012 → low/left at 2025 (DESIGN §7).
   Exponential decay shaped like a real training curve. */
function lossX(t, railW) {
  return railW * (0.16 + 0.68 * Math.exp(-2.4 * t));
}

function smoothPath(pts) {
  if (!pts.length) return '';
  let d = `M ${pts[0].x.toFixed(1)} ${pts[0].y.toFixed(1)}`;
  for (let i = 1; i < pts.length; i++) {
    const a = pts[i - 1], b = pts[i];
    const my = (a.y + b.y) / 2;
    d += ` C ${a.x.toFixed(1)} ${my.toFixed(1)}, ${b.x.toFixed(1)} ${my.toFixed(1)}, ${b.x.toFixed(1)} ${b.y.toFixed(1)}`;
  }
  return d;
}

export function initSpine(section) {
  const rail = section.querySelector('.spine-rail');
  const cards = [...section.querySelectorAll('.node-card')];
  const youNode = section.querySelector('[data-you-node]');
  if (!rail || !cards.length) return;

  const svg = document.createElementNS(SVG_NS, 'svg');
  svg.classList.add('spine-svg');
  svg.setAttribute('aria-hidden', 'true');
  const back = document.createElementNS(SVG_NS, 'path');   // undrawn, ahead of scroll
  back.classList.add('spine-path--undrawn');
  const front = document.createElementNS(SVG_NS, 'path');  // drawn, behind scroll
  front.classList.add('spine-path--drawn');
  const dotsGroup = document.createElementNS(SVG_NS, 'g');
  svg.append(back, front, dotsGroup);
  rail.replaceChildren(svg);

  let pathLength = 0;
  let target = 0;
  let current = 0;
  let parked = true;

  const measure = () => {
    const railBox = rail.getBoundingClientRect();
    const secTop = section.getBoundingClientRect().top;
    const railW = railBox.width;
    const T0 = 2012.9, T1 = 2026.0;      // AlexNet → the 15th node
    const nodes = cards.map((card) => {
      const r = card.getBoundingClientRect();
      const [y0, m0] = card.dataset.date.split('-').map(Number);
      return {
        y: r.top - secTop + r.height / 2,
        t: Math.min(1, Math.max(0, (y0 + (m0 - 1) / 12 - T0) / (T1 - T0))),
        cat: card.dataset.cat,
        slug: card.dataset.slug,
        live: !!card.querySelector('.chip-live'),
      };
    });
    if (youNode) {
      const r = youNode.getBoundingClientRect();
      nodes.push({ y: r.top - secTop + r.height / 2, t: 1, cat: null, slug: 'you', you: true });
    }
    const pts = nodes.map((n) => ({ ...n, x: lossX(n.t, railW) }));
    const sectionH = section.getBoundingClientRect().height;
    svg.setAttribute('viewBox', `0 0 ${railW} ${sectionH}`);

    const d = smoothPath(pts);
    back.setAttribute('d', d);
    front.setAttribute('d', d);
    pathLength = front.getTotalLength();
    front.style.strokeDasharray = pathLength;
    front.style.strokeDashoffset = reduced.matches ? 0 : pathLength * (1 - progress());

    dotsGroup.replaceChildren(...pts.map((p) => {
      const c = document.createElementNS(SVG_NS, 'circle');
      c.setAttribute('cx', p.x); c.setAttribute('cy', p.y);
      c.setAttribute('r', p.you ? 7 : p.live ? 6 : 5);
      c.classList.add('spine-node');
      if (p.you) c.classList.add('spine-node--you');
      if (p.live) c.classList.add('spine-node--live');
      if (p.cat) c.setAttribute('data-cat', p.cat);
      c.setAttribute('data-dot', p.slug);
      return c;
    }));
  };

  const progress = () => {
    const r = section.getBoundingClientRect();
    const total = r.height - window.innerHeight * 0.4;
    return Math.min(1, Math.max(0, (window.innerHeight * 0.6 - r.top) / total));
  };

  const tick = () => {
    const delta = target - current;
    if (Math.abs(delta) < 0.5) { parked = true; return; }
    current += delta * 0.15;
    front.style.strokeDashoffset = pathLength * (1 - current);
    requestAnimationFrame(tick);
  };

  const onScroll = () => {
    if (reduced.matches) return;
    target = progress();
    if (parked) { parked = false; requestAnimationFrame(tick); }
  };

  document.fonts.ready.then(() => {
    measure();
    new ResizeObserver(measure).observe(section);
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  });

  /* 15th-node reveal: unlabeled at rest, caption fades in on approach.
     Ships revealed in static HTML for JS-off; we strip it at boot. */
  if (youNode) {
    if (reduced.matches) return; // stays revealed
    youNode.classList.remove('is-revealed');
    new IntersectionObserver((entries, obs) => {
      if (entries.some((e) => e.isIntersecting)) {
        youNode.classList.add('is-revealed');
        svg.querySelector('.spine-node--you')?.classList.add('is-revealed');
        obs.disconnect();
      }
    }, { rootMargin: '0px 0px -30% 0px' }).observe(youNode);
  }
}

/** Horizontal mini-spine for paper pages. papers = papers.json "papers" array. */
export function renderMinimap(el, papers, currentSlug) {
  const rail = document.createElement('div');
  rail.className = 'minimap-rail';
  const frag = document.createDocumentFragment();

  const dot = (href, slug, cat, label, extra = '') => {
    const a = document.createElement('a');
    a.className = `mm-dot ${extra}`.trim();
    a.href = href;
    a.title = label;
    if (cat) a.setAttribute('data-cat', cat);
    if (slug === currentSlug) {
      a.classList.add('is-current');
      a.setAttribute('aria-current', 'page');
      const name = document.createElement('span');
      name.className = 'mm-label';
      name.textContent = label;
      a.append(name);
    }
    let checked = [];
    try { checked = JSON.parse(localStorage.getItem(`mlp.ladder.${slug}`) || '[]'); } catch { /* ignore */ }
    if (Array.isArray(checked) && checked.length) a.classList.add('is-checked');
    return a;
  };

  for (const p of papers) {
    frag.append(dot(`${p.slug}.html`, p.slug, p.category, p.nickname));
  }
  frag.append(dot('../build.html', 'you', null, '2026: you', 'mm-dot-you'));
  rail.append(frag);
  el.append(rail);
}
