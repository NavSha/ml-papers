#!/usr/bin/env python3
"""Internal link/asset checker for the deployed site under docs/ (stdlib-only).

Verifies every internal href/src in docs/**/*.html resolves to a real file.
External (http/mailto/#/data:) links are skipped. Site-absolute paths under
/ml-papers/ (GitHub Pages subpath, used by 404.html) map to docs/.
Ported from interactive-explainers/scripts/check_links.py.

Exit 0 with an OK line when clean; exit 1 listing every broken reference.
"""
import argparse
import os
import re
import sys
from urllib.parse import urlparse, unquote

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUBPATH = "/ml-papers/"
ATTR_RE = re.compile(r"""(?:href|src)\s*=\s*["']([^"']+)["']""", re.I)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=os.path.join(REPO, "docs"),
                    help="site root to check (default: docs/)")
    args = ap.parse_args()
    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        print(f"ERROR: site root {root} not found", file=sys.stderr)
        sys.exit(1)

    html_files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for f in filenames:
            if f.endswith(".html"):
                html_files.append(os.path.join(dirpath, f))

    errors = []
    checked = 0
    for hf in sorted(html_files):
        rel_hf = os.path.relpath(hf, root)
        with open(hf, encoding="utf-8") as fh:
            content = fh.read()
        for m in ATTR_RE.finditer(content):
            url = m.group(1).strip()
            if not url or url.startswith(("http://", "https://", "mailto:", "#",
                                          "data:", "javascript:", "//")):
                continue
            path = unquote(urlparse(url).path)
            if not path:  # pure query/fragment link
                continue
            checked += 1
            if path.startswith(SUBPATH) or path == SUBPATH.rstrip("/"):
                # site-absolute GitHub Pages path — maps to docs/ root
                sub = path[len(SUBPATH):] if path.startswith(SUBPATH) else ""
                target = os.path.join(root, sub) if sub else os.path.join(root, "index.html")
            elif path.startswith("/"):
                target = os.path.join(root, path.lstrip("/"))
            else:
                target = os.path.normpath(os.path.join(os.path.dirname(hf), path))
            if os.path.isdir(target):
                if not os.path.isfile(os.path.join(target, "index.html")):
                    errors.append((rel_hf, url, "directory without index.html"))
                continue
            if not os.path.isfile(target):
                errors.append((rel_hf, url, "missing file"))

    if errors:
        for src, url, why in errors:
            print(f"BROKEN  {src}  ->  {url}  ({why})")
        print(f"\n{len(errors)} broken reference(s) in {len(html_files)} HTML files")
        sys.exit(1)
    print(f"OK: all internal references resolve "
          f"({len(html_files)} HTML files, {checked} internal refs checked)")


if __name__ == "__main__":
    main()
