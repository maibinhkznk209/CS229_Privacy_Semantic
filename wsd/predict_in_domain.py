#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Run WSD predictions on your paragraph target words.

Inputs:
  - data/paragraph.txt
  - wsd/mfs_model.json
  - (optional) wsd/per_lemma_models.pkl

Output:
  - wsd/predictions.json

Requires:
  nltk corpora: punkt, averaged_perceptron_tagger, wordnet, omw-1.4
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import List, Tuple

import nltk
import joblib

ROOT = Path(__file__).resolve().parents[1]
PAR_PATH = ROOT / "data" / "paragraph.txt"
MFS_PATH = ROOT / "wsd" / "mfs_model.json"
PER_LEMMA_PATH = ROOT / "wsd" / "per_lemma_models.pkl"
OUT_PATH = ROOT / "wsd" / "predictions.json"


def penn_to_wn(pos: str) -> str | None:
    if pos.startswith("NN"):
        return "n"
    if pos.startswith("VB"):
        return "v"
    if pos.startswith("JJ"):
        return "a"
    if pos.startswith("RB"):
        return "r"
    return None


def main() -> None:
    if not PAR_PATH.exists():
        raise FileNotFoundError(f"Missing {PAR_PATH}")
    if not MFS_PATH.exists():
        raise FileNotFoundError(f"Missing {MFS_PATH}. Run wsd/baseline_mfs.py first.")

    text = PAR_PATH.read_text(encoding="utf-8", errors="ignore")
    tokens = [w.lower() for w in nltk.word_tokenize(text)]
    tagged = nltk.pos_tag(tokens)

    mfs = json.loads(MFS_PATH.read_text(encoding="utf-8"))
    per_models = joblib.load(PER_LEMMA_PATH) if PER_LEMMA_PATH.exists() else {}

    targets: List[Tuple[str, str]] = []
    for w, ppos in tagged:
        if not re.match(r"^[a-z][a-z\-]+$", w):
            continue
        wn_pos = penn_to_wn(ppos)
        if wn_pos in {"n", "v", "a"}:
            targets.append((w, wn_pos))

    # unique targets preserving order
    seen = set()
    targets = [(w, p) for (w, p) in targets if not ((w, p) in seen or seen.add((w, p)))]

    context_text = " ".join(tokens)

    preds = []
    for lemma, pos in targets:
        key = f"{lemma}::{pos}"
        mfs_label = mfs.get(key)

        model_label = None
        if key in per_models:
            vec = per_models[key]["vectorizer"]
            clf = per_models[key]["classifier"]
            model_label = clf.predict(vec.transform([context_text]))[0]

        preds.append({"lemma": lemma, "pos": pos, "mfs": mfs_label, "model": model_label})

    OUT_PATH.write_text(json.dumps({"n_targets": len(preds), "predictions": preds}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] Wrote: {OUT_PATH}")


if __name__ == "__main__":
    main()
