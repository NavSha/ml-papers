#!/usr/bin/env python3
"""STUB (implemented at CP5) — bake forward-diffusion webp strips for
widgets/stable-diffusion.js.

Forward-noises the source image (NASA "Blue Marble", Apollo 17, public
domain — credited in colophon; fallback: an author-owned frame from
video-editing-experiment/) with a linear beta schedule 1e-4 -> 0.02, T=1000,
~12 evenly-spaced frames, TWO seeds (the second powers the "shuffle the
noise" break-it button), and writes webp frames to
docs/data/stable-diffusion/ (<=3MB total; SPEC §6d).

DEPENDENCIES — runs in the project venv, NOT system python:
    .venv/bin/python tools/bake_diffusion_strip.py
    venv recipe (CP0): uv venv --python 3.11 .venv &&
        uv pip install --python .venv/bin/python torch transformers numpy pillow
    uses: numpy, PIL (Pillow, webp encoding; fallback encoder: cwebp).
"""
import argparse


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--source", default=None,
                    help="source image path (default: fetched Blue Marble)")
    ap.add_argument("--out-dir", default="docs/data/stable-diffusion",
                    help="output dir (default: docs/data/stable-diffusion)")
    ap.parse_args()
    raise NotImplementedError(
        "bake_diffusion_strip.py is a CP0 stub — implemented at CP5. "
        "See SPEC §6d and CHECKPOINTS.md CP5.")


if __name__ == "__main__":
    main()
