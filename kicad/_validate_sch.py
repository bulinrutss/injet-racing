#!/usr/bin/env python3
"""Valida .kicad_sch e mostra contexto de offset."""
import sys
from pathlib import Path
from sexpdata import loads

ROOT = Path(__file__).parent
files = [ROOT / "injet-racing-ecu.kicad_sch"] + sorted((ROOT / "sheets").glob("*.kicad_sch"))

for p in files:
    text = p.read_text(encoding="utf-8")
    depth = 0
    for i, ch in enumerate(text):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if depth < 0:
            print(f"{p.name}: extra ) at {i}")
            break
    else:
        ok = depth == 0
        print(f"{p.name}: depth={depth} len={len(text)} {'OK' if ok else 'UNBALANCED'}")
    try:
        loads(text)
        print(f"  parse: OK")
    except Exception as e:
        print(f"  parse: FAIL {e}")

text = (ROOT / "injet-racing-ecu.kicad_sch").read_text(encoding="utf-8")
o = 25031
print("\n--- context offset 25031 ---")
print(repr(text[max(0, o - 120) : o + 120]))
