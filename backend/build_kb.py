#!/usr/bin/env python3
# -*- coding: utf-8 -*-



from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent
PAR_PATH = PROJECT_ROOT / "data" / "paragraph.txt"
VOCAB_JSON = PROJECT_ROOT / "out" / "vocabulary.json"
KB_OUT = PROJECT_ROOT / "kb" / "kb.pl"
FOL_MD_OUT = PROJECT_ROOT / "kb" / "kb_fol.md"


def norm(s: str) -> str:
    s = s.lower()
    s = s.replace("–", "-").replace("—", "-")
    s = s.replace("…", "...")  
    s = re.sub(r"\s+", " ", s).strip()
    return s


def load_vocab_constants() -> Dict[str, List[str]]:
    if not VOCAB_JSON.exists():
        return {}
    obj = json.loads(VOCAB_JSON.read_text(encoding="utf-8"))
    return obj.get("constants_by_type", {})


def extract_facts(text: str) -> Tuple[List[str], List[str]]:
  
    t = norm(text)

    facts: List[str] = []
    fol_lines: List[str] = []

    # Always declare main actors
    facts += ["company(google).", "actor(google).", "actor(user)."]
    fol_lines += ["- company(google) ∧ actor(google) ∧ actor(user)."]

    # Collects information
    if "collect" in t:
        facts.append("collects(google, information).")
        fol_lines.append("- collects(google, information).")

    # Personal information / Google Account (best-effort)
    if "google account" in t:
        facts.append("context(google_account).")
        fol_lines.append("- context(google_account).")
        if "provide" in t or "provided" in t:
            facts.append("collects(google, personal_information).")
            facts.append("purpose(google, personal_information, create_or_use_account).")
            fol_lines.append("- collects(google, personal_information) ∧ purpose(google, personal_information, create_or_use_account).")

    # Content collection
    if "content" in t:
        facts.append("collects_content(google, user_content).")
        fol_lines.append("- collects_content(google, user_content).")

    # Technologies: cookies and server logs
    if "cookie" in t:
        facts.append("uses_technology(google, cookies).")
        fol_lines.append("- uses_technology(google, cookies).")
    if "server log" in t or "server logs" in t:
        facts.append("uses_technology(google, server_logs).")
        fol_lines.append("- uses_technology(google, server_logs).")

    # Technical data examples: apps/browsers/devices/IP
    tech_markers = ["device", "devices", "browser", "browsers", "app", "apps", "ip address", "ip"]
    if any(m in t for m in tech_markers):
        facts.append("collects_tech_data(google, technical_data).")
        fol_lines.append("- collects_tech_data(google, technical_data).")
    if "ip address" in t:
        facts.append("collects_tech_data(google, ip_address).")
        fol_lines.append("- collects_tech_data(google, ip_address).")

    # Varies by usage and privacy controls
    if "vary" in t or "varies" in t:
        facts.append("varies_by(data_collection, service_usage).")
        facts.append("varies_by(data_collection, privacy_controls).")
        fol_lines.append("- varies_by(data_collection, service_usage) ∧ varies_by(data_collection, privacy_controls).")

    # Not signed in -> unique identifiers to store preferences
    if "not signed" in t or "not signed in" in t:
        if "unique identifier" in t or "unique identifiers" in t or "identifier" in t:
            facts.append("stores_under_identifier(google, unique_identifier, not_signed_in, remember_preferences).")
            fol_lines.append("- stores_under_identifier(google, unique_identifier, not_signed_in, remember_preferences).")

    # Purposes
    purpose_map = {
        "provide": "provide_services",
        "deliver": "provide_services",
        "maintain": "maintain_services",
        "keep": "maintain_services",
        "improve": "improve_services",
        "personalize": "personalize_content_ads",
        "communicate": "communicate_with_users",
        "protect": "protect_from_fraud_abuse_security_risks",
        "fraud": "protect_from_fraud_abuse_security_risks",
        "abuse": "protect_from_fraud_abuse_security_risks",
        "security": "protect_from_fraud_abuse_security_risks",
        "risk": "protect_from_fraud_abuse_security_risks",
    }
    purposes = set()
    for k, v in purpose_map.items():
        if k in t:
            purposes.add(v)

    for p in sorted(purposes):
        facts.append(f"uses_for(google, {p}).")
        fol_lines.append(f"- uses_for(google, {p}).")

    # Retention + delete/auto-delete + business/legal needs
    if "retain" in t or "retention" in t or "kept" in t:
        facts.append("retains(google, data, retention_policy).")
        fol_lines.append("- retains(google, data, retention_policy).")

    if "auto-delete" in t or "auto delete" in t:
        facts.append("allows_setting(google, auto_delete).")
        fol_lines.append("- allows_setting(google, auto_delete).")
    if "delete" in t:
        facts.append("allows_setting(google, delete).")
        fol_lines.append("- allows_setting(google, delete).")

    if "business needs" in t:
        facts.append("may_keep_longer_for(google, data, business_needs).")
        fol_lines.append("- may_keep_longer_for(google, data, business_needs).")
    if "legal needs" in t:
        facts.append("may_keep_longer_for(google, data, legal_needs).")
        fol_lines.append("- may_keep_longer_for(google, data, legal_needs).")

    # Deduplicate while preserving order
    seen = set()
    facts = [f for f in facts if not (f in seen or seen.add(f))]
    return facts, fol_lines


def write_kb(facts: List[str]) -> None:
    KB_OUT.parent.mkdir(parents=True, exist_ok=True)
    rules = [
        "",
        "% --- derived relations (optional) ---",
        "technology(T) :- uses_technology(google, T).",
    ]
    KB_OUT.write_text("\n".join(["% kb.pl (auto-generated)"] + facts + rules) + "\n", encoding="utf-8")


def write_fol_md(lines: List[str]) -> None:
    FOL_MD_OUT.parent.mkdir(parents=True, exist_ok=True)
    md = ["Manual Translation Summary (FOL-ish)\n", "## Statements derived from the paragraph\n"]
    md += lines
   
    FOL_MD_OUT.write_text("\n".join(md), encoding="utf-8")


def main() -> None:
    if not PAR_PATH.exists():
        raise FileNotFoundError(f"Missing {PAR_PATH}")
    text = PAR_PATH.read_text(encoding="utf-8", errors="ignore").strip()
    facts, fol_lines = extract_facts(text)
    write_kb(facts)
    write_fol_md(fol_lines)
    print(f"[OK] Wrote KB: {KB_OUT}")
    print(f"[OK] Wrote FOL summary: {FOL_MD_OUT}")


if __name__ == "__main__":
    main()
