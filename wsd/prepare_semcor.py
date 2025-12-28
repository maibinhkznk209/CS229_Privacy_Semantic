#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fixed SemCor preparation - correctly parse NLTK Tree structure.
"""

from __future__ import annotations

import json
from pathlib import Path
from nltk.corpus import semcor
from nltk.tree import Tree

OUT = Path(__file__).parent / "data" / "semcor_instances.jsonl"


def extract_words_and_labels(tree):
    """
    Recursively extract words and synset labels from SemCor tree.
    Returns: (words_list, labeled_instances)
    """
    words = []
    instances = []
    
    def traverse(node, word_list):
        if isinstance(node, Tree):
            label = node.label()
            
            # Check if this is a labeled node (has synset)
            if hasattr(label, 'synset') and label.synset() is not None:
                # This is a labeled word
                synset = label.synset()
                lemma = label.name().split('.')[0]  # Extract lemma from label
                pos = synset.pos()
                
                # Get the word(s) under this node
                node_words = node.leaves()
                word = ' '.join(node_words) if isinstance(node_words, list) else str(node_words)
                
                instances.append({
                    'lemma': lemma.lower(),
                    'pos': pos,
                    'word': word.lower(),
                    'label': synset.name()
                })
                
                # Add words to context
                for w in node.leaves():
                    if isinstance(w, str):
                        word_list.append(w.lower())
            else:
                # Recurse into children
                for child in node:
                    traverse(child, word_list)
        elif isinstance(node, list):
            # List of words
            for item in node:
                if isinstance(item, str):
                    word_list.append(item.lower())
                else:
                    traverse(item, word_list)
        elif isinstance(node, str):
            word_list.append(node.lower())
    
    traverse(tree, words)
    return words, instances


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    
    print("[INFO] Loading SemCor corpus...")
    sents = list(semcor.tagged_sents(tag='sem'))
    print(f"[INFO] Found {len(sents)} sentences")
    
    n_written = 0
    with OUT.open("w", encoding="utf-8") as f:
        for i, sent in enumerate(sents):
            if i % 5000 == 0:
                print(f"[INFO] Processing sentence {i}/{len(sents)}...")
            
            # Extract words and labeled instances
            words, instances = extract_words_and_labels(sent)
            
            # Write each instance with full sentence context
            for inst in instances:
                inst['context'] = words
                f.write(json.dumps(inst, ensure_ascii=False) + "\n")
                n_written += 1
    
    print(f"[OK] Wrote {n_written} instances to {OUT}")


if __name__ == "__main__":
    main()
