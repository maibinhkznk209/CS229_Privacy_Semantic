#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent

def run(cmd: list[str]) -> None:
    print("\n$ " + " ".join(cmd))
    subprocess.check_call(cmd, cwd=str(ROOT))

def main() -> None:
    run([
        sys.executable,
        "build_vocab.py",
        "--paragraph",
        str(PROJECT_ROOT / "data" / "paragraph.txt"),
        "--outdir",
        str(PROJECT_ROOT / "out"),
    ])
    run([sys.executable, "build_kb.py"])
    run([sys.executable, "generate_queries.py"])
    print("\n[OK] Done. See out/, kb/, results/.")
    print("If you have SWI-Prolog: swipl -q -f results/queries.pl")

if __name__ == "__main__":
    main()
