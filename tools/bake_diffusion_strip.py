#!/usr/bin/env python3
"""Bake the forward-diffusion strip for docs/papers/stable-diffusion.html.

Forward diffusion is model-free math (SPEC §6d): x_t = sqrt(abar_t)*x_0 +
sqrt(1-abar_t)*eps, with a linear beta schedule 1e-4 -> 0.02, T=1000. We
noise one public-domain image (NASA Blue Marble, Apollo 17 — via Wikimedia
Commons, credited in colophon) at 12 evenly spaced timesteps, for TWO seeds
(the second powers the "shuffle the noise" break-it button), plus a 64x64
downsample per frame illustrating latent-space SCALE (labeled as an
illustration, not a real VAE latent — see manifest note + colophon).

DEPENDENCIES — runs in the project venv, NOT system python:
    .venv/bin/python tools/bake_diffusion_strip.py
    uses: numpy, PIL (Pillow with webp).
Outputs: docs/data/stable-diffusion/{seed0,seed1}/t####.webp (+ _64 variants)
         and manifest.json with provenance. Asset budget <=3MB enforced.
"""
import argparse
import json
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC_URL = "https://commons.wikimedia.org/wiki/Special:FilePath/The_Earth_seen_from_Apollo_17.jpg"
SIZE = 480
LATENT = 64
T = 1000
TIMESTEPS = [0, 40, 90, 150, 220, 300, 400, 520, 650, 780, 900, 999]
SEEDS = [17, 42]


def alpha_bar(t):
    betas = np.linspace(1e-4, 0.02, T)
    return float(np.prod(1.0 - betas[: t + 1])) if t >= 0 else 1.0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--source", default=None, help="source image path (default: fetch Blue Marble)")
    ap.add_argument("--out-dir", default=str(ROOT / "docs" / "data" / "stable-diffusion"))
    args = ap.parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    if args.source:
        src_path = Path(args.source)
        cleanup_src = False
    else:
        src_path = out / "source.jpg"
        cleanup_src = True
        if not src_path.exists():
            print(f"downloading {SRC_URL}")
            req = urllib.request.Request(SRC_URL, headers={"User-Agent": "ml-papers-baker/1.0"})
            src_path.write_bytes(urllib.request.urlopen(req, timeout=60).read())

    img = Image.open(src_path).convert("RGB")
    side = min(img.size)
    img = img.crop(((img.width - side) // 2, (img.height - side) // 2,
                    (img.width + side) // 2, (img.height + side) // 2)).resize((SIZE, SIZE), Image.LANCZOS)
    x0 = np.asarray(img, dtype=np.float32) / 127.5 - 1.0

    total = 0
    for i, seed in enumerate(SEEDS):
        rng = np.random.default_rng(seed)
        eps = rng.standard_normal(x0.shape).astype(np.float32)
        sdir = out / f"seed{i}"
        sdir.mkdir(exist_ok=True)
        for t in TIMESTEPS:
            if i > 0 and t < 150:
                continue  # low-noise frames are ~identical across seeds; JS falls back to seed0
            ab = alpha_bar(t - 1) if t > 0 else 1.0
            xt = np.sqrt(ab) * x0 + np.sqrt(1.0 - ab) * eps
            arr = np.clip((xt + 1.0) * 127.5, 0, 255).astype(np.uint8)
            frame = Image.fromarray(arr)
            p = sdir / f"t{t:04d}.webp"
            frame.save(p, "WEBP", quality=52)
            lp = sdir / f"t{t:04d}_64.webp"
            frame.resize((LATENT, LATENT), Image.NEAREST).save(lp, "WEBP", quality=70)
            total += p.stat().st_size + lp.stat().st_size

    if cleanup_src and src_path.exists():
        src_path.unlink()  # don't ship the multi-MB source jpg

    (out / "manifest.json").write_text(json.dumps({
        "baker": "tools/bake_diffusion_strip.py",
        "source": {"title": "The Earth seen from Apollo 17 (Blue Marble)",
                   "url": SRC_URL, "license": "public domain (NASA)"},
        "schedule": {"beta": "linear 1e-4 -> 0.02", "T": T},
        "timesteps": TIMESTEPS, "seeds": len(SEEDS), "size": SIZE, "latent": LATENT,
        "seedFallbackBelowT": 150,
        "note": ("64px variants illustrate latent-space SCALE; they are downsamples, "
                 "not a real VAE latent (see colophon)."),
    }, indent=2))
    print(f"baked {len(SEEDS)}x{len(TIMESTEPS)} frames (+latent variants), {total/1e6:.2f} MB total")
    assert total < 3_000_000, "asset budget exceeded (SPEC §2 rule 6)"


if __name__ == "__main__":
    main()
