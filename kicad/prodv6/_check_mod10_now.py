#!/usr/bin/env python3
"""Checagem MOD10 — CAN (footprints + nets nos pads; rotas = pendente)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from _check_mod6_now import fp_positions  # noqa: E402
from prodv6_layout import POS_CAN  # noqa: E402

PCB = ROOT / "injet-racing-prodv6.kicad_pcb"

U6_PADS = {
    "TX": "CAN_TX",
    "RX": "CAN_RX",
    "VCC": "+3V3",
    "GND": "GND",
    "H": "CANH",
    "L": "CANL",
}

U1_CAN = {
    "CAN_RX": ("L6O", (86.00, 92.76)),
    "CAN_TX": ("L6I", (88.54, 92.76)),
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


def main() -> int:
    text = PCB.read_text(encoding="utf-8")
    ok = True

    print("=== MOD10 posicoes PCB (origem footprint) ===")
    refs = list(POS_CAN.keys())
    fps = fp_positions(text)
    for ref in refs:
        if ref in fps:
            exp = POS_CAN[ref]
            got = fps[ref]
            mark = "OK" if abs(got[0] - exp[0]) < 0.01 and abs(got[1] - exp[1]) < 0.01 else f"diff exp {exp}"
            print(f"  {ref}: {got} ({mark})")
        else:
            print(f"  FALTA {ref}")
            ok = False

    print("\n=== U6 SN65HVD230 (pads) ===")
    u6 = fp_block(text, "U6")
    if not u6:
        print("  FALTA U6")
        ok = False
    else:
        for pad, want in U6_PADS.items():
            net = pad_net(u6, pad)
            mark = "OK" if net == want else f"ERR (tem {net})"
            print(f"  U6.{pad} -> {want}: {mark}")
            if net != want:
                ok = False

    print("\n=== Caps decoupling (+3V3 pad A · GND pad B) ===")
    for ref in ("C40", "C41"):
        blk = fp_block(text, ref)
        if not blk:
            print(f"  FALTA {ref}")
            ok = False
            continue
        na, nb = pad_net(blk, "A"), pad_net(blk, "B")
        ma = "OK" if na == "+3V3" else f"ERR ({na})"
        mb = "OK" if nb == "GND" else f"ERR ({nb})"
        print(f"  {ref}.A -> +3V3: {ma}  ·  {ref}.B -> GND: {mb}")
        if na != "+3V3" or nb != "GND":
            ok = False

    print("\n=== U1 CAN (pendente rotear) ===")
    u1 = fp_block(text, "U1")
    for net, (pad, pt) in U1_CAN.items():
        pn = pad_net(u1, pad) if u1 else None
        note = "OK" if pn == net else f"tem {pn}"
        print(f"  {pad} {net} @ {pt}: {note}")

    print("\n=== Resultado ===")
    if ok:
        print("  MOD10 footprints OK (3 pecas). Rotas U1/CN1 = pendente.")
        return 0
    print("  MOD10 incompleto — ver FALTA/ERR acima.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
