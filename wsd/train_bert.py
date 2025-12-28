#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Train BERT WSD model using SemCor data.
Simple approach: Per-lemma SVM classifiers on BERT embeddings.

Training: SemCor corpus
Output: models/bert_semcor_model.pkl
"""

from __future__ import annotations

import json
import random
from pathlib import Path
from collections import defaultdict

import torch
from transformers import AutoTokenizer, AutoModel
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score
import numpy as np
import joblib

# Paths - updated for new folder structure
SCRIPT_DIR = Path(__file__).parent
SEMCOR_PATH = SCRIPT_DIR / "data" / "semcor_instances.jsonl"
MODEL_OUT = SCRIPT_DIR / "models" / "bert_semcor_model.pkl"
EVAL_OUT = SCRIPT_DIR / "results" / "bert_semcor_train_eval.json"

BERT_MODEL = "bert-base-uncased"
MAX_INSTANCES_PER_LEMMA = 500  # Limit to avoid memory issues


def get_device():
    if torch.cuda.is_available():
        print(f"[INFO] GPU: {torch.cuda.get_device_name(0)}")
        return torch.device("cuda")
    elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        print("[INFO] Using MPS (Apple Silicon)")
        return torch.device("mps")
    print("[INFO] Using CPU")
    return torch.device("cpu")


def load_semcor_data(semcor_path: Path, max_per_lemma=500):
    """Load SemCor instances, grouped by lemma::pos."""
    print(f"[INFO] Loading SemCor data from: {semcor_path}")
    grouped = defaultdict(list)
    
    with semcor_path.open(encoding="utf-8") as f:
        for line in f:
            inst = json.loads(line)
            key = f"{inst['lemma']}::{inst['pos']}"
            
            # Limit instances per lemma
            if len(grouped[key]) < max_per_lemma:
                grouped[key].append(inst)
    
    print(f"[INFO] Loaded data for {len(grouped)} lemma::pos combinations")
    return grouped


def get_bert_embedding(text: str, tokenizer, model, device) -> np.ndarray:
    """Get BERT embedding."""
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=128)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    with torch.no_grad():
        outputs = model(**inputs)
        embedding = outputs.last_hidden_state[:, 0, :].cpu().numpy()[0]
    
    return embedding


def train_per_lemma_models(grouped_data, tokenizer, model, device):
    """Train SVM for each lemma::pos with enough data."""
    models = {}
    
    print("[INFO] Training per-lemma models...")
    total = len(grouped_data)
    
    for i, (key, instances) in enumerate(grouped_data.items()):
        if len(instances) < 10:  # Need at least 10 instances
            continue
        
        if i % 100 == 0:
            print(f"  Processing {i}/{total}: {key}")
        
        # Prepare data
        X = []
        y = []
        
        for inst in instances:
            ctx = inst.get('context', [])
            if isinstance(ctx, list):
                context = ' '.join(ctx[:50])  # Limit context length
            else:
                context = str(ctx)[:500]
            emb = get_bert_embedding(context, tokenizer, model, device)
            X.append(emb)
            y.append(inst['label'])
        
        X = np.array(X)
        
        # Check if we have multiple classes
        unique_labels = set(y)
        if len(unique_labels) < 2:
            continue  # Skip if only one class
        
        # Train/test split
        n_train = int(0.8 * len(X))
        indices = list(range(len(X)))
        random.shuffle(indices)
        
        train_idx = indices[:n_train]
        test_idx = indices[n_train:]
        
        X_train, y_train = X[train_idx], [y[i] for i in train_idx]
        X_test, y_test = X[test_idx], [y[i] for i in test_idx]
        
        # Check train set has multiple classes
        if len(set(y_train)) < 2:
            continue
        
        # Train SVM
        try:
            clf = LinearSVC(random_state=42, max_iter=1000)
            clf.fit(X_train, y_train)
        except Exception as e:
            print(f"  Warning: Failed to train {key}: {e}")
            continue  # Skip if training fails
        
        # Evaluate
        train_acc = accuracy_score(y_train, clf.predict(X_train))
        test_acc = accuracy_score(y_test, clf.predict(X_test)) if len(X_test) > 0 else 0.0
        
        models[key] = {
            "classifier": clf,
            "n_train": len(X_train),
            "n_test": len(X_test),
            "train_acc": train_acc,
            "test_acc": test_acc
        }
    
    print(f"[OK] Trained {len(models)} models")
    return models


def main() -> None:
    print("=" * 60)
    print("BERT + SVM WSD Training")
    print("=" * 60)
    
    # Check SemCor file exists
    if not SEMCOR_PATH.exists():
        raise FileNotFoundError(f"Missing {SEMCOR_PATH}. Run 1_prepare_semcor.py first.")
    
    device = get_device()
    
    # Load BERT
    print(f"[INFO] Loading BERT model: {BERT_MODEL}")
    tokenizer = AutoTokenizer.from_pretrained(BERT_MODEL)
    model = AutoModel.from_pretrained(BERT_MODEL)
    model.to(device)
    model.eval()
    
    # Load SemCor
    grouped_data = load_semcor_data(SEMCOR_PATH, MAX_INSTANCES_PER_LEMMA)
    
    # Train models
    models = train_per_lemma_models(grouped_data, tokenizer, model, device)
    
    # Calculate average accuracy
    if models:
        avg_train_acc = np.mean([m["train_acc"] for m in models.values()])
        avg_test_acc = np.mean([m["test_acc"] for m in models.values() if m["n_test"] > 0])
    else:
        avg_train_acc = 0.0
        avg_test_acc = 0.0
    
    print(f"\n{'='*60}")
    print("TRAINING RESULTS")
    print('='*60)
    print(f"  Models trained: {len(models)}")
    print(f"  Avg train accuracy: {avg_train_acc:.2%}")
    print(f"  Avg test accuracy: {avg_test_acc:.2%}")
    
    # Save
    MODEL_OUT.parent.mkdir(parents=True, exist_ok=True)
    EVAL_OUT.parent.mkdir(parents=True, exist_ok=True)
    
    joblib.dump({
        "models": models,
        "tokenizer_name": BERT_MODEL
    }, MODEL_OUT)
    
    eval_results = {
        "n_models": len(models),
        "avg_train_accuracy": round(avg_train_acc, 4),
        "avg_test_accuracy": round(avg_test_acc, 4),
        "model_name": BERT_MODEL
    }
    
    EVAL_OUT.write_text(json.dumps(eval_results, indent=2), encoding="utf-8")
    
    print(f"\n[OK] Saved model to: {MODEL_OUT}")
    print(f"[OK] Saved evaluation to: {EVAL_OUT}")


if __name__ == "__main__":
    random.seed(42)
    main()
