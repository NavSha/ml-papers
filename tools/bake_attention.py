#!/usr/bin/env python3
"""Bake GPT-2 small attention data for widgets/transformer.js (CP4).

Runs GPT-2 small (HF transformers, output_attentions=True) over 8 curated
sentences — 6 success cases, each a named attention phenomenon (pronoun
coreference, negation scope, long-range subject-verb agreement, idiom
completion, repeated-name binding, previous-token head) — and 2 designed
failure cases (SPEC break-it rule) where gpt2-small's attention visibly
diffuses. For each sentence the single most pedagogically clear
(layer, head) is selected by max attention mass from the source token onto
the target word, and the outcome is recorded as HOLDS or DIFFUSES (the
failure evidence). Emits ONLY the selected head's TxT weights per sentence,
quantized to uint8 (scale 1/255), to docs/data/transformer/attention.json
(<=3MB total; SPEC §6c).

DEPENDENCIES — runs in the project venv, NOT system python:
    .venv/bin/python tools/bake_attention.py
    venv recipe (CP0): uv venv --python 3.11 .venv &&
        uv pip install --python .venv/bin/python torch transformers numpy pillow
    uses: torch, transformers (GPT-2 small, downloads from HF on first run,
    public model, no token; budget 5-15 min), numpy.
Fallback variant if this bake fails: taylor-transformer char-level ONNX model
(SPEC §6c fallback contract).
"""
import argparse
import datetime
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# HOLDS criterion (empirical, per SPEC §6c break-it rule): the selected head
# must put >=30% of the source token's attention on the target word, AND the
# target must be the top attended position other than the source itself —
# allowing the well-known first-token attention sink to outrank it.
HOLD_MASS = 0.30

SENTENCES = [
    dict(
        id="coref",
        text="The trophy would not fit in the suitcase because it was too big.",
        src=("it", 1), dst=("trophy", 1), fail=False,
        why="Winograd-style pronoun coreference: to make sense of “it,” "
            "something inside the model has to look back at “trophy.”",
        note_holds="From “it,” {pct}% of this head’s attention lands "
                   "on “trophy” — a learned coreference lookup nobody "
                   "programmed in.",
        note_diffuse="Expected a coreference lookup from “it” to "
                     "“trophy”, but the best head only puts {pct}% there.",
    ),
    dict(
        id="negation",
        text="She did not eat anything at the party last night.",
        src=("anything", 1), dst=("not", 1), fail=False,
        why="Negation scope: “anything” is only grammatical because "
            "“not” came earlier — a head has to track the negation "
            "that licenses it.",
        note_holds="From “anything,” {pct}% of this head’s attention "
                   "goes straight to “not” — the word that licenses it.",
        note_diffuse="Expected “anything” to find its licensing "
                     "“not”, but the best head only puts {pct}% there.",
    ),
    dict(
        id="agreement",
        text="The keys to the old wooden cabinet were on the table.",
        src=("were", 1), dst=("keys", 1), fail=False,
        why="Long-range subject–verb agreement: “were” agrees with "
            "“keys,” not the nearer singular “cabinet.” The head "
            "must skip the distractor.",
        note_holds="“were” reaches over “cabinet” back to its real "
                   "subject “keys” with {pct}% of this head’s attention.",
        note_diffuse="Expected “were” to find “keys” past the "
                     "distractor, but the best head only puts {pct}% there.",
    ),
    dict(
        id="idiom",
        text="He decided to spill the beans about the surprise party.",
        src=("beans", 1), dst=("spill", 1), fail=False,
        why="Idiom binding: “beans” only means secrets next to "
            "“spill” — the pair behaves like one unit, and a head "
            "links the two halves.",
        note_holds="“beans” binds back to “spill” with {pct}% of "
                   "this head’s attention — the idiom is stored as a pair.",
        note_diffuse="Expected “beans” to bind to “spill”, but the "
                     "best head only puts {pct}% there.",
    ),
    dict(
        id="repeat",
        text="When John and Mary went to the store, John handed a drink to Mary.",
        src=("John", 2), dst=("John", 1), fail=False,
        why="Repeated-name binding: the second “John” looks back at the "
            "first — duplicate-token heads like this one are an ingredient "
            "of in-context learning.",
        note_holds="The second “John” finds the first with {pct}% of this "
                   "head’s attention — a duplicate-token head at work.",
        note_diffuse="Expected the second “John” to find the first, but "
                     "the best head only puts {pct}% there.",
    ),
    dict(
        id="prevtoken",
        text="The quick brown fox jumps over the lazy dog.",
        src=("fox", 1), dst=("brown", 1), fail=False,
        why="A previous-token head: some heads ignore meaning entirely and just "
            "attend one position back — pure positional plumbing that later "
            "layers build on.",
        note_holds="From “fox,” {pct}% of this head’s attention sits "
                   "on the previous token “brown” — and it does the "
                   "same from every position. Pure plumbing.",
        note_diffuse="Expected a previous-token head, but the best candidate "
                     "only puts {pct}% one position back.",
    ),
    dict(
        id="fail-pileup",
        text="The book that the professor whom the students admired wrote "
             "became a bestseller.",
        src=("became", 1), dst=("book", 1), fail=True,
        why="Break it: “became” needs its subject “book,” buried "
            "behind two stacked relative clauses. Watch what the attention "
            "does instead.",
        note_holds="Surprise: even across the clause pile-up, {pct}% of this "
                   "head’s attention still finds “book.”",
        note_diffuse="This breaks. The best head in the whole model puts only "
                     "{pct}% of “became”’s attention on “book” "
                     "— the rest smears across the pile-up. gpt2-small has "
                     "no head that can thread two nested clauses; bigger models "
                     "earn this the same way they earn everything: scale.",
    ),
    dict(
        id="fail-gardenpath",
        text="The horse raced past the barn fell.",
        src=("fell", 1), dst=("horse", 1), fail=True,
        why="Break it: the classic garden-path sentence. “fell” is the "
            "real verb of “horse” — but the model has already "
            "committed to the wrong parse of “raced.”",
        note_holds="Surprise: {pct}% of this head’s attention recovers the "
                   "“horse–fell” link despite the garden path.",
        note_diffuse="This breaks. “fell” should attach to "
                     "“horse,” but the best head anywhere in the model "
                     "puts only {pct}% of its attention there — the model "
                     "parsed “raced” as the main verb and never looked "
                     "back. Humans stumble on this sentence too.",
    ),
]


