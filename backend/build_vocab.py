#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Build First-Order Logic (FOL) vocabulary + schema from a paragraph (privacy policy).
Inputs:
  - paragraph.txt (required)
  - questions.txt (optional)
Outputs:
  - out/vocabulary.json
  - out/vocabulary.md
  - out/vocab.pl
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Set, Tuple


# --------- 1) Domain phrases you want to treat as single terms ----------
# Add/remove phrases to match your paragraph.
PHRASES = [
    "privacy policy",
    "google account",
    "privacy controls",
    "unique identifiers",
    "unique identifier",
    "server logs",
    "ip address",
    "personal information",
    "business needs",
    "legal needs",
    "auto-delete",
    "auto delete",
]

# --------- 2) Keyword-based categorization ----------
# Each category has a set of keywords (single or multi-word) that, if matched, assigns term to that category.
CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "actors": [
        "google", "user", "users", "we", "our", "you",
    ],
    "contexts": [
        "service", "services", "account", "browser", "browsers", "app", "apps", "device", "devices",
        "settings", "controls", "privacy controls", "google account",
    ],
    "data_types": [
        "information", "personal information", "content", "data", "ip address",
        "identifiers", "unique identifiers", "unique identifier", "activity", "usage",
    ],
    "technologies": [
        "cookies", "cookie", "server logs", "logs",
    ],
    "purposes": [
        "provide", "deliver", "maintain", "keep", "improve", "personalize", "communicate",
        "protect", "fraud", "abuse", "security", "risk", "preferences",
    ],
    "retention": [
        "retain", "retention", "keep longer", "kept longer", "delete", "auto-delete", "auto delete",
    ],
    "reasons": [
        "business needs", "legal needs", "business", "legal",
    ],
}

# --------- 3) Predicate schema templates ----------
DEFAULT_PREDICATES: List[Tuple[str, int, str]] = [
    ("collects", 2, "collects(Actor, DataType)"),
    ("collects_content", 2, "collects_content(Actor, ContentType)"),
    ("collects_tech_data", 2, "collects_tech_data(Actor, TechDataType)"),
    ("uses_technology", 2, "uses_technology(Actor, Technology)"),
    ("uses_for", 2, "uses_for(Actor, Purpose)"),
    ("purpose", 3, "purpose(Actor, DataType, Purpose)"),
    ("varies_by", 2, "varies_by(Process, Factor)  % e.g., varies_by(data_collection, privacy_controls)"),
    ("stores_under_identifier", 4, "stores_under_identifier(Actor, IdentifierType, Context, Purpose)"),
    ("retains", 3, "retains(Actor, DataType, RetentionPolicy)"),
    ("allows_setting", 2, "allows_setting(Actor, SettingAction)  % e.g., delete/auto_delete"),
    ("may_keep_longer_for", 3, "may_keep_longer_for(Actor, DataType, Reason)"),
]

# Optional: only keep predicates that are relevant to terms present in the text.
PREDICATE_TRIGGER_KEYWORDS: Dict[str, List[str]] = {
    "collects": ["collect", "collects", "information", "data", "personal information", "content"],
    "collects_content": ["content"],
    "collects_tech_data": ["device", "ip address", "cookies", "server logs", "logs"],
    "uses_technology": ["cookies", "server logs", "logs"],
    "uses_for": ["use", "uses", "purpose", "provide", "improve", "protect", "personalize", "communicate"],
    "purpose": ["purpose", "use", "uses"],
    "varies_by": ["vary", "varies", "privacy controls"],
    "stores_under_identifier": ["unique identifier", "unique identifiers", "identifier"],
    "retains": ["retain", "retention", "kept longer", "keep longer"],
    "allows_setting": ["delete", "auto-delete", "auto delete"],
    "may_keep_longer_for": ["business", "legal", "business needs", "legal needs"],
}


@dataclass(frozen=True)
class PredicateSig:
    name: str
    arity: int
    template: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore").strip()


def normalize(s: str) -> str:
    s = s.lower()
    s = s.replace("–", "-").replace("—", "-")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def extract_terms(text: str) -> Set[str]:
    """
    Lightweight extraction:
      - capture configured PHRASES (multiword)
      - capture single tokens (alphabetic) excluding short tokens
    """
    t = normalize(text)

    terms: Set[str] = set()

    # 1) extract multi-word phrases first (exact substring match)
    for ph in PHRASES:
        ph_norm = normalize(ph)
        if ph_norm in t:
            terms.add(ph_norm)

    # 2) basic tokenization for single terms
    tokens = re.findall(r"[a-z]+(?:'[a-z]+)?", t)
    for tok in tokens:
        if len(tok) <= 2:
            continue
        terms.add(tok)

    return terms


