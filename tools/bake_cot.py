#!/usr/bin/env python3
"""bake_cot.py — bake verbatim paper content + token counts for widgets/cot.js.

Primary content path (SPEC §6b, binding — no metered API key exists in this
environment): every response shown in the widget is reproduced VERBATIM from
Wei et al., "Chain-of-Thought Prompting Elicits Reasoning in Large Language
Models" (arXiv 2201.11903, NeurIPS 2022). Costs recompute in-widget from
docs/prices.json.

Sources, per section of the output JSON:
  headline   Table 2 (PaLM 540B on GSM8K: standard 17.9 -> CoT 56.9).
  exemplar   Figure 1 (the Roger tennis-balls exemplar, both conditions).
             Figure 1 is a vector PDF in the arXiv e-print
             (main_fables/new-pull-figure-landscape.pdf); its text was
             extracted with pdftotext on 2026-07-12 and embedded below,
             because ar5iv renders the figure as an image.
  cases      * case 0: Figure 1's held-out test problem (cafeteria apples) —
               the model output under each condition (standard: wrong 27;
               CoT: right 9). Same pdftotext extraction as the exemplar.
             * cases 1-5: five of the eight few-shot exemplars from Table 20,
               Appendix G ("Few-shot exemplars for full chain of thought
               prompt for math word problems"). CoT answers are extracted
               LIVE from the ar5iv HTML at bake time (urllib) and verified
               against the embedded copies; the "answer directly" condition
               uses the paper's standard-prompting format (Sec. 3.1 /
               Figure 1 left): the bare final answer, "The answer is N."
  breakit    Figure 10, Appendix A.1: fluent-but-wrong chains from PaLM 62B
             (sub-threshold) that scaling to 540B fixed. Also a vector PDF
             (fables/palm-errors-fixed.pdf); pdftotext extraction embedded.

Token counts: GPT-2 tokenizer (GPT2TokenizerFast), offline, per SPEC §6b.

DEPENDENCIES — runs in the project venv, NOT system python:
    .venv/bin/python tools/bake_cot.py
    venv recipe (CP0): uv venv --python 3.11 .venv &&
        uv pip install --python .venv/bin/python torch transformers numpy pillow
    uses: transformers (GPT2TokenizerFast only — no model download needed).
"""
import argparse
import datetime
import html as htmllib
import json
import pathlib
import re
import sys
import urllib.request

AR5IV_URL = "https://ar5iv.labs.arxiv.org/html/2201.11903"
ARXIV_ABS_URL = "https://arxiv.org/abs/2201.11903"

# ---------------------------------------------------------------------------
# Figure 1 (pull figure) — pdftotext of main_fables/new-pull-figure-landscape.pdf
# from the arXiv e-print tarball (arxiv.org/e-print/2201.11903), 2026-07-12.
# ---------------------------------------------------------------------------
EXEMPLAR_Q = ("Roger has 5 tennis balls. He buys 2 more cans of tennis balls. "
              "Each can has 3 tennis balls. How many tennis balls does he have now?")
EXEMPLAR_DIRECT = "The answer is 11."
EXEMPLAR_COT = ("Roger started with 5 balls. 2 cans of 3 tennis balls each is "
                "6 tennis balls. 5 + 6 = 11. The answer is 11.")

FIG1_TEST_Q = ("The cafeteria had 23 apples. If they used 20 to make lunch and "
               "bought 6 more, how many apples do they have?")
FIG1_TEST_DIRECT = "The answer is 27."          # model output, standard prompting — WRONG
FIG1_TEST_COT = ("The cafeteria had 23 apples originally. They used 20 to make "
                 "lunch. So they had 23 - 20 = 3. They bought 6 more apples, so "
                 "they have 3 + 6 = 9. The answer is 9.")  # model output, CoT — right

# ---------------------------------------------------------------------------
# Table 20, Appendix G — the paper's 8-shot math-word-problem CoT prompt.
# We use five of the eight. Embedded copies double as the offline fallback and
# as the verification target for the live ar5iv extraction.
# ---------------------------------------------------------------------------
TABLE20_PICKS = [
    ("There are 15 trees in the grove. Grove workers will plant trees in the "
     "grove today. After they are done, there will be 21 trees. How many trees "
     "did the grove workers plant today?",
     "There are 15 trees originally. Then there were 21 trees after some more "
     "were planted. So there must have been 21 - 15 = 6. The answer is 6."),
    ("Leah had 32 chocolates and her sister had 42. If they ate 35, how many "
     "pieces do they have left in total?",
     "Originally, Leah had 32 chocolates. Her sister had 42. So in total they "
     "had 32 + 42 = 74. After eating 35, they had 74 - 35 = 39. The answer is 39."),
    ("There were nine computers in the server room. Five more computers were "
     "installed each day, from monday to thursday. How many computers are now "
     "in the server room?",
     "There were originally 9 computers. For each of 4 days, 5 more computers "
     "were added. So 5 * 4 = 20 computers were added. 9 + 20 is 29. The answer is 29."),
    ("Michael had 58 golf balls. On tuesday, he lost 23 golf balls. On "
     "wednesday, he lost 2 more. How many golf balls did he have at the end of "
     "wednesday?",
     "Michael started with 58 golf balls. After losing 23 on tuesday, he had "
     "58 - 23 = 35. After losing 2 more, he had 35 - 2 = 33 golf balls. The "
     "answer is 33."),
    ("Olivia has $23. She bought five bagels for $3 each. How much money does "
     "she have left?",
     "Olivia had 23 dollars. 5 bagels for 3 dollars each will be 5 x 3 = 15 "
     "dollars. So she has 23 - 15 dollars left. 23 - 15 is 8. The answer is 8."),
]

