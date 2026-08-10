#!/usr/bin/env python3
"""Passo 5 — GRL3: remove stub morto B.Cu @ (115.0325, 115.5325)."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PCB = ROOT / "injet-racing-prodv6.kicad_pcb"

# Cotovelo órfão (0,05 mm) — não liga R52.A; fileira B.Cu já passa em (119.588, 115.532)
DEAD = (
    (115.0325, 115.5325),
    (115.0, 115.5),
)


def _seg_endpoints(block: str) -> tuple[tuple[float, float], tuple[float, float]] | None:
    sm = re.search(r"\(start ([\d.-]+) ([\d.-]+)\)", block)
    em = re.search(r"\(end ([\d.-]+) ([\d.-]+)\)", block)
    if not sm or not em:
        return None
    return (
        (round(float(sm.group(1)), 4), round(float(sm.group(2)), 4)),
        (round(float(em.group(1)), 4), round(float(em.group(2)), 4)),
    )


def main() -> None:
    text = PCB.read_text(encoding="utf-8")
    dead_a = (round(DEAD[0][0], 4), round(DEAD[0][1], 4))
    dead_b = (round(DEAD[1][0], 4), round(DEAD[1][1], 4))
    removed = 0

    def repl(m: re.Match[str]) -> str:
        nonlocal removed
        block = m.group(0)
        if 'net "GRL3"' not in block:
            return block
        pts = _seg_endpoints(block)
        if not pts:
            return block
        if pts == (dead_a, dead_b) or pts == (dead_b, dead_a):
            removed += 1
            return ""
        return block

    out = re.sub(
        r"\t\(segment\n[\s\S]*?\t\)\n",
        repl,
        text,
    )
    if not removed:
        print("GRL3 stub: segmento morto nao encontrado (ja removido?)")
        return

    PCB.write_text(out, encoding="utf-8")
    print(f"GRL3 stub: removido {removed} segmento(s) B.Cu @ {DEAD[0]}")


if __name__ == "__main__":
    main()
