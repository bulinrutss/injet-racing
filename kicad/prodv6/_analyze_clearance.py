#!/usr/bin/env python3
"""Clearance edge-to-edge entre segmentos (mesma camada)."""
from __future__ import annotations

import math
import re
from collections import defaultdict
from pathlib import Path

PCB = Path(__file__).parent / "injet-racing-prodv6.kicad_pcb"

# MOD8 injetores
ZONE = dict(x=(148, 218), y=(82, 128))
INJ_NETS = {"INJ1", "INJ2", "INJ3", "INJ4", "GINJ1", "GINJ2", "GINJ3", "GINJ4", "+12V_PROT"}


def parse_segments(text: str) -> list[dict]:
    pat = re.compile(
        r"\(segment\s+\(start\s+([\d.-]+)\s+([\d.-]+)\)\s+\(end\s+([\d.-]+)\s+([\d.-]+)\)\s+"
        r"\(width\s+([\d.-]+)\)\s+\(layer\s+\"([^\"]+)\"\)\s+\(net\s+\"([^\"]+)\"\)",
    )
    segs = []
    for m in pat.finditer(text):
        x1, y1, x2, y2 = map(float, m.groups()[:4])
        segs.append(
            dict(
                x1=x1,
                y1=y1,
                x2=x2,
                y2=y2,
                w=float(m.group(5)),
                layer=m.group(6),
                net=m.group(7),
            )
        )
    return segs


def seg_bbox(s: dict) -> tuple[float, float, float, float]:
    hw = s["w"] / 2
    return (
        min(s["x1"], s["x2"]) - hw,
        min(s["y1"], s["y2"]) - hw,
        max(s["x1"], s["x2"]) + hw,
        max(s["y1"], s["y2"]) + hw,
    )


def bbox_gap(a: tuple, b: tuple) -> float:
    """Gap between expanded bboxes; negative = overlap."""
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    dx = max(0.0, max(ax0 - bx1, bx0 - ax1))
    dy = max(0.0, max(ay0 - by1, by0 - ay1))
    return math.hypot(dx, dy)


def in_zone(s: dict) -> bool:
    for x, y in ((s["x1"], s["y1"]), (s["x2"], s["y2"])):
        if ZONE["x"][0] <= x <= ZONE["x"][1] and ZONE["y"][0] <= y <= ZONE["y"][1]:
            return True
    return False


def parallel_x_spacing(segs: list[dict]) -> list[tuple]:
    """Vertical-ish segments: center-x distance minus half widths."""
    out = []
    verts = []
    for s in segs:
        if abs(s["x1"] - s["x2"]) > 0.5:
            continue
        if abs(s["y1"] - s["y2"]) < 2:
            continue
        verts.append(s)
    for i, a in enumerate(verts):
        for b in verts[i + 1 :]:
            if a["layer"] != b["layer"] or a["net"] == b["net"]:
                continue
            xa = (a["x1"] + a["x2"]) / 2
            xb = (b["x1"] + b["x2"]) / 2
            ya0, ya1 = sorted((a["y1"], a["y2"]))
            yb0, yb1 = sorted((b["y1"], b["y2"]))
            overlap = min(ya1, yb1) - max(ya0, yb0)
            if overlap < 5:
                continue
            edge = abs(xa - xb) - a["w"] / 2 - b["w"] / 2
            out.append((edge, a["net"], b["net"], a["layer"], xa, xb, overlap))
    return sorted(out, key=lambda t: t[0])


def main() -> None:
    segs = parse_segments(PCB.read_text(encoding="utf-8"))
    mod8 = [s for s in segs if in_zone(s)]

    print(f"MOD8 segmentos: {len(mod8)}\n")

    # Global min clearance (different nets, same layer)
    worst: list[tuple] = []
    by_layer: dict[str, list[tuple]] = defaultdict(list)
    for layer in {s["layer"] for s in segs}:
        ls = [s for s in segs if s["layer"] == layer]
        for i, a in enumerate(ls):
            ba = seg_bbox(a)
            for b in ls[i + 1 :]:
                if a["net"] == b["net"]:
                    continue
                g = bbox_gap(ba, seg_bbox(b))
                if g < 1.0:
                    by_layer[layer].append((g, a["net"], b["net"], a))
                    worst.append((g, layer, a["net"], b["net"], a))

    print("=== Menor gap cobre-cobre (PCB inteira, bbox) ===")
    for g, layer, n1, n2, s in sorted(worst, key=lambda t: t[0])[:15]:
        print(f"  {g:.2f} mm  {layer}  {n1} x {n2}  @ x~{(s['x1']+s['x2'])/2:.1f} y~{(s['y1']+s['y2'])/2:.1f}")

    print("\n=== MOD8 — trilhas verticais paralelas (edge gap) ===")
    par = parallel_x_spacing(mod8)
    for edge, n1, n2, layer, xa, xb, ov in par[:20]:
        print(f"  gap {edge:.2f} mm  {n1:10} x {n2:10}  {layer}  x={xa:.1f}/{xb:.1f}  overlap {ov:.0f} mm")

    print("\n=== MOD8 — só nets injetor / +12V ===")
    inj = [s for s in mod8 if s["net"] in INJ_NETS]
    par_inj = parallel_x_spacing(inj)
    for edge, n1, n2, layer, xa, xb, ov in par_inj[:15]:
        print(f"  gap {edge:.2f} mm  {n1} x {n2}  x={xa:.1f}/{xb:.1f}")

    if par_inj:
        mn = min(p[0] for p in par_inj)
        print(f"\n  MENOR gap injetores: {mn:.2f} mm")


if __name__ == "__main__":
    main()
