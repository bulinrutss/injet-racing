#!/usr/bin/env python3
"""Checagem MOD7 — RPM PC817 (pads reais PCB; U1 R17O opcional)."""
from __future__ import annotations

import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from _check_mod6_now import fp_positions, rot_pt  # noqa: E402

PCB = ROOT / "injet-racing-prodv6.kicad_pcb"
CN1_AT = (12.0, 14.0)
CN1_RPM = (CN1_AT[0] + 44, CN1_AT[1] + 6)  # pad 12
U1_RPM = (136.0, 64.82)  # R17O PE8

# Origem footprint @ KiCad (at x y [rot])
POS_EXPECT = {
    "R20": (77.5, 31.5, 90.0),
    "R21": (77.5, 20.0, 0.0),
    "U7": (89.19, 26.73, 0.0),
    "D3": (83.5, 25.5, 0.0),
    "R22": (104.0, 26.5, -90.0),
    "C25": (104.0, 21.0, 180.0),
}

# PC817: pin1 e pin4 compartilham net no esquematico mas NAO sao curto no cobre
NO_SERIES_BRIDGE = frozenset({"U7"})


def parse_graph_mod7(text: str):
    from _review_routes import NetGraph, _pt_key

    g = NetGraph()
    for m in re.finditer(
        r'\(segment\s+\(start\s+([\d.-]+)\s+([\d.-]+)\)\s+\(end\s+([\d.-]+)\s+([\d.-]+)\)[\s\S]*?\(net\s+"([^"]+)"\)',
        text,
    ):
        x1, y1, x2, y2, net = m.groups()
        g.add_segment(net, _pt_key(float(x1), float(y1)), _pt_key(float(x2), float(y2)))
    for m in re.finditer(
        r'\(via\s+\(at\s+([\d.-]+)\s+([\d.-]+)\)[\s\S]*?\(net\s+"([^"]+)"\)',
        text,
    ):
        x, y, net = m.groups()
        drill_m = re.search(r'\(drill\s+([\d.-]+)\)', m.group(0))
        if drill_m and float(drill_m.group(1)) <= 0:
            continue
        g.add_junctions(net, [_pt_key(float(x), float(y))])
    for fp in re.finditer(r'\(footprint[\s\S]*?\n\t\)', text):
        block = fp.group(0)
        ref_m = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', block)
        at_m = re.search(r'\(at\s+([\d.-]+)\s+([\d.-]+)(?:\s+([\d.-]+))?', block)
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
            g.add_junctions(net, [_pt_key(*abs_pt)])
            pads.append((net, abs_pt))
        if ref in NO_SERIES_BRIDGE:
            continue
        by_net: dict[str, list[tuple[float, float]]] = {}
        for net, pt in pads:
            by_net.setdefault(net, []).append(pt)
        for net, pts in by_net.items():
            if len(pts) == 2:
                g.add_segment(net, _pt_key(*pts[0]), _pt_key(*pts[1]))
    return g


def pad_abs(block: str, ref: str, pad: str) -> tuple[float, float, str] | None:
    at_m = re.search(r'\(at\s+([\d.-]+)\s+([\d.-]+)(?:\s+([\d.-]+))?', block)
    if not at_m:
        return None
    ox, oy = float(at_m.group(1)), float(at_m.group(2))
    rot = float(at_m.group(3)) if at_m.group(3) else 0.0
    for pm in re.finditer(
        rf'\(pad\s+"{re.escape(pad)}"[\s\S]*?\(at\s+([\d.-]+)\s+([\d.-]+)[\s\S]*?\(net\s+"([^"]+)"\)',
        block,
    ):
        px, py = float(pm.group(1)), float(pm.group(2))
        net = pm.group(3)
        return (*rot_pt(ox, oy, rot, px, py), net)
    return None


def fp_block(text: str, ref: str) -> str | None:
    for fp in re.finditer(r'\(footprint[\s\S]*?\n\t\)', text):
        if re.search(rf'\(property\s+"Reference"\s+"{ref}"', fp.group(0)):
            return fp.group(0)
    return None


def same_net(g, net: str, a: tuple[float, float], b: tuple[float, float]) -> bool:
    from _review_routes import _pt_key

    return g.connected(net, _pt_key(*a), _pt_key(*b))


