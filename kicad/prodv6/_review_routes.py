#!/usr/bin/env python3
"""Revisão de conectividade das rotas ProdV6 (parse .kicad_pcb).

Uso: python _review_routes.py [caminho/injet-racing-prodv6.kicad_pcb]
"""
from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PCB = ROOT / "injet-racing-prodv6.kicad_pcb"

# Nets críticas por bloco — todos os pads/segmentos devem formar um componente conectado
BLOCK_NETS = {
    "MOD4": {
        "+12V_PROT": [
            (48, 118), (46, 118), (46, 40), (48, 40), (30, 50), (30, 38),
        ],
        "+5V": [
            (65, 40), (65, 44.5), (78, 44.5), (68, 44.5), (68, 38), (68, 111),
        ],
    },
    "MOD5": {
        "+5V": [
            (65, 40), (78, 44.5), (68, 111), (146, 111),
            (136, 108), (136, 105.46), (146, 108),
        ],
        "+3V3": [
            (86, 108), (88.54, 105.46), (128.46, 105.46), (129.5, 105.5),
            (136, 102.92), (150.5, 102.5), (150.5, 110.5), (150.5, 88),
            (148.5, 110.5),
        ],
        "VREF+": [
            (136, 82.6), (129.5, 89.1), (144.5, 113), (147, 94.5), (147, 88),
        ],
    },
    "MOD6": {
        "+3V3": [
            (36, 14), (14, 14), (14, 94), (16, 94), (14, 105.46), (88.54, 105.46),
        ],
        "+5V": [
            (32, 14), (32, 111), (68, 111),
        ],
        "+12V_PROT": [
            (48, 118), (14, 118), (14, 62), (16, 62),
        ],
        "IAT": [
            (40, 14), (34, 94), (40, 94), (86, 94), (86, 67.36),
        ],
        "CLT": [
            (44, 14), (34, 86), (40, 86), (86, 86), (86, 64.82),
        ],
        "MAP": [
            (48, 14), (34, 78), (22, 78), (86, 78), (86, 77.52),
        ],
        "TPS": [
            (52, 14), (34, 70), (40, 70), (88.54, 70), (88.54, 64.82),
        ],
        "VBAT": [
            (22, 62), (88.54, 62), (88.54, 62.28),
        ],
    },
}


def _pt_key(x: float, y: float) -> tuple[float, float]:
    return (round(x, 3), round(y, 3))


def _on_segment(px: float, py: float, x1: float, y1: float, x2: float, y2: float, tol: float = 0.01) -> bool:
    if abs(x1 - x2) < tol:
        if abs(px - x1) > tol:
            return False
        lo, hi = sorted((y1, y2))
        return lo - tol <= py <= hi + tol
    if abs(y1 - y2) < tol:
        if abs(py - y1) > tol:
            return False
        lo, hi = sorted((x1, x2))
        return lo - tol <= px <= hi + tol
    return False


class NetGraph:
    def __init__(self) -> None:
        self.segments: dict[str, list[tuple[tuple, tuple]]] = defaultdict(list)
        self._junctions: dict[str, set[tuple]] = defaultdict(set)

    def add_segment(self, net: str, start: tuple, end: tuple) -> None:
        self.segments[net].append((start, end))
        self._junctions[net].update((start, end))

    def add_junctions(self, net: str, points: list[tuple]) -> None:
        self._junctions[net].update(points)

    def connected(self, net: str, a: tuple, b: tuple) -> bool:
        """BFS — junções T em segmentos colineares (como KiCad)."""
        segs = self.segments.get(net, [])
        extra = self._junctions.get(net, set())
        if not segs:
            return False

        def neighbors(p: tuple) -> set[tuple]:
            n: set[tuple] = set()
            for s, e in segs:
                on_seg = p == s or p == e or _on_segment(p[0], p[1], s[0], s[1], e[0], e[1])
                if not on_seg:
                    continue
                n.update((s, e))
                for q in extra:
                    if q != p and _on_segment(q[0], q[1], s[0], s[1], e[0], e[1]):
                        n.add(q)
            return n

        seen = {a}
        stack = [a]
        while stack:
            cur = stack.pop()
            if cur == b:
                return True
            for n in neighbors(cur):
                if n not in seen:
                    seen.add(n)
                    stack.append(n)
        return False

    def component_count(self, net: str, points: list[tuple]) -> int:
        if not points:
            return 0
        parent = {p: p for p in points}

        def find(p: tuple) -> tuple:
            while parent[p] != p:
                parent[p] = parent[parent[p]]
                p = parent[p]
            return p

        def union(a: tuple, b: tuple) -> None:
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[rb] = ra

        for i, a in enumerate(points):
            for b in points[i + 1:]:
                if self.connected(net, a, b):
                    union(a, b)

        return len({find(p) for p in points})


