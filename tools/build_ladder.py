#!/usr/bin/env python3
"""Bake the participation ladder into docs/build.html from docs/papers.json.

Idempotently rewrites the <!-- BEGIN:LADDER -->…<!-- END:LADDER --> block.
Grouping is fixed by SPEC §7. Stdlib only. Run from repo root:

    python3 tools/build_ladder.py
"""
import argparse
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GROUPS = [
    ("see it",            ["alexnet", "resnet", "clip"]),
    ("build it",          ["transformer", "moe"]),
    ("scale it",          ["gpt2", "scaling-laws", "gpt3"]),
    ("shape it",          ["rlhf", "constitutional-ai", "lora", "cot"]),
    ("generate & reason", ["stable-diffusion", "deepseek-r1"]),
]

def esc(s):
    return html.escape(s, quote=True)

def render(papers):
    by_slug = {p["slug"]: p for p in papers}
    out = []
    for title, slugs in GROUPS:
        out.append(f'<section class="ladder-group">')
        out.append(f'  <p class="kicker"><span class="cat">{esc(title)}</span></p>')
        for slug in slugs:
            p = by_slug[slug]
            out.append(f'  <div class="ladder-paper" data-paper="{esc(slug)}">')
            out.append(f'    <p class="ladder-paper-name"><a href="papers/{esc(slug)}.html">'
                       f'{esc(p["nickname"])}</a> <span class="ladder-chip">{esc(p["buildChip"])}</span></p>')
            out.append('    <ol class="coda-rungs">')
            for i, r in enumerate(p["coda"]["rungs"]):
                out.append(f'''    <li class="rung rung--check" data-tag="{esc(r["tag"])}">
      <input class="ladder-check" type="checkbox" id="lc-{esc(slug)}-{i}"
             data-slug="{esc(slug)}" data-rung="{i}"
             aria-label="done: {esc(p["nickname"])} — {esc(r["tag"])}">
      <span class="rung-tag">{esc(r["tag"])}</span>
      <label class="rung-text" for="lc-{esc(slug)}-{i}">{esc(r["text"])}</label>
      <p class="rung-meta">{esc(r["time"])} &middot; {esc(r["cost"])}</p>
    </li>''')
            out.append('    </ol>')
            out.append('  </div>')
        out.append('</section>')
    return "\n".join(out)

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=str(ROOT))
    args = ap.parse_args()
    root = Path(args.root)
    page = root / "docs" / "build.html"
    data = json.loads((root / "docs" / "papers.json").read_text())
    block = "<!-- BEGIN:LADDER -->\n" + render(data["papers"]) + "\n<!-- END:LADDER -->"
    src = page.read_text()
    new = re.sub(r"<!-- BEGIN:LADDER -->.*?<!-- END:LADDER -->", lambda m: block, src, flags=re.S)
    if new == src:
        print("unchanged: docs/build.html (LADDER block already up to date)")
    else:
        page.write_text(new)
        print("updated: docs/build.html (LADDER block)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
