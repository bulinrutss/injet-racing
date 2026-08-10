#!/usr/bin/env python3
"""Fecha frestas DRC MOD11 (VM/UN @ U4) + MOD12 (GHEAT F.Cu ↔ B.Cu)."""
from __future__ import annotations

import importlib.util
import re
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# (x1, y1, x2, y2, net, width, layer)
ADD_SEG = [
    (212.54, 73.69, 215.08, 73.69, "VM", 1.0, "F.Cu"),
    (204.92, 73.69, 207.46, 73.69, "UN", 1.0, "F.Cu"),
    (184.0, 31.0, 187.0, 31.0, "GHEAT", 1.0, "F.Cu"),
    (187.0, 31.0, 190.0, 31.0, "GHEAT", 0.8, "B.Cu"),
]

# (x, y, net)
ADD_VIA = [
    (187.0, 31.0, "GHEAT"),
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
        print("MOD11/12 close: trechos ja presentes — nada a fazer")
        return

    insert_at = seg_start
    out = pre[:insert_at] + "".join(new_blocks) + pre[insert_at:] + post
    pcb.write_text(out, encoding="utf-8")
    print(
        f"MOD11/12 close: +{added_seg} segmento(s), +{added_via} via "
        f"(VM/UN @ U4 · GHEAT @ 187,31)"
    )


if __name__ == "__main__":
    main()
