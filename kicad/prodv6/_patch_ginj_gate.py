#!/usr/bin/env python3
"""Fecha GINJ1-4 — cobre em ambos pads R_gate + ilha GINJ2 @ B.Cu."""
from __future__ import annotations

import importlib.util
import re
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# (x1, y1, x2, y2, net, width, layer)
ADD_SEG = [
    # GINJ2: ilha MCU (170.5,86.5) -> ramo gate (177,91) sem cobre A-B do R31
    (178.5, 86.5, 177.0, 91.0, "GINJ2", 0.65, "B.Cu"),
    # F.Cu stubs nos R_gate (footprint em F.Cu; reforca ligacao pad/trilha)
    (167.5, 91.0, 167.5, 89.0, "GINJ1", 0.65, "F.Cu"),
    (161.5, 91.0, 161.5, 93.0, "GINJ1", 0.65, "F.Cu"),
    (162.0, 120.0, 162.0, 118.0, "GINJ3", 0.65, "F.Cu"),
    (156.0, 120.0, 156.0, 122.0, "GINJ3", 0.65, "F.Cu"),
    (179.0, 123.5, 179.0, 121.5, "GINJ4", 0.65, "F.Cu"),
    (173.0, 123.5, 173.0, 125.5, "GINJ4", 0.65, "F.Cu"),
]

# (x, y, net)
ADD_VIA = [
    # U1 GINJ pads -> tronco B.Cu
    (138.54, 62.28, "GINJ1"),
    (138.54, 59.74, "GINJ2"),
    (138.54, 57.2, "GINJ3"),
    (138.54, 54.66, "GINJ4"),
    # R30 / R32 / R33 — ambos pads F.Cu <-> B.Cu
    (167.5, 91.0, "GINJ1"),
    (161.5, 91.0, "GINJ1"),
    (162.0, 120.0, "GINJ3"),
    (156.0, 120.0, "GINJ3"),
    (179.0, 123.5, "GINJ4"),
    (173.0, 123.5, "GINJ4"),
]


def _load_gen():
    spec = importlib.util.spec_from_file_location("gen", ROOT / "_gen_kicad_prodv6.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


gen = _load_gen()


def _segment(x1, y1, x2, y2, net: str, w: float, layer: str) -> str:
    return gen.fmt_pcb(
        [
            gen.S("segment"),
            [gen.S("start"), x1, y1],
            [gen.S("end"), x2, y2],
            [gen.S("width"), w],
            [gen.S("layer"), layer],
            [gen.S("net"), net],
            [gen.S("uuid"), str(uuid.uuid4())],
        ],
        1,
    )


def _via(x, y, net: str) -> str:
    return gen.fmt_pcb(
        [
            gen.S("via"),
            [gen.S("at"), x, y],
            [gen.S("size"), 0.5],
            [gen.S("drill"), 0.3],
            [gen.S("layers"), "F.Cu", "B.Cu"],
            [gen.S("net"), net],
            [gen.S("uuid"), str(uuid.uuid4())],
        ],
        1,
    )


def _has_segment(text: str, x1: float, y1: float, x2: float, y2: float) -> bool:
    a = (round(x1, 3), round(y1, 3))
    b = (round(x2, 3), round(y2, 3))
    for m in re.finditer(
        r"\(segment[\s\S]*?\(start ([\d.-]+) ([\d.-]+)\)[\s\S]*?"
        r"\(end ([\d.-]+) ([\d.-]+)\)",
        text,
    ):
        p = (
            (round(float(m.group(1)), 3), round(float(m.group(2)), 3)),
            (round(float(m.group(3)), 3), round(float(m.group(4)), 3)),
        )
        if p == (a, b) or p == (b, a):
            return True
    return False


def _has_via(text: str, x: float, y: float) -> bool:
    rx = round(x, 3)
    ry = round(y, 3)
    for m in re.finditer(r"\(via[\s\S]*?\(at ([\d.-]+) ([\d.-]+)\)", text):
        if round(float(m.group(1)), 3) == rx and round(float(m.group(2)), 3) == ry:
            return True
    return False


def main() -> None:
    pcb = ROOT / "injet-racing-prodv6.kicad_pcb"
    text = pcb.read_text(encoding="utf-8")
    zone_anchor = '\t(zone\n\t\t(net "GND")\n\t\t(layer "F.Cu")'
    zidx = text.find(zone_anchor)
    if zidx < 0:
        raise SystemExit("ancora zone GND nao encontrada")

    pre = text[:zidx]
    post = text[zidx:]
    seg_start = pre.find("\t(segment\n")
    if seg_start < 0:
        raise SystemExit("nenhum segment encontrado")

    new_blocks: list[str] = []
    added_seg = 0
    for x1, y1, x2, y2, net, w, layer in ADD_SEG:
        if _has_segment(text, x1, y1, x2, y2):
            continue
        new_blocks.append(_segment(x1, y1, x2, y2, net, w, layer) + "\n")
        added_seg += 1

    added_via = 0
    for x, y, net in ADD_VIA:
        if _has_via(text, x, y):
            continue
        new_blocks.append(_via(x, y, net) + "\n")
        added_via += 1

    if not new_blocks:
        print("GINJ gate: trechos ja presentes -- nada a fazer")
        return

    insert_at = seg_start
    out = pre[:insert_at] + "".join(new_blocks) + pre[insert_at:] + post
    pcb.write_text(out, encoding="utf-8")
    print(
        f"GINJ gate: +{added_seg} segmento(s), +{added_via} via "
        f"(R30/R32/R33 pads + GINJ2 ilha + U1 vias)"
    )


if __name__ == "__main__":
    main()
