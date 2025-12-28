#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Baseline MFS (Most Frequent Sense) for WSD.

Input:
  - wsd/semcor_instances.jsonl
Output:
  - wsd/mfs_model.json
  - wsd/mfs_eval.json
"""

from __future__ import annotations

import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[1]
INP = ROOT / "wsd" / "semcor_instances.jsonl"
MODEL_OUT = ROOT / "wsd" / "mfs_model.json"
EVAL_OUT = ROOT / "wsd" / "mfs_eval.json"


def load_instances(path: Path) -> List[dict]:
    items = []
    for ln in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if ln.strip():
            items.append(json.loads(ln))
    return items


def build_mfs(train: List[dict]) -> Dict[str, str]:
    counts = defaultdict(Counter)
    for ex in train:
        key = f"{ex['lemma']}::{ex['pos']}"
        counts[key][ex["label"]] += 1
    return {k: c.most_common(1)[0][0] for k, c in counts.items()}


def main() -> None:
    if not INP.exists():
        raise FileNotFoundError(f"Missing {INP}. Run wsd/prepare_semcor.py first.")

    data = load_instances(INP)
    random.seed(42)
    random.shuffle(data)

    split = int(0.8 * len(data))
    train, test = data[:split], data[split:]

    model = build_mfs(train)

    correct = 0
    total = 0
    for ex in test:
        key = f"{ex['lemma']}::{ex['pos']}"
        yhat = model.get(key)
        if yhat is None:
            continue
        total += 1
        correct += int(yhat == ex["label"])

    acc = correct / total if total else 0.0

    MODEL_OUT.write_text(json.dumps(model, ensure_ascii=False, indent=2), encoding="utf-8")
    EVAL_OUT.write_text(json.dumps({"accuracy": acc, "n_test": total}, indent=2), encoding="utf-8")
    print(f"[OK] acc={acc:.4f} (n_test={total})")
    print(f"[OK] Wrote: {MODEL_OUT}")
    print(f"[OK] Wrote: {EVAL_OUT}")


if __name__ == "__main__":
    main()
