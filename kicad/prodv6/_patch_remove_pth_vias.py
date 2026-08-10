#!/usr/bin/env python3
"""Remove vias redundantes em cima de pads PTH (pad furado ja liga F.Cu/B.Cu)."""
from __future__ import annotations

import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PCB = ROOT / "injet-racing-prodv6.kicad_pcb"

sys.path.insert(0, str(ROOT))
from _check_mod6_now import rot_pt  # noqa: E402

TOL = 0.05


def _pad_centers(text: str) -> list[tuple[float, float, str, str]]:
    out: list[tuple[float, float, str, str]] = []
    for fp in re.finditer(r"\(footprint[\s\S]*?\n\t\)", text):
        block = fp.group(0)
        ref_m = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', block)
        at_m = re.search(r"\(at\s+([\d.-]+)\s+([\d.-]+)(?:\s+([\d.-]+))?", block)
        if not ref_m or not at_m:
            continue
        ref = ref_m.group(1)
        ox, oy = float(at_m.group(1)), float(at_m.group(2))
        rot = float(at_m.group(3)) if at_m.group(3) else 0.0
        for pm in re.finditer(
            r'\(pad\s+"([^"]+)"[\s\S]*?'
            r"\(at\s+([\d.-]+)\s+([\d.-]+)(?:\s+([\d.-]+))?"
            r"[\s\S]*?"
            r"\(drill\s+([\d.-]+)\)",
            block,
        ):
            pad_name = pm.group(1)
            pad_block = pm.group(0)
            if "thru_hole" not in pad_block and '"*.Cu"' not in pad_block:
                continue
            drill = float(pm.group(5))
            if drill <= 0:
                continue
            px, py = float(pm.group(2)), float(pm.group(3))
            ax, ay = rot_pt(ox, oy, rot, px, py)
            out.append((ax, ay, ref, pad_name))
    return out


def _dist(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def main() -> None:
    text = PCB.read_text(encoding="utf-8")
    pads = _pad_centers(text)
    via_pat = re.compile(
        r"\t\(via\n"
        r"\t\t\(at\s+([\d.-]+)\s+([\d.-]+)\)\n"
        r"[\s\S]*?"
        r'\t\t\(net\s+"([^"]+)"\)\n'
        r"[\s\S]*?"
        r"\t\)\n"
    )

    removed: list[str] = []

    def repl(m: re.Match[str]) -> str:
        x, y = float(m.group(1)), float(m.group(2))
        net = m.group(3)
        for px, py, ref, pname in pads:
            if _dist((x, y), (px, py)) <= TOL:
                removed.append(f"  {net} @ ({x},{y}) on {ref}.{pname}")
                return ""
        return m.group(0)

    out = via_pat.sub(repl, text)
    if not removed:
        print("PTH vias: nenhuma via co-localizada com pad PTH")
        return

    PCB.write_text(out, encoding="utf-8")
    print(f"PTH vias: removidas {len(removed)} via(s) redundante(s):")
    for line in removed:
        print(line)


if __name__ == "__main__":
    main()