def categorize_terms(terms: Set[str]) -> Dict[str, Set[str]]:
    categorized: Dict[str, Set[str]] = {k: set() for k in CATEGORY_KEYWORDS.keys()}
    categorized["other"] = set()

    for term in terms:
        placed = False
        for cat, keys in CATEGORY_KEYWORDS.items():
            for key in keys:
                key_norm = normalize(key)
                # match if term equals key, or term contains key for multi-words
                if term == key_norm or (len(key_norm.split()) > 1 and key_norm in term):
                    categorized[cat].add(term)
                    placed = True
                    break
            if placed:
                break

        if not placed:
            categorized["other"].add(term)

    return categorized


def pick_predicates(text: str, terms: Set[str]) -> List[PredicateSig]:
    t = normalize(text)
    joined = t + " " + " ".join(sorted(terms))

    selected: List[PredicateSig] = []
    for name, arity, template in DEFAULT_PREDICATES:
        triggers = PREDICATE_TRIGGER_KEYWORDS.get(name, [])
        keep = any(normalize(tr) in joined for tr in triggers)
        if keep:
            selected.append(PredicateSig(name=name, arity=arity, template=template))

    # Always keep a minimal core if nothing matched (failsafe)
    if not selected:
        selected = [
            PredicateSig("collects", 2, "collects(Actor, DataType)"),
            PredicateSig("uses_for", 2, "uses_for(Actor, Purpose)"),
        ]

    return selected


def to_sorted_list(s: Set[str]) -> List[str]:
    return sorted(s, key=lambda x: (len(x.split()), x))


def write_json(out_path: Path, obj: dict) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def write_md(out_path: Path, vocab: dict) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)

    lines: List[str] = []
    lines.append("FOL Vocabulary & Predicate Schema\n")

    lines.append("## Constants / Terms by Category\n")
    for cat, items in vocab["constants_by_type"].items():
        lines.append(f"### {cat}\n")
        if not items:
            lines.append("_None_\n")
            continue
        for it in items:
            lines.append(f"- `{it}`")
        lines.append("")

    lines.append("\n## Predicate Signatures\n")
    for p in vocab["predicates"]:
        lines.append(f"- `{p['name']}/{p['arity']}`: {p['template']}")
    lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")


def write_prolog(out_path: Path, vocab: dict) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)

    lines: List[str] = []
    lines.append("% Auto-generated vocabulary")
    lines.append("% Entities (constants) by type")
    for cat, items in vocab["constants_by_type"].items():
        prolog_cat = cat.lower()
        for it in items:
            const = re.sub(r"[^a-z0-9_]", "_", it.lower())
            lines.append(f"entity_type({const}, {prolog_cat}).")

    lines.append("\n% Predicate signatures")
    for p in vocab["predicates"]:
        lines.append(f"predicate_signature({p['name']}, {p['arity']}).")

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--paragraph", required=True, type=str, help="Path to paragraph.txt")
    ap.add_argument("--questions", required=False, type=str, help="Optional path to questions.txt")
    ap.add_argument("--outdir", default="out", type=str, help="Output directory")
    args = ap.parse_args()

    paragraph_path = Path(args.paragraph)
    if not paragraph_path.exists():
        raise FileNotFoundError(f"paragraph not found: {paragraph_path}")

    paragraph = read_text(paragraph_path)

    questions_text = ""
    if args.questions:
        qpath = Path(args.questions)
        if qpath.exists():
            questions_text = read_text(qpath)

    combined_text = paragraph + ("\n" + questions_text if questions_text else "")

    terms = extract_terms(combined_text)
    categorized = categorize_terms(terms)
    preds = pick_predicates(combined_text, terms)

    vocab = {
        "source_files": {
            "paragraph": str(paragraph_path),
            "questions": str(args.questions) if args.questions else None,
        },
        "constants_by_type": {cat: to_sorted_list(items) for cat, items in categorized.items()},
        "predicates": [{"name": p.name, "arity": p.arity, "template": p.template} for p in preds],
    }

    outdir = Path(args.outdir)
    write_json(outdir / "vocabulary.json", vocab)
    write_md(outdir / "vocabulary.md", vocab)
    write_prolog(outdir / "vocab.pl", vocab)

    print(f"[OK] Wrote: {outdir / 'vocabulary.json'}")
    print(f"[OK] Wrote: {outdir / 'vocabulary.md'}")
    print(f"[OK] Wrote: {outdir / 'vocab.pl'}")


if __name__ == "__main__":
    main()
