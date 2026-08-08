#!/usr/bin/env python3
"""Checagem MOD9 — relés (footprints presentes; rotas = pendente)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from _check_mod6_now import fp_positions  # noqa: E402
from prodv6_layout import POS_REL  # noqa: E402

PCB = ROOT / "injet-racing-prodv6.kicad_pcb"

U1_GRL = {
    "GRL1": ("L23I", (88.54, 49.58)),
    "GRL2": ("L22O", (86.00, 52.12)),
    "GRL3": ("L22I", (88.54, 52.12)),
}

CN1_AT = (12.0, 14.0)
CN1_REL_PAD = {
    "RL_PUMP": (CN1_AT[0] + 16, CN1_AT[1]),
    "RL_MAIN": (CN1_AT[0] + 20, CN1_AT[1]),
    "RL_IAC": (CN1_AT[0] + 24, CN1_AT[1]),
}

CHANNELS = [
    ("RL1", "GRL1", "RL_MAIN", "Q20", "R50", "R55", "D20", "RL1", 18),
    ("RL2", "GRL2", "RL_PUMP", "Q21", "R51", "R56", "D21", "RL2", 17),
    ("RL3", "GRL3", "RL_IAC", "Q22", "R52", "R57", "D22", "RL3", 19),
]


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

    print("=== MOD9 posicoes PCB (origem footprint) ===")
    refs = list(POS_REL.keys())
    fps = fp_positions(text)
    for ref in refs:
        if ref in fps:
            exp = POS_REL[ref]
            got = fps[ref]
            mark = "OK" if abs(got[0] - exp[0]) < 0.01 and abs(got[1] - exp[1]) < 0.01 else f"diff exp {exp}"
            print(f"  {ref}: {got} ({mark})")
        else:
            print(f"  FALTA {ref}")
            ok = False

    print("\n=== Nets nos pads (sem trilhas ainda) ===")
    for coil, grl, out_net, q, rg, rpd, d, rl, cn_pin in CHANNELS:
        print(f"\n  --- {coil} / {grl} -> {out_net} ---")
        for ref, pads in [
            (q, [("G", grl), ("D", coil), ("S", "GND")]),
            (rg, [("A", grl), ("B", grl)]),
            (rpd, [("A", grl), ("B", "GND")]),
            (d, [("A", coil), ("K", "+12V_PROT")]),
            (rl, [("1", "+12V_PROT"), ("2", coil), ("3", "+12V_PROT"), ("4", out_net)]),
        ]:
            blk = fp_block(text, ref)
            if not blk:
                print(f"    FALTA {ref}")
                ok = False
                continue
            for pad, want in pads:
                net = pad_net(blk, pad)
                mark = "OK" if net == want else f"ERR (tem {net})"
                print(f"    {ref}.{pad} -> {want}: {mark}")
                if net != want:
                    ok = False

    print("\n=== U1 pads GRL (MCU — net pode ser RL* ate F8/sync) ===")
    u1 = fp_block(text, "U1")
    for grl, (pad, pt) in U1_GRL.items():
        net = pad_net(u1, pad) if u1 else None
        note = "OK" if net == grl else f"tem {net} — rotear como {grl}"
        print(f"  {pad} {grl} @ {pt}: {note}")

    print("\n=== Resultado ===")
    if ok:
        print("  MOD9 footprints OK (15 pecas). Rotas e CN1 = pendente.")
        return 0
    print("  MOD9 incompleto — ver FALTA/ERR acima.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
