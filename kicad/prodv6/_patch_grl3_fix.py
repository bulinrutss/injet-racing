#!/usr/bin/env python3
"""GRL3 — via F->B antes do R52; B.Cu so em R52.A; gate em R52.B (pad injetor)."""
from __future__ import annotations

import importlib.util
import re
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PCB = ROOT / "injet-racing-prodv6.kicad_pcb"

# segmentos a remover: (x1,y1,x2,y2) — fileira A<->B no B.Cu / F.Cu ate pad A
REMOVE_SEG = [
    # F.Cu direto em R52.A (MCU deve ir via @ 119.5,112.5)
    (119.5875, 113.5875, 119.5875, 115.5325),
    (119.5, 113.5, 119.5875, 113.5875),
    (119.5, 112.5, 119.5, 113.5),
    # B.Cu atravessando R52 A-B (bypass 1k)
    (119.588, 115.532, 124.088, 115.532),
    (125.5875, 115.5325, 124.0875, 115.5325),
    (124.0875, 115.5325, 119.5875, 120.0325),
]

# (x1,y1,x2,y2, net, w, layer)
ADD_SEG = [
    # MCU B.Cu -> R52.A (pad A only)
    (119.5, 112.5, 119.5875, 115.5325, "GRL3", 0.8, "B.Cu"),
    # R52.B -> R57.A (nó gate)
    (125.5875, 115.5325, 119.5875, 120.0325, "GRL3", 0.8, "B.Cu"),
]

ADD_VIA = (119.5, 112.5, "GRL3")


def _load_gen():
    spec = importlib.util.spec_from_file_location("gen", ROOT / "_gen_kicad_prodv6.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


gen = _load_gen()


def _seg_endpoints(block: str) -> tuple[tuple[float, float], tuple[float, float]] | None:
    sm = re.search(r"\(start ([\d.-]+) ([\d.-]+)\)", block)
    em = re.search(r"\(end ([\d.-]+) ([\d.-]+)\)", block)
    if not sm or not em:
        return None
    return (
        (round(float(sm.group(1)), 4), round(float(sm.group(2)), 4)),
        (round(float(em.group(1)), 4), round(float(em.group(2)), 4)),
    )


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
    for m in re.finditer(r"\t\(segment\n[\s\S]*?\t\)\n", text):
        pts = _seg_endpoints(m.group(0))
        if not pts:
            continue
        p = (
            (round(pts[0][0], 3), round(pts[0][1], 3)),
            (round(pts[1][0], 3), round(pts[1][1], 3)),
        )
        if p == (a, b) or p == (b, a):
            return True
    return False


def _has_via(text: str, x: float, y: float) -> bool:
    rx, ry = round(x, 3), round(y, 3)
    for m in re.finditer(r"\(via[\s\S]*?\(at ([\d.-]+) ([\d.-]+)\)", text):
        if round(float(m.group(1)), 3) == rx and round(float(m.group(2)), 3) == ry:
            return True
    return False


def main() -> None:
    text = PCB.read_text(encoding="utf-8")
    dead_set = set()
    for x1, y1, x2, y2 in REMOVE_SEG:
        dead_set.add((round(x1, 4), round(y1, 4), round(x2, 4), round(y2, 4)))
        dead_set.add((round(x2, 4), round(y2, 4), round(x1, 4), round(y1, 4)))

    removed = 0

    def seg_repl(m: re.Match[str]) -> str:
        nonlocal removed
        block = m.group(0)
        pts = _seg_endpoints(block)
        if not pts:
            return block
        key = (
            round(pts[0][0], 4),
            round(pts[0][1], 4),
            round(pts[1][0], 4),
            round(pts[1][1], 4),
        )
        rev = (key[2], key[3], key[0], key[1])
        if key in dead_set or rev in dead_set:
            removed += 1
            return ""
        return block

    text = re.sub(r"\t\(segment\n[\s\S]*?\t\)\n", seg_repl, text)

    zone_anchor = '\t(zone\n\t\t(net "GND")\n\t\t(layer "F.Cu")'
    zidx = text.find(zone_anchor)
    if zidx < 0:
        raise SystemExit("ancora zone GND nao encontrada")
    pre, post = text[:zidx], text[zidx:]
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

    vx, vy, vnet = ADD_VIA
    added_via = 0
    if not _has_via(text, vx, vy):
        new_blocks.append(_via(vx, vy, vnet) + "\n")
        added_via += 1

    if new_blocks:
        text = pre[:seg_start] + "".join(new_blocks) + pre[seg_start:] + post
    else:
        text = pre + post

    PCB.write_text(text, encoding="utf-8")
    print(
        f"GRL3 fix: -{removed} segmento(s) errado(s), "
        f"+{added_seg} B.Cu, +{added_via} via @ ({vx},{vy})"
    )


if __name__ == "__main__":
    main()
