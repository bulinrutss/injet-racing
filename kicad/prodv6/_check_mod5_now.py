#!/usr/bin/env python3
"""Conectividade MOD5 nos pads/refs — usa mesma lógica T-junction de _review_routes.py."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PCB = ROOT / "injet-racing-prodv6.kicad_pcb"

spec = importlib.util.spec_from_file_location("review", ROOT / "_review_routes.py")
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)

CHECKS = {
    "+5V": [(65, 40), (136, 108), (136, 105.46), (78, 44.5)],
    "+3V3": [
        (86, 108),
        (88.54, 105.46),
        (136, 102.92),
        (150.5, 88),
        (150.5, 110.5),
    ],
    "VREF+": [(136, 82.6), (147, 88), (147, 94.5)],
}


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else PCB
    g = review.parse_pcb(path)
    err = 0
    print(f"MOD5 pads/refs: {path.name}\n")
    for net, pts in CHECKS.items():
        root = review._pt_key(*pts[0])
        bad = [p for p in pts[1:] if not g.connected(net, root, review._pt_key(*p))]
        print(f"  {net}: {'OK' if not bad else 'FALHA ' + str(bad)}")
        if bad:
            err += 1
    return err


if __name__ == "__main__":
    raise SystemExit(main())
