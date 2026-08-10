#!/usr/bin/env python3
"""Dump pad nets + positions MOD11/MOD12 from PCB."""
import re
from pathlib import Path

PCB = Path(__file__).resolve().parent / "injet-racing-prodv6.kicad_pcb"
text = PCB.read_text(encoding="utf-8")

REFS = [
    "U4", "U5", "CN2", "R70", "R71", "R76", "R77", "R78", "C30", "C31", "C32", "C33",
    "R80", "R81", "Q30", "D30", "U1",
]


def fp_block(ref: str) -> str | None:
    for fp in re.finditer(r"\(footprint[\s\S]*?\n\t\)", text):
        if re.search(rf'\(property\s+"Reference"\s+"{ref}"', fp.group(0)):
            return fp.group(0)
    return None


def pad_nets(block: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for m in re.finditer(r'\(pad\s+"([^"]+)"[\s\S]*?\(net\s+"([^"]+)"\)', block):
        out[m.group(1)] = m.group(2)
    return out


def main() -> None:
    for ref in REFS:
        b = fp_block(ref)
        if not b:
            print(f"{ref}: MISSING")
            continue
        at = re.search(r"\(at\s+([^\)]+)\)", b)
        pos = at.group(1) if at else "?"
        layer = re.search(r'\(footprint[^\n]+\n\t\t\(layer\s+"([^"]+)"\)', b)
        lyr = layer.group(1) if layer else "?"
        nets = pad_nets(b)
        print(f"=== {ref} @ {pos} layer={lyr} ===")
        for p in sorted(nets, key=lambda x: (len(x), x)):
            print(f"  {p}: {nets[p]}")


if __name__ == "__main__":
    main()
