#!/usr/bin/env python3
"""Fecha MOD5 — adiciona apenas trechos em falta nas rotas manuais (não reaplica layout)."""
from __future__ import annotations

import importlib.util
import re
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def _load_gen():
    spec = importlib.util.spec_from_file_location("gen", ROOT / "_gen_kicad_prodv6.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


gen = _load_gen()

# Trechos mínimos para fechar nets (layout manual KiCad preservado)
ADD = [
    # +5V — porta MOD4 (78,44.5) → tronco x=68
    (78.0, 44.5, 68.0, 44.5, "+5V", 1.0),
    # +3V3 — J2 esq. → barra norte x=72 → cluster leste (C11/U8)
    (86.0, 108.0, 72.0, 108.0, "+3V3", 1.0),
    (72.0, 108.0, 72.0, 110.5, "+3V3", 1.0),
    (72.0, 110.5, 150.5, 110.5, "+3V3", 1.0),
    # +3V3 OUT — porta leste para MOD6+
    (150.5, 110.5, 156.0, 110.5, "+3V3", 1.0),
]

# Segmentos mortos (78→76 repetidos, não ligam tronco)
REMOVE_PAIRS = {
    ((78.0, 44.5), (76.0, 44.5)),
    ((76.0, 44.5), (78.0, 44.5)),
}


def _seg_end(block: str) -> tuple[tuple[float, float], tuple[float, float]] | None:
    m = re.search(
        r"\(start ([\d.-]+) ([\d.-]+)\)\s+\(end ([\d.-]+) ([\d.-]+)\)",
        block,
    )
    if not m:
        return None
    a = (round(float(m.group(1)), 3), round(float(m.group(2)), 3))
    b = (round(float(m.group(3)), 3), round(float(m.group(4)), 3))
    return a, b


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

    head, seg_region = pre[:seg_start], pre[seg_start:]
    parts = re.split(r"(?<=\n)\t\(segment\n", seg_region)
    seg_head = parts[0]
    segs = ["\t(segment\n" + p for p in parts[1:] if p.strip()]

    kept: list[str] = []
    removed = 0
    for s in segs:
        ends = _seg_end(s)
        if ends and ends in REMOVE_PAIRS:
            removed += 1
            continue
        kept.append(s)

    existing = set()
    for s in kept:
        ends = _seg_end(s)
        if ends:
            existing.add(ends)
            existing.add((ends[1], ends[0]))

    new_blocks: list[str] = []
    added = 0
    for x1, y1, x2, y2, net, w in ADD:
        key = ((round(x1, 3), round(y1, 3)), (round(x2, 3), round(y2, 3)))
        rev = (key[1], key[0])
        if key in existing or rev in existing:
            continue
        new_blocks.append(_segment(x1, y1, x2, y2, net, w) + "\n")
        existing.add(key)
        added += 1

    out = head + seg_head + "".join(kept) + "".join(new_blocks) + post
    pcb.write_text(out, encoding="utf-8")
    print(f"  MOD5 close: +{added} segmento(s), -{removed} morto(s)")


if __name__ == "__main__":
    main()
