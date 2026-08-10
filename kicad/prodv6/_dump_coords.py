#!/usr/bin/env python3
import re, sys
sys.path.insert(0, ".")
from _check_mod8_now import fp_block, pad_abs, U1_GINJ
from _check_mod6_now import fp_positions

text = open("injet-racing-prodv6.kicad_pcb", encoding="utf-8").read()

refs = [
    "R10", "R11", "R12", "R13", "R16", "R17",
    "R30", "R31", "R32", "R33", "R40", "R41", "R42", "R43",
    "R50", "R51", "R52", "Q10", "Q11", "Q12", "Q13",
    "D10", "D11", "D12", "D13", "R20", "R21", "U7", "D3", "R80", "Q30",
]
for ref in refs:
    b = fp_block(text, ref)
    if not b:
        continue
    fps = fp_positions(text)
    ox, oy, rot = fps.get(ref, (0, 0, 0))
    parts = []
    for p in ("A", "B", "G", "D", "S", "K", "1", "2", "3"):
        pa = pad_abs(b, p)
        if pa:
            parts.append(f"{p}=({pa[0]:.2f},{pa[1]:.2f}) {pa[2]}")
    print(f"{ref} orig=({ox},{oy}) rot={rot}: " + " | ".join(parts))

print("\nU1 GINJ pads:")
for net, (_, pt) in U1_GINJ.items():
    print(f"  {net}: {pt}")

from prodv6_layout import U1_SENS  # noqa: E402

print("\nU1 sensor pads (J2 esq):")
for net, pt in U1_SENS.items():
    print(f"  {net}: {pt}")

print("\nGRL MCU vias:")
for net, xy in [("GRL1", (74, 100)), ("GRL2", (76.5, 100)), ("GRL3", (78.5, 100))]:
    print(f"  {net}: via {xy}")

print("\nGINJ2 ilha — ponte B.Cu:")
print("  (170.5, 86.5) <-> (177.0, 91.0)  [R31.B / ramo gate]")
print("  MCU R19I: (138.54, 59.74) -> R31.A: (183.0, 91.0)")