# ---------------------------------------------------------------------------
# Figure 10, Appendix A.1 — pdftotext of fables/palm-errors-fixed.pdf from the
# arXiv e-print, 2026-07-12. PaLM 62B outputs (fluent, wrong); the paper's
# error category is quoted from the figure; scaling to 540B fixed all three.
# ---------------------------------------------------------------------------
BREAKIT = [
    {
        "q": ("Tracy used a piece of wire 4 feet long to support tomato plants "
              "in the garden. The wire was cut into pieces 6 inches long. How "
              "many pieces did she obtain?"),
        "model": "PaLM 62B",
        "text": ("She cut the wire into 6 inch pieces. This means she got "
                 "4 * 6 = 24 pieces. The answer is 24."),
        "error": ("semantic understanding error (paper's label) — it never "
                  "converts feet to inches, then multiplies the two numbers it "
                  "was given. 540B gets 8."),
    },
    {
        "q": ("Tom's ship can travel at 10 miles per hour. He is sailing from "
              "1 to 4 PM. He then travels back at a rate of 6 mph. How long "
              "does it take him to get back?"),
        "model": "PaLM 62B",
        "text": ("He travels from 1 to 4 PM. That means he travels for 3 hours. "
                 "He travels back at 6 mph. That means he travels for 3 * 6 = "
                 "18 miles. The answer is 18."),
        "error": ("semantic understanding error (paper's label) — asked \"how "
                  "long\", it answers with a distance, and 3 x 6 isn't even the "
                  "distance. 540B gets 5 hours."),
    },
    {
        "q": ("There are four schools competing at a basketball tournament. "
              "Each school has sent a girls’ basketball team and a boys’ "
              "basketball team and each team has 5 players each. Each school "
              "has also sent a coach for each team. In total, how many people "
              "have all of the schools sent?"),
        "model": "PaLM 62B",
        "text": ("There are 4 schools. Each school has sent a girls’ "
                 "basketball team and a boys’ basketball team. Each team has "
                 "5 players each. That means there are 4 * 2 * 5 = 40 players. "
                 "Each team has a coach. That means there are 40 + 4 = 44 "
                 "coaches. The answer is 44."),
        "error": ("one step missing error (paper's label) — every sentence is "
                  "fluent, but it counts 4 coaches instead of 8 (one per team, "
                  "two teams per school). 540B gets 48."),
    },
]

FINAL_ANSWER_RE = re.compile(r"The answer is ([^.]+)\.\s*$")


def norm(s: str) -> str:
    """Whitespace-normalize for verbatim comparison (ar5iv wraps lines)."""
    return re.sub(r"\s+", " ", s.replace(" ", " ")).strip()


def fetch(url: str, timeout: int = 90) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 "
                                 "(ml-papers bake_cot; contact: repo NavSha/ml-papers)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def extract_table20(page: str) -> list[tuple[str, str]]:
    """Return (question, cot_answer) pairs from Table 20 in the ar5iv HTML."""
    start = page.find("Few-shot exemplars for full chain of thought prompt for math word problems")
    if start < 0:
        raise ValueError("Table 20 caption not found in fetched HTML")
    end = page.find("Table 21", start)
    seg = page[start:end if end > 0 else start + 40000]
    rows = []
    for m in re.finditer(r"<tr[^>]*>(.*?)</tr>", seg, re.S):
        text = re.sub(r"<[^>]+>", "", m.group(1))
        text = norm(htmllib.unescape(text))
        if text:
            rows.append(text)
    pairs, q = [], None
    for row in rows:
        if row.startswith("Q: "):
            q = row[3:]
        elif row.startswith("A: ") and q is not None:
            pairs.append((q, row[3:]))
            q = None
    if len(pairs) != 8:
        raise ValueError(f"expected 8 exemplar pairs in Table 20, got {len(pairs)}")
    return pairs