def main() -> None:
    text = PCB.read_text(encoding="utf-8")
    g = parse_graph_mod7(text)
    fps = fp_positions(text)
    ok = True

    print("=== MOD7 posicoes PCB vs gerador ===")
    for ref, exp in POS_EXPECT.items():
        got = fps.get(ref)
        if not got:
            print(f"  FALTA {ref}")
            ok = False
            continue
        dx = abs(got[0] - exp[0])
        dy = abs(got[1] - exp[1])
        dr = abs(got[2] - exp[2])
        mark = "OK" if dx < 0.01 and dy < 0.01 and dr < 0.01 else "DIFF"
        if mark != "OK":
            print(f"  {ref}: PCB {got} != esperado {exp}")
        else:
            print(f"  {ref}: {got} OK")

    u7 = fp_block(text, "U7")
    d3 = fp_block(text, "D3")
    if not u7 or not d3:
        raise SystemExit("U7 ou D3 ausente")

    p1 = pad_abs(u7, "U7", "1")
    p2 = pad_abs(u7, "U7", "2")
    p3 = pad_abs(u7, "U7", "3")
    p4 = pad_abs(u7, "U7", "4")
    da = pad_abs(d3, "D3", "A")
    dk = pad_abs(d3, "D3", "K")

    print("\n=== PC817 pinagem (nets) ===")
    expect = {
        "U7-1 anodo": (p1, "RPM_IN"),
        "U7-2 catodo": (p2, "GND"),
        "U7-3 emissor": (p3, "GND"),
        "U7-4 coletor": (p4, "RPM_IN"),
    }
    for label, (pad, net_exp) in expect.items():
        if pad and pad[2] == net_exp:
            print(f"  {label}: {net_exp} OK @ ({pad[0]:.2f},{pad[1]:.2f})")
        else:
            print(f"  {label}: ESPERADO {net_exp} — got {pad}")
            ok = False

    print("\n=== D3 protecao LED ===")
    if da and dk:
        print(f"  D3 A={da[2]} @ ({da[0]:.2f},{da[1]:.2f})")
        print(f"  D3 K={dk[2]} @ ({dk[0]:.2f},{dk[1]:.2f})")
        if da[2] == "GND" and dk[2] == "RPM_IN":
            print("  D3 pinagem gerador OK (A=GND, K=no LED/bobina)")
        elif da[2] == "GND" and dk[2] == "GND":
            print("  AVISO: D3 A e K ambos GND — diodo nao protege LED (corrigir K para RPM_IN no KiCad)")
            ok = False
        else:
            print("  AVISO: D3 nets inesperadas")
            ok = False

    print("\n=== Conectividade (ilhas copper) ===")
    chain = [
        ("CN1-12", CN1_RPM),
        ("U7-1", (p1[0], p1[1]) if p1 else (0, 0)),
        ("U7-4", (p4[0], p4[1]) if p4 else (0, 0)),
        ("R17O", U1_RPM),
    ]
    cn_ok = same_net(g, "RPM_IN", CN1_RPM, (p1[0], p1[1])) if p1 else False
    iso_ok = p1 and p4 and not same_net(g, "RPM_IN", (p1[0], p1[1]), (p4[0], p4[1]))
    mcu_ok = same_net(g, "RPM_IN", (p4[0], p4[1]), U1_RPM) if p4 else False

    print(f"  CN1-12 -> U7-1 (bobina): {'OK' if cn_ok else 'FALTA trilha'}")
    print(f"  U7-1 vs U7-4 (opto isolado): {'OK' if iso_ok else 'CURTO - pin1 e pin4 na mesma ilha!'}")
    print(f"  U7-4 -> R17O PE8: {'OK' if mcu_ok else 'FALTA trilha'}")
    if not cn_ok or not iso_ok:
        ok = False

    r22 = fp_block(text, "R22")
    if r22:
        ra = pad_abs(r22, "R22", "A")
        rb = pad_abs(r22, "R22", "B")
        if ra and rb:
            pull = rb[2] == "+3V3" and same_net(g, "RPM_IN", (ra[0], ra[1]), (p4[0], p4[1]) if p4 else (0, 0))
            print(f"  R22 pull-up +3V3: {'OK' if pull else 'verificar'}")
            if ra[2] != "RPM_IN" or rb[2] != "+3V3":
                ok = False

    print("\n=== Resultado ===")
    if ok and mcu_ok:
        print("  MOD7 completo (bobina + opto + R17O).")
    elif ok and not mcu_ok:
        print("  MOD7 bobina+opto OK — falta coletor -> R17O.")
    elif ok:
        print("  MOD7 completo.")
    else:
        print("  MOD7 com pendencias — ver acima.")
        sys.exit(1)


if __name__ == "__main__":
    main()
