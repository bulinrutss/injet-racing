#!/usr/bin/env python3
"""Checagem MOD11 — lambda (PCB real vs topologia esquema §7)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from _check_mod6_now import fp_positions  # noqa: E402
from prodv6_layout import POS_LAMBDA  # noqa: E402

PCB = ROOT / "injet-racing-prodv6.kicad_pcb"

# MCP6004 @ -90°: ch.A 1-3=VM · ch.B 5-7=UN · 4=GND · 14=+5V
U4_PADS = {
    "1": "VM", "2": "VM", "3": "VM",
    "4": "GND",
    "5": "UN", "6": "UN", "7": "UN",
    "14": "+5V",
}

# AD8628: pin2 −IN=IP · pin3 +IN=VM · pin6 OUT=IP · pin4 GND · pin7 +5V
U5_PADS = {
    "2": "IP", "3": "VM", "4": "GND", "6": "IP", "7": "+5V",
}

PASSIVE_NETS = {
    "R70": ("A", "IP", "B", "VM"),       # shunt bomba Ip↔Vm
    "R71": ("A", "UN", "B", "RI_PULSE"),  # R_ESR pulso Ri
    "R76": ("A", "+3V3", "B", "VM"),
    "R77": ("A", "VM", "B", "GND"),
    "R78": ("A", "UN", "B", "RI_PULSE"),  # série filtro Un → nó Ri/ADC
    "C30": ("A", "IP", "B", "GND"),
    "C31": ("A", "UN", "B", "GND"),
    "C32": ("A", "+5V", "B", "GND"),
    "C33": ("A", "+5V", "B", "GND"),
}

U1_LAMBDA = {
    "VM": ("R13I", (138.54, 74.98)),   # PA4 DAC
    "IP": ("R13O", (136.00, 74.98)),   # PA5 ADC
    "UN": ("R14I", (138.54, 77.52)),   # PA6 ADC — não RI_PULSE
}


def fp_block(text: str, ref: str) -> str | None:
    for fp in re.finditer(r"\(footprint[\s\S]*?\n\t\)", text):
        if re.search(rf'\(property\s+"Reference"\s+"{ref}"', fp.group(0)):
            return fp.group(0)
    return None


def pad_net(block: str, pad: str) -> str | None:
    pm = re.search(
        rf'\(pad\s+"{re.escape(pad)}"[\s\S]*?\(net\s+"([^"]+)"\)',
        block,
    )
    return pm.group(1) if pm else None


def check_passive(blk: str, ref: str) -> bool:
    spec = PASSIVE_NETS[ref]
    ok = True
    for i in range(0, len(spec), 2):
        pad, want = spec[i], spec[i + 1]
        net = pad_net(blk, pad)
        mark = "OK" if net == want else f"ERR (tem {net})"
        print(f"  {ref}.{pad} -> {want}: {mark}")
        if net != want:
            ok = False
    return ok


def main() -> int:
    text = PCB.read_text(encoding="utf-8")
    ok = True

    print("=== MOD11 posicoes PCB (origem footprint) ===")
    fps = fp_positions(text)
    for ref in POS_LAMBDA:
        if ref in fps:
            exp = POS_LAMBDA[ref]
            got = fps[ref]
            dx = abs(got[0] - exp[0])
            dy = abs(got[1] - exp[1])
            mark = "OK" if dx < 0.05 and dy < 0.05 else f"diff exp {exp}"
            print(f"  {ref}: ({got[0]:.2f}, {got[1]:.2f}) rot={got[2]:.0f} ({mark})")
        else:
            print(f"  FALTA {ref}")
            ok = False

    print("\n=== U4 MCP6004 ===")
    u4 = fp_block(text, "U4")
    if not u4:
        print("  FALTA U4")
        ok = False
    else:
        for pad, want in U4_PADS.items():
            net = pad_net(u4, pad)
            mark = "OK" if net == want else f"ERR (tem {net})"
            print(f"  U4.{pad} -> {want}: {mark}")
            if net != want:
                ok = False

    print("\n=== U5 AD8628 B.Cu ===")
    u5 = fp_block(text, "U5")
    if not u5:
        print("  FALTA U5")
        ok = False
    else:
        for pad, want in U5_PADS.items():
            net = pad_net(u5, pad)
            mark = "OK" if net == want else f"ERR (tem {net})"
            print(f"  U5.{pad} -> {want}: {mark}")
            if net != want:
                ok = False

    print("\n=== Passivos lambda ===")
    for ref in PASSIVE_NETS:
        blk = fp_block(text, ref)
        if not blk:
            print(f"  FALTA {ref}")
            ok = False
            continue
        if not check_passive(blk, ref):
            ok = False

    print("\n=== CN2 lambda ===")
    cn2 = fp_block(text, "CN2")
    for pin, net in [(1, "+12V_PROT"), (2, "H-"), (3, "IP"), (4, "VM"), (5, "UN")]:
        got = pad_net(cn2, str(pin)) if cn2 else None
        mark = "OK" if got == net else f"tem {got}"
        print(f"  CN2-{pin} {net}: {mark}")
        if got != net:
            ok = False

    print("\n=== U1 lambda (J3 dir.) ===")
    u1 = fp_block(text, "U1")
    for net, (pad, pt) in U1_LAMBDA.items():
        pn = pad_net(u1, pad) if u1 else None
        note = "OK" if pn == net else f"ERR tem {pn} (esperado {net})"
        print(f"  {pad} {net} @ {pt}: {note}")
        if pn != net:
            ok = False

    print("\n=== Resultado ===")
    if ok:
        print("  MOD11 OK — topologia conferida.")
        return 0
    print("  MOD11 — corrigir ERR acima.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
