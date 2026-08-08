#!/usr/bin/env python3
"""Checagem MOD12 — aquecedor λ (footprints + nets; rotas = pendente)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from _check_mod6_now import fp_positions  # noqa: E402
from prodv6_layout import POS_HEAT  # noqa: E402

PCB = ROOT / "injet-racing-prodv6.kicad_pcb"

Q30_PADS = {"G": "GHEAT", "D": "H-", "S": "GND"}

PASSIVE_NETS = {
    "R80": ("A", "GHEAT", "B", "GHEAT"),
    "R81": ("A", "GHEAT", "B", "GND"),
    "D30": ("A", "H-", "K", "+12V_PROT"),
}

U1_HEAT = {
    "GHEAT": ("L21I", (88.54, 54.66)),
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

    print("=== MOD12 posicoes PCB (origem footprint) ===")
    fps = fp_positions(text)
    for ref in POS_HEAT:
        if ref in fps:
            exp = POS_HEAT[ref]
            got = fps[ref]
            mark = "OK" if abs(got[0] - exp[0]) < 0.01 and abs(got[1] - exp[1]) < 0.01 else f"diff exp {exp}"
            print(f"  {ref}: {got[:2]} ({mark})")
        else:
            print(f"  FALTA {ref}")
            ok = False

    print("\n=== Q30 IRLZ44N ===")
    q30 = fp_block(text, "Q30")
    if not q30:
        print("  FALTA Q30")
        ok = False
    else:
        for pad, want in Q30_PADS.items():
            net = pad_net(q30, pad)
            mark = "OK" if net == want else f"ERR (tem {net})"
            print(f"  Q30.{pad} -> {want}: {mark}")
            if net != want:
                ok = False

    print("\n=== Passivos aquecedor ===")
    for ref, spec in PASSIVE_NETS.items():
        blk = fp_block(text, ref)
        if not blk:
            print(f"  FALTA {ref}")
            ok = False
            continue
        for i in range(0, len(spec), 2):
            pad, want = spec[i], spec[i + 1]
            net = pad_net(blk, pad)
            mark = "OK" if net == want else f"ERR (tem {net})"
            print(f"  {ref}.{pad} -> {want}: {mark}")
            if net != want:
                ok = False

    print("\n=== CN2 aquecedor (rotas pendentes) ===")
    cn2 = fp_block(text, "CN2")
    for pin, net in [(1, "+12V_PROT"), (2, "H-")]:
        got = pad_net(cn2, str(pin)) if cn2 else None
        print(f"  CN2-{pin} {net}: {'OK' if got == net else f'tem {got}'}")

    print("\n=== U1 GHEAT (pendente rotear · pad U1 pode estar H- ate F8) ===")
    u1 = fp_block(text, "U1")
    for net, (pad, pt) in U1_HEAT.items():
        pn = pad_net(u1, pad) if u1 else None
        note = "OK" if pn == net else f"tem {pn} (esperado {net})"
        print(f"  {pad} {net} @ {pt}: {note}")

    print("\n=== Resultado ===")
    if ok:
        print("  MOD12 footprints OK (4 pecas). Rotas U1/CN2 = pendente.")
        return 0
    print("  MOD12 incompleto — ver FALTA/ERR acima.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
