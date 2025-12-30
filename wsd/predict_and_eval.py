#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
BERT + SVM WSD Prediction.

Model: Trained on SemCor (per-lemma SVM with BERT embeddings)
Evaluation: reference_annotations.csv (Privacy Policy domain)
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Optional

import torch
import numpy as np
import joblib
from transformers import AutoTokenizer, AutoModel
from nltk.corpus import wordnet as wn

# Paths
SCRIPT_DIR = Path(__file__).parent
REF_PATH = SCRIPT_DIR / "data" / "reference_annotations.csv"
PARAGRAPH_PATH = SCRIPT_DIR.parent / "data" / "paragraph.txt"
MODEL_PATH = SCRIPT_DIR / "models" / "bert_semcor_model.pkl"
EVAL_OUT = SCRIPT_DIR / "results" / "bert_eval.json"
PREDICTIONS_OUT = SCRIPT_DIR / "results" / "predictions_bert_semcor.json"


def get_device():
    if torch.cuda.is_available():
        return torch.device("cuda")
    elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def get_bert_embedding(text: str, tokenizer, model, device) -> np.ndarray:
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=128)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    with torch.no_grad():
        outputs = model(**inputs)
        embedding = outputs.last_hidden_state[:, 0, :].cpu().numpy()[0]
    
    return embedding


def mfs_predict(lemma: str, pos: str) -> Optional[str]:
    """MFS fallback - WordNet first synset."""
    pos_map = {'n': wn.NOUN, 'v': wn.VERB, 'a': wn.ADJ, 's': wn.ADJ, 'r': wn.ADV}
    wn_pos = pos_map.get(pos.lower())
    synsets = wn.synsets(lemma.lower(), pos=wn_pos) if wn_pos else wn.synsets(lemma.lower())
    return synsets[0].name() if synsets else None


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


def main() -> None:
    print("[INFO] BERT + SVM WSD Evaluation")
    print("=" * 60)
    
    # Check files
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Missing {MODEL_PATH}. Run 3_train_bert_semcor.py first.")
    if not REF_PATH.exists():
        raise FileNotFoundError(f"Missing {REF_PATH}.")
    
    # Load model
    print("[INFO] Loading BERT SemCor model...")
    device = get_device()
    print(f"[INFO] Using device: {device}")
    
    model_data = joblib.load(MODEL_PATH)
    models = model_data["models"]
    tokenizer_name = model_data["tokenizer_name"]
    
    print(f"[INFO] Loaded {len(models)} per-lemma models")
    
    # Load BERT
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
    bert_model = AutoModel.from_pretrained(tokenizer_name)
    bert_model.to(device)
    bert_model.eval()
    
    # Load paragraph for context
    paragraph = ""
    if PARAGRAPH_PATH.exists():
        paragraph = PARAGRAPH_PATH.read_text(encoding='utf-8')
        print(f"[INFO] Loaded paragraph ({len(paragraph)} chars)")
    
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
    print("\n[INFO] Running predictions...")
    
    # Get embedding for paragraph context
    context_emb = get_bert_embedding(paragraph[:500], tokenizer, bert_model, device)
    
    # Run predictions
    predictions = []
    correct = 0
    correct_mfs = 0
    total = 0
    covered = 0
    
    for i, ann in enumerate(annotations):
        lemma = ann['lemma']
        pos = ann['pos']
        reference = ann['reference']
        key = f"{lemma}::{pos}"
        
        # MFS fallback
        mfs_pred = mfs_predict(lemma, pos)
        
        # BERT model prediction
        model_pred = None
        has_model = False
        
        if key in models:
            has_model = True
            covered += 1
            clf = models[key]["classifier"]
            model_pred = clf.predict([context_emb])[0]
        else:
            model_pred = mfs_pred  # Fallback to MFS
        
        # Normalize for comparison
        ref_norm = normalize_synset(reference)
        pred_norm = normalize_synset(model_pred or "")
        mfs_norm = normalize_synset(mfs_pred or "")
        
        match = (ref_norm == pred_norm) if ref_norm and pred_norm else False
        mfs_match = (ref_norm == mfs_norm) if ref_norm and mfs_norm else False
        
        if ref_norm:
            total += 1
            if match:
                correct += 1
            if mfs_match:
                correct_mfs += 1
        
        predictions.append({
            'lemma': lemma,
            'pos': pos,
            'reference': reference,
            'model': model_pred,
            'mfs': mfs_pred,
            'has_model': has_model,
            'match': match,
            'mfs_match': mfs_match
        })
        
        if (i + 1) % 20 == 0:
            print(f"  Processed {i + 1}/{len(annotations)}")
    
    acc = correct / total if total else 0.0
    mfs_acc = correct_mfs / total if total else 0.0
    coverage = covered / total if total else 0.0
    
    # Save results - same format as mfs_eval.json
    results = {
        "method": "BERT + SVM (trained on SemCor)",
        "dataset": "reference_annotations.csv",
        "accuracy": round(acc, 4),
        "correct": correct,
        "total": total,
        "accuracy_display": f"{acc:.2%} ({correct}/{total})"
    }
    
    EVAL_OUT.parent.mkdir(parents=True, exist_ok=True)
    EVAL_OUT.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    PREDICTIONS_OUT.write_text(
        json.dumps({
            "model_name": tokenizer_name,
            "method": "BERT + SVM trained on SemCor",
            "predictions": predictions
        }, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    
    print(f"\n{'='*60}")
    print("RESULTS - BERT + SVM")
    print('='*60)
    print(f"Models available: {len(models)}")
    print(f"Coverage on test set: {coverage:.2%} ({covered}/{total} tokens)")
    print(f"\n{'Model':<25} {'Accuracy':<20}")
    print("-"*45)
    print(f"{'MFS Baseline':<25} {mfs_acc:.2%} ({correct_mfs}/{total})")
    print(f"{'BERT + SVM (this model)':<25} {acc:.2%} ({correct}/{total})")
    print("-"*45)
    print(f"Improvement: {(acc - mfs_acc):+.2%}")
    print(f"\n[OK] Saved: {EVAL_OUT}")
    print(f"[OK] Saved: {PREDICTIONS_OUT}")


if __name__ == "__main__":
    main()