def direct_from_cot(cot: str) -> str:
    """Standard-prompting condition (Sec 3.1 / Fig 1 left): the bare final answer."""
    m = FINAL_ANSWER_RE.search(cot)
    if not m:
        raise ValueError(f"no final answer in: {cot!r}")
    return f"The answer is {m.group(1)}."


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default="docs/data/cot/cases.json")
    ap.add_argument("--offline", action="store_true",
                    help="skip the ar5iv fetch; use embedded verbatim copies")
    args = ap.parse_args()

    # -- live extraction + verification against embedded copies -------------
    fetched_from, verified = None, False
    picks = list(TABLE20_PICKS)
    if not args.offline:
        for url in (AR5IV_URL, ARXIV_ABS_URL):
            try:
                page = fetch(url)
                pairs = extract_table20(page)
                by_q = {norm(q): a for q, a in pairs}
                live = []
                for q, a_embedded in TABLE20_PICKS:
                    a_live = by_q.get(norm(q))
                    if a_live is None:
                        raise ValueError(f"exemplar not found live: {q[:40]}...")
                    if norm(a_live) != norm(a_embedded):
                        raise ValueError(f"live text differs from embedded copy: {q[:40]}...")
                    live.append((q, a_live))
                picks, fetched_from, verified = live, url, True
                break
            except Exception as e:                      # noqa: BLE001
                print(f"[bake_cot] fetch/extract failed for {url}: {e}", file=sys.stderr)
    if not verified:
        print("[bake_cot] using embedded verbatim copies (offline path)", file=sys.stderr)

    # -- token counts (GPT-2 tokenizer, per SPEC §6b) ------------------------
    from transformers import GPT2TokenizerFast                 # venv dep
    tok = GPT2TokenizerFast.from_pretrained("gpt2")
    ntok = lambda s: len(tok(s)["input_ids"])                   # noqa: E731

    cases = [{
        "id": "cafeteria",
        "q": FIG1_TEST_Q,
        "src": "Figure 1 (model outputs under each condition)",
        "direct": {"text": FIG1_TEST_DIRECT, "tokens": ntok(FIG1_TEST_DIRECT), "correct": False},
        "cot": {"text": FIG1_TEST_COT, "tokens": ntok(FIG1_TEST_COT), "correct": True},
    }]
    for q, cot in picks:
        direct = direct_from_cot(cot)
        cases.append({
            "id": q.split()[0].lower() + "-" + q.split()[2].lower().strip(".,$"),
            "q": q,
            "src": "Table 20, Appendix G (few-shot CoT prompt exemplar)",
            "direct": {"text": direct, "tokens": ntok(direct), "correct": True},
            "cot": {"text": cot, "tokens": ntok(cot), "correct": True},
        })

    breakit = [{**b, "tokens": ntok(b["text"]),
                "src": "Figure 10, Appendix A.1 (62B errors fixed by scaling to 540B)"}
               for b in BREAKIT]

    out = {
        "baker": "tools/bake_cot.py",
        "baked": datetime.date.today().isoformat(),
        "provenance": "reproduced verbatim from arXiv 2201.11903 appendix",
        "provenanceDetail": {
            "paper": "Wei et al. (2022). Chain-of-Thought Prompting Elicits Reasoning "
                     "in Large Language Models. NeurIPS 2022. arXiv:2201.11903",
            "exemplar": "Figure 1 (text extracted via pdftotext from the arXiv "
                        "e-print figure PDF; ar5iv renders it as an image)",
            "cases": "Figure 1 test problem + Table 20, Appendix G. The 'answer "
                     "directly' condition follows the paper's standard-prompting "
                     "format (Sec. 3.1 / Figure 1 left): the bare final answer.",
            "breakit": "Figure 10, Appendix A.1 — PaLM 62B outputs, verbatim; "
                       "error categories are the paper's own labels",
            "table20FetchedFrom": fetched_from,
            "table20VerifiedAgainstLiveFetch": verified,
            "tokenizer": "GPT-2 (GPT2TokenizerFast), counted offline",
        },
        "headline": {"before": 17.9, "after": 56.9, "model": "PaLM 540B",
                     "bench": "GSM8K", "src": "Table 2, arXiv 2201.11903 — "
                     "same weights, only the prompt changed"},
        "exemplar": {
            "q": EXEMPLAR_Q,
            "direct": {"text": EXEMPLAR_DIRECT, "tokens": ntok(EXEMPLAR_DIRECT)},
            "cot": {"text": EXEMPLAR_COT, "tokens": ntok(EXEMPLAR_COT)},
            "src": "Figure 1 — the one worked example shown to the model",
        },
        "cases": cases,
        "breakit": breakit,
    }

    dest = pathlib.Path(args.out)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    kb = dest.stat().st_size / 1024
    print(f"[bake_cot] wrote {dest} ({kb:.1f} KB) — {len(cases)} cases, "
          f"{len(breakit)} break-it examples, live-verified={verified}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
