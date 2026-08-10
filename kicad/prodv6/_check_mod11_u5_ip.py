#!/usr/bin/env python3
"""Grafo IP B.Cu — verifica U5 pad2 vs pad6 conectados."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from _review_routes import NetGraph, _pt_key  # noqa: E402

PCB = ROOT / "injet-racing-prodv6.kicad_pcb"

PAD2 = _pt_key(225.3, 42.365)
PAD6 = _pt_key(230.7, 43.635)


def main() -> int:
    text = PCB.read_text(encoding="utf-8")
    g = NetGraph()
    for m in re.finditer(
        r"\(segment\s+\(start\s+([\d.-]+)\s+([\d.-]+)\)\s+\(end\s+([\d.-]+)\s+([\d.-]+)\)"
        r"[\s\S]*?\(layer\s+\"B\.Cu\"\)[\s\S]*?\(net\s+\"IP\"\)",
        text,
    ):
        x1, y1, x2, y2 = map(float, m.groups())
        g.add_segment("IP", _pt_key(x1, y1), _pt_key(x2, y2))

    ok = g.connected("IP", PAD2, PAD6)
    print(f"U5 pad2 {PAD2} <-> pad6 {PAD6}: {'OK' if ok else 'FALHA'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
