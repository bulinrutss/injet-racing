#!/usr/bin/env python3
"""Reaplica trilhas MOD6 (sens_traces) no PCB — preserva footprints e resto da placa."""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


gen = _load("gen", ROOT / "_gen_kicad_prodv6.py")
layout = _load("layout", ROOT / "prodv6_layout.py")

SENSOR_NETS = {"IAT", "CLT", "MAP", "TPS", "VBAT"}
MOD6_POWER = {"+3V3", "+5V", "+12V_PROT"}
X0, Y0, X1, Y1 = layout.MOD6_IO["body"]


def _strip_zone(x: float, y: float, net: str) -> bool:
    if net in SENSOR_NETS:
        return (X0 - 2 <= x <= 136 and Y0 - 2 <= y <= Y1 + 2) or (128 <= x <= 133 and 60 <= y <= 96)
    if net in MOD6_POWER:
        return X0 - 2 <= x <= X1 + 2 and Y0 - 10 <= y <= Y1 + 2
    return False


def main() -> None:
    pcb = ROOT / "injet-racing-prodv6.kicad_pcb"
    text = pcb.read_text(encoding="utf-8")

    seg_re = re.compile(r"\t\(segment\n.*?\n\t\)\n", re.DOTALL)
    removed = 0

    def _keep(m: re.Match) -> str:
        nonlocal removed
        block = m.group(0)
        net_m = re.search(r'\(net "([^"]+)"\)', block)
        if not net_m:
            return block
        net = net_m.group(1)
        if net not in SENSOR_NETS and net not in MOD6_POWER:
            return block
        coords = re.findall(r"\(start ([\d.]+) ([\d.]+)\)|\(end ([\d.]+) ([\d.]+)\)", block)
        pts = [(float(a or c), float(b or d)) for a, b, c, d in coords]
        if all(_strip_zone(x, y, net) for x, y in pts):
            removed += 1
            return ""
        return block

    text = seg_re.sub(_keep, text)

    segs = "\n".join(gen.fmt_pcb(s, 1) for s in layout.sens_traces())
    zanchor = '\t(zone\n\t\t(net "GND")\n\t\t(layer "F.Cu")'
    if zanchor not in text:
        raise SystemExit("ancora zone GND nao encontrada")
    text = text.replace(zanchor, segs + "\n" + zanchor, 1)

    pcb.write_text(text, encoding="utf-8")
    print(f"  MOD6 trilhas atualizadas ({removed} segmento(s) removido(s))")


if __name__ == "__main__":
    main()
