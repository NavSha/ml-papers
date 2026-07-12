/**
 * stable-diffusion.js — forward-process scrubber (SPEC §6d; frames baked by
 * tools/bake_diffusion_strip.py, provenance in data/stable-diffusion/manifest.json).
 *
 * Scrub t over 12 baked frames of forward noising (linear β 1e-4→0.02, T=1000).
 * Latent-vs-pixel toggle swaps 64px variants rendered pixelated at the same
 * display size — a SCALE illustration, not a real VAE latent (manifest note).
 * Break-it: "shuffle the noise" swaps to the second baked seed — same photo,
 * unrelated noise at every t. The information is destroyed, not hidden.
 */

const DATA = '../data/stable-diffusion';

const SHUFFLED_NOTE =
  'same photo, completely different noise at every step — the information is ' +
  'destroyed, not hidden; there is no image lurking in the static. Generation ' +
  'starts from exactly this.';

export async function init(panel) {
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const manifest = await (await fetch(`${DATA}/manifest.json`)).json();
  const TS = manifest.timesteps; // [0, 40, …, 999]
  const T = manifest.schedule?.T ?? 1000;
  const FALLBACK_T = manifest.seedFallbackBelowT ?? 0;
  console.assert(Array.isArray(TS) && TS.length === 12, 'stable-diffusion: expected 12 timesteps', TS);

  /* √ᾱ_t (photo weight) and √(1−ᾱ_t) (noise weight) from the baked schedule */
  const abar = new Float64Array(T + 1);
  abar[0] = 1;
  for (let i = 0; i < T; i++) abar[i + 1] = abar[i] * (1 - (1e-4 + (0.02 - 1e-4) * i / (T - 1)));
  const mix = (t) => ({ sig: Math.sqrt(abar[t]), noi: Math.sqrt(1 - abar[t]) });

  /* frame URLs — seed 1 was baked only for t ≥ seedFallbackBelowT (the two
     draws are visually identical below it), so fall back to seed 0 there */
  const url = (i, sd, lat) => {
    const t = TS[i];
    const dir = sd === 1 && t >= FALLBACK_T ? 'seed1' : 'seed0';
    return `${DATA}/${dir}/t${String(t).padStart(4, '0')}${lat ? '_64' : ''}.webp`;
  };

  const cache = new Map();
  const preload = (u) => { if (!cache.has(u)) { const im = new Image(); im.src = u; cache.set(u, im); } };

  panel.innerHTML = `
    <div class="widget-head">
      <p class="kicker"><span class="cat">the forward process</span> · destroy a photo yourself</p>
      <span class="chip" title="noising schedule used by the baker">β linear 1e-4→0.02 · T = 1000</span>
    </div>

    <figure class="widget-frame">
      <img src="${url(0, 0, false)}" width="480" height="480" decoding="async"
           alt="The Blue Marble photo, untouched (t = 0)">
    </figure>

    <label class="widget-label">noising step
      <input type="range" data-in="t" min="0" max="${TS.length - 1}" step="1" value="0"
             aria-valuetext="t = 0 of 1000">
      <span class="num" data-out="t" aria-live="off">t = 0 / 1000</span></label>

    <div class="widget-tabs" role="group" aria-label="view scale">
      <button class="chip" type="button" data-view="pixel" aria-pressed="true">pixel space · 512×512</button>
      <button class="chip" type="button" data-view="latent" aria-pressed="false">latent scale · 64×64</button>
    </div>

    <div class="widget-readouts" aria-live="polite">
      <p title="√ᾱ_t·x₀ + √(1−ᾱ_t)·ε, from the manifest's linear β schedule">
        what the model sees:
        <strong class="num" data-out="sig"></strong>·photo +
        <strong class="num" data-out="noi"></strong>·noise ·
        draw <strong class="num" data-out="seed">#0</strong></p>
      <p data-out="arith" hidden>64×64×4 = <strong class="num">16,384</strong> numbers
        vs 512×512×3 = <strong class="num">786,432</strong> —
        ~48× less work on every one of ~50 denoising steps.</p>
      <p class="breakit-note" data-out="latentnote" hidden></p>
    </div>

    <button class="btn-primary" type="button" data-shuffle aria-pressed="false">shuffle the noise</button>
    <div aria-live="polite"><p class="breakit-note" data-out="shufflenote"></p></div>

    <p class="widget-attrib">photo:
      <a href="${manifest.source?.url ?? 'https://commons.wikimedia.org/wiki/File:The_Earth_seen_from_Apollo_17.jpg'}"
         rel="noopener">NASA Blue Marble</a> (Apollo 17) — public domain.</p>`;

  const $ = (sel) => panel.querySelector(sel);
  const out = {}; panel.querySelectorAll('[data-out]').forEach((e) => { out[e.dataset.out] = e; });
  const img = $('.widget-frame img');
  const slider = $('[data-in="t"]');
  const viewBtns = [...panel.querySelectorAll('[data-view]')];
  const shuffleBtn = $('[data-shuffle]');
  out.latentnote.textContent = manifest.note ?? '64px variants illustrate latent-space scale; they are downsamples, not a real VAE latent.';

  let idx = 0, seed = 0, latent = false, everShuffled = false;
  let gen = 0;   // cancels in-flight scripted scrubs on any user input
  let rafId = 0; // coalesce updates: one rAF write per frame

  const render = () => {
    rafId = 0;
    const t = TS[idx];
    img.src = url(idx, seed, latent);
    img.classList.toggle('is-latent', latent);
    img.alt = (t === 0 ? 'The Blue Marble photo, untouched (t = 0)'
      : `The Blue Marble photo after ${t} of 1000 forward-noising steps`)
      + (latent ? ', shown at 64×64 latent scale' : '')
      + (seed === 1 ? ', noise draw #1' : '');
    out.t.textContent = `t = ${t} / 1000`;
    slider.setAttribute('aria-valuetext', `t = ${t} of 1000`);
    const m = mix(t);
    out.sig.textContent = m.sig.toFixed(2);
    out.noi.textContent = m.noi.toFixed(2);
    out.seed.textContent = '#' + seed;
    out.arith.hidden = !latent;
    out.latentnote.hidden = !latent;
    out.shufflenote.textContent = seed === 1
      ? SHUFFLED_NOTE + (t < FALLBACK_T
          ? ` (Below t = ${FALLBACK_T} the noise is too faint to tell draws apart — the strip reuses draw #0.)`
          : '')
      : everShuffled ? 'back to the first noise draw — scrub and compare the static.' : '';
    /* preload adjacent frames + the counterpart seed/scale at this t */
    if (idx > 0) preload(url(idx - 1, seed, latent));
    if (idx < TS.length - 1) preload(url(idx + 1, seed, latent));
    preload(url(idx, 1 - seed, latent));
    preload(url(idx, seed, !latent));
  };
  const schedule = () => { if (!rafId) rafId = requestAnimationFrame(render); };

  /* scripted scrub for scroll beats: steps through the strip like a flipbook;
     reduced motion jumps straight to the final frame */
  const animateTo = (target) => {
    gen++;
    if (reduced || Math.abs(target - idx) <= 1) { idx = target; slider.value = idx; schedule(); return; }
    const g = gen, dir = Math.sign(target - idx);
    let last = 0;
    const step = (ts) => {
      if (g !== gen) return;
      if (ts - last >= 70) { last = ts; idx += dir; slider.value = idx; schedule(); }
      if (idx !== target) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  };

  /* ——— wiring ——— */
  slider.addEventListener('input', () => { gen++; idx = +slider.value; schedule(); });
  viewBtns.forEach((b) => b.addEventListener('click', () => {
    latent = b.dataset.view === 'latent';
    viewBtns.forEach((x) => x.setAttribute('aria-pressed', String((x.dataset.view === 'latent') === latent)));
    schedule();
  }));
  shuffleBtn.addEventListener('click', () => {
    seed = 1 - seed;
    everShuffled = true;
    shuffleBtn.setAttribute('aria-pressed', String(seed === 1));
    schedule();
  });
  render();

  /* scroll-driven story beats (widget-tier scrolly contract) */
  return (stepIndex) => {
    if (stepIndex === 0) animateTo(0);
    if (stepIndex === 1) animateTo(TS.indexOf(300));
    if (stepIndex >= 2) animateTo(TS.length - 1);
    if (stepIndex === 3 && seed === 0) shuffleBtn.click();
  };
}
