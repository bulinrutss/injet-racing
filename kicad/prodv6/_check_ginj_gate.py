#!/usr/bin/env python3
"""Checagem GINJ — MCU -> R_gate.A, R_gate.B -> Q.G (sem depender de ilha flutuante)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from _check_mod8_now import (  # noqa: E402
    CHANNELS,
    U1_GINJ,
    fp_block,
    pad_abs,
    same_net,
    parse_graph,
)

PCB = ROOT / "injet-racing-prodv6.kicad_pcb"

# Pontos DRC / ilhas reportadas
GINJ2_ISLAND = ((170.5, 86.5), (177.0, 91.0))


def main() -> int:
    text = PCB.read_text(encoding="utf-8")
    g = parse_graph(text)
    ok = True

    print("=== GINJ gate resistors (MCU + Q.G) ===")
    for _, ginj, q, rg, rpd, _, _ in CHANNELS:
        qb = fp_block(text, q)
        rgb = fp_block(text, rg)
        rpdb = fp_block(text, rpd)
        if not all([qb, rgb, rpdb]):
            print(f"  {ginj}: FALTA footprint")
            ok = False
            continue
        qg = pad_abs(qb, "G")
        rga = pad_abs(rgb, "A")
        rgb_b = pad_abs(rgb, "B")
        rpda = pad_abs(rpdb, "A")
        _, u1_pt = U1_GINJ[ginj]
        mcu_a = rga and same_net(g, ginj, u1_pt, (rga[0], rga[1]))
        gate_b = (
            rgb_b
            and qg
            and rpda
            and same_net(g, ginj, (rgb_b[0], rgb_b[1]), (qg[0], qg[1]))
            and same_net(g, ginj, (rpda[0], rpda[1]), (qg[0], qg[1]))
        )
        # A e B no mesmo net via corpo R (parse_graph liga pads do footprint)
        body = (
            rga
            and rgb_b
            and same_net(g, ginj, (rga[0], rga[1]), (rgb_b[0], rgb_b[1]))
        )
        print(
            f"  {ginj} MCU->{rg}.A: {'OK' if mcu_a else 'FALTA'} | "
            f"{rg}.B->Q.G: {'OK' if gate_b else 'FALTA'} | "
            f"{rg} A-B: {'OK' if body else 'FALTA'}"
        )
        if not (mcu_a and gate_b and body):
            ok = False

    print("\n=== GINJ2 ilha B.Cu (170.5,86.5) <-> (177,91) ===")
    a, b = GINJ2_ISLAND
    ilha = same_net(g, "GINJ2", a, b)
    print(f"  {'OK' if ilha else 'FALTA'}")
    ok = ok and ilha

    print("\n=== Resultado ===")
    if ok:
        print("  GINJ gate OK")
        return 0
    print("  GINJ com ilhas")
    return 1


if __name__ == "__main__":
    sys.exit(main())
