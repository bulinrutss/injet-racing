#!/usr/bin/env python3
"""Fecha U5 pad 2 (−IN) → tronco IP B.Cu (pad 6 / stub @ 232.135, 43.635)."""
from __future__ import annotations

import importlib.util
import re
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# U5 @ (225.3, 41.095) B.Cu — contornar pad 7 (+5V @ 230.7, 42.365)
# Tronco y=41.2 sul do SOIC · sobe x=231.5 · liga stub IP existente
ADD = [
    (225.3, 42.365, 225.3, 41.2, "IP", 0.5),      # stub pad 2 ↓
    (225.3, 41.2, 231.5, 41.2, "IP", 0.5),        # bus sul U5 →
    (231.5, 41.2, 231.5, 43.635, "IP", 0.5),       # sobe leste
    (231.5, 43.635, 232.135, 43.635, "IP", 0.5),   # → stub existente
]


def _load_gen():
    spec = importlib.util.spec_from_file_location("gen", ROOT / "_gen_kicad_prodv6.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


gen = _load_gen()


def _segment(x1, y1, x2, y2, net: str, w: float) -> str:
    return gen.fmt_pcb(
        [
            gen.S("segment"),
            [gen.S("start"), x1, y1],
            [gen.S("end"), x2, y2],
            [gen.S("width"), w],
            [gen.S("layer"), "B.Cu"],
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
    added = 0
    for x1, y1, x2, y2, net, w in ADD:
        if _has_segment(text, x1, y1, x2, y2):
            continue
        new_blocks.append(_segment(x1, y1, x2, y2, net, w) + "\n")
        added += 1

    if not added:
        print("MOD11 U5 IP: trechos ja presentes — nada a fazer")
        return

    insert_at = seg_start
    out = pre[:insert_at] + "".join(new_blocks) + pre[insert_at:] + post
    pcb.write_text(out, encoding="utf-8")
    print(f"MOD11 U5 IP: +{added} segmento(s) B.Cu (pad 2 -> tronco IP)")


if __name__ == "__main__":
    main()
