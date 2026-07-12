#!/usr/bin/env python3
"""Bake the timeline spine into docs/index.html from docs/papers.json (stdlib-only).

Idempotently rewrites the SINGLE marked block

    <!-- BEGIN:NODES --> ... <!-- END:NODES -->

with act bands, node cards, and gap captions interleaved chronologically
(SPEC §2 data flow, §4 node-card anatomy). Everything outside the markers is
preserved byte-for-byte. Running twice produces no diff.

Generated markup per node card: year + nickname + hook + consequence +
minutes chip + buildChip + data-cat (category accent) + data-slug +
href to papers/{slug}.html + "interactive" chip when status=live +
hidden checkmark placeholder span (filled by timeline.js from mlp.ladder.*).
The 15th node ("2026: you") is static HTML owned by index.html itself,
OUTSIDE this block.
"""
import argparse
import html
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BEGIN = "<!-- BEGIN:NODES -->"
END = "<!-- END:NODES -->"
ROMAN = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V"}


def esc(s):
    return html.escape(str(s), quote=True)


def render_act_band(act):
    n = act["act"]
    return f"""<header class="act-band" data-act="{n}">
  <p class="act-kicker">Act {ROMAN.get(n, n)} &middot; {esc(act["years"])}</p>
  <h2 class="act-title">{esc(act["title"])}</h2>
  <p class="act-copy">{esc(act["bandCopy"])}</p>
</header>"""


def render_node_card(p):
    year = p["date"][:4]
    chips = [f'<span class="chip chip-minutes">{p["minutes"]} min</span>',
             f'<span class="chip chip-build">{esc(p["buildChip"])}</span>']
    if p.get("status") == "live":
        chips.append('<span class="chip chip-live">interactive</span>')
    chips_html = "\n      ".join(chips)
    return f"""<article class="node-card" data-slug="{esc(p["slug"])}" data-cat="{esc(p["category"])}" data-date="{esc(p["date"])}">
  <a class="node-link" href="papers/{esc(p["slug"])}.html">
    <p class="node-year">{year}</p>
    <h3 class="node-nickname">{esc(p["nickname"])}</h3>
    <p class="node-hook">{esc(p["hook"])}</p>
    <p class="node-consequence">{esc(p["consequence"])}</p>
    <p class="node-chips">
      {chips_html}
    </p>
  </a>
  <span class="node-check" data-check="{esc(p["slug"])}" hidden aria-hidden="true">&#10003;</span>
</article>"""


def render_gap_caption(act):
    return (f'<p class="gap-caption" data-gap-after="{act["act"]}">'
            f'{esc(act["gapCaptionAfter"])}</p>')


def render_nodes(data):
    acts = sorted(data["acts"], key=lambda a: a["act"])
    parts = []
    for act in acts:
        parts.append(render_act_band(act))
        papers = [p for p in data["papers"] if p["act"] == act["act"]]
        papers.sort(key=lambda p: p["date"])
        for p in papers:
            parts.append(render_node_card(p))
        if act.get("gapCaptionAfter"):
            parts.append(render_gap_caption(act))
    return "\n".join(parts)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=os.path.join(REPO, "docs"),
                    help="site root containing papers.json and index.html (default: docs/)")
    args = ap.parse_args()

    papers_path = os.path.join(args.root, "papers.json")
    index_path = os.path.join(args.root, "index.html")
    for path in (papers_path, index_path):
        if not os.path.isfile(path):
            print(f"ERROR: {path} not found", file=sys.stderr)
            sys.exit(1)

    with open(papers_path, encoding="utf-8") as fh:
        data = json.load(fh)
    with open(index_path, encoding="utf-8") as fh:
        content = fh.read()

    for marker in (BEGIN, END):
        n = content.count(marker)
        if n != 1:
            print(f"ERROR: index.html must contain exactly one '{marker}' (found {n})",
                  file=sys.stderr)
            sys.exit(1)
    head, rest = content.split(BEGIN, 1)
    _, tail = rest.split(END, 1)

    block = render_nodes(data)
    new_content = f"{head}{BEGIN}\n{block}\n{END}{tail}"

    rel = os.path.relpath(index_path, REPO)
    if new_content == content:
        print(f"unchanged: {rel} (NODES block already up to date)")
        return
    with open(index_path, "w", encoding="utf-8") as fh:
        fh.write(new_content)
    n_papers = len(data["papers"])
    n_gaps = sum(1 for a in data["acts"] if a.get("gapCaptionAfter"))
    print(f"updated: {rel} — NODES block rebaked "
          f"({len(data['acts'])} act bands, {n_papers} node cards, {n_gaps} gap captions)")


if __name__ == "__main__":
    main()
