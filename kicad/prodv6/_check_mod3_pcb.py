#!/usr/bin/env python3
"""MOD3 connectivity from injet-racing-prodv6.kicad_pcb."""
import re
from pathlib import Path

PCB = Path(__file__).resolve().parent / "injet-racing-prodv6.kicad_pcb"
text = PCB.read_text(encoding="utf-8", errors="replace")

MOD3_REFS = {"F1", "Q1", "R1", "D1", "D2", "C1", "C2", "CN1", "F2"}
MOD3_BOX = (0, 55, 120, 160)  # x0, x1, y0, y1


def parse_footprints(raw: str) -> list:
    out = []
    for block in re.split(r"\n\t\(footprint ", raw)[1:]:
        m_ref = re.search(r'property "Reference" "([^"]+)"', block)
        m_at = re.search(r"\n\t\t\(at ([^\)]+)\)", block)
        if not m_ref or not m_at:
            continue
        ref = m_ref.group(1)
        parts = m_at.group(1).split()
        x, y = float(parts[0]), float(parts[1])
        pads = []
        for pm in re.finditer(
            r'\(pad "([^"]+)"[^\)]*\)[^\(]*(?:\([^\)]*\)[^\(]*)*\(net "([^"]+)"',
            block,
        ):
            pads.append((pm.group(1), pm.group(2)))
        if not pads:
            for pm in re.finditer(r'\(pad "([^"]+)".*?\(net "([^"]+)"', block, re.DOTALL):
                pads.append((pm.group(1), pm.group(2)))
        x0, x1, y0, y1 = MOD3_BOX
        in_zone = x0 <= x <= x1 and y0 <= y <= y1
        if ref in MOD3_REFS or (ref.startswith("F") and in_zone):
            out.append({"ref": ref, "at": (x, y), "pads": pads, "zone": in_zone})
    return out


def net_segments(raw: str, nets: set) -> dict:
    segs = {n: [] for n in nets}
    for m in re.finditer(
        r'\(segment\s+\(start ([^\)]+)\)\s+\(end ([^\)]+)\)\s+\(width[^\)]+\)\s+\(layer "([^"]+)"\)\s+\(net (\d+)\)',
        raw,
    ):
        net_id = m.group(5)
        segs.setdefault(net_id, []).append(m.groups())
    # map net names to ids
    names = {}
    for m in re.finditer(r'\(net (\d+) "([^"]+)"\)', raw):
        names[m.group(2)] = m.group(1)
    return {n: segs.get(names.get(n, ""), []) for n in nets}


fps = parse_footprints(text)
print("=== MOD3 footprints (zona oeste y120-160) ===\n")
for fp in sorted(fps, key=lambda f: (f["at"][1], f["at"][0])):
    ax, ay = fp["at"]
    tag = "MOD3" if fp["ref"] in MOD3_REFS else "jump?"
    print(f"{fp['ref']:5} @ ({ax:.1f}, {ay:.1f}) [{tag}]")
    for pad, net in fp["pads"]:
        print(f"  {pad:3} -> {net}")
    print()

for net in ("+12V_BAT", "+12V_IN", "+12V_PROT", "QG", "GND"):
    n = len(net_segments(text, {net})[net])
    print(f"segments {net}: {n}")
