#!/usr/bin/env python3
"""Checagem CN3 — posição + nets nos pads (sem trilhas)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from prodv6_layout import CN3_AT, CN3_PAD_NETS, CN3_ROT  # noqa: E402

PCB = ROOT / "injet-racing-prodv6.kicad_pcb"
TOL = 0.15


def fp_block(text: str, ref: str) -> str | None:
    for fp in re.finditer(r"\(footprint[\s\S]*?\n\t\)", text):
        if re.search(rf'\(property\s+"Reference"\s+"{ref}"', fp.group(0)):
            return fp.group(0)
    return None


def fp_at(block: str) -> tuple[float, float, float]:
    m = re.search(r"\(at\s+([\d.-]+)\s+([\d.-]+)(?:\s+([\d.-]+))?", block)
    if not m:
        return (0.0, 0.0, 0.0)
    rot = float(m.group(3)) if m.group(3) else 0.0
    return float(m.group(1)), float(m.group(2)), rot


def pad_net(block: str, pad: str) -> str | None:
    pm = re.search(
        rf'\(pad\s+"{re.escape(pad)}"[\s\S]*?\(net\s+"([^"]+)"\)',
        block,
    )
    return pm.group(1) if pm else None


def main() -> int:
    text = PCB.read_text(encoding="utf-8")
    blk = fp_block(text, "CN3")
    if not blk:
        print("CN3: FALTA footprint")
        return 1

    x, y, rot = fp_at(blk)
    pos_ok = abs(x - CN3_AT[0]) <= TOL and abs(y - CN3_AT[1]) <= TOL and abs(rot - CN3_ROT) <= 0.1
    print(f"=== CN3 @ ({x}, {y}) rot={rot} === {'OK' if pos_ok else 'ERR'}")

    ok = pos_ok
    for pin, want in CN3_PAD_NETS.items():
        got = pad_net(blk, str(pin))
        mark = "OK" if got == want else f"ERR (tem {got})"
        print(f"  pad {pin} -> {want}: {mark}")
        if got != want:
            ok = False
    for pin in (5, 6):
        got = pad_net(blk, str(pin))
        print(f"  pad {pin} -> NC: {'OK' if not got else f'ERR net {got}'}")

    print("\n=== Resultado ===")
    if ok:
        print("  CN3 footprint OK — rotear RLx.4 -> CN3 depois.")
        return 0
    print("  CN3 com erro — ver acima.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
