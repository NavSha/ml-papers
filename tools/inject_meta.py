#!/usr/bin/env python3
"""Inject OG/Twitter/description meta tags + favicon links into docs/**/*.html
(stdlib-only). Ported from interactive-explainers/scripts/inject_meta.py.

Idempotent: skips tags a page already has (re-run => no diff). Descriptions
come from, in priority order:
  1. a data-description="..." attribute anywhere in the page,
  2. the page's .lead paragraph,
  3. the first <p> inside <article>/<main>,
  4. the site-wide default (both index deck lines).

OG image is the site-wide docs/og.png (SPEC: no per-paper OG images). Favicon
links are injected only when the favicon files actually exist under
docs/assets/, so check_links.py stays green before the assets land.
"""
import argparse
import html as htmllib
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_URL = "https://navsha.github.io/ml-papers/"
SITE_NAME = "The Fourteen"
DEFAULT_DESC = ("Thirteen years of AI, drawn as a single descending loss curve — "
                "the 14 papers that matter. Every one is reproducible this weekend "
                "for under $30 — each page shows you how.")

DATA_DESC_RE = re.compile(r"""data-description\s*=\s*["']([^"']+)["']""")
LEAD_RE = re.compile(r"<(?:p|div)[^>]*class=\"[^\"]*lead[^\"]*\"[^>]*>(.*?)</(?:p|div)>", re.S)
P_RE = re.compile(r"<(?:article|main)[^>]*>.*?<p[^>]*>(.*?)</p>", re.S)
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.S)


def clean(text):
    text = re.sub(r"<[^>]+>", "", text)
    text = htmllib.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > 160:
        text = text[:157].rsplit(" ", 1)[0] + "…"
    return text


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=os.path.join(REPO, "docs"),
                    help="site root (default: docs/)")
    args = ap.parse_args()
    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        print(f"ERROR: site root {root} not found", file=sys.stderr)
        sys.exit(1)

    pages = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for f in filenames:
            if f.endswith(".html"):
                pages.append(os.path.join(dirpath, f))

    have_favicon = os.path.isfile(os.path.join(root, "assets", "favicon-32.png"))
    have_touch = os.path.isfile(os.path.join(root, "assets", "apple-touch-icon.png"))

    changed = 0
    for path in sorted(pages):
        rel = os.path.relpath(path, root).replace(os.sep, "/")
        depth = rel.count("/")
        prefix = "../" * depth
        url = BASE_URL + ("" if rel == "index.html" else rel)

        with open(path, encoding="utf-8") as fh:
            content = fh.read()

        m = TITLE_RE.search(content)
        title = htmllib.unescape(m.group(1).strip()) if m else SITE_NAME
        m = DATA_DESC_RE.search(content) or LEAD_RE.search(content) or P_RE.search(content)
        desc = clean(m.group(1)) if m else DEFAULT_DESC

        def esc(s):
            return htmllib.escape(s, quote=True)

        lines = []
        if 'name="description"' not in content:
            lines.append(f'  <meta name="description" content="{esc(desc)}">')
        if 'property="og:' not in content:
            og_type = "website" if rel == "index.html" else "article"
            lines += [
                f'  <meta property="og:type" content="{og_type}">',
                f'  <meta property="og:title" content="{esc(title)}">',
                f'  <meta property="og:description" content="{esc(desc)}">',
                f'  <meta property="og:url" content="{esc(url)}">',
                f'  <meta property="og:image" content="{BASE_URL}og.png">',
                f'  <meta property="og:site_name" content="{esc(SITE_NAME)}">',
            ]
        if 'name="twitter:' not in content:
            lines += [
                '  <meta name="twitter:card" content="summary_large_image">',
                f'  <meta name="twitter:title" content="{esc(title)}">',
                f'  <meta name="twitter:description" content="{esc(desc)}">',
                f'  <meta name="twitter:image" content="{BASE_URL}og.png">',
            ]
        if 'rel="icon"' not in content and have_favicon:
            lines.append(f'  <link rel="icon" type="image/png" sizes="32x32" '
                         f'href="{prefix}assets/favicon-32.png">')
        if 'rel="apple-touch-icon"' not in content and have_touch:
            lines.append(f'  <link rel="apple-touch-icon" '
                         f'href="{prefix}assets/apple-touch-icon.png">')
        if not lines:
            continue

        block = "\n" + "\n".join(lines)
        new_content, n = re.subn(r"(</title>)", lambda m: m.group(1) + block,
                                 content, count=1)
        if n != 1:
            print(f"SKIP (no <title> anchor): {rel}")
            continue
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(new_content)
        changed += 1
        short = desc if len(desc) <= 60 else desc[:60] + "…"
        print(f"OK {rel}  [{short}]")

    if not (have_favicon and have_touch):
        print("note: favicon assets not found under docs/assets/ — favicon links "
              "not injected (re-run after the assets land)")
    print(f"\n{changed} page(s) updated ({len(pages)} checked)")


if __name__ == "__main__":
    main()
