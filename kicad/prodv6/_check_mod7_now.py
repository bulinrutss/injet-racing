#!/usr/bin/env python3
"""Checagem MOD7 — RPM PC817 → U1 R17O (PCB 2026-08-11)."""
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
NO_SERIES_BRIDGE = frozenset({"U7"})


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


def parse_graph_mod7(text: str):
    from _review_routes import NetGraph, _pt_key as pk

    g = NetGraph()
    for m in re.finditer(
        r'\(segment\s+\(start\s+([\d.-]+)\s+([\d.-]+)\)\s+\(end\s+([\d.-]+)\s+([\d.-]+)\)[\s\S]*?\(net\s+"([^"]+)"\)',
        text,
    ):
        x1, y1, x2, y2, net = m.groups()
        g.add_segment(net, pk(float(x1), float(y1)), pk(float(x2), float(y2)))
    for m in re.finditer(
        r'\(via\s+\(at\s+([\d.-]+)\s+([\d.-]+)\)[\s\S]*?\(net\s+"([^"]+)"\)',
        text,
    ):
        x, y, net = m.groups()
        drill_m = re.search(r'\(drill\s+([\d.-]+)\)', m.group(0))
        if drill_m and float(drill_m.group(1)) <= 0:
            continue
        g.add_junctions(net, [pk(float(x), float(y))])
    for fp in re.finditer(r"\(footprint[\s\S]*?\n\t\)", text):
        block = fp.group(0)
        ref_m = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', block)
        at_m = re.search(r"\(at\s+([\d.-]+)\s+([\d.-]+)(?:\s+([\d.-]+))?", block)
        if not ref_m or not at_m:
            continue
        ref = ref_m.group(1)
        ox, oy = float(at_m.group(1)), float(at_m.group(2))
        rot = float(at_m.group(3)) if at_m.group(3) else 0.0
        pads: list[tuple[str, tuple[float, float]]] = []
        for pm in re.finditer(
            r'\(pad\s+"([^"]+)"[\s\S]*?\(at\s+([\d.-]+)\s+([\d.-]+)[\s\S]*?\(net\s+"([^"]+)"\)',
            block,
        ):
            px, py = float(pm.group(2)), float(pm.group(3))
            net = pm.group(4)
            abs_pt = rot_pt(ox, oy, rot, px, py)
            g.add_junctions(net, [pk(*abs_pt)])
            pads.append((net, abs_pt))
        if ref in NO_SERIES_BRIDGE:
            continue
        by_net: dict[str, list[tuple[float, float]]] = {}
        for net, pt in pads:
            by_net.setdefault(net, []).append(pt)
        for net, pts in by_net.items():
            if len(pts) == 2:
                g.add_segment(net, pk(*pts[0]), pk(*pts[1]))
    return g


def same_net(g, net: str, a: tuple[float, float], b: tuple[float, float]) -> bool:
    return g.connected(net, _pt_key(*a), _pt_key(*b))


def main() -> None:
    text = PCB.read_text(encoding="utf-8")
    g = parse_graph_mod7(text)
    fps = fp_positions(text)
    ok = True
    u1_rpm = jl.u1_pad_xy(jl.U1_RPM_PAD)

    print(f"PCB: {PCB.name} · U1 {jl.U1_RPM_PAD} @ {u1_rpm}\n=== MOD7 posicoes ===")
    for ref in ["R20", "R21", "U7", "D3", "R22", "C25"]:
        got = fps.get(ref)
        print(f"  {ref}: {got if got else 'AUSENTE'}")
        if not got:
            ok = False

    u7 = fp_block(text, "U7")
    d3 = fp_block(text, "D3")
    if not u7 or not d3:
        raise SystemExit("U7 ou D3 ausente")

    p1 = pad_abs(u7, "1")
    p2 = pad_abs(u7, "2")
    p3 = pad_abs(u7, "3")
    p4 = pad_abs(u7, "4")
    da = pad_abs(d3, "A")
    dk = pad_abs(d3, "K")

    print("\n=== PC817 (pin1=anodo bobina · pin4=coletor MCU) ===")
    for label, pad, net_exp in [
        ("U7-1", p1, "RPM_IN"),
        ("U7-2", p2, "GND"),
        ("U7-3", p3, "GND"),
        ("U7-4", p4, "RPM_IN"),
    ]:
        if pad and pad[2] == net_exp:
            print(f"  {label}: {net_exp} OK")
        else:
            print(f"  {label}: ESPERADO {net_exp} — got {pad}")
            ok = False

    print("\n=== D3 1N4148 (protege LED) ===")
    if da and dk:
        print(f"  A={da[2]} · K={dk[2]}")
        if not (da[2] == "GND" and dk[2] == "RPM_IN"):
            print("  FALHA: esperado A=GND K=RPM_IN")
            ok = False
        else:
            print("  OK")

    cn22 = cn1_pad(22)
    r20a = fp_pad(text, "R20", "A")
    r21b = fp_pad(text, "R21", "B")
    print("\n=== Sequencia bobina ===")
    chain_cn = r20a and same_net(g, "RPM_IN", cn22, r20a)
    chain_r = r20a and r21b and same_net(g, "RPM_IN", r20a, r21b)
    chain_u7 = p1 and r21b and same_net(g, "RPM_IN", r21b, (p1[0], p1[1]))
    print(f"  CN1-22 -> R20: {'OK' if chain_cn else 'FALHA'}")
    print(f"  R20 -> R21: {'OK' if chain_r else 'FALHA'}")
    print(f"  R21 -> U7-1: {'OK' if chain_u7 else 'FALHA'}")
    if not (chain_cn and chain_r and chain_u7):
        ok = False

    iso_ok = p1 and p4 and not same_net(g, "RPM_IN", (p1[0], p1[1]), (p4[0], p4[1]))
    mcu_ok = p4 and same_net(g, "RPM_IN", (p4[0], p4[1]), u1_rpm)
    print(f"  U7-1 vs U7-4 isolado: {'OK' if iso_ok else 'CURTO!'}")
    print(f"  U7-4 -> {jl.U1_RPM_PAD}: {'OK' if mcu_ok else 'FALHA'}")
    if not iso_ok or not mcu_ok:
        ok = False

    r22b = fp_pad(text, "R22", "B")
    r22a = fp_pad(text, "R22", "A")
    c25a = fp_pad(text, "C25", "A")
    pull = r22b and r22a and p4 and same_net(g, "+3V3", cn1_pad(4), r22b) and same_net(
        g, "RPM_IN", r22a, (p4[0], p4[1])
    )
    filt = c25a and r22a and same_net(g, "RPM_IN", c25a, r22a)
    print(f"  R22 pull-up +3V3: {'OK' if pull else 'verificar'}")
    print(f"  C25 filtro: {'OK' if filt else 'verificar'}")

    print("\n=== Resultado ===")
    if ok and mcu_ok:
        print("  MOD7 completo.")
    else:
        print("  MOD7 com pendencias.")
        sys.exit(1)


if __name__ == "__main__":
    main()
