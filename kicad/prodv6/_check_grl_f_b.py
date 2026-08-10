#!/usr/bin/env python3
"""Checagem GRL1/2/3 — F.Cu MCU ↔ fileira relé B.Cu @ y~115.5."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from _check_mod6_now import parse_graph  # noqa: E402
from _review_routes import _pt_key  # noqa: E402

PCB = ROOT / "injet-racing-prodv6.kicad_pcb"

CHECKS = [
    ("GRL1", "F stub -> fileira B", (67.0875, 115.5), (71.5875, 115.5)),
    ("GRL1", "MCU via (74,100) -> fileira", (74, 100), (71.5875, 115.5)),
    ("GRL2", "F fileira -> B fileira", (80.0325, 115.5325), (99.5875, 115.5325)),
    ("GRL2", "MCU via (76.5,100) -> fileira", (76.5, 100), (98.0875, 115.5325)),
    # GRL3 — pad injetor: via F->B @112.5, MCU->R52.A, gate R52.B->R57.A (sem fileira A-B)
    ("GRL3", "via F-B -> R52.A", (119.5, 112.5), (119.5875, 115.5325)),
    ("GRL3", "MCU via (78.5,100) -> R52.A", (78.5, 100), (119.5875, 115.5325)),
    ("GRL3", "R52.B -> R57.A gate", (125.5875, 115.5325), (119.5875, 120.0325)),
]


def main() -> int:
    g = parse_graph(PCB.read_text(encoding="utf-8"))
    ok = True
    print("=== GRL F.Cu <-> B.Cu fileira relé ===")
    for net, label, a, b in CHECKS:
        c = g.connected(net, _pt_key(*a), _pt_key(*b))
        print(f"  {net} {label}: {'OK' if c else 'FALHA'}")
        ok = ok and c
    print("=== Resultado ===")
    if ok:
        print("  GRL1/2/3 fileira OK")
        return 0
    print("  GRL com ilhas")
    return 1


if __name__ == "__main__":
    sys.exit(main())
