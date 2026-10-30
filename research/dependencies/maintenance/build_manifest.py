#!/usr/bin/env python3
"""Regenerate SHA256SUMS for the step-4 publication set."""

import hashlib
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "SHA256SUMS"


def main():
    files = [p for p in HERE.rglob("*") if p.is_file() and p != MANIFEST
             and "__pycache__" not in p.parts and not p.name.endswith(".tmp")]
    files.append(HERE.parent / "attributions" / "source-repos.csv")
    lines = []
    for path in sorted(files, key=lambda p: os.path.relpath(p, HERE)):
        relative = os.path.relpath(path, HERE)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {relative}\n")
    temp = MANIFEST.with_suffix(".tmp")
    temp.write_text("".join(lines), encoding="utf-8")
    temp.replace(MANIFEST)
    print(f"wrote {len(lines)} entries to {MANIFEST.name}")


if __name__ == "__main__":
    main()
