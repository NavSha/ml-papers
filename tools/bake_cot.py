#!/usr/bin/env python3
"""STUB (implemented at CP3) — bake token counts + cost data for widgets/cot.js.

Primary content path (binding — no metered API key exists in this
environment): responses are hand-authored from Wei et al. arXiv 2201.11903's
own published exemplars and appendix outputs (both conditions, plus the
sub-threshold "small model" break-it examples). This tool computes token
counts offline with the GPT-2 tokenizer and emits
docs/data/cot/exemplars.json; costs recompute in-widget from prices.json.
An API bake is an optional enhancement ONLY behind an env-var check at CP3
start (named model, ~$1 cap; SPEC §6b).

DEPENDENCIES — runs in the project venv, NOT system python:
    .venv/bin/python tools/bake_cot.py
    venv recipe (CP0): uv venv --python 3.11 .venv &&
        uv pip install --python .venv/bin/python torch transformers numpy pillow
    uses: transformers (GPT2TokenizerFast only — no model download needed).
"""
import argparse


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default="docs/data/cot/exemplars.json",
                    help="output path (default: docs/data/cot/exemplars.json)")
    ap.parse_args()
    raise NotImplementedError(
        "bake_cot.py is a CP0 stub — implemented at CP3. "
        "See SPEC §6b and CHECKPOINTS.md CP3.")


if __name__ == "__main__":
    main()
