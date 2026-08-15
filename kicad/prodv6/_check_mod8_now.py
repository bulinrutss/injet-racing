#!/usr/bin/env python3
"""Checagem MOD8 — injetores IRLZ44N x4 (PCB 2026-08-11)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from _check_mod6_now import cn1_pad, fp_pad, parse_graph, rot_pt  # noqa: E402
from _review_routes import _pt_key  # noqa: E402
import jl32_pinout as jl  # noqa: E402

PCB = ROOT / "injet-racing-prodv6.kicad_pcb"

CHANNELS = [
    ("INJ1", "GINJ1", "Q10", "R30", "R40", "D10", 13, "R18I"),
    ("INJ2", "GINJ2", "Q11", "R31", "R41", "D11", 14, "R19I"),
    ("INJ3", "GINJ3", "Q12", "R32", "R42", "D12", 15, "R20I"),
    ("INJ4", "GINJ4", "Q13", "R33", "R43", "D13", 16, "R21I"),
]


def fp_positions(text: str) -> dict[str, tuple[float, float, float]]:
    out: dict[str, tuple[float, float, float]] = {}
    for fp in re.finditer(r"\(footprint[\s\S]*?\n\t\)", text):
        block = fp.group(0)
        ref_m = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', block)
        at_m = re.search(r"\(at\s+([\d.-]+)\s+([\d.-]+)(?:\s+([\d.-]+))?", block)
        if ref_m and at_m:
            rot = float(at_m.group(3)) if at_m.group(3) else 0.0
            out[ref_m.group(1)] = (float(at_m.group(1)), float(at_m.group(2)), rot)
    return out


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
    pm = re.search(
        rf'\(pad\s+"{re.escape(pad)}"[\s\S]*?\(at\s+([\d.-]+)\s+([\d.-]+)[\s\S]*?\(net\s+"([^"]+)"\)',
        block,
    )
    if not pm:
        return None
    px, py, net = float(pm.group(1)), float(pm.group(2)), pm.group(3)
    return (*rot_pt(ox, oy, rot, px, py), net)


def same_net(g, net: str, a: tuple[float, float], b: tuple[float, float]) -> bool:
    return g.connected(net, _pt_key(*a), _pt_key(*b))


def main() -> int:
    text = PCB.read_text(encoding="utf-8")
    g = parse_graph(text)
    fps = fp_positions(text)
    ok = True

    print(f"PCB: {PCB.name}\n=== MOD8 posicoes ===")
    for ref in ["Q10", "Q11", "Q12", "Q13", "R30", "R31", "R32", "R33",
                "R40", "R41", "R42", "R43", "D10", "D11", "D12", "D13"]:
        print(f"  {ref}: {fps.get(ref, 'AUSENTE')}")
        if ref not in fps:
            ok = False

    print("\n=== U1 pads GINJ ===")
    u1 = fp_block(text, "U1")
    for ginj, pad in jl.U1_INJ_PAD.items():
        pm = re.search(rf'\(pad\s+"{pad}"[\s\S]*?\(net\s+"([^"]+)"\)', u1 or "")
        net = pm.group(1) if pm else "?"
        pt = jl.u1_pad_xy(pad)
        mark = "OK" if net == ginj else f"ERR ({net})"
        print(f"  {pad} {ginj} @ {pt}: {mark}")
        if net != ginj:
            ok = False

    print("\n=== Por canal ===")
    for inj, ginj, q, rg, rpd, d, cn_pin, u1_pad in CHANNELS:
        print(f"\n  --- {inj} / {ginj} / {u1_pad} ---")
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

        u1_pt = jl.u1_pad_xy(u1_pad)
        mcu = rga and same_net(g, ginj, u1_pt, (rga[0], rga[1]))
        gate_node = (
            rgb_b and rpda and qg
            and same_net(g, ginj, (rgb_b[0], rgb_b[1]), (qg[0], qg[1]))
            and same_net(g, ginj, (rpda[0], rpda[1]), (qg[0], qg[1]))
        )
        gnd = qs and qs[2] == "GND" and rpdb_b and rpdb_b[2] == "GND"
        drain = qd and da and same_net(g, inj, (qd[0], qd[1]), (da[0], da[1]))
        fly = dk and dk[2] == "+12V_PROT"
        cn_pt = cn1_pad(cn_pin)
        cn_ok = qd and same_net(g, inj, cn_pt, (qd[0], qd[1]))

        print(f"    {u1_pad} -> {rg}.A: {'OK' if mcu else 'FALHA'}")
        print(f"    gate {rg}.B = {rpd}.A = {q}.G: {'OK' if gate_node else 'FALHA'}")
        print(f"    {q}.S + {rpd}.B -> GND: {'OK' if gnd else 'FALHA'}")
        print(f"    dreno {q}.D = {d}.A ({inj}): {'OK' if drain else 'FALHA'}")
        print(f"    {d}.K -> +12V_PROT: {'OK' if fly else 'FALHA'}")
        print(f"    CN1-{cn_pin} -> dreno: {'OK' if cn_ok else 'FALHA'}")

        if not all([mcu, gate_node, gnd, drain, fly, cn_ok]):
            ok = False

    print("\n=== Resultado ===")
    if ok:
        print("  MOD8 completo.")
        return 0
    print("  MOD8 com pendencias.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
