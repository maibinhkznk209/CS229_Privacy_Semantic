#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Prepare WSD training instances from NLTK SemCor.

Output JSONL:
  {"lemma": "...", "pos": "n|v|a|r", "context": ["..."], "label": "bank.n.01"}

Requires:
  nltk corpora: semcor, wordnet, omw-1.4, punkt

Download example:
  python -c "import nltk; nltk.download('semcor'); nltk.download('wordnet'); nltk.download('omw-1.4'); nltk.download('punkt')"
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

import nltk
from nltk.corpus import semcor

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "wsd" / "semcor_instances.jsonl"


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)

    # semcor.tagged_sents(tag="sem") yields trees with synset labels
    # We'll also take leaves as context words.
    n_written = 0
    with OUT.open("w", encoding="utf-8") as f:
        for sent in semcor.tagged_sents(tag="sem"):
            # SemCor sentence types vary across NLTK versions; normalize to word list.
            if hasattr(sent, "leaves"):
                tokens: Iterable = sent.leaves()
            elif hasattr(sent, "words"):
                tokens = sent.words()
            elif hasattr(sent, "tokens"):
                tokens = sent.tokens
            else:
                tokens = sent

            words = [w.lower() for w in tokens if isinstance(w, str)]
            for node in sent:
                if not hasattr(node, "label"):
                    continue
                label = node.label()
                if isinstance(label, nltk.corpus.reader.wordnet.Synset):
                    syn = label
                    lemma = syn.lemmas()[0].name().lower()
                    pos = syn.pos()
                    instance = {"lemma": lemma, "pos": pos, "context": words, "label": syn.name()}
                    f.write(json.dumps(instance, ensure_ascii=False) + "\n")
                    n_written += 1

    print(f"[OK] Wrote {n_written} instances to {OUT}")


if __name__ == "__main__":
    main()
