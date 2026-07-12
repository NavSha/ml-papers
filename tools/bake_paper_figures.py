#!/usr/bin/env python3
"""STUB (implemented at CP1a for plates, CP6 for scrollies) — produce
docs/data/{slug}/figure.json for every redrawn data figure.

Extracts values from ar5iv HTML / paper tables where tabulated; where only a
figure exists (e.g. DeepSeek-R1's training curve), traces approximate points
and emits "provenance": "traced, approximate" — colophon.html surfaces
provenance verbatim per figure (SPEC §2). Each figure.json records which
baker, which source, and when.

DEPENDENCIES — runs in the project venv, NOT system python:
    .venv/bin/python tools/bake_paper_figures.py --slug rlhf
    venv recipe (CP0): uv venv --python 3.11 .venv &&
        uv pip install --python .venv/bin/python torch transformers numpy pillow
    uses: numpy (value extraction/tracing), stdlib urllib for ar5iv fetches.
"""
import argparse


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--slug", default=None,
                    help="bake only this paper's figure (default: all with data figures)")
    ap.add_argument("--out-root", default="docs/data",
                    help="output root (default: docs/data)")
    ap.parse_args()
    raise NotImplementedError(
        "bake_paper_figures.py is a CP0 stub — implemented at CP1a/CP6. "
        "See SPEC §2 and CHECKPOINTS.md CP1a/CP6.")


if __name__ == "__main__":
    main()
