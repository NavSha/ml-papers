#!/usr/bin/env python3
"""Cache-bust the stylesheet: bump site.css?v=N across all docs/**/*.html
(stdlib-only, SPEC §2 engineering rule 7).

Finds every `site.css?v=N` reference (and bare `site.css` references, which
get a version added), computes new N = max(existing N) + 1 (or --set N), and
rewrites every reference so the whole site agrees on one version. Idempotent
in the sense that all pages always end up on the same single version.
"""
import argparse
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VER_RE = re.compile(r"(site\.css)\?v=(\d+)")
BARE_RE = re.compile(r"(site\.css)(?!\?)")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=os.path.join(REPO, "docs"),
                    help="site root (default: docs/)")
    ap.add_argument("--set", dest="set_n", type=int, default=None, metavar="N",
                    help="pin the version to N instead of max+1")
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

    versions = []
    contents = {}
    for path in pages:
        with open(path, encoding="utf-8") as fh:
            contents[path] = fh.read()
        versions += [int(v) for _, v in VER_RE.findall(contents[path])]

    if not versions and not any(BARE_RE.search(c) for c in contents.values()):
        print(f"no site.css references found in {len(pages)} HTML files — nothing to bump")
        return

    new_n = args.set_n if args.set_n is not None else (max(versions) if versions else 0) + 1
    changed = 0
    for path in sorted(pages):
        content = contents[path]
        new_content = VER_RE.sub(rf"\g<1>?v={new_n}", content)
        new_content = BARE_RE.sub(rf"\g<1>?v={new_n}", new_content)
        if new_content != content:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(new_content)
            changed += 1
            print(f"bumped: {os.path.relpath(path, root)}")
    old = f"max v={max(versions)}" if versions else "unversioned"
    print(f"\nsite.css {old} -> v={new_n}; {changed} of {len(pages)} page(s) rewritten")


if __name__ == "__main__":
    main()
