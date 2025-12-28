#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Map natural-language questions to Prolog queries (pattern-based),
and generate a SWI-Prolog script to run them.

Inputs:
  - data/questions.txt (preferred) or data/questions.example.txt
  - kb/kb.pl

Outputs:
  - results/queries.pl     : Prolog file that loads KB and runs all queries
  - results/queries.json   : machine-readable query list
  - results/queries.md     : readable mapping table
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent
QUESTIONS_PATH = PROJECT_ROOT / "data" / "questions.txt"
QUESTIONS_EXAMPLE = PROJECT_ROOT / "data" / "questions.example.txt"

OUT_DIR = PROJECT_ROOT / "results"
OUT_PL = OUT_DIR / "queries.pl"
OUT_JSON = OUT_DIR / "queries.json"
OUT_MD = OUT_DIR / "queries.md"


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())


def read_questions() -> List[Tuple[str, str]]:
    path = QUESTIONS_PATH if QUESTIONS_PATH.exists() else QUESTIONS_EXAMPLE
    lines = [ln.strip() for ln in path.read_text(encoding="utf-8", errors="ignore").splitlines() if ln.strip()]
    items: List[Tuple[str, str]] = []
    for i, ln in enumerate(lines, 1):
        m = re.match(r"^(q\d+)\s+(.*)$", ln.strip(), flags=re.IGNORECASE)
        if m:
            qid, qtext = m.group(1).upper(), m.group(2).strip()
        else:
            qid, qtext = f"Q{i}", ln
        items.append((qid, qtext))
    return items


def map_question_to_query(qtext: str) -> Tuple[str, str]:
    t = norm(qtext)

    if "what information" in t and "collect" in t:
        return "collects(google, X).", "X (all collected data types)"
    if "why" in t and ("collect" in t or "use" in t):
        return "uses_for(google, Purpose).", "Purpose (all purposes)"
    if "depend" in t and "privacy control" in t:
        return "varies_by(data_collection, privacy_controls).", "true/false"
    if "not signed" in t and "identifier" in t:
        return "stores_under_identifier(google, unique_identifier, not_signed_in, Purpose).", "Purpose"
    if ("google account" in t) and ("what" in t or "information" in t):
        return "purpose(google, personal_information, create_or_use_account).", "true/false"
    if "content" in t and ("create" in t or "upload" in t or "collect" in t):
        return "collects_content(google, X).", "X (content type)"
    if ("technology" in t or "technologies" in t) and ("cookie" in t or "server log" in t or "logs" in t):
        return "uses_technology(google, Tech).", "Tech"
    if ("how long" in t or "retain" in t or "keep data" in t) and ("delete" in t or "auto" in t):
        return "retains(google, data, Policy), allows_setting(google, delete), (allows_setting(google, auto_delete) ; true).", "Policy + delete/auto-delete availability"

    return "% TODO: add mapping rule for this question.", "N/A"


def write_outputs(items: List[Dict]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")

    md = ["Question → Prolog Query Mapping\n",
          "| QID | Question | Prolog Query | Answer shape |",
          "|---|---|---|---|"]
    for it in items:
        md.append(f"| {it['qid']} | {it['question']} | `{it['prolog_query']}` | {it['answer_shape']} |")
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")

    pl_lines = [
        "% queries.pl (auto-generated)",
        ":- initialization(main).",
        "",
        "main :-",
        "  consult('../kb/kb.pl'),",
        "  format('Loaded KB.~n', []),",
        "  run_all,",
        "  halt.",
        "",
        "run_all :-",
    ]

    for it in items:
        qid = it["qid"]
        q = it["prolog_query"]
        if q.strip().startswith("% TODO"):
            pl_lines.append(f"  format('~n[{qid}] TODO mapping.~n', []),")
            continue

        pl_lines.append(f"  format('~n[{qid}] {it['question']}~n', []),")
        pl_lines.append(f"  ( findall(X, ({q}), Xs), Xs \\= [] -> format('  Answers: ~w~n', [Xs])")
        pl_lines.append(f"  ; ( call(({q})) -> format('  true.~n', []) ; format('  false / no answers.~n', []) ) ),")

    pl_lines.append("  true.")
    OUT_PL.write_text("\n".join(pl_lines) + "\n", encoding="utf-8")


def main() -> None:
    qs = read_questions()
    items = []
    for qid, qtext in qs:
        query, shape = map_question_to_query(qtext)
        items.append({"qid": qid, "question": qtext, "prolog_query": query, "answer_shape": shape})

    write_outputs(items)
    print(f"[OK] Wrote: {OUT_JSON}")
    print(f"[OK] Wrote: {OUT_MD}")
    print(f"[OK] Wrote: {OUT_PL}")
    print("Run with: swipl -q -f results/queries.pl")


if __name__ == "__main__":
    main()
