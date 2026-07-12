#!/usr/bin/env python3
"""Bake HOOK / CODA / HANDOFF blocks into docs/papers/{slug}.html (stdlib-only).

For every paper in docs/papers.json, idempotently rewrites the marked blocks

    <!-- BEGIN:HOOK -->    ... <!-- END:HOOK -->
    <!-- BEGIN:CODA -->    ... <!-- END:CODA -->
    <!-- BEGIN:HANDOFF --> ... <!-- END:HANDOFF -->

in the corresponding page (SPEC §2 prose ownership, §5 anatomy). Everything
outside the markers is preserved byte-for-byte; running twice yields no diff.

HOOK    = the hook line as a `.lead` paragraph (inject_meta.py reads it for
          the page description).
CODA    = "Build it yourself" section: one <li> per rung (tag / linked text /
          time · cost), from the coda.rungs array.
HANDOFF = this paper's cliffhanger + prev/next chronological links.
          alexnet prev -> ../index.html ("timeline"); deepseek-r1 next ->
          ../build.html ("2026: you") — never wraps to alexnet. The
          data-handoff attributes are the hooks components.js uses for
          fast-path href swapping; the hrefs themselves are the static
          fallback.

Pages that don't exist yet are skipped (skip list printed).
"""
import argparse
import html
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARKS = ("HOOK", "CODA", "HANDOFF")


def esc(s):
    return html.escape(str(s), quote=True)


def render_hook(p):
    return f'<p class="lead hook">{esc(p["hook"])}</p>'


def render_coda(p):
    rungs = []
    for i, r in enumerate(p["coda"]["rungs"]):
        rungs.append(f"""  <li class="rung" data-tag="{esc(r["tag"])}">
    <span class="rung-tag">{esc(r["tag"])}</span>
    <p class="rung-text"><a href="{esc(r["href"])}">{esc(r["text"])}</a></p>
    <p class="rung-meta">{esc(r["time"])} &middot; {esc(r["cost"])}</p>
  </li>""")
    rungs_html = "\n".join(rungs)
    return f"""<section class="coda" aria-labelledby="coda-title">
  <h2 class="coda-title" id="coda-title">Build it yourself</h2>
  <p class="coda-chip">{esc(p["buildChip"])}</p>
  <ol class="coda-rungs">
{rungs_html}
  </ol>
</section>"""


def render_handoff(p, prev_p, next_p):
    if prev_p is None:
        prev_href, prev_label = "../index.html", "timeline"
    else:
        prev_href = f"{prev_p['slug']}.html"
        prev_label = f"{prev_p['nickname']} ({prev_p['date'][:4]})"
    if next_p is None:  # deepseek-r1: there is no next paper — never wrap
        next_href, next_label = "../build.html", "2026: you"
    else:
        next_href = f"{next_p['slug']}.html"
        next_label = f"{next_p['nickname']} ({next_p['date'][:4]})"
    return f"""<nav class="handoff" aria-label="Paper navigation">
  <p class="cliffhanger">{esc(p["cliffhanger"])}</p>
  <p class="handoff-links">
    <a class="handoff-prev" data-handoff="prev" href="{esc(prev_href)}">&larr; {esc(prev_label)}</a>
    <a class="handoff-next" data-handoff="next" href="{esc(next_href)}">{esc(next_label)} &rarr;</a>
  </p>
</nav>"""


def replace_block(content, name, block, missing):
    begin, end = f"<!-- BEGIN:{name} -->", f"<!-- END:{name} -->"
    if content.count(begin) != 1 or content.count(end) != 1:
        missing.append(name)
        return content
    head, rest = content.split(begin, 1)
    _, tail = rest.split(end, 1)
    return f"{head}{begin}\n{block}\n{end}{tail}"


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=os.path.join(REPO, "docs"),
                    help="site root containing papers.json and papers/ (default: docs/)")
    args = ap.parse_args()

    papers_path = os.path.join(args.root, "papers.json")
    if not os.path.isfile(papers_path):
        print(f"ERROR: {papers_path} not found", file=sys.stderr)
        sys.exit(1)
    with open(papers_path, encoding="utf-8") as fh:
        papers = json.load(fh)["papers"]

    updated, unchanged, skipped = [], [], []
    problems = []
    for i, p in enumerate(papers):
        slug = p["slug"]
        page = os.path.join(args.root, "papers", f"{slug}.html")
        if not os.path.isfile(page):
            skipped.append(slug)
            continue
        with open(page, encoding="utf-8") as fh:
            content = fh.read()

        prev_p = papers[i - 1] if i > 0 else None
        next_p = papers[i + 1] if i + 1 < len(papers) else None
        blocks = {"HOOK": render_hook(p),
                  "CODA": render_coda(p),
                  "HANDOFF": render_handoff(p, prev_p, next_p)}

        missing = []
        new_content = content
        for name in MARKS:
            new_content = replace_block(new_content, name, blocks[name], missing)
        if missing:
            problems.append(f"{slug}: marker pair(s) not found exactly once: {', '.join(missing)}")
        if new_content != content:
            with open(page, "w", encoding="utf-8") as fh:
                fh.write(new_content)
            updated.append(slug)
        else:
            unchanged.append(slug)

    if updated:
        print(f"updated ({len(updated)}): " + ", ".join(updated))
    if unchanged:
        print(f"unchanged ({len(unchanged)}): " + ", ".join(unchanged))
    if skipped:
        print(f"skipped — page not built yet ({len(skipped)}): " + ", ".join(skipped))
    if problems:
        for msg in problems:
            print(f"ERROR: {msg}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