def _seg_bbox(x1, y1, x2, y2) -> tuple[float, float, float, float]:
    return (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))


def _segments_overlap(a: tuple, b: tuple, tol: float = 0.01) -> bool:
    """Colinear overlap on B.Cu between two different-net segments (short risk)."""
    (x1, y1, x2, y2), net_a = a
    (u1, v1, u2, v2), net_b = b
    if net_a == net_b:
        return False
    if abs(y1 - y2) < tol and abs(v1 - v2) < tol and abs(y1 - v1) < tol:
        lo_a, hi_a = sorted((x1, x2))
        lo_b, hi_b = sorted((u1, u2))
        return lo_a < hi_b - tol and lo_b < hi_a - tol
    if abs(x1 - x2) < tol and abs(u1 - u2) < tol and abs(x1 - u1) < tol:
        lo_a, hi_a = sorted((y1, y2))
        lo_b, hi_b = sorted((v1, v2))
        return lo_a < hi_b - tol and lo_b < hi_a - tol
    return False


def check_mod5_overlaps(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    segs: list[tuple[tuple[float, float, float, float], str]] = []
    for m in re.finditer(
        r'\(segment\s+\(start\s+([\d.-]+)\s+([\d.-]+)\)\s+\(end\s+([\d.-]+)\s+([\d.-]+)\)[\s\S]*?\(layer\s+"B\.Cu"\)[\s\S]*?\(net\s+"([^"]+)"\)',
        text,
    ):
        x1, y1, x2, y2, net = m.groups()
        bx = _seg_bbox(float(x1), float(y1), float(x2), float(y2))
        if bx[0] >= 70 and bx[1] >= 44:
            segs.append((bx, net))
    hits = 0
    for i, a in enumerate(segs):
        for b in segs[i + 1 :]:
            if _segments_overlap(a, b):
                hits += 1
                print(f"    SOBREPOSICAO: {a[1]} x {b[1]} em {a[0]}")
    return hits


def parse_pcb(path: Path) -> NetGraph:
    text = path.read_text(encoding="utf-8")
    g = NetGraph()
    for m in re.finditer(
        r'\(segment\s+\(start\s+([\d.-]+)\s+([\d.-]+)\)\s+\(end\s+([\d.-]+)\s+([\d.-]+)\)[\s\S]*?\(net\s+"([^"]+)"\)',
        text,
    ):
        x1, y1, x2, y2, net = m.groups()
        g.add_segment(net, _pt_key(float(x1), float(y1)), _pt_key(float(x2), float(y2)))
    for block in BLOCK_NETS.values():
        for net, anchors in block.items():
            g.add_junctions(net, [_pt_key(*p) for p in anchors])
    return g


def review(path: Path) -> int:
    g = parse_pcb(path)
    errors = 0
    print(f"Revisão de rotas: {path.name}\n")

    for block, nets in BLOCK_NETS.items():
        print(f"  [{block}]")
        for net, anchors in nets.items():
            n_comp = g.component_count(net, [_pt_key(*p) for p in anchors])
            ok = n_comp == 1
            status = "OK" if ok else f"FALHA ({n_comp} ilhas)"
            print(f"    {net}: {status}")
            if not ok:
                errors += 1
                for i, a in enumerate(anchors):
                    for b in anchors[i + 1:]:
                        if not g.connected(net, _pt_key(*a), _pt_key(*b)):
                            print(f"      desconectado: {a} <-> {b}")
        print()

    print("  [MOD5 sobreposicao B.Cu]")
    overlaps = check_mod5_overlaps(path)
    if overlaps:
        print(f"    FALHA: {overlaps} trecho(s) colinear(es) entre nets diferentes")
        errors += overlaps
    else:
        print("    OK — sem sobreposicao colinear entre nets")
    print()

    if errors:
        print(f"RESULTADO: {errors} problema(s).")
        return 1
    print("RESULTADO: conectividade OK nos blocos revisados.")
    return 0


if __name__ == "__main__":
    pcb = Path(sys.argv[1]) if len(sys.argv) > 1 else PCB
    raise SystemExit(review(pcb))
