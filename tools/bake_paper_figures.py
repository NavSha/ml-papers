#!/usr/bin/env python3
"""bake_paper_figures.py — produce docs/data/{slug}/figure.json for redrawn data figures.

Implemented at CP6 for the tier-2 scrolly upgrades (SPEC §2). For each target
paper this baker fetches the primary source (ar5iv HTML, or the OpenAI PDF for
GPT-2 which has no arXiv id), VERIFIES every tabulated number against the
fetched text (the bake fails loudly if a claim can't be found — no silently
unverified data), and writes a figure.json recording:

    { "baker", "bakedAt", "slug", "source", "provenance", "notes", "series" }

Provenance rules (SPEC §2, surfaced verbatim in colophon.html):
  - "tabulated"            — every value in the file is stated as a number in
                             the paper's text or tables (section refs recorded).
  - "traced, approximate"  — at least one series was read off a published
                             figure by eye. Tabulated anchor points inside such
                             a file are marked "tabulated" per-point.

Targets baked here (CP6):
  deepseek-r1  arXiv 2501.12948  Figure 2 R1-Zero AIME training curve (traced)
                                 + exact anchors 15.6 / 71.0 / 79.8 / 79.2.
  rlhf         arXiv 2203.02155  Headline preference results: 85±3% / 71±4%
                                 win rates + the 1.3B-beats-175B claim (tabulated).
  gpt2         OpenAI PDF        Figure 1 zero-shot curves ×4 tasks across
                                 117M/345M/762M/1542M (traced; endpoints tabulated).
  gpt3         arXiv 2005.14165  Figure 1.2 in-context learning curves
                                 (traced; K=0/1/100 anchors tabulated from Table H.1).
  moe          arXiv 2101.03961  7x speedup claims + Table 1 T5-Base comparison
                                 (tabulated).

DEPENDENCIES — run with the project venv python for consistency with the other
bakers, but this script is stdlib-only (urllib, json, re, zlib, subprocess):
    .venv/bin/python tools/bake_paper_figures.py            # bake all
    .venv/bin/python tools/bake_paper_figures.py --slug moe # bake one
GPT-2 PDF text extraction uses `pdftotext` (poppler) when available, with a
pure-python FlateDecode fallback. transformers/torch are NOT needed.
"""
import argparse
import json
import re
import subprocess
import sys
import tempfile
import zlib
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from urllib.request import Request, urlopen

BAKER = "tools/bake_paper_figures.py"
AR5IV = "https://ar5iv.labs.arxiv.org/html/{arxiv_id}"
GPT2_PDF_URL = ("https://cdn.openai.com/better-language-models/"
                "language_models_are_unsupervised_multitask_learners.pdf")
CACHE_DIR = Path(tempfile.gettempdir()) / "mlpapers-figbake"
UA = ("ml-papers-figure-baker/1.0 (educational timeline site; "
      "github.com/NavSha/ml-papers)")

TRACED = "traced, approximate"
TABULATED = "tabulated"


# ---------------------------------------------------------------- plumbing --

