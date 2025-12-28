#!/usr/bin/env python3
# -*- coding: utf-8 -*-



from __future__ import annotations

import json
import re
from pathlib import Path
from typing import List, Set

import nltk
from nltk.corpus import wordnet as wn

ROOT = Path(__file__).resolve().parents[1]
PRED_PATH = ROOT / "wsd" / "results" / "predictions_bert_semcor.json"
OUT_PATH = ROOT / "kb" / "kb_aug.pl"


def slug(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    if not s:
        return "x"
    if s[0].isdigit():
        s = "x_" + s
    return s


def main() -> None:
    if not PRED_PATH.exists():
        raise FileNotFoundError(f"Missing {PRED_PATH}. Run wsd/predict_in_domain.py first.")

    obj = json.loads(PRED_PATH.read_text(encoding="utf-8"))
    preds = obj.get("predictions", [])

    facts: List[str] = []
    facts.append("% kb_aug.pl (auto-generated WordNet augmentation)")
    facts.append("% Provides: synonym/2, is_a/2")

    seen: Set[str] = set()

    for ex in preds:
        lemma = ex["lemma"]
        syn_name = ex.get("model") or ex.get("mfs")
        if not syn_name:
            continue
        try:
            syn = wn.synset(syn_name)
        except Exception:
            continue

        term = slug(lemma)

        for l in syn.lemma_names():
            l2 = slug(l)
            f = f"synonym({term}, {l2})."
            if f not in seen:
                seen.add(f); facts.append(f)

        for h in syn.hypernyms():
            if not h.lemma_names():
                continue
            hyper = slug(h.lemma_names()[0])
            f = f"is_a({term}, {hyper})."
            if f not in seen:
                seen.add(f); facts.append(f)

    OUT_PATH.write_text("\n".join(facts) + "\n", encoding="utf-8")
    print(f"[OK] Wrote: {OUT_PATH}")


if __name__ == "__main__":
    main()
