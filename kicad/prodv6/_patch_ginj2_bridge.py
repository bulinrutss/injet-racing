#!/usr/bin/env python3
"""Passo 3 — GINJ2: ponte B.Cu (178.5,86.5) -> (177,91) entre ramos MCU e gate."""
from __future__ import annotations

import importlib.util
import re
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PCB = ROOT / "injet-racing-prodv6.kicad_pcb"

BRIDGE = (178.5, 86.5, 177.0, 91.0, "GINJ2", 0.65, "B.Cu")


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
    x1, y1, x2, y2, net, w, layer = BRIDGE
    if _has_segment(text, x1, y1, x2, y2):
        print("GINJ2 ponte: trecho ja presente")
        return

    zone_anchor = '\t(zone\n\t\t(net "GND")\n\t\t(layer "F.Cu")'
    zidx = text.find(zone_anchor)
    if zidx < 0:
        raise SystemExit("ancora zone GND nao encontrada")
    pre, post = text[:zidx], text[zidx:]
    seg_start = pre.find("\t(segment\n")
    if seg_start < 0:
        raise SystemExit("nenhum segment encontrado")

    block = _segment(x1, y1, x2, y2, net, w, layer) + "\n"
    out = pre[:seg_start] + block + pre[seg_start:] + post
    PCB.write_text(out, encoding="utf-8")
    print(f"GINJ2 ponte: +1 segmento B.Cu ({x1},{y1}) -> ({x2},{y2})")


if __name__ == "__main__":
    main()
