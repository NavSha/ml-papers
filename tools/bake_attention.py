#!/usr/bin/env python3
"""STUB (implemented at CP4) — bake attention data for widgets/transformer.js.

Runs GPT-2 small over ~8 curated sentences (including 1-2 designed failure
cases, e.g. a long-range dependency where attention visibly diffuses) and
emits per-sentence, per-layer/head attention weights, quantized to uint8, to
docs/data/transformer/attention.json (<=3MB total; SPEC §6c).

DEPENDENCIES — runs in the project venv, NOT system python:
    .venv/bin/python tools/bake_attention.py
    venv recipe (CP0): uv venv --python 3.11 .venv &&
        uv pip install --python .venv/bin/python torch transformers numpy pillow
    uses: torch, transformers (GPT-2 small, downloads from HF on first run,
    public model, no token; budget 5-15 min), numpy.
Fallback variant if this bake fails: taylor-transformer char-level ONNX model
(SPEC §6c fallback contract).
"""
import argparse


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default="docs/data/transformer/attention.json",
                    help="output path (default: docs/data/transformer/attention.json)")
    ap.parse_args()
    raise NotImplementedError(
        "bake_attention.py is a CP0 stub — implemented at CP4. "
        "See SPEC §6c and CHECKPOINTS.md CP4.")


if __name__ == "__main__":
    main()
