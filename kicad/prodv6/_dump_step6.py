#!/usr/bin/env python3
from __future__ import annotations

import math
import re
from pathlib import Path

from _check_mod6_now import cn1_pad, fp_pad, parse_graph, rot_pt
from _review_routes import _pt_key

PCB = Path(__file__).resolve().parent / "injet-racing-prodv6.kicad_pcb"
U1 = {
    "L18I": (88.54, 62.28),
    "L17O": (86.0, 64.82),
    "L16O": (86.0, 67.36),
    "L12O": (86.0, 77.52),
    "R17O": (136.0, 64.82),
    "L21I": (88.54, 54.66),
}


def pad_q30_g(text: str):
    for fp in re.finditer(r"\(footprint[\s\S]*?\n\t\)", text):
        b = fp.group(0)
        if not re.search(r'\(property\s+"Reference"\s+"Q30"', b):
            continue
        at = re.search(r"\(at\s+([\d.-]+)\s+([\d.-]+)(?:\s+([\d.-]+))?", b)
        ox, oy = float(at.group(1)), float(at.group(2))
        rot = float(at.group(3) or 0)
        pm = re.search(r'\(pad\s+"G"[\s\S]*?\(at\s+([\d.-]+)\s+([\d.-]+)', b)
        return rot_pt(ox, oy, rot, float(pm.group(1)), float(pm.group(2))) if pm else None
    return None


def pad_u7(text: str, p: str):
    for fp in re.finditer(r"\(footprint[\s\S]*?\n\t\)", text):
        b = fp.group(0)
        if not re.search(r'\(property\s+"Reference"\s+"U7"', b):
            continue
        at = re.search(r"\(at\s+([\d.-]+)\s+([\d.-]+)(?:\s+([\d.-]+))?", b)
        ox, oy = float(at.group(1)), float(at.group(2))
        rot = float(at.group(3) or 0)
        pm = re.search(rf'\(pad\s+"{re.escape(p)}"[\s\S]*?\(at\s+([\d.-]+)\s+([\d.-]+)', b)
        return rot_pt(ox, oy, rot, float(pm.group(1)), float(pm.group(2))) if pm else None
    return None


def d(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def main():
    text = PCB.read_text(encoding="utf-8")
    g = parse_graph(text)

    nets = {
        "TPS": [
            ("CN1-11", cn1_pad(11)),
            ("R17.A", fp_pad(text, "R17", "A")),
            ("R17.B", fp_pad(text, "R17", "B")),
            ("C23.A", fp_pad(text, "C23", "A")),
            ("C23.B", fp_pad(text, "C23", "B")),
            ("U1.L18I", U1["L18I"]),
        ],
        "MAP": [
            ("CN1-10", cn1_pad(10)),
            ("R16.A", fp_pad(text, "R16", "A")),
            ("R16.B", fp_pad(text, "R16", "B")),
            ("R12.A", fp_pad(text, "R12", "A")),
            ("R12.B", fp_pad(text, "R12", "B")),
            ("R13.A", fp_pad(text, "R13", "A")),
            ("C22.A", fp_pad(text, "C22", "A")),
            ("U1.L17O", U1["L17O"]),
        ],
        "CLT": [
            ("CN1-9", cn1_pad(9)),
            ("R19.A", fp_pad(text, "R19", "A")),
            ("R19.B", fp_pad(text, "R19", "B")),
            ("R11.A", fp_pad(text, "R11", "A")),
            ("R11.B", fp_pad(text, "R11", "B")),
            ("C21.A", fp_pad(text, "C21", "A")),
            ("U1.L16O", U1["L16O"]),
        ],
        "IAT": [
            ("CN1-8", cn1_pad(8)),
            ("R18.A", fp_pad(text, "R18", "A")),
            ("R18.B", fp_pad(text, "R18", "B")),
            ("R10.A", fp_pad(text, "R10", "A")),
            ("C20.A", fp_pad(text, "C20", "A")),
            ("U1.L12O", U1["L12O"]),
        ],
        "RPM_IN": [
            ("CN1-12", (56.0, 20.0)),
            ("R20.A", fp_pad(text, "R20", "A")),
            ("R20.B", fp_pad(text, "R20", "B")),
            ("R21.A", fp_pad(text, "R21", "A")),
            ("R21.B", fp_pad(text, "R21", "B")),
            ("U7.1", pad_u7(text, "1")),
            ("U7.4", pad_u7(text, "4")),
            ("D3.K", fp_pad(text, "D3", "K")),
            ("U1.R17O", U1["R17O"]),
        ],
        "GHEAT": [
            ("U1.L21I", U1["L21I"]),
            ("R80.A", fp_pad(text, "R80", "A")),
            ("R80.B", fp_pad(text, "R80", "B")),
            ("R81.A", fp_pad(text, "R81", "A")),
            ("Q30.G", pad_q30_g(text)),
        ],
    }

    for net, pts in nets.items():
        pts = [(l, p) for l, p in pts if p]
        print(f"\n=== {net} ===")
        for l, p in pts:
            print(f"  {l:10} ({p[0]:.2f}, {p[1]:.2f})")
        print("  gaps (<25mm, nao conectados):")
        for i, (la, a) in enumerate(pts):
            for lb, b in pts[i + 1 :]:
                if not g.connected(net, _pt_key(*a), _pt_key(*b)) and d(a, b) < 25:
                    print(f"    {la} <-> {lb}  dist={d(a,b):.1f}mm")


if __name__ == "__main__":
    main()
