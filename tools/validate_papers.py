#!/usr/bin/env python3
"""Validate docs/papers.json against the SPEC §2 schema (stdlib-only).

Checks:
  * top level is { "acts": [...], "papers": [...] }
  * acts: exactly 5, act numbers 1..5 in order, canonical titles, non-empty
    bandCopy, gapCaptionAfter is str|null (act 4's 2023-24 gap caption required)
  * papers: slug set AND order match the canonical SPEC §2 table
  * per paper: required fields present with correct types; date/venue/category/
    tier/act match the canonical table; arxiv null ONLY for alexnet + gpt2
    (arXiv-ID format for all others); paperUrl is http(s); status plate|live;
    minutes positive int; hook/consequence/cliffhanger non-empty
  * buildChip format: "build it: $<amount> · <time>"
  * coda: >=2 rungs, every rung has tag/text/href/time/cost, tag in
    {read,run,tweak,train}, and at least one "read" rung pointing at paperUrl

Exit 0 and print OK when valid; exit 1 with one precise error per line.
"""
import argparse
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_FILE = os.path.join(REPO, "docs", "papers.json")

# Canonical table — SPEC §2: slug -> (date, venue, category, tier, act)
CANON = [
    ("alexnet",           "2012-12", "NeurIPS 2012", "foundations",  "plate",  1),
    ("resnet",            "2015-12", "CVPR 2016",    "foundations",  "plate",  1),
    ("transformer",       "2017-06", "NeurIPS 2017", "foundations",  "widget", 2),
    ("gpt2",              "2019-02", "OpenAI 2019",  "llm-core",     "scrolly", 3),
    ("scaling-laws",      "2020-01", "arXiv 2020",   "llm-core",     "widget", 3),
    ("gpt3",              "2020-05", "NeurIPS 2020", "llm-core",     "scrolly", 3),
    ("moe",               "2021-01", "JMLR 2022",    "llm-core",     "scrolly", 3),
    ("clip",              "2021-03", "ICML 2021",    "beyond-text",  "plate",  4),
    ("lora",              "2021-06", "ICLR 2022",    "for-builders", "plate",  4),
    ("stable-diffusion",  "2021-12", "CVPR 2022",    "beyond-text",  "widget", 4),
    ("cot",               "2022-01", "NeurIPS 2022", "making-useful", "widget", 4),
    ("rlhf",              "2022-03", "NeurIPS 2022", "making-useful", "scrolly", 4),
    ("constitutional-ai", "2022-12", "arXiv 2022",   "making-useful", "scrolly", 4),
    ("deepseek-r1",       "2025-01", "arXiv 2025",   "making-useful", "scrolly", 5),
]
CANON_BY_SLUG = {row[0]: row for row in CANON}
ARXIV_NULL_OK = {"alexnet", "gpt2"}

ACT_TITLES = {
    1: "The bet on scale",
    2: "The architecture",
    3: "The scaling era",
    4: "Four threads at once",
    5: "The reasoning era",
}

RUNG_TAGS = {"read", "run", "tweak", "train"}
ARXIV_RE = re.compile(r"^\d{4}\.\d{4,5}(v\d+)?$")
DATE_RE = re.compile(r"^\d{4}-\d{2}$")
BUILDCHIP_RE = re.compile(r"^build it: \$\S[^·]* · \S.*$")

STR_FIELDS = ("slug", "title", "nickname", "authorsShort", "date", "paperUrl",
              "venue", "category", "tier", "status", "hook", "consequence",
              "cliffhanger", "buildChip")


