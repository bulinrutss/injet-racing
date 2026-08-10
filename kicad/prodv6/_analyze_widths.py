#!/usr/bin/env python3
"""Analisa larguras de trilha no .kicad_pcb vs regras prodv6."""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from pathlib import Path

PCB = Path(__file__).parent / "injet-racing-prodv6.kicad_pcb"

RULES = {
    "+12V": 1.2,
    "+12V_PROT": 1.2,
    "+12V_BAT": 1.2,
    "+12V_IN": 1.2,
    "+5V": 1.0,
    "+3V3": 1.0,
    "GND": 0.8,
}
LOAD = ("INJ1", "INJ2", "INJ3", "INJ4", "RL_MAIN", "RL_PUMP", "RL_IAC", "RL1", "RL2", "RL3")
SIG_MIN = 0.5


def main() -> None:
    t = PCB.read_text(encoding="utf-8")
    pat = re.compile(
        r"\(segment\s+\(start\s+([\d.-]+)\s+([\d.-]+)\)\s+\(end\s+([\d.-]+)\s+([\d.-]+)\)\s+"
        r"\(width\s+([\d.-]+)\)\s+\(layer\s+\"([^\"]+)\"\)\s+\(net\s+\"([^\"]+)\"\)",
    )
    min_w: dict[str, float] = defaultdict(lambda: 999.0)
    issues: list[tuple[float, str, str, str, float, float]] = []
    seg_count = 0

    for m in pat.finditer(t):
        seg_count += 1
        x1, y1, x2, y2 = map(float, m.groups()[:4])
        w = float(m.group(5))
        layer = m.group(6)
        net = m.group(7)
        min_w[net] = min(min_w[net], w)

        if net in RULES and w < RULES[net] - 0.01:
            issues.append((w, net, layer, f"< {RULES[net]} mm (pot)", x1, y1))
        elif net in LOAD[:4] and w < 0.8:
            issues.append((w, net, layer, "inj < 0.8 mm", x1, y1))
        elif net in LOAD[4:] and w < 1.0:
            issues.append((w, net, layer, "relé NO < 1.0 mm", x1, y1))
        elif w < 0.35 and net not in RULES and net != "GND":
            issues.append((w, net, layer, "sinal < 0.35 mm", x1, y1))

    print(f"PCB: {PCB.name}  segmentos: {seg_count}\n")

    print("=== Min largura — potência / carga ===")
    for net in sorted(RULES.keys()):
        if min_w[net] < 900:
            ok = "OK" if min_w[net] >= RULES[net] - 0.01 else "FINO"
            print(f"  {net:12} min {min_w[net]:.2f} mm  (regra {RULES[net]})  {ok}")
    for net in LOAD:
        if min_w[net] < 900:
            print(f"  {net:12} min {min_w[net]:.2f} mm")

    print("\n=== Problemas reais (potência/carga abaixo da regra) ===")
    power_issues = [i for i in issues if "pot" in i[3] or "inj" in i[3] or "relé" in i[3]]
    power_issues.sort(key=lambda x: (x[1], x[0]))
    by_net = Counter(i[1] for i in power_issues)
    for net, n in by_net.most_common():
        print(f"  {net}: {n} trecho(s) fino(s), min {min(i[0] for i in power_issues if i[1]==net):.2f} mm")
    for w, net, layer, why, x, y in power_issues[:12]:
        print(f"    {w:.2f} mm  {net}  {layer}  @ ({x:.1f},{y:.1f})  {why}")

    print("\n=== Sinal < 0.35 mm (stubs curtos — revisar se tronco OK) ===")
    sig = [i for i in issues if "sinal" in i[3]]
    by_sig = Counter(i[1] for i in sig)
    for net, n in by_sig.most_common(12):
        mw = min(i[0] for i in sig if i[1] == net)
        print(f"  {net}: {n} seg, min {mw:.2f} mm")

    print("\n=== Todos os segmentos 0.30 mm ===")
    thin30 = []
    for m in pat.finditer(t):
        w = float(m.group(5))
        if abs(w - 0.3) < 0.001:
            thin30.append((m.group(7), m.group(6), *map(float, m.groups()[:4])))
    for net, layer, x1, y1, x2, y2 in thin30:
        print(f"  {net:12} {layer:5} ({x1:.1f},{y1:.1f})-({x2:.1f},{y2:.1f})")

    print("\n=== +5V abaixo de 1.0 mm ===")
    for m in pat.finditer(t):
        if m.group(7) != "+5V":
            continue
        w = float(m.group(5))
        if w < 0.99:
            x1, y1, x2, y2 = map(float, m.groups()[:4])
            print(f"  {w:.2f} mm {m.group(6)} ({x1:.1f},{y1:.1f})-({x2:.1f},{y2:.1f})")


if __name__ == "__main__":
    main()
