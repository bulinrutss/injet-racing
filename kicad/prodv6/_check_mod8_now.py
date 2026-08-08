#!/usr/bin/env python3
"""Checagem MOD8 — injetores (pads reais PCB; CN1 opcional)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from _check_mod6_now import fp_positions, parse_graph, rot_pt  # noqa: E402
from _review_routes import _pt_key  # noqa: E402

PCB = ROOT / "injet-racing-prodv6.kicad_pcb"
CN1_AT = (12.0, 14.0)

U1_GINJ = {
    "GINJ1": ("R18I", (138.54, 62.28)),
    "GINJ2": ("R19I", (138.54, 59.74)),
    "GINJ3": ("R20I", (138.54, 57.20)),
    "GINJ4": ("R21I", (138.54, 54.66)),
}

CN1_INJ = {
    "INJ1": (CN1_AT[0] + 0, CN1_AT[1]),
    "INJ2": (CN1_AT[0] + 4, CN1_AT[1]),
    "INJ3": (CN1_AT[0] + 8, CN1_AT[1]),
    "INJ4": (CN1_AT[0] + 12, CN1_AT[1]),
}

CHANNELS = [
    ("INJ1", "GINJ1", "Q10", "R30", "R40", "D10", 13),
    ("INJ2", "GINJ2", "Q11", "R31", "R41", "D11", 14),
    ("INJ3", "GINJ3", "Q12", "R32", "R42", "D12", 15),
    ("INJ4", "GINJ4", "Q13", "R33", "R43", "D13", 16),
]


def fp_block(text: str, ref: str) -> str | None:
    for fp in re.finditer(r"\(footprint[\s\S]*?\n\t\)", text):
        if re.search(rf'\(property\s+"Reference"\s+"{ref}"', fp.group(0)):
            return fp.group(0)
    return None


def pad_abs(block: str, pad: str) -> tuple[float, float, str] | None:
    at_m = re.search(r"\(at\s+([\d.-]+)\s+([\d.-]+)(?:\s+([\d.-]+))?", block)
    if not at_m:
        return None
    ox, oy = float(at_m.group(1)), float(at_m.group(2))
    rot = float(at_m.group(3)) if at_m.group(3) else 0.0
    for pm in re.finditer(
        rf'\(pad\s+"{re.escape(pad)}"[\s\S]*?\(at\s+([\d.-]+)\s+([\d.-]+)[\s\S]*?\(net\s+"([^"]+)"\)',
        block,
    ):
        px, py = float(pm.group(1)), float(pm.group(2))
        return (*rot_pt(ox, oy, rot, px, py), pm.group(3))
    return None


def same_net(g, net: str, a: tuple[float, float], b: tuple[float, float]) -> bool:
    return g.connected(net, _pt_key(*a), _pt_key(*b))


def main() -> int:
    text = PCB.read_text(encoding="utf-8")
    g = parse_graph(text)
    ok = True

    print("=== MOD8 posicoes PCB (origem footprint) ===")
    refs = ["Q10", "Q11", "Q12", "Q13", "R30", "R31", "R32", "R33",
            "R40", "R41", "R42", "R43", "D10", "D11", "D12", "D13"]
    fps = fp_positions(text)
    for ref in refs:
        if ref in fps:
            print(f"  {ref}: {fps[ref]}")
        else:
            print(f"  FALTA {ref}")
            ok = False

    print("\n=== U1 pads GINJ (nets) ===")
    for ginj, (pad, pt) in U1_GINJ.items():
        # read net from U1 block
        u1 = fp_block(text, "U1")
        if u1:
            pm = re.search(
                rf'\(pad\s+"{pad}"[\s\S]*?\(net\s+"([^"]+)"\)',
                u1,
            )
            net = pm.group(1) if pm else "?"
            mark = "OK" if net == ginj else f"ERR (tem {net})"
            print(f"  {pad} {ginj} @ {pt}: {mark}")
            if net != ginj:
                ok = False

    print("\n=== Por canal (sem CN1) ===")
    for inj, ginj, q, rg, rpd, d, cn_pin in CHANNELS:
        print(f"\n  --- {inj} / {ginj} ---")
        qb = fp_block(text, q)
        rgb = fp_block(text, rg)
        rpdb = fp_block(text, rpd)
        db = fp_block(text, d)
        if not all([qb, rgb, rpdb, db]):
            print("    FALTA footprint")
            ok = False
            continue

        qg = pad_abs(qb, "G")
        qd = pad_abs(qb, "D")
        qs = pad_abs(qb, "S")
        rga = pad_abs(rgb, "A")
        rgb_b = pad_abs(rgb, "B")
        rpda = pad_abs(rpdb, "A")
        rpdb_b = pad_abs(rpdb, "B")
        da = pad_abs(db, "A")
        dk = pad_abs(db, "K")

        _, u1_pt = U1_GINJ[ginj]
        mcu = same_net(g, ginj, u1_pt, (rga[0], rga[1])) if rga else False
        gate = (
            rga and rgb_b and qg
            and same_net(g, ginj, (rgb_b[0], rgb_b[1]), (qg[0], qg[1]))
            and same_net(g, ginj, (rpda[0], rpda[1]), (qg[0], qg[1]))
        )
        gnd = qs and rpdb_b and qs[2] == "GND" and rpdb_b[2] == "GND"
        gnd_c = gnd  # pads GND — ligação via zone (tecla B)
        drain = qd and da and same_net(g, inj, (qd[0], qd[1]), (da[0], da[1]))
        fly = dk and dk[2] == "+12V_PROT"

        cn_pt = CN1_INJ[inj]
        cn_ok = same_net(g, inj, cn_pt, (qd[0], qd[1])) if qd else False

        print(f"    MCU -> {rg} A: {'OK' if mcu else 'FALTA'}")
        print(f"    gate ({rg} B / {rpd} A / {q} G): {'OK' if gate else 'FALTA'}")
        print(f"    GND ({q} S / {rpd} B): {'OK (zone)' if gnd else 'FALTA net GND'}")
        print(f"    dreno ({q} D / {d} A) net {inj}: {'OK' if drain else 'FALTA'}")
        print(f"    flyback {d} K -> +12V_PROT: {'OK' if fly else f'net={dk[2] if dk else None}'}")
        print(f"    CN1-{cn_pin} -> dreno: {'OK' if cn_ok else 'PENDENTE (ok se nao for ligar agora)'}")

        if not mcu or not gate or not gnd or not drain or not fly:
            ok = False

    print("\n=== Resultado ===")
    if ok:
        print("  MOD8 bloco OK (MCU+gate+GND+dreno+flyback). CN1 injetor = pendente se nao ligado.")
        return 0
    print("  MOD8 com ilhas — ver itens FALTA acima.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