def find_word_span(text, word, occurrence):
    """Character span of the nth (1-based) whole-word occurrence of `word`."""
    matches = list(re.finditer(r"\b" + re.escape(word) + r"\b", text))
    if len(matches) < occurrence:
        raise ValueError(f"occurrence {occurrence} of {word!r} not in {text!r}")
    m = matches[occurrence - 1]
    return m.start(), m.end()


def tokens_in_span(offsets, start, end):
    """Indices of tokens whose character span overlaps [start, end)."""
    return [i for i, (s, e) in enumerate(offsets) if s < end and e > start]


def bake(out_path):
    import torch
    from transformers import GPT2TokenizerFast, GPT2Model

    tok = GPT2TokenizerFast.from_pretrained("gpt2")
    model = GPT2Model.from_pretrained("gpt2", output_attentions=True)
    model.eval()

    baked = []
    for spec in SENTENCES:
        enc = tok(spec["text"], return_offsets_mapping=True, return_tensors="pt")
        offsets = enc.pop("offset_mapping")[0].tolist()
        with torch.no_grad():
            att = model(**enc).attentions  # 12 x [1, 12, T, T]

        src_span = find_word_span(spec["text"], *spec["src"])
        dst_span = find_word_span(spec["text"], *spec["dst"])
        src_idx = tokens_in_span(offsets, *src_span)[-1]   # last token of word
        dst_idxs = tokens_in_span(offsets, *dst_span)

        # pick the single clearest (layer, head): max mass src -> dst word
        best = None
        for layer in range(12):
            mass = att[layer][0, :, src_idx, dst_idxs].sum(dim=-1)  # [12]
            h = int(mass.argmax())
            if best is None or float(mass[h]) > best[2]:
                best = (layer, h, float(mass[h]))
        layer, head, w = best

        row = att[layer][0, head, src_idx]                  # [T]
        dst_tok = dst_idxs[int(att[layer][0, head, src_idx, dst_idxs].argmax())]
        order = row.argsort(descending=True).tolist()
        top_others = [i for i in order if i != src_idx]
        top1 = top_others[0]
        holds = w >= HOLD_MASS and (
            top1 in dst_idxs or (top1 == 0 and top_others[1] in dst_idxs))

        pct = round(w * 100)
        note = (spec["note_holds"] if holds else spec["note_diffuse"]).format(pct=pct)

        A = att[layer][0, head]                             # [T, T]
        q = torch.clamp((A * 255).round(), 0, 255).to(torch.uint8).tolist()
        toks = [tok.decode([i]) for i in enc["input_ids"][0].tolist()]

        baked.append({
            "id": spec["id"], "text": spec["text"], "tokens": toks,
            "why": spec["why"],
            "expect": {"from": src_idx, "to": dst_tok},
            "layer": layer, "head": head,
            "holds": holds, "fail": spec["fail"], "note": note,
            "weights": q,
        })

        top3 = ", ".join(f"{toks[i].strip()!r}:{row[i]:.2f}" for i in top_others[:3])
        verdict = "HOLDS" if holds else "DIFFUSES"
        want = "diffuse" if spec["fail"] else "hold"
        flag = "" if (holds != spec["fail"]) else "  << UNEXPECTED"
        print(f"  {spec['id']:<16} L{layer}H{head:<2} mass={w:.3f} {verdict:<8} "
              f"(designed to {want}) top:[{top3}]{flag}")

    doc = {
        "baker": "tools/bake_attention.py",
        "model": "gpt2",
        "quantization": "uint8",
        "generated": datetime.date.today().isoformat(),
        "sentences": baked,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(doc, separators=(",", ":")) + "\n")
    kb = out_path.stat().st_size / 1024
    print(f"\nwrote {out_path} ({kb:.0f} KB; budget 3072 KB)")
    assert kb <= 3072, "attention.json exceeds the 3MB SPEC budget"
    return doc


def spot_check(doc):
    """AC spot-check: the coreference sentence attends to its antecedent."""
    s = next(x for x in doc["sentences"] if x["id"] == "coref")
    f, t = s["expect"]["from"], s["expect"]["to"]
    w = s["weights"][f][t] / 255
    ok = s["holds"] and w >= HOLD_MASS
    print(f"spot-check coref: L{s['layer']}H{s['head']} "
          f"{s['tokens'][f].strip()!r} -> {s['tokens'][t].strip()!r} "
          f"weight={w:.2f} holds={s['holds']} => {'PASS' if ok else 'FAIL'}")
    if not ok:
        raise SystemExit("coreference spot-check failed (SPEC §6c AC)")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default="docs/data/transformer/attention.json",
                    help="output path (default: docs/data/transformer/attention.json)")
    args = ap.parse_args()
    out = Path(args.out)
    if not out.is_absolute():
        out = ROOT / out
    print("baking attention.json (gpt2 small, 12 layers x 12 heads)...")
    doc = bake(out)
    spot_check(doc)


if __name__ == "__main__":
    main()
