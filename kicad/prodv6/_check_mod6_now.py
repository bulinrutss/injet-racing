#!/usr/bin/env python3
"""Checagem MOD6 — CN1 + condicionamento → U1 (coords PCB 2026-08-11)."""
from __future__ import annotations

import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from _review_routes import NetGraph, _pt_key  # noqa: E402
import jl32_pinout as jl  # noqa: E402

PCB = ROOT / "injet-racing-prodv6.kicad_pcb"
CN1_AT = (12.0, 29.0)


def rot_pt(ox: float, oy: float, rot_deg: float, px: float, py: float) -> tuple[float, float]:
    r = math.radians(-rot_deg)
    c, s = math.cos(r), math.sin(r)
    return (ox + px * c - py * s, oy + px * s + py * c)


def parse_graph(text: str) -> NetGraph:
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
    for fp in re.finditer(r"\(footprint[\s\S]*?\n\t\)", text):
        block = fp.group(0)
        ref_m = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', block)
        at_m = re.search(r"\(at\s+([\d.-]+)\s+([\d.-]+)(?:\s+([\d.-]+))?", block)
        if not ref_m or not at_m:
            continue
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
        by_net: dict[str, list[tuple[float, float]]] = {}
        for net, pt in pads:
            by_net.setdefault(net, []).append(pt)
        for net, pts in by_net.items():
            if len(pts) == 2:
                g.add_segment(net, _pt_key(*pts[0]), _pt_key(*pts[1]))
    return g


def fp_pad(text: str, ref: str, pad_name: str) -> tuple[float, float] | None:
    for fp in re.finditer(r"\(footprint[\s\S]*?\n\t\)", text):
        block = fp.group(0)
        if not re.search(rf'\(property\s+"Reference"\s+"{ref}"', block):
            continue
        at_m = re.search(r"\(at\s+([\d.-]+)\s+([\d.-]+)(?:\s+([\d.-]+))?", block)
        if not at_m:
            return None
        ox, oy = float(at_m.group(1)), float(at_m.group(2))
        rot = float(at_m.group(3)) if at_m.group(3) else 0.0
        pm = re.search(
            rf'\(pad\s+"{pad_name}"[\s\S]*?\(at\s+([\d.-]+)\s+([\d.-]+)',
            block,
        )
        if not pm:
            return None
        return rot_pt(ox, oy, rot, float(pm.group(1)), float(pm.group(2)))
    return None


def cn1_pad(n: int) -> tuple[float, float]:
    """CN1 @ (12,29): fileira superior y+6, inferior y+0, passo x=4."""
    if n <= 12:
        return (CN1_AT[0] + (n - 1) * 4, CN1_AT[1] + 6)
    return (CN1_AT[0] + (n - 13) * 4, CN1_AT[1])


def main() -> None:
    text = PCB.read_text(encoding="utf-8")
    g = parse_graph(text)
    print(f"PCB: {PCB.name} · U1 @ {jl.U1_AT_PCB} · CN1 @ {CN1_AT}\n=== MOD6 ===\n")

    r12a = fp_pad(text, "R12", "A")
    r12b = fp_pad(text, "R12", "B")
    r13a = fp_pad(text, "R13", "A")
    c22a = fp_pad(text, "C22", "A")
    r16a = fp_pad(text, "R16", "A")
    r16b = fp_pad(text, "R16", "B")
    ok_map_div = all(
        [
            r12b and c22a and g.connected("MAP", _pt_key(*r12b), _pt_key(*c22a)),
            r12b and r13a and g.connected("MAP", _pt_key(*r12b), _pt_key(*r13a)),
            r16b and r12a and g.connected("MAP", _pt_key(*r16b), _pt_key(*r12a)),
        ]
    )
    print(f"1. MAP divisor R16-R12-R13/C22: {'OK' if ok_map_div else 'FALHA'}")

    cn6 = cn1_pad(6)
    r18a = fp_pad(text, "R18", "A")
    r18b = fp_pad(text, "R18", "B")
    c20a = fp_pad(text, "C20", "A")
    ok_iat = all(
        [
            r18a and g.connected("IAT", _pt_key(*cn6), _pt_key(*r18a)),
            r18b and c20a and g.connected("IAT", _pt_key(*r18b), _pt_key(*c20a)),
        ]
    )
    print(f"2. IAT CN1-6-R18-C20: {'OK' if ok_iat else 'FALHA'}")

    cn7 = cn1_pad(7)
    r19a = fp_pad(text, "R19", "A")
    r19b = fp_pad(text, "R19", "B")
    c21a = fp_pad(text, "C21", "A")
    ok_clt = all(
        [
            r19a and g.connected("CLT", _pt_key(*cn7), _pt_key(*r19a)),
            r19b and c21a and g.connected("CLT", _pt_key(*r19b), _pt_key(*c21a)),
        ]
    )
    print(f"3. CLT CN1-7-R19-C21: {'OK' if ok_clt else 'FALHA'}")

    cn8 = cn1_pad(8)
    ok_map_cn = r16a and g.connected("MAP", _pt_key(*cn8), _pt_key(*r16a))
    print(f"4. MAP CN1-8-R16: {'OK' if ok_map_cn else 'FALHA'}")

    cn10 = cn1_pad(10)
    r17a = fp_pad(text, "R17", "A")
    r17b = fp_pad(text, "R17", "B")
    c23a = fp_pad(text, "C23", "A")
    ok_tps = all(
        [
            r17a and g.connected("TPS", _pt_key(*cn10), _pt_key(*r17a)),
            r17b and c23a and g.connected("TPS", _pt_key(*r17b), _pt_key(*c23a)),
        ]
    )
    print(f"5. TPS CN1-10-R17-C23: {'OK' if ok_tps else 'FALHA'}")

    cn3 = cn1_pad(3)
    cn4 = cn1_pad(4)
    r10a = fp_pad(text, "R10", "A")
    ok_5v = g.connected("+5V", _pt_key(*cn3), _pt_key(*cn3))
    ok_33 = r10a and g.connected("+3V3", _pt_key(*cn4), _pt_key(*r10a))
    print(f"6. CN1-3 +5V / CN1-4 +3V3 pull-ups: {'OK' if ok_5v and ok_33 else 'FALHA'}")

    cn11 = cn1_pad(11)
    r14a = fp_pad(text, "R14", "A")
    ok_vbat = r14a and g.connected("+12V_PROT", _pt_key(*cn11), _pt_key(*r14a))
    print(f"7. VBAT +12V_PROT CN1-11-R14: {'OK' if ok_vbat else 'FALHA'}")

    print("\n=== U1 J2 (GPIO via pad_gpio) ===")
    src_ref = {"IAT": "R18", "CLT": "R19", "MAP": "R12", "TPS": "R17", "VBAT": "R14"}
    fails = 0
    for net, pad in jl.U1_SENS_PAD.items():
        pt = jl.u1_pad_xy(pad)
        gpio = jl.pad_gpio(pad)
        src = fp_pad(text, src_ref[net], "B")
        ok = src and g.connected(net, _pt_key(*pt), _pt_key(*src))
        if not ok:
            fails += 1
        print(f"  {net} {pad}={gpio} @ {pt}: {'OK' if ok else 'FALHA'}")
    print(f"\n{'TUDO OK' if fails == 0 and ok_map_div and ok_iat and ok_clt and ok_map_cn and ok_tps else 'REVISAR'}")


if __name__ == "__main__":
    main()