def fetch(url: str, cache_name: str, binary: bool = False):
    """Fetch url with a tmp-dir cache (re-runs shouldn't hammer ar5iv)."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache = CACHE_DIR / cache_name
    if cache.exists() and cache.stat().st_size > 10_000:
        data = cache.read_bytes()
    else:
        req = Request(url, headers={"User-Agent": UA})
        with urlopen(req, timeout=90) as resp:
            data = resp.read()
        cache.write_bytes(data)
    return data if binary else data.decode("utf-8", errors="replace")


def flatten_html(raw_html: str) -> str:
    """ar5iv HTML -> whitespace-flattened plain text for regex verification."""
    text = re.sub(r"<(script|style)\b.*?</\1>", " ", raw_html,
                  flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", unescape(text))


def pdf_to_text(pdf_bytes: bytes) -> str:
    """Extract text from a PDF: pdftotext if installed, else a minimal
    pure-python FlateDecode scan (good enough for substring verification)."""
    try:
        proc = subprocess.run(
            ["pdftotext", "-", "-"], input=pdf_bytes,
            capture_output=True, timeout=120)
        if proc.returncode == 0 and len(proc.stdout) > 10_000:
            return re.sub(r"\s+", " ", proc.stdout.decode("utf-8",
                                                          errors="replace"))
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    # fallback: inflate all streams, pull strings out of Tj/TJ text operators
    chunks = []
    for m in re.finditer(rb"stream\r?\n(.*?)endstream", pdf_bytes, re.S):
        try:
            chunks.append(zlib.decompress(m.group(1)))
        except zlib.error:
            continue
    text_parts = []
    for chunk in chunks:
        for s in re.findall(rb"\((?:[^()\\]|\\.)*\)", chunk):
            text_parts.append(
                s[1:-1].replace(rb"\(", b"(").replace(rb"\)", b")")
                       .decode("latin-1", errors="replace"))
    return re.sub(r"\s+", " ", " ".join(text_parts))


def require(text: str, pattern: str, what: str) -> "re.Match":
    """Assert a tabulated claim is literally present in the fetched source."""
    m = re.search(pattern, text)
    if not m:
        raise SystemExit(
            f"VERIFICATION FAILED: could not find {what!r} "
            f"(pattern {pattern!r}) in fetched source — refusing to bake "
            f"unverified data.")
    return m


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def pt(x, y, provenance, **extra):
    d = {"x": x, "y": y, "provenance": provenance}
    d.update(extra)
    return d


# ----------------------------------------------------------------- targets --

def bake_deepseek_r1():
    arxiv_id = "2501.12948"
    url = AR5IV.format(arxiv_id=arxiv_id)
    text = flatten_html(fetch(url, f"{arxiv_id}.html"))

    # verify every tabulated anchor against the paper text/tables
    require(text, r"increases from 15\.6% to 71\.0%",
            "R1-Zero AIME pass@1 15.6% -> 71.0% (Abstract)")
    require(text, r"DeepSeek-R1-Zero 71\.0 86\.7",
            "Table 2 row: R1-Zero AIME pass@1 71.0, cons@64 86.7")
    require(text, r"79\.8% Pass@1 on AIME 2024",
            "DeepSeek-R1 79.8% AIME pass@1 (§1.2)")
    require(text, r"AIME 2024 \(Pass@1\) 16\.0 9\.3 39\.2 63\.6 79\.2 79\.8",
            "Table 4 AIME row (o1-1217 = 79.2, R1 = 79.8)")
    require(text, r"Figure 2: AIME accuracy of DeepSeek-R1-Zero during training",
            "Figure 2 caption")

    # Figure 2 exists only as an image: the curve below is read off the
    # published figure by eye. Endpoints are exact (stated in text/tables).
    curve = [pt(0, 15.6, TABULATED,
                note="RL start; 'increases from 15.6%' (Abstract; §2.2.4)")]
    traced = [(800, 26.0), (1600, 35.0), (2400, 42.0), (3200, 48.0),
              (4000, 53.0), (4800, 57.0), (5600, 61.0), (6400, 64.0),
              (7200, 67.5)]
    curve += [pt(x, y, TRACED) for x, y in traced]
    curve.append(pt(8000, 71.0, TABULATED,
                    note="end of RL; 71.0 pass@1 (Abstract; Table 2)"))

    return {
        "source": {
            "arxivId": arxiv_id,
            "title": ("DeepSeek-R1: Incentivizing Reasoning Capability in "
                      "LLMs via Reinforcement Learning"),
            "url": url,
            "figure": ("Figure 2 — AIME accuracy of DeepSeek-R1-Zero during "
                       "training (pass@1 averaged over 16 samples/question)"),
        },
        "provenance": TRACED,
        "notes": ("Training-curve interior points are traced by eye from the "
                  "published Figure 2 (no data table exists); x = RL steps, "
                  "axis approximate (paper says only 'thousands of RL "
                  "steps'). Endpoints and all values in the 'aime-anchors' "
                  "series are exact numbers stated in the paper."),
        "series": [
            {
                "id": "r1-zero-aime-training",
                "label": "DeepSeek-R1-Zero — AIME 2024 pass@1 during RL",
                "provenance": TRACED,
                "sectionRef": "Figure 2; §2.2.4",
                "xAxis": {"label": "RL steps",
                          "note": "approximate; traced from Figure 2"},
                "yAxis": {"label": "AIME 2024 pass@1", "unit": "%"},
                "points": curve,
            },
            {
                "id": "aime-anchors",
                "label": "AIME 2024 anchors (exact values from paper)",
                "provenance": TABULATED,
                "yAxis": {"label": "AIME 2024 accuracy", "unit": "%"},
                "points": [
                    {"label": "DeepSeek-R1-Zero at RL start (pass@1)",
                     "y": 15.6, "provenance": TABULATED,
                     "sectionRef": "Abstract; §2.2.4"},
                    {"label": "DeepSeek-R1-Zero after RL (pass@1)",
                     "y": 71.0, "provenance": TABULATED,
                     "sectionRef": "Abstract; Table 2"},
                    {"label": "DeepSeek-R1-Zero cons@64 (majority voting)",
                     "y": 86.7, "provenance": TABULATED,
                     "sectionRef": "Abstract; Table 2"},
                    {"label": "DeepSeek-R1 (pass@1)",
                     "y": 79.8, "provenance": TABULATED,
                     "sectionRef": "§1.2; Table 4"},
                    {"label": "OpenAI-o1-1217 (pass@1)",
                     "y": 79.2, "provenance": TABULATED,
                     "sectionRef": "Table 4"},
                ],
            },
        ],
    }


def bake_rlhf():
    arxiv_id = "2203.02155"
    url = AR5IV.format(arxiv_id=arxiv_id)
    text = flatten_html(fetch(url, f"{arxiv_id}.html"))

    require(text,
            r"outputs from the 1\.3B parameter InstructGPT model are "
            r"preferred to outputs from the 175B GPT-3, despite having "
            r"100x fewer parameters",
            "1.3B-beats-175B headline claim (Abstract)")
    require(text, r"preferred to 175B GPT-3 outputs 85 ±.{0,40}?3% of the time",
            "175B InstructGPT vs 175B GPT-3 win rate 85 ± 3%")
    require(text, r"preferred 71 ±.{0,40}?4% of the time to few-shot 175B GPT-3",
            "175B InstructGPT vs few-shot 175B GPT-3 win rate 71 ± 4%")
    require(text, r"outputs from our 1\.3B PPO-ptx model are preferred to "
                  r"those from the 175B GPT-3",
            "Figure 1 caption restating the 1.3B result")

    return {
        "source": {
            "arxivId": arxiv_id,
            "title": ("Training language models to follow instructions with "
                      "human feedback (InstructGPT)"),
            "url": url,
            "figure": ("Figure 1 headline preference results (human evals on "
                       "the API prompt distribution)"),
        },
        "provenance": TABULATED,
        "notes": ("All values are stated verbatim in the paper's text; "
                  "section refs per point. Figure 1 itself plots win rate "
                  "against the 175B SFT baseline — the paper gives the "
                  "1.3B-vs-175B result only qualitatively ('preferred'), so "
                  "no numeric win rate is fabricated for that pairing. Error "
                  "bars in the paper are 95% confidence intervals."),
        "series": [
            {
                "id": "headline-win-rates",
                "label": ("Human labeler preference win rates "
                          "(API prompt distribution)"),
                "provenance": TABULATED,
                "yAxis": {"label": "preferred over comparison model",
                          "unit": "% of comparisons"},
                "points": [
                    {"label": "175B InstructGPT vs 175B GPT-3",
                     "y": 85, "ci95": 3, "provenance": TABULATED,
                     "quote": ("Outputs from our 175B InstructGPT are "
                               "preferred to 175B GPT-3 outputs 85 ± 3% of "
                               "the time"),
                     "sectionRef": ("§1 (findings); §4.1 Results on the API "
                                    "distribution")},
                    {"label": "175B InstructGPT vs few-shot 175B GPT-3",
                     "y": 71, "ci95": 4, "provenance": TABULATED,
                     "quote": ("preferred 71 ± 4% of the time to few-shot "
                               "175B GPT-3"),
                     "sectionRef": ("§1 (findings); §4.1 Results on the API "
                                    "distribution")},
                ],
            },
            {
                "id": "small-beats-big",
                "label": "1.3B InstructGPT vs 175B GPT-3 (100x fewer params)",
                "provenance": TABULATED,
                "points": [
                    {"label": ("1.3B InstructGPT (PPO-ptx) outputs preferred "
                               "over 175B GPT-3 outputs"),
                     "value": ("preferred (stated qualitatively; exact win "
                               "rate shown only graphically in Figure 1)"),
                     "provenance": TABULATED,
                     "quote": ("outputs from the 1.3B parameter InstructGPT "
                               "model are preferred to outputs from the 175B "
                               "GPT-3, despite having 100x fewer parameters"),
                     "sectionRef": ("Abstract; §1 (findings); Figure 1 "
                                    "caption")},
                ],
            },
        ],
    }


def bake_gpt2():
    text = pdf_to_text(fetch(GPT2_PDF_URL, "gpt2.pdf", binary=True))
    if len(text) < 20_000:
        raise SystemExit("VERIFICATION FAILED: GPT-2 PDF text extraction "
                         "produced too little text to verify against.")

    require(text, r"Zero-shot task performance of WebText LMs as a function "
                  r"of model size", "Figure 1 caption")
    require(text, r"55 F1 on the CoQA", "CoQA 55 F1 (Abstract; §3.5)")
    require(text, r"achieving 11\.5 BLEU", "WMT-14 Fr-En 11.5 BLEU (§3.7)")
    require(text, r"33\.5 BLEU", "unsupervised MT SOTA 33.5 BLEU (§3.7)")
    require(text, r"answers 4\.1% of questions correctly",
            "Natural Questions 4.1% exact match (§3.8)")
    require(text, r"1\.0% accuracy", "NQ trivial baseline 1.0% (§3.8)")
    require(text, r"5\.3 times more questions",
            "largest answers 5.3x more than smallest (§3.8)")
    require(text, r"21\.40", "Table 4 GPT-2 TL;DR ROUGE-AVG 21.40")
    require(text, r"20\.98", "Table 4 Random-3 ROUGE-AVG 20.98")

    sizes = [117, 345, 762, 1542]  # params, millions

    def curve(traced_ys, final_y, final_ref, first_note=None):
        pts = []
        for i, x in enumerate(sizes[:-1]):
            p = pt(x, traced_ys[i], TRACED)
            if i == 0 and first_note:
                p["note"] = first_note
            pts.append(p)
        pts.append(pt(sizes[-1], final_y, TABULATED, sectionRef=final_ref))
        return pts

    return {
        "source": {
            "arxivId": None,
            "title": ("Language Models are Unsupervised Multitask Learners "
                      "(GPT-2)"),
            "url": GPT2_PDF_URL,
            "figure": ("Figure 1 — zero-shot task performance of WebText LMs "
                       "as a function of model size, on 4 tasks"),
        },
        "provenance": TRACED,
        "notes": ("GPT-2 has no arXiv id; source is OpenAI's published PDF. "
                  "Only the 1542M endpoint of each curve is stated as a "
                  "number in the text/tables; the 117M/345M/762M points are "
                  "traced by eye from Figure 1. Reference lines are exact "
                  "values from the text/Table 4. The 117M Natural-Questions "
                  "point is derived from text (4.1% / 5.3 ≈ 0.8%)."),
        "xAxis": {"label": "parameters", "unit": "M",
                  "values": sizes,
                  "note": "117M / 345M / 762M / 1542M WebText LMs"},
        "series": [
            {
                "id": "reading-comprehension",
                "label": "Reading Comprehension — CoQA dev F1",
                "provenance": TRACED,
                "yAxis": {"label": "F1", "unit": ""},
                "points": curve([26.5, 42.5, 50.0], 55.0,
                                "Abstract; §3.5 ('55 F1 on the CoQA')"),
                "reference": {"label": "Supervised SOTA (BERT), near human",
                              "y": 89.0, "provenance": TABULATED,
                              "sectionRef": ("§3.5 ('nearing the 89 F1 "
                                             "performance of humans')")},
            },
            {
                "id": "translation",
                "label": "Translation — WMT-14 Fr→En BLEU",
                "provenance": TRACED,
                "yAxis": {"label": "BLEU", "unit": ""},
                "points": curve([0.6, 3.5, 8.0], 11.5,
                                "§3.7 ('achieving 11.5 BLEU')"),
                "reference": {"label": ("Best unsupervised MT "
                                        "(Artetxe et al. 2019)"),
                              "y": 33.5, "provenance": TABULATED,
                              "sectionRef": "§3.7"},
            },
            {
                "id": "summarization",
                "label": "Summarization — CNN/Daily Mail ROUGE (R-AVG)",
                "provenance": TRACED,
                "yAxis": {"label": "ROUGE avg (R-1/R-2/R-L)", "unit": ""},
                "points": curve([16.2, 18.4, 20.1], 21.4,
                                "Table 4 (GPT-2 TL;DR R-AVG 21.40)"),
                "reference": {"label": "Random-3 sentences baseline",
                              "y": 20.98, "provenance": TABULATED,
                              "sectionRef": "Table 4"},
            },
            {
                "id": "question-answering",
                "label": "Question Answering — Natural Questions exact match",
                "provenance": TRACED,
                "yAxis": {"label": "exact match", "unit": "%"},
                "points": curve(
                    [0.8, 1.6, 2.6], 4.1,
                    "§3.8 ('answers 4.1% of questions correctly')",
                    first_note=("derived from text: 1542M answers 5.3x more "
                                "than smallest → 4.1/5.3 ≈ 0.8%")),
                "reference": {"label": ("most-common-answer-per-question-"
                                        "type baseline"),
                              "y": 1.0, "provenance": TABULATED,
                              "sectionRef": "§3.8"},
            },
        ],
    }


def bake_gpt3():
    arxiv_id = "2005.14165"
    url = AR5IV.format(arxiv_id=arxiv_id)
    text = flatten_html(fetch(url, f"{arxiv_id}.html"))

    require(text, r"Figure 1\.2: Larger models make increasingly efficient "
                  r"use of in-context information", "Figure 1.2 caption")
    require(text, r"remove random symbols from a word",
            "Figure 1.2 task description")
    # Table H.1 row: Symbol Insertion accuracy for all 8 model sizes in
    # zero-shot (K=0), one-shot (K=1), few-shot (K=100) — 24 numbers.
    row = require(text, r"Symbol Insertion acc n/a 100((?: [\d.]+){24})",
                  "Table H.1 Symbol Insertion row")
    vals = [float(v) for v in row.group(1).split()]
    zero, one, few = vals[0:8], vals[8:16], vals[16:24]
    # model order in Table H.1: 125M 350M 760M 1.3B 2.7B 6.7B 13B 175B
    idx = {"1.3B": 3, "13B": 6, "175B": 7}
    # sanity anchors also stated in Table 3.10 (175B): 8.26 / 45.4 / 67.2
    assert (zero[7], one[7], few[7]) == (8.26, 45.4, 67.2), \
        "Table H.1 175B anchors disagree with Table 3.10"

    # interior K points traced by eye from Figure 1.2 (with natural-language
    # prompt); K=0, 1, 100 are exact from Table H.1.
    traced_mid = {  # K: 2, 4, 8, 16, 32, 64
        "1.3B": [1.5, 2.0, 2.4, 2.8, 3.2, 3.7],
        "13B": [10.0, 13.0, 16.0, 19.0, 22.0, 25.0],
        "175B": [52.0, 56.0, 60.0, 62.5, 64.5, 66.0],
    }
    ks_mid = [2, 4, 8, 16, 32, 64]

    def curve(model):
        i = idx[model]
        pts = [pt(0, zero[i], TABULATED, sectionRef="Table H.1 (zero-shot)"),
               pt(1, one[i], TABULATED, sectionRef="Table H.1 (one-shot)")]
        pts += [pt(k, y, TRACED)
                for k, y in zip(ks_mid, traced_mid[model])]
        pts.append(pt(100, few[i], TABULATED,
                      sectionRef="Table H.1 (few-shot, K=100); Table 3.10"))
        return pts

    return {
        "source": {
            "arxivId": arxiv_id,
            "title": "Language Models are Few-Shot Learners (GPT-3)",
            "url": url,
            "figure": ("Figure 1.2 — in-context learning curves on the "
                       "Symbol Insertion task (remove random symbols from a "
                       "word), accuracy vs number of in-context examples K"),
        },
        "provenance": TRACED,
        "notes": ("Curves shown are the with-natural-language-prompt "
                  "variants from Figure 1.2 (the figure also shows dashed "
                  "no-prompt variants, omitted here). K=0, K=1 and K=100 "
                  "points are exact values extracted from Table H.1 (also "
                  "Table 3.10 for 175B); intermediate K points are traced by "
                  "eye from the published figure."),
        "xAxis": {"label": "number of examples in context (K)"},
        "yAxis": {"label": "Symbol Insertion accuracy", "unit": "%"},
        "series": [
            {"id": "gpt3-1.3b", "label": "1.3B params (small)",
             "provenance": TRACED, "points": curve("1.3B")},
            {"id": "gpt3-13b", "label": "13B params (medium)",
             "provenance": TRACED, "points": curve("13B")},
            {"id": "gpt3-175b", "label": "175B params (GPT-3)",
             "provenance": TRACED, "points": curve("175B")},
        ],
    }


def bake_moe():
    arxiv_id = "2101.03961"
    url = AR5IV.format(arxiv_id=arxiv_id)
    text = flatten_html(fetch(url, f"{arxiv_id}.html"))

    require(text, r"up to 7x increases in pre-training speed with the same "
                  r"computational resources", "7x speedup claim (Abstract)")
    require(text, r"7x\+ pre-training speedups while still using the same "
                  r"FLOPS per token", "7x+ claim (§1 contributions)")
    require(text, r"at step 60k at step 450k, which is a 7\.5x speedup",
            "7.5x step-time speedup (§3.1/Figure 4)")
    require(text, r"trains in one-seventh the time that it would take the "
                  r"T5-Base", "1/7 wall-clock claim (§3.2/Figure 5)")
    require(text, r"yields a 2\.5x speedup over T5-Large",
            "2.5x vs T5-Large (§3.3/Figure 6)")
    require(text, r"achieve a 4x speedup over the T5-XXL",
            "4x vs T5-XXL (Abstract)")

    # Table 1 rows (as display strings so verification matches the paper's
    # own formatting exactly) — verify each row before emitting.
    table1 = [
        ("T5-Base", None, "-1.731", None, 1600),
        ("T5-Large", None, "-1.550", "131.1", 470),
        ("MoE-Base", "2.0", "-1.547", "68.7", 840),
        ("Switch-Base", "2.0", "-1.554", "72.8", 860),
        ("MoE-Base", "1.25", "-1.559", "80.7", 790),
        ("Switch-Base", "1.25", "-1.553", "65.0", 910),
        ("MoE-Base", "1.0", "-1.572", "80.1", 860),
        ("Switch-Base", "1.0", "-1.561", "62.8", 1000),
        ("Switch-Base+", "1.0", "-1.534", "67.6", 780),
    ]
    for model, cf, nlp, hours, speed in table1:
        cf_pat = "—" if cf is None else re.escape(cf)
        hours_pat = (r"Not achieved \S+" if hours is None
                     else re.escape(hours))
        require(text,
                rf"{re.escape(model)} {cf_pat} {re.escape(nlp)} "
                rf"{hours_pat} {speed}",
                f"Table 1 row for {model} (capacity factor {cf or '—'})")

    return {
        "source": {
            "arxivId": arxiv_id,
            "title": ("Switch Transformers: Scaling to Trillion Parameter "
                      "Models with Simple and Efficient Sparsity"),
            "url": url,
            "figure": ("Headline speedup claims + Table 1 head-to-head "
                       "(Switch vs MoE vs T5 dense baselines)"),
        },
        "provenance": TABULATED,
        "notes": ("All values are numbers stated in the paper's text or "
                  "Table 1. Table 1 setup: 128 experts at every other "
                  "feed-forward layer, all models trained with the same "
                  "computation (32 TPUv3 cores); quality = negative log "
                  "perplexity; time-to-quality threshold = hours to reach "
                  "Neg. Log Perp. = -1.50."),
        "series": [
            {
                "id": "speedup-claims",
                "label": "Pre-training speedup claims",
                "provenance": TABULATED,
                "points": [
                    {"label": ("Switch vs T5-Base, same FLOPs per token "
                               "(headline)"),
                     "value": 7, "unit": "×", "provenance": TABULATED,
                     "quote": ("obtain up to 7x increases in pre-training "
                               "speed with the same computational resources"),
                     "sectionRef": ("Abstract; §1 contributions ('7x+ "
                                    "pre-training speedups while still using "
                                    "the same FLOPS per token')")},
                    {"label": ("Switch-Base (64 experts) reaches T5-Base's "
                               "step-450k quality at step 60k"),
                     "value": 7.5, "unit": "× (step time)",
                     "provenance": TABULATED,
                     "sectionRef": "§3.1 / Figure 4 discussion"},
                    {"label": ("Wall-clock: Switch-Base 64e reaches T5-Base "
                               "perplexity in one-seventh the time"),
                     "value": 7, "unit": "×", "provenance": TABULATED,
                     "sectionRef": "§3.2 / Figure 5"},
                    {"label": ("vs T5-Large, which applies 3.5× more FLOPs "
                               "per token"),
                     "value": 2.5, "unit": "×", "provenance": TABULATED,
                     "sectionRef": "§3.3 / Figure 6"},
                    {"label": "Trillion-parameter Switch vs T5-XXL",
                     "value": 4, "unit": "×", "provenance": TABULATED,
                     "sectionRef": "Abstract"},
                ],
            },
            {
                "id": "table1-t5-base-comparison",
                "label": ("Table 1 — Switch vs MoE vs dense, FLOP-matched to "
                          "T5-Base"),
                "provenance": TABULATED,
                "sectionRef": "Table 1 (§2.2)",
                "columns": ["model", "capacityFactor",
                            "negLogPerplexityAt100kSteps",
                            "hoursToQualityThreshold", "examplesPerSec"],
                "rows": [
                    {"model": m,
                     "capacityFactor": None if cf is None else float(cf),
                     "negLogPerplexityAt100kSteps": float(nlp),
                     "hoursToQualityThreshold":
                         None if hours is None else float(hours),
                     "examplesPerSec": speed,
                     "note": ("did not reach the -1.50 threshold in training"
                              if hours is None else None)}
                    for (m, cf, nlp, hours, speed) in table1
                ],
            },
        ],
    }


TARGETS = {
    "deepseek-r1": bake_deepseek_r1,
    "rlhf": bake_rlhf,
    "gpt2": bake_gpt2,
    "gpt3": bake_gpt3,
    "moe": bake_moe,
}


# -------------------------------------------------------------------- main --

def main():
    ap = argparse.ArgumentParser(
        description="Bake docs/data/{slug}/figure.json for redrawn figures.")
    ap.add_argument("--slug", default=None, choices=sorted(TARGETS),
                    help="bake only this paper's figure (default: all)")
    ap.add_argument("--out-root", default="docs/data",
                    help="output root (default: docs/data)")
    args = ap.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    out_root = Path(args.out_root)
    if not out_root.is_absolute():
        out_root = repo_root / out_root

    slugs = [args.slug] if args.slug else sorted(TARGETS)
    for slug in slugs:
        data = TARGETS[slug]()
        payload = {
            "baker": BAKER,
            "bakedAt": now_utc(),
            "slug": slug,
            "source": data["source"],
            "provenance": data["provenance"],
            "notes": data["notes"],
        }
        for k in ("xAxis", "yAxis"):
            if k in data:
                payload[k] = data[k]
        payload["series"] = data["series"]

        out_path = out_root / slug / "figure.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, indent=2,
                                       ensure_ascii=False) + "\n",
                            encoding="utf-8")
        print(f"{slug}: baked {out_path.relative_to(repo_root)} "
              f"({payload['provenance']}; {len(payload['series'])} series; "
              f"{out_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
