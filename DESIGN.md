# DESIGN.md — "The Fourteen" design system (source of truth)

Locked at CP0 per SPEC §3. **Every visual decision in `docs/css/site.css` and every widget derives from this file.**
Zero hardcoded colors outside the token block; if a value isn't here, add it here first.

## 0. Identity — the third sibling

- taylor-transformer = warm amber `#120E0B`, "the machine learns to write."
- dogs-vs-cats = cool cyan `#080b12`, "the machine learns to see."
- **ml-papers = dark graphite `#0C0D0F`, "how we got here."** Near-neutral ground sitting between the siblings' temperatures (R−B = −3, vs taylor's +7 warm and dogs' −10 cool). Same structural DNA: dark scrollytelling, sticky panels, mono kickers, panel recipe, feTurbulence grain, footer cross-links.
- **Signature rule ("The Paper Speaks"):** whenever the paper itself speaks — citation headers, attributed quotes, redrawn-figure captions — it appears on a **cream paper-chip in system serif** (§4), light-on-dark inverted against the graphite ground. The narrator speaks in Literata/Inter on graphite. This is the site's equivalent of taylor's "Two Voices" and it is non-negotiable.
- **Color logic:** chronology owns position; **category owns color** (five accent quads, §3, remapped via `[data-cat]`). Acts own only era bands + gap captions, which stay neutral graphite.
- Numbers always get engineering suffixes (91M, 1.4T, $2.6k) and always render in mono.

## 1. Ground palette (neutral graphite)

```css
:root {
  --ground:    #0C0D0F;   /* page background; <meta name="theme-color"> */
  --surface:   #141519;   /* cards, panels */
  --surface-2: #1B1D23;   /* nested chrome: chips, rungs, code, inputs */
  --border:    #262A31;   /* 1px hairlines everywhere */
  --line:      #1B1D23;   /* sub-hairline: act band edges, minimap rail */
  --text:      #E8EAED;   /* primary text */
  --muted:     #9BA1A9;   /* secondary text, captions, meta */
  --ok:        #4CC38A;   /* semantic: ladder checkmarks, pass states */
  --warn:      #E2B93B;   /* semantic: caveats, estimate labels */
  --err:       #E5646E;   /* semantic: failed loads, break-it verdicts */
}
```

Computed contrast (WCAG, vs stated background):

| pair | ratio | AA requirement at usage size |
|---|---|---|
| `--text` on `--ground` | **16.13** | 4.5 ✓ |
| `--muted` on `--ground` | **7.47** | 4.5 ✓ |
| `--text` on `--surface` | **15.14** | 4.5 ✓ |
| `--muted` on `--surface` | **7.01** | 4.5 ✓ |
| `--text` on `--surface-2` | **13.98** | 4.5 ✓ |
| `--muted` on `--surface-2` | **6.47** | 4.5 ✓ |

Background depth: one fixed radial glow only — `background: radial-gradient(1200px 800px at 70% -10%, rgba(215,219,225,.04), transparent 60%), var(--ground);` on `body`. No per-category glows.

## 2. Category accent quads

Applied via remap so every component authored against `--cat-*` retheme automatically:

```css
:root, [data-cat] {         /* neutral default (index chrome, colophon, 404) */
  --cat-base:  #D7DBE1;
  --cat-deep:  #565C66;
  --cat-light: #EDEFF2;
  --cat-grad:  linear-gradient(135deg, #565C66, #D7DBE1);
}
body[data-cat="foundations"],   [data-cat="foundations"]   { --cat-base:#F0954C; --cat-deep:#9C5A26; --cat-light:#FFC08A; --cat-grad:linear-gradient(135deg,#9C5A26,#F0954C 55%,#FFC08A); }
body[data-cat="llm-core"],      [data-cat="llm-core"]      { --cat-base:#A48FFF; --cat-deep:#6A55C2; --cat-light:#C9BCFF; --cat-grad:linear-gradient(135deg,#6A55C2,#A48FFF 55%,#C9BCFF); }
body[data-cat="making-useful"], [data-cat="making-useful"] { --cat-base:#4CC38A; --cat-deep:#2E7D57; --cat-light:#8FE6BC; --cat-grad:linear-gradient(135deg,#2E7D57,#4CC38A 55%,#8FE6BC); }
body[data-cat="beyond-text"],   [data-cat="beyond-text"]   { --cat-base:#E87BB0; --cat-deep:#A24775; --cat-light:#FFB3D4; --cat-grad:linear-gradient(135deg,#A24775,#E87BB0 55%,#FFB3D4); }
body[data-cat="for-builders"],  [data-cat="for-builders"]  { --cat-base:#D9B84A; --cat-deep:#8F7524; --cat-light:#EFD98C; --cat-grad:linear-gradient(135deg,#8F7524,#D9B84A 55%,#EFD98C); }
```

