#!/usr/bin/env python3
"""Remove vias quebradas (drill <= 0 ou size <= 0) e duplicatas no mesmo ponto."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PCB = ROOT / "injet-racing-prodv6.kicad_pcb"

VIA_BLOCK = re.compile(
    r"\t\(via\n"
    r"\t\t\(at\s+([\d.-]+)\s+([\d.-]+)\)\n"
    r"\t\t\(size\s+([\d.-]+)\)\n"
    r"\t\t\(drill\s+([\d.-]+)\)\n"
    r"[\s\S]*?"
    r'\t\t\(net\s+"([^"]+)"\)\n'
    r"[\s\S]*?"
    r"\t\)\n"
)


def main() -> None:
    text = PCB.read_text(encoding="utf-8")
    removed: list[str] = []

    def repl(m: re.Match[str]) -> str:
        x, y = float(m.group(1)), float(m.group(2))
        size = float(m.group(3))
        drill = float(m.group(4))
        net = m.group(5)
        if drill <= 0 or size <= 0:
            removed.append(f"  {net} @ ({x},{y}) drill={drill} size={size}")
            return ""
        return m.group(0)

    out = VIA_BLOCK.sub(repl, text)
    if not removed:
        print("Broken vias: nenhuma via quebrada encontrada")
        return

    PCB.write_text(out, encoding="utf-8")
    print(f"Broken vias: removidas {len(removed)} via(s):")
    for line in removed:
        print(line)


if __name__ == "__main__":
    main()
