#!/usr/bin/env python3
"""Checagem MOD11 — lambda (footprints + nets nos pads; rotas = pendente)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from _check_mod6_now import fp_positions  # noqa: E402
from prodv6_layout import POS_LAMBDA  # noqa: E402

PCB = ROOT / "injet-racing-prodv6.kicad_pcb"

U4_PADS = {
    "1": "VM", "2": "VM", "4": "GND", "5": "VM", "14": "+5V",
}

U5_PADS = {
    "2": "VM", "3": "VM", "4": "GND", "5": "VM", "6": "VM",
}

PASSIVE_NETS = {
    "R70": ("A", "IP", "B", "IP"),
    "R71": ("A", "UN", "B", "RI_PULSE"),
    "R76": ("A", "+3V3", "B", "VM"),
    "R77": ("A", "VM", "B", "GND"),
    "R78": ("A", "UN", "B", "RI_PULSE"),
    "C30": ("A", "IP", "B", "GND"),
    "C31": ("A", "UN", "B", "GND"),
    "C32": ("A", "+5V", "B", "GND"),
    "C33": ("A", "+5V", "B", "GND"),
}

U1_LAMBDA = {
    "VM": ("R13I", (138.54, 74.98)),
    "IP": ("R13O", (136.00, 74.98)),
    "UN": ("R14I", (138.54, 77.52)),
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
            mark = "OK" if abs(got[0] - exp[0]) < 0.01 and abs(got[1] - exp[1]) < 0.01 else f"diff exp {exp}"
            print(f"  {ref}: {got} ({mark})")
        else:
            print(f"  FALTA {ref}")
            ok = False

    print("\n=== U4 MCP6004 (pads power/VM) ===")
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

    print("\n=== U5 AD8628 B.Cu (pads power/VM) ===")
    u5 = fp_block(text, "U5")
    if not u5:
        print("  FALTA U5")
        ok = False
    else:
        layer = re.search(r'\(layer\s+"([^"]+)"\)', u5)
        print(f"  layer footprint: {layer.group(1) if layer else '?'}")
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

    print("\n=== CN2 (ja na placa — rotas pendentes) ===")
    cn2 = fp_block(text, "CN2")
    for pin, net in [(1, "+12V_PROT"), (2, "H-"), (3, "IP"), (4, "VM"), (5, "UN")]:
        got = pad_net(cn2, str(pin)) if cn2 else None
        mark = "OK" if got == net else f"tem {got}"
        print(f"  CN2-{pin} {net}: {mark}")

    print("\n=== U1 lambda (pendente rotear) ===")
    u1 = fp_block(text, "U1")
    for net, (pad, pt) in U1_LAMBDA.items():
        pn = pad_net(u1, pad) if u1 else None
        note = "OK" if pn == net else f"tem {pn}"
        print(f"  {pad} {net} @ {pt}: {note}")

    print("\n=== Resultado ===")
    if ok:
        print("  MOD11 footprints OK (11 pecas). Rotas U1/CN2/+5V = pendente.")
        return 0
    print("  MOD11 incompleto — ver FALTA/ERR acima.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
