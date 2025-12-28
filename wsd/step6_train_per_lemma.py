#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Train per-lemma classifier (Logistic Regression) using bag-of-words context features.

Inputs:
  - wsd/semcor_instances.jsonl
Outputs:
  - wsd/per_lemma_models.pkl
  - wsd/per_lemma_meta.json
  - wsd/per_lemma_eval.json

Requires:
  pip install scikit-learn joblib
"""

from __future__ import annotations

import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression

ROOT = Path(__file__).resolve().parents[1]
INP = ROOT / "wsd" / "semcor_instances.jsonl"
MODEL_OUT = ROOT / "wsd" / "per_lemma_models.pkl"
META_OUT = ROOT / "wsd" / "per_lemma_meta.json"
EVAL_OUT = ROOT / "wsd" / "per_lemma_eval.json"

MIN_EXAMPLES = 50


def load_instances(path: Path) -> List[dict]:
    items = []
    for ln in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if ln.strip():
            items.append(json.loads(ln))
    return items


def ctx_to_text(ctx: List[str]) -> str:
    return " ".join(ctx)


def main() -> None:
    if not INP.exists():
        raise FileNotFoundError(f"Missing {INP}. Run wsd/prepare_semcor.py first.")

    data = load_instances(INP)
    random.seed(42)
    random.shuffle(data)

    split = int(0.8 * len(data))
    train, test = data[:split], data[split:]

    groups = defaultdict(list)
    for ex in train:
        key = f"{ex['lemma']}::{ex['pos']}"
        groups[key].append(ex)

    models = {}
    meta = {}

    for key, exs in groups.items():
        labels = sorted(set(e["label"] for e in exs))
        if len(exs) < MIN_EXAMPLES or len(labels) < 2:
            continue

        X = [ctx_to_text(e["context"]) for e in exs]
        y = [e["label"] for e in exs]

        vec = CountVectorizer(ngram_range=(1, 2), max_features=5000)
        Xv = vec.fit_transform(X)

        clf = LogisticRegression(max_iter=200)
        clf.fit(Xv, y)

        models[key] = {"vectorizer": vec, "classifier": clf}
        meta[key] = {"n_train": len(exs), "labels": labels}

    total = 0
    covered = 0
    correct = 0
    for ex in test:
        total += 1
        key = f"{ex['lemma']}::{ex['pos']}"
        if key not in models:
            continue
        covered += 1
        vec = models[key]["vectorizer"]
        clf = models[key]["classifier"]
        pred = clf.predict(vec.transform([ctx_to_text(ex["context"])]))[0]
        correct += int(pred == ex["label"])

    acc = correct / covered if covered else 0.0
    coverage = covered / total if total else 0.0

    joblib.dump(models, MODEL_OUT)
    META_OUT.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    EVAL_OUT.write_text(json.dumps({"accuracy": acc, "coverage": coverage, "n_test": total, "n_covered": covered}, indent=2), encoding="utf-8")

    print(f"[OK] acc={acc:.4f} coverage={coverage:.4f}")
    print(f"[OK] Wrote: {MODEL_OUT}")
    print(f"[OK] Wrote: {META_OUT}")
    print(f"[OK] Wrote: {EVAL_OUT}")


if __name__ == "__main__":
    main()
