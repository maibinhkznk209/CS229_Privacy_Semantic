#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MFS (Most Frequent Sense) Baseline for WSD.

Evaluates on reference_annotations.csv (in-domain Privacy Policy data).
MFS = WordNet first synset (most frequent sense in WordNet).
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Optional, List

from nltk.corpus import wordnet as wn
from sklearn.metrics import precision_score, recall_score, f1_score

# Paths - updated for new folder structure
SCRIPT_DIR = Path(__file__).parent
REF_PATH = SCRIPT_DIR / "data" / "reference_annotations.csv"
OUT_PATH = SCRIPT_DIR / "results" / "mfs_eval.json"
PREDICTIONS_OUT = SCRIPT_DIR / "results" / "predictions_mfs.json"


def mfs_predict(lemma: str, pos: str) -> Optional[str]:
    """
    Most Frequent Sense baseline.
    Returns first synset from WordNet (most common sense).
    """
    pos_map = {
        'n': wn.NOUN, 'v': wn.VERB, 'a': wn.ADJ, 's': wn.ADJ, 'r': wn.ADV,
    }
    
    wn_pos = pos_map.get(pos.lower())
    synsets = wn.synsets(lemma.lower(), pos=wn_pos) if wn_pos else wn.synsets(lemma.lower())
    
    if synsets:
        return synsets[0].name()
    return None


def normalize_synset(synset_name: str) -> str:
    """Normalize synset name for comparison."""
    if not synset_name:
        return ""
    parts = synset_name.split('.')
    if len(parts) >= 3:
        try:
            return f"{parts[0]}.{parts[1]}.{int(parts[2]):02d}"
        except:
            return synset_name.lower()
    return synset_name.lower()


def calculate_metrics(y_true: List[str], y_pred: List[str]) -> dict:
    """Calculate precision, recall, F1 metrics."""
    # Filter out empty predictions
    valid_indices = [i for i in range(len(y_true)) if y_true[i] and y_pred[i]]
    y_true_valid = [y_true[i] for i in valid_indices]
    y_pred_valid = [y_pred[i] for i in valid_indices]
    
    if not y_true_valid:
        return {"precision_macro": 0, "recall_macro": 0, "f1_weighted": 0}
    
    return {
        "precision_macro": round(precision_score(y_true_valid, y_pred_valid, average='macro', zero_division=0), 4),
        "recall_macro": round(recall_score(y_true_valid, y_pred_valid, average='macro', zero_division=0), 4),
        "f1_weighted": round(f1_score(y_true_valid, y_pred_valid, average='weighted', zero_division=0), 4),
    }


def main() -> None:
    if not REF_PATH.exists():
        raise FileNotFoundError(f"Missing {REF_PATH}. Please ensure reference_annotations.csv exists.")
    
    print(f"[INFO] Loading reference from: {REF_PATH}")
    
    # Load reference annotations
    annotations = []
    with REF_PATH.open(encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            annotations.append({
                'lemma': row['lemma'],
                'pos': row['pos'],
                'reference': row['synset'],
            })
    
    print(f"[INFO] Loaded {len(annotations)} annotations")
    
    # Run MFS predictions
    predictions = []
    y_true = []
    y_pred = []
    correct = 0
    total = 0
    
    for ann in annotations:
        lemma = ann['lemma']
        pos = ann['pos']
        reference = ann['reference']
        
        # MFS prediction
        mfs_pred = mfs_predict(lemma, pos)
        
        # Normalize for comparison
        ref_norm = normalize_synset(reference)
        mfs_norm = normalize_synset(mfs_pred or "")
        
        match = (ref_norm == mfs_norm) if ref_norm and mfs_norm else False
        
        if ref_norm:
            total += 1
            y_true.append(ref_norm)
            y_pred.append(mfs_norm)
            if match:
                correct += 1
        
        predictions.append({
            'lemma': lemma,
            'pos': pos,
            'reference': reference,
            'mfs': mfs_pred,
            'match': match
        })
    
    acc = correct / total if total else 0.0
    metrics = calculate_metrics(y_true, y_pred)
    
    # Save results
    results = {
        "method": "MFS Baseline (WordNet first synset)",
        "dataset": "reference_annotations.csv",
        "accuracy": round(acc, 4),
        "correct": correct,
        "total": total,
        "precision_macro": metrics["precision_macro"],
        "recall_macro": metrics["recall_macro"],
        "f1_weighted": metrics["f1_weighted"],
        "accuracy_display": f"{acc:.2%} ({correct}/{total})"
    }
    
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    PREDICTIONS_OUT.write_text(
        json.dumps({"predictions": predictions}, indent=2, ensure_ascii=False), 
        encoding="utf-8"
    )
    
    print(f"\n[RESULTS]")
    print(f"  Dataset: reference_annotations.csv ({total} tokens)")
    print(f"  Accuracy: {acc:.2%} ({correct}/{total})")
    print(f"  Precision (macro): {metrics['precision_macro']:.4f}")
    print(f"  Recall (macro): {metrics['recall_macro']:.4f}")
    print(f"  F1 (weighted): {metrics['f1_weighted']:.4f}")
    print(f"\n[OK] Saved: {OUT_PATH}")
    print(f"[OK] Saved: {PREDICTIONS_OUT}")


if __name__ == "__main__":
    main()