Paper pages set `data-cat` on `<body>`; index node cards set it per-card. Semantics: foundations = ember (the first fire), llm-core = iris (the scaling era), making-useful = green (aligned/OK), beyond-text = magenta (other senses), for-builders = gold (the workbench).

Computed contrast vs `--ground #0C0D0F` (vs `--surface` in parens):

| category | base (text at any size) | light (hover/emphasis text) | deep (non-text only) |
|---|---|---|---|
| foundations `#F0954C` | **8.43** ✓ (7.91) | `#FFC08A` **12.18** ✓ | `#9C5A26` **3.61** ✓ (≥3:1 non-text) |
| llm-core `#A48FFF` | **7.36** ✓ (6.91) | `#C9BCFF` **11.22** ✓ | `#6A55C2` **3.42** ✓ |
| making-useful `#4CC38A` | **8.78** ✓ (8.24) | `#8FE6BC` **13.16** ✓ | `#2E7D57` **3.88** ✓ |
| beyond-text `#E87BB0` | **7.31** ✓ (6.86) | `#FFB3D4` **11.71** ✓ | `#A24775` **3.42** ✓ |
| for-builders `#D9B84A` | **10.10** ✓ (9.47) | `#EFD98C` **13.86** ✓ | `#8F7524` **4.39** ✓ |

**Usage rules (binding):** `--cat-base` may set text at any size (all ≥ 4.5:1, AA normal text, even at 12px kickers). `--cat-deep` is **never a text color** — borders, fills, gradient stops, chart strokes only (all ≥ 3:1, passing WCAG 1.4.11 non-text contrast). `--cat-light` is for hover text, odometer digits, and chart emphasis. `--ok` shares its hex with making-useful base by design (aligned = OK); acceptable because checkmarks never sit on making-useful chips.

## 3. Typography — exactly three families