def check_paper(p, i, errors):
    slug = p.get("slug")
    tag = f"papers[{i}] ({slug!r})"

    for f in STR_FIELDS:
        if not isinstance(p.get(f), str) or not p.get(f).strip():
            errors.append(f"{tag}: field '{f}' missing or not a non-empty string")
    for f in ("act", "minutes"):
        if not isinstance(p.get(f), int) or isinstance(p.get(f), bool):
            errors.append(f"{tag}: field '{f}' missing or not an int")

    if slug not in CANON_BY_SLUG:
        errors.append(f"{tag}: unknown slug (not in the canonical 14)")
        return
    _, c_date, c_venue, c_cat, c_tier, c_act = CANON_BY_SLUG[slug]

    if isinstance(p.get("date"), str):
        if not DATE_RE.match(p["date"]):
            errors.append(f"{tag}: date {p['date']!r} not YYYY-MM")
        elif p["date"] != c_date:
            errors.append(f"{tag}: date {p['date']!r} != canonical {c_date!r}")
    if isinstance(p.get("venue"), str) and p["venue"] != c_venue:
        errors.append(f"{tag}: venue {p['venue']!r} != canonical {c_venue!r}")
    if isinstance(p.get("category"), str) and p["category"] != c_cat:
        errors.append(f"{tag}: category {p['category']!r} != canonical {c_cat!r}")
    if isinstance(p.get("tier"), str) and p["tier"] != c_tier:
        errors.append(f"{tag}: tier {p['tier']!r} != canonical {c_tier!r}")
    if isinstance(p.get("act"), int) and p["act"] != c_act:
        errors.append(f"{tag}: act {p['act']} != canonical {c_act}")

    if "arxiv" not in p:
        errors.append(f"{tag}: field 'arxiv' missing (use null for alexnet/gpt2)")
    elif p["arxiv"] is None:
        if slug not in ARXIV_NULL_OK:
            errors.append(f"{tag}: arxiv is null — null allowed only for alexnet, gpt2")
    else:
        if slug in ARXIV_NULL_OK:
            errors.append(f"{tag}: arxiv must be null for {slug} (no arXiv v1)")
        elif not (isinstance(p["arxiv"], str) and ARXIV_RE.match(p["arxiv"])):
            errors.append(f"{tag}: arxiv {p['arxiv']!r} not an arXiv id (NNNN.NNNNN)")

    if isinstance(p.get("paperUrl"), str) and not p["paperUrl"].startswith(("http://", "https://")):
        errors.append(f"{tag}: paperUrl {p['paperUrl']!r} not an http(s) URL")
    if isinstance(p.get("status"), str) and p["status"] not in ("plate", "live"):
        errors.append(f"{tag}: status {p['status']!r} not 'plate'|'live'")
    if isinstance(p.get("minutes"), int) and not isinstance(p.get("minutes"), bool) and p["minutes"] <= 0:
        errors.append(f"{tag}: minutes {p['minutes']} not a positive int")
    if isinstance(p.get("buildChip"), str) and not BUILDCHIP_RE.match(p["buildChip"]):
        errors.append(f"{tag}: buildChip {p['buildChip']!r} not 'build it: $<amount> · <time>'")

    coda = p.get("coda")
    if not isinstance(coda, dict) or not isinstance(coda.get("rungs"), list):
        errors.append(f"{tag}: coda missing or coda.rungs not an array")
        return
    rungs = coda["rungs"]
    if len(rungs) < 2:
        errors.append(f"{tag}: coda has {len(rungs)} rung(s); minimum is 2 (read + run)")
    has_read_paper = False
    for j, r in enumerate(rungs):
        rt = f"{tag} coda.rungs[{j}]"
        if not isinstance(r, dict):
            errors.append(f"{rt}: not an object")
            continue
        for f in ("tag", "text", "href", "time", "cost"):
            if not isinstance(r.get(f), str) or not r.get(f).strip():
                errors.append(f"{rt}: field '{f}' missing or not a non-empty string")
        if isinstance(r.get("tag"), str) and r["tag"] not in RUNG_TAGS:
            errors.append(f"{rt}: tag {r['tag']!r} not in {sorted(RUNG_TAGS)}")
        if r.get("tag") == "read" and r.get("href") == p.get("paperUrl"):
            has_read_paper = True
    if not has_read_paper:
        errors.append(f"{tag}: no 'read' rung whose href equals paperUrl "
                      "(rung-expansion rule: read = the paper itself)")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--file", default=DEFAULT_FILE,
                    help="path to papers.json (default: docs/papers.json)")
    args = ap.parse_args()

    if not os.path.isfile(args.file):
        print(f"ERROR: {args.file} not found", file=sys.stderr)
        sys.exit(1)
    try:
        with open(args.file, encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as e:
        print(f"ERROR: {args.file} is not valid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    errors = []
    if not isinstance(data, dict):
        errors.append("top level: not an object")
    acts = data.get("acts") if isinstance(data, dict) else None
    papers = data.get("papers") if isinstance(data, dict) else None

    # --- acts -------------------------------------------------------------
    if not isinstance(acts, list):
        errors.append("acts: missing or not an array")
    else:
        if len(acts) != 5:
            errors.append(f"acts: expected 5 entries, got {len(acts)}")
        for i, a in enumerate(acts):
            at = f"acts[{i}]"
            if not isinstance(a, dict):
                errors.append(f"{at}: not an object")
                continue
            if a.get("act") != i + 1:
                errors.append(f"{at}: act number {a.get('act')!r} != {i + 1} (must be 1..5 in order)")
            want = ACT_TITLES.get(i + 1)
            if want and a.get("title") != want:
                errors.append(f"{at}: title {a.get('title')!r} != canonical {want!r}")
            for f in ("title", "years", "bandCopy"):
                if not isinstance(a.get(f), str) or not a.get(f).strip():
                    errors.append(f"{at}: field '{f}' missing or not a non-empty string")
            gap = a.get("gapCaptionAfter", "MISSING")
            if gap == "MISSING":
                errors.append(f"{at}: field 'gapCaptionAfter' missing (use null if none)")
            elif gap is not None and (not isinstance(gap, str) or not gap.strip()):
                errors.append(f"{at}: gapCaptionAfter must be a non-empty string or null")
            if a.get("act") == 4 and not (isinstance(gap, str) and gap.strip()):
                errors.append(f"{at}: act 4 requires the 2023-24 gapCaptionAfter string")

    # --- papers -----------------------------------------------------------
    if not isinstance(papers, list):
        errors.append("papers: missing or not an array")
    else:
        slugs = [p.get("slug") for p in papers if isinstance(p, dict)]
        canon_slugs = [row[0] for row in CANON]
        missing = [s for s in canon_slugs if s not in slugs]
        extra = [s for s in slugs if s not in canon_slugs]
        if missing:
            errors.append(f"papers: missing slugs {missing}")
        if extra:
            errors.append(f"papers: unknown slugs {extra}")
        if not missing and not extra and slugs != canon_slugs:
            errors.append(f"papers: order {slugs} != canonical chronological order {canon_slugs}")
        for i, p in enumerate(papers):
            if not isinstance(p, dict):
                errors.append(f"papers[{i}]: not an object")
                continue
            check_paper(p, i, errors)

    if errors:
        for e in errors:
            print(f"INVALID  {e}")
        print(f"\n{len(errors)} error(s) in {os.path.relpath(args.file, REPO)}")
        sys.exit(1)
    print(f"OK: {os.path.relpath(args.file, REPO)} passes SPEC §2 schema "
          f"({len(papers)} papers, {len(acts)} acts)")


if __name__ == "__main__":
    main()
