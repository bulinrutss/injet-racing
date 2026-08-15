#!/usr/bin/env python3
"""Checagem MOD12 — aquecedor lambda IRLZ44N (PCB 2026-08-11)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from _check_mod6_now import fp_pad, parse_graph, rot_pt  # noqa: E402
from _review_routes import _pt_key  # noqa: E402
import jl32_pinout as jl  # noqa: E402

PCB = ROOT / "injet-racing-prodv6.kicad_pcb"


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


def pad_net(block: str, pad: str) -> str | None:
    pm = re.search(rf'\(pad\s+"{re.escape(pad)}"[\s\S]*?\(net\s+"([^"]+)"\)', block)
    return pm.group(1) if pm else None


def cn2_pad(n: int, text: str) -> tuple[float, float] | None:
    blk = fp_block(text, "CN2")
    if not blk:
        return None
    at_m = re.search(r"\(at\s+([\d.-]+)\s+([\d.-]+)(?:\s+([\d.-]+))?", blk)
    if not at_m:
        return None
    ox, oy = float(at_m.group(1)), float(at_m.group(2))
    rot = float(at_m.group(3)) if at_m.group(3) else 0.0
    pm = re.search(rf'\(pad\s+"{n}"[\s\S]*?\(at\s+([\d.-]+)\s+([\d.-]+)', blk)
    if not pm:
        return None
    return rot_pt(ox, oy, rot, float(pm.group(1)), float(pm.group(2)))


def same_net(g, net: str, a: tuple[float, float], b: tuple[float, float]) -> bool:
    return g.connected(net, _pt_key(*a), _pt_key(*b))


def main() -> int:
    text = PCB.read_text(encoding="utf-8")
    g = parse_graph(text)
    ok = True
    u1_pad = jl.U1_HEAT_PAD["GHEAT"]

    print("PCB MOD12 — aquecedor lambda\n=== Posicoes ===")
    for ref in ["Q30", "R80", "R81", "D30"]:
        print(f"  {ref}: {fp_positions(text).get(ref, 'AUSENTE')}")

    print("\n=== Q30 IRLZ44N ===")
    q30 = fp_block(text, "Q30")
    for pad, want in [("G", "GHEAT"), ("D", "H-"), ("S", "GND")]:
        net = pad_net(q30, pad) if q30 else None
        mark = "OK" if net == want else f"ERR ({net})"
        print(f"  Q30.{pad} -> {want}: {mark}")
        if net != want:
            ok = False

    print("\n=== Passivos ===")
    for ref, spec in [
        ("R80", ("A", "GHEAT", "B", "GHEAT")),
        ("R81", ("A", "GHEAT", "B", "GND")),
        ("D30", ("A", "H-", "K", "+12V_PROT")),
    ]:
        blk = fp_block(text, ref)
        if not blk:
            print(f"  FALTA {ref}")
            ok = False
            continue
        for i in range(0, 4, 2):
            pad, want = spec[i], spec[i + 1]
            net = pad_net(blk, pad)
            mark = "OK" if net == want else f"ERR ({net})"
            print(f"  {ref}.{pad} -> {want}: {mark}")
            if net != want:
                ok = False

    print("\n=== U1 GHEAT ===")
    u1 = fp_block(text, "U1")
    pn = pad_net(u1, u1_pad) if u1 else None
    u1_pt = jl.u1_pad_xy(u1_pad)
    print(f"  {u1_pad} GHEAT @ {u1_pt}: {'OK' if pn == 'GHEAT' else f'ERR ({pn})'}")
    if pn != "GHEAT":
        ok = False

    print("\n=== Conectividade ===")
    r80a = fp_pad(text, "R80", "A")
    qg = fp_pad(text, "Q30", "G")
    qd = fp_pad(text, "Q30", "D")
    da = fp_pad(text, "D30", "A")
    cn2_1 = cn2_pad(1, text)
    cn2_2 = cn2_pad(2, text)
    dk = fp_pad(text, "D30", "K")

    mcu = r80a and same_net(g, "GHEAT", u1_pt, r80a)
    gate = r80a and qg and same_net(g, "GHEAT", r80a, qg)
    drain = qd and da and same_net(g, "H-", qd, da)
    cn_h = qd and cn2_2 and same_net(g, "H-", qd, cn2_2)
    cn_12 = cn2_1 and dk and same_net(g, "+12V_PROT", cn2_1, dk)
    fly = dk and dk == fp_pad(text, "D30", "K")  # net checked above

    print(f"  {u1_pad} -> R80 -> Q30.G: {'OK' if mcu and gate else 'FALHA'}")
    print(f"  Q30.D = D30.A (H-): {'OK' if drain else 'FALHA'}")
    print(f"  H- -> CN2-2: {'OK' if cn_h else 'FALHA'}")
    print(f"  D30.K -> +12V_PROT + CN2-1: {'OK' if cn_12 else 'FALHA'}")

    if not all([mcu, gate, drain, cn_h, cn_12]):
        ok = False

    print("\n=== Resultado ===")
    if ok:
        print("  MOD12 completo.")
        return 0
    print("  MOD12 com pendencias.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
