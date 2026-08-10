#!/usr/bin/env python3
"""Passo 4 — GINJ1/3/4: stubs F.Cu nos pads A/B de R30/R32/R33 (sem via, sem ponte A-B no B.Cu)."""
from __future__ import annotations

import importlib.util
import re
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PCB = ROOT / "injet-racing-prodv6.kicad_pcb"

# (x1, y1, x2, y2, net, width, layer) — stubs curtos para fora do resistor
ADD_SEG = [
    # R30 @ (167.5, 91) rot 180 — A=(167.5,91) B=(161.5,91)
    (167.5, 91.0, 167.5, 93.0, "GINJ1", 0.8, "F.Cu"),
    (161.5, 91.0, 159.0, 91.0, "GINJ1", 0.8, "F.Cu"),
    # R32 @ (162, 120) rot 180 — A=(162,120) B=(156,120)
    (162.0, 120.0, 162.0, 122.0, "GINJ3", 0.8, "F.Cu"),
    (156.0, 120.0, 154.0, 120.0, "GINJ3", 0.8, "F.Cu"),
    # R33 @ (179, 123.5) rot 180 — A=(179,123.5) B=(173,123.5)
    (179.0, 123.5, 179.0, 125.5, "GINJ4", 0.8, "F.Cu"),
    (173.0, 123.5, 171.0, 123.5, "GINJ4", 0.8, "F.Cu"),
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


def main() -> None:
    text = PCB.read_text(encoding="utf-8")
    zone_anchor = '\t(zone\n\t\t(net "GND")\n\t\t(layer "F.Cu")'
    zidx = text.find(zone_anchor)
    if zidx < 0:
        raise SystemExit("ancora zone GND nao encontrada")
    pre, post = text[:zidx], text[zidx:]
    seg_start = pre.find("\t(segment\n")
    if seg_start < 0:
        raise SystemExit("nenhum segment encontrado")

    new_blocks: list[str] = []
    added = 0
    for x1, y1, x2, y2, net, w, layer in ADD_SEG:
        if _has_segment(text, x1, y1, x2, y2):
            continue
        new_blocks.append(_segment(x1, y1, x2, y2, net, w, layer) + "\n")
        added += 1

    if not added:
        print("GINJ1/3/4 passo 4: stubs F.Cu ja presentes")
        return

    out = pre[:seg_start] + "".join(new_blocks) + pre[seg_start:] + post
    PCB.write_text(out, encoding="utf-8")
    print(f"GINJ1/3/4 passo 4: +{added} stub(s) F.Cu em R30/R32/R33")


if __name__ == "__main__":
    main()