1. **Literata** (display serif — the narrator). Variable optical axis gives it real display presence at 84px and bookish warmth at 22px; it is the Google Books long-form serif, unmistakably "a thing made of reading." Distinct from taylor's Fraunces and dogs' Space Grotesk. Weights 400–700 + italic; set `font-optical-sizing: auto`.
2. **Inter** (body + UI). Weights 400/500/600.
3. **JetBrains Mono** (data, labels, kickers, arXiv IDs, readouts). Chosen over IBM Plex Mono (taylor's mono) for its taller x-height and unambiguous 0/O/1/l at the 11–13px sizes where this site's dense numeric readouts live.

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;700&family=Literata:ital,opsz,wght@0,7..72,400..700;1,7..72,400..700&display=swap" rel="stylesheet">
```

(The cream paper-chip uses a **system** serif stack — Charter/Georgia, §4 — deliberately not loaded from Google: the paper speaks in the reader's own print voice.)

### Type scale

| token | value | family/weight | line-height | letter-spacing |
|---|---|---|---|---|
| `--fs-display` (index hero) | `clamp(44px, 6.5vw, 84px)` | Literata 400 | 1.05 | −0.015em |
| `--fs-h1` (paper title) | `clamp(34px, 4.5vw, 56px)` | Literata 500 | 1.12 | −0.01em |
| `--fs-h2` (section heads, act titles) | `clamp(26px, 3.2vw, 36px)` | Literata 500 | 1.2 | 0 |
| `--fs-h3` (widget/sub heads) | `clamp(20px, 2.2vw, 24px)` | Inter 600 | 1.3 | 0 |
| `--fs-body` | `17px` | Inter 400 | 1.7 | 0 |
| `--fs-small` (consequence lines, captions) | `14px` | Inter 400 | 1.55 | 0 |
| `--fs-kicker` | `12px` | JetBrains Mono 500, uppercase | 1 | .18em |
| `--fs-chip` | `12px` | JetBrains Mono 500 | 1 | .02em |
| `--fs-data` (widget readouts) | `clamp(15px, 1.5vw, 18px)` | JetBrains Mono 500 | 1.4 | 0 |
| `--fs-odometer` ($ odometer, big numbers) | `clamp(28px, 3.4vw, 40px)` | JetBrains Mono 700 | 1.1 | −0.01em |

Heading accent device (sibling echo): one `<em>` word per display heading in Literata *italic*, colored `var(--cat-base)` (neutral silver on index). Reading column **680px**; page max **1120px**.

## 4. The paper-chip (signature component)

Cream inverted card used ONLY when the paper speaks: citation headers, attributed quotes, redrawn-figure captions, the constitutional-ai quoted principles.

```css
.paper-chip {
  --chip-ground: #F5EFE3;  /* cream */
  --chip-ink:    #21201B;  /* ink text — 14.25:1 on cream ✓ */
  --chip-muted:  #5C564A;  /* meta text — 6.36:1 on cream ✓ */
  background: var(--chip-ground);
  color: var(--chip-ink);
  border: 1px solid #E3DAC5;
  border-radius: 12px;
  padding: clamp(20px, 2.5vw, 28px);
  box-shadow: 0 12px 40px rgba(0,0,0,.55);
  font-family: Charter, 'Bitstream Charter', 'Sitka Text', Cambria, Georgia, 'Times New Roman', serif;
  font-size: 17px; line-height: 1.55;
}
```

- **arXiv-ID tab:** a file-folder tab attached above the chip's top-left corner. `background: #21201B; color: #F5EFE3;` (14.25:1 ✓), JetBrains Mono 11px, `letter-spacing: .08em`, `padding: 4px 10px`, `border-radius: 6px 6px 0 0`. Label follows the source per SPEC: `arXiv 1706.03762` / `NeurIPS 2012` / `openai.com`.
- Title inside chip: serif 600, 19px. Authors/venue line: `--chip-muted`, 15px. Quotes: serif italic. Figure captions: serif italic 15px `--chip-muted`.
- Links inside: `--chip-ink`, underlined, `text-underline-offset: 3px`.
- Copy-citation button: ghost chip styled per §8 but with ink borders (`1px solid rgba(33,32,27,.35)`), radius 8.
- Inside `.paper-chip`: `::selection { background:#21201B; color:#F5EFE3; }` and `:focus-visible { outline-color:#21201B; }`.
- The grain overlay (§10) passes over chips too — cream reads as paper stock, not a hole in the page.

## 5. Spacing, radii, shadows

- **8px base scale:** `--s1: 8px; --s2: 16px; --s3: 24px; --s4: 32px; --s5: 48px; --s6: 64px; --s7: 96px; --s8: 128px;`. Minimum 96px (`--s7`) between major sections on paper pages; timeline node spacing is time-proportional (§7) and overrides this on index.
- **Radii — never pill:** `--r1: 4px` (tags, tab corners), `--r2: 8px` (buttons, chips, rungs, inputs), `--r3: 12px` (panels, cards, paper-chips). Circles are permitted for spine/minimap **dots only** — dots are geometry, not pills.
- **Panel recipe** (all sticky visuals, widget frames, coda containers):
  `background: var(--surface); border: 1px solid var(--border); border-radius: var(--r3); box-shadow: 0 20px 60px rgba(0,0,0,.5); padding: clamp(20px, 3vw, 32px);`
  Widget panels add a header row: kicker (left) + status chip (right, e.g. `LIVE` in `--cat-base` or `PRICES AS OF 2026-07` in `--muted`).
- Card shadow (node cards, lighter): `0 12px 32px rgba(0,0,0,.35)`.

## 6. Kicker / chapter-marker

`font: 500 12px 'JetBrains Mono'; text-transform: uppercase; letter-spacing: .18em;`
Category word in `var(--cat-base)`, remainder in `var(--muted)`. Act/step numerals in `--muted`: e.g. `ACT III` / `05 · SCALING LAWS` / `STEP 02 / 04`. Every section, widget panel, and act band opens with one.

## 7. The spine (index) — the descending loss curve

- **Layout ≥780px:** two columns — spine rail column `clamp(280px, 30vw, 400px)` on the left, node cards `min(560px, 100%)` on the right. Within the rail, x-position encodes loss (2012 high/right → 2025 low/left); y encodes time.
- **Time scale:** `--time-scale: 220px` per year desktop, capped: minimum 96px between adjacent nodes (the 2021–22 pileup compresses but never collides), maximum 480px per empty year (the 2023–24 gap is felt, not endless). `<780px`: `--time-scale: 110px`.
- **Stroke:** `2.5px` desktop / `2px` mobile, `stroke-linecap: round`, `fill: none`.
  - Undrawn (ahead of scroll): `#565C66` at 45% opacity (decorative, non-content).
  - Drawn (behind scroll): `#D7DBE1` (13.99:1 on ground ✓) with glow `filter: drop-shadow(0 0 6px rgba(215,219,225,.35))` applied to the drawn path only. If the glow janks (per SPEC §11), drop the filter before dropping anything else.
  - The curve stays **neutral silver** for its whole length — category color lives in the node dots; the curve is the one thing all fourteen share.
- **Node dots** (SVG circles on the curve, one per paper + the 15th):
  - default: r=5px (10px Ø) fill `var(--cat-base)`, ring `2px` stroke `var(--ground)` (punches the dot off the curve).
  - hover/focus: scale 1.25, glow `0 0 10px color-mix(in srgb, var(--cat-base) 45%, transparent)`, 150ms.
  - **live** (`status:"live"`): r=6px + halo pulse — box-shadow ring expanding 0→8px and fading, 2.4s ease-out infinite.
  - **checked** (ladder progress via `mlp.ladder.*`): 14px badge offset top-right of the dot, fill `var(--ok)`, check glyph in `var(--ground)`.
  - **the 15th node**: hollow ring, r=7px, `2px dashed #D7DBE1` stroke, no fill, unlabeled at rest. On scroll-approach (node crosses 70% viewport height): fill animates to `#E8EAED` with glow `0 0 16px rgba(232,234,236,.5)` (400ms), caption "2026: you" fades in (400ms, 150ms delay), dashes fade out. It is the only white node — deliberately outside the category system, because it isn't a paper.
- **Mobile <780px (git-graph left rail):** curve straightens into a near-vertical line in a fixed 44px left gutter; cards take the remaining width; dots sit on the rail at 8px Ø; the 15th node keeps its ring treatment. Same draw-on-scroll behavior.
- Heights reserved pre-boot: the rail column gets its full computed height in static HTML/CSS so spine.js boot causes zero layout shift; path geometry is always measured from node DOM positions (ResizeObserver + `document.fonts.ready`), never hardcoded.

## 8. Components

### Node card (index)
`background: var(--surface); border: 1px solid var(--border); border-left: 3px solid var(--cat-base); border-radius: var(--r3); padding: 20px 24px;` shadow per §5. Anatomy: row 1 — year (JBM 13px `--muted`) + nickname (Literata 500 22px `--text`); hook (Inter 17px `--text`); consequence (Inter 14px `--muted`, above a `--line` hairline); chip row (gap 8px): minutes chip, buildChip, "interactive" chip, ladder ✓. Whole card is the link. Hover: `translateY(-2px)`, border-color `color-mix(in srgb, var(--cat-base) 60%, var(--border))`, shadow to `0 16px 40px rgba(0,0,0,.45)`, 150ms.

### Act band (index)
Full-width; `padding: 24px 32px; border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); background: linear-gradient(180deg, rgba(255,255,255,.025), transparent);` — **always neutral**, never category-colored. Contents: `ACT III` kicker (`--muted`) · years (JBM 13px `--muted`) · title (Literata **italic** 500 `clamp(22px, 2.6vw, 30px)` `--text`) · bandCopy (Inter 16px `--muted`, max-width 560px).
**Gap caption** (2023–24): centered row — hairline (1px `--border`, flex-grow) · Inter italic 15px `--muted` · hairline.

### Chips & buttons
- Base chip: `background: var(--surface-2); border: 1px solid var(--border); border-radius: var(--r2); padding: 5px 10px;` JBM 12px `--muted`. Min 44px tap target on touch via padding/hit-area.
- Metadata chips (minutes, buildChip) stay neutral. The **"interactive" chip** alone carries `color: var(--cat-base); border-color: color-mix(in srgb, var(--cat-base) 40%, var(--border))`.
- Toggle/pressed (`aria-pressed="true"`, fast-path toggle, widget mode tabs): `background: color-mix(in srgb, var(--cat-base) 16%, var(--surface-2)); color: var(--cat-light); border-color: var(--cat-base)`.
- Hover: border-color `--cat-base`, text brightens one step, 150ms. Disabled: opacity .45, no pointer events.
- Primary button (rare — e.g. break-it preset): `background: var(--cat-base); color: var(--ground);` JBM 500 13px, `padding: 10px 16px; border-radius: var(--r2)`; hover `background: var(--cat-light)`. Never pill.

### Coda rung (paper pages + build.html ladder)
Container: panel recipe + kicker `BUILD THIS YOURSELF`. Each rung: grid `[tag | text | meta]`, `background: var(--surface-2); border: 1px solid var(--border); border-left: 2px solid var(--cat-base); border-radius: var(--r2); padding: 14px 16px;` 8px between rungs.
- Tag (`read`/`run`/`tweak`/`train`): JBM 11px uppercase ls .08em, `background: color-mix(in srgb, var(--cat-base) 16%, transparent); color: var(--cat-light); border-radius: var(--r1); padding: 3px 8px`.
- Text: Inter 15px `--text`, links underlined. Meta right-aligned: JBM 12px `--muted` — `2 hrs · $0`.
- build.html checkbox: 18px square, radius `--r1`, `border: 1.5px solid #565C66`; checked: `background: var(--ok)`, check in `var(--ground)`; 250ms.

### Minimap (paper pages, injected by components.js → spine.renderMinimap)
Sticky top bar, height 56px: `background: color-mix(in srgb, var(--surface) 92%, transparent); backdrop-filter: blur(8px); border-bottom: 1px solid var(--line)`. Left: `← timeline` (JBM 13px `--muted`; also the static no-JS fallback). Center: 15 dots on a 1px `--border` rail — others 6px `#565C66`; current 10px `var(--cat-base)` + glow `0 0 8px color-mix(in srgb, var(--cat-base) 45%, transparent)` + nickname label (JBM 11px `--muted`); checked dots fill `var(--ok)`. Each dot anchor gets a ≥24×44px hit area via padding; native `title` tooltips.

## 9. Motion

```css
--ease-out:   cubic-bezier(.16, 1, .3, 1);   /* shared sibling easing */
--ease-inout: cubic-bezier(.65, 0, .35, 1);
--dur-1: 150ms;  /* hover, chip states */
--dur-2: 250ms;  /* bar widths, fills, checkboxes — update-in-place */
--dur-3: 400ms;  /* scrolly step reveal: opacity + translateY(12px) */
--dur-4: 700ms;  /* panel/figure entrances */
```

- **Curve draw:** scroll-bound, not timed. `stroke-dasharray = pathLength`; target `dashoffset = pathLength × (1 − progress)`; each frame lerp `current += (target − current) × 0.15`, ONE rAF write, rAF loop parks when `|delta| < 0.5px`. Inactive scrolly steps: `opacity: .25; translateY(12px)`; active: full, `--dur-3 --ease-out`. Live-node pulse 2.4s infinite. Odometer digits: 250ms stepped roll.
- **`prefers-reduced-motion: reduce` — CSS:** kill all transitions/animations (`animation-duration: .01ms !important; transition-duration: .01ms !important`), spine fully drawn (`stroke-dashoffset: 0 !important`), no pulse/glow animation, steps always `opacity: 1; transform: none`.
- **— JS (spine.js, timeline.js, every widget):** check `matchMedia('(prefers-reduced-motion: reduce)')` at init; skip the rAF draw loop and render the curve complete; 15th-node reveal, odometers, and counters jump straight to final values; scrolly step callbacks still fire (instant state swaps, no tweens).

## 10. Texture, focus, selection

- **Grain** (sibling DNA): single fixed feTurbulence overlay —

```css
body::before {
  content: ""; position: fixed; inset: 0; z-index: 1; pointer-events: none;
  opacity: .22; mix-blend-mode: overlay;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}
```

  (`.22` vs taylor's `.35` — graphite is more austere than warm paper.) Page content sits at `position: relative; z-index: 2` where interactivity matters; the overlay is pointer-transparent regardless.
- **Focus:** `:focus-visible { outline: 2px solid var(--cat-light); outline-offset: 2px; }` (neutral pages fall back to `#D7DBE1`); inside `.paper-chip` the outline is `#21201B`. Never remove outlines without replacement.
- **Selection:** `::selection { background: var(--cat-base); color: var(--ground); }` — selecting text momentarily floods it with the paper's category color (neutral silver on index). Paper-chip override in §4.

## 11. CSS architecture

One file, `docs/css/site.css?v=N` (bump via `tools/bump_css.py`), ordered: **tokens → skeleton → components → per-page sections → reduced-motion block**. All colors, sizes, durations from tokens; `[data-cat]` remap is the only theming mechanism. Mobile breakpoints: **780px** (scrolly inversion + spine left-rail), 480px (chip wrapping, minimap label hidden).
