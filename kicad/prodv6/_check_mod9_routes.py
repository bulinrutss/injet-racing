#!/usr/bin/env python3
"""Checagem MOD9 — conectividade das rotas (sem U1 / sem CN1)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from _check_mod6_now import fp_positions, parse_graph, rot_pt  # noqa: E402
from _review_routes import _pt_key  # noqa: E402

PCB = ROOT / "injet-racing-prodv6.kicad_pcb"

CHANNELS = [
    ("RL1", "GRL1", "RL_MAIN", "Q20", "R50", "R55", "D20", "RL1"),
    ("RL2", "GRL2", "RL_PUMP", "Q21", "R51", "R56", "D21", "RL2"),
    ("RL3", "GRL3", "RL_IAC", "Q22", "R52", "R57", "D22", "RL3"),
]


def fp_block(text: str, ref: str) -> str | None:
    for fp in re.finditer(r"\(footprint[\s\S]*?\n\t\)", text):
        if re.search(rf'\(property\s+"Reference"\s+"{ref}"', fp.group(0)):
            return fp.group(0)
    return None


def pad_abs(block: str, pad: str) -> tuple[float, float, str] | None:
    at_m = re.search(r"\(at\s+([\d.-]+)\s+([\d.-]+)(?:\s+([\d.-]+))?", block)
    if not at_m:
        return None
    ox, oy = float(at_m.group(1)), float(at_m.group(2))
    rot = float(at_m.group(3)) if at_m.group(3) else 0.0
    for pm in re.finditer(
        rf'\(pad\s+"{re.escape(pad)}"[\s\S]*?\(at\s+([\d.-]+)\s+([\d.-]+)[\s\S]*?\(net\s+"([^"]+)"\)',
        block,
    ):
        px, py = float(pm.group(1)), float(pm.group(2))
        return (*rot_pt(ox, oy, rot, px, py), pm.group(3))
    return None


def same_net(g, net: str, a: tuple[float, float], b: tuple[float, float]) -> bool:
    return g.connected(net, _pt_key(*a), _pt_key(*b))


def main() -> int:
    text = PCB.read_text(encoding="utf-8")
    g = parse_graph(text)
    ok = True

    print("=== MOD9 posicoes (PCB real) ===")
    fps = fp_positions(text)
    for ref in ["Q20", "Q21", "Q22", "RL1", "RL2", "RL3"]:
        if ref in fps:
            print(f"  {ref}: {fps[ref]}")

    print("\n=== Por canal (driver + bobina + flyback + contato NO) ===")
    for coil, grl, out_net, q, rg, rpd, d, rl in CHANNELS:
        print(f"\n  --- {coil} / {grl} -> {out_net} ---")
        qb = fp_block(text, q)
        rgb = fp_block(text, rg)
        rpdb = fp_block(text, rpd)
        db = fp_block(text, d)
        rlb = fp_block(text, rl)
        if not all([qb, rgb, rpdb, db, rlb]):
            print("    FALTA footprint")
            ok = False
            continue

        qg = pad_abs(qb, "G")
        qd = pad_abs(qb, "D")
        qs = pad_abs(qb, "S")
        rga = pad_abs(rgb, "A")
        rgb_b = pad_abs(rgb, "B")
        rpda = pad_abs(rpdb, "A")
        rpdb_b = pad_abs(rpdb, "B")
        da = pad_abs(db, "A")
        dk = pad_abs(db, "K")
        rl_p1 = pad_abs(rlb, "1")
        rl_p2 = pad_abs(rlb, "2")
        rl_p3 = pad_abs(rlb, "3")
        rl_p4 = pad_abs(rlb, "4")

        gate = (
            rga and rgb_b and qg and rpda
            and same_net(g, grl, (rga[0], rga[1]), (qg[0], qg[1]))
            and same_net(g, grl, (rgb_b[0], rgb_b[1]), (qg[0], qg[1]))
            and same_net(g, grl, (rpda[0], rpda[1]), (qg[0], qg[1]))
        )
        gnd = qs and rpdb_b and qs[2] == "GND" and rpdb_b[2] == "GND"
        drain = (
            qd and da and rl_p2
            and same_net(g, coil, (qd[0], qd[1]), (da[0], da[1]))
            and same_net(g, coil, (qd[0], qd[1]), (rl_p2[0], rl_p2[1]))
        )
        fly = dk and dk[2] == "+12V_PROT"
        pwr = rl_p1 and rl_p3 and rl_p1[2] == rl_p3[2] == "+12V_PROT"
        out_ok = rl_p4 and rl_p4[2] == out_net

        print(f"    gate ({rg} + {rpd} -> {q}.G): {'OK' if gate else 'FALTA'}")
        print(f"    GND ({q}.S + {rpd}.B): {'OK (zone)' if gnd else 'FALTA'}")
        print(f"    bobina ({q}.D + {d}.A + {rl}.2) net {coil}: {'OK' if drain else 'FALTA'}")
        print(f"    flyback {d}.K -> +12V_PROT: {'OK' if fly else 'FALTA'}")
        print(f"    {rl}.1 + {rl}.3 -> +12V_PROT: {'OK' if pwr else 'FALTA'}")
        print(f"    {rl}.4 net {out_net} (stub CN1 depois): {'OK' if out_ok else 'FALTA'}")

        if not gate or not gnd or not drain or not fly or not pwr or not out_ok:
            ok = False

    # Tronco +12V entre canais (amostra)
    print("\n=== Tronco +12V_PROT (amostra) ===")
    d20 = fp_block(text, "D20")
    rl1 = fp_block(text, "RL1")
    if d20 and rl1:
        k = pad_abs(d20, "K")
        p1 = pad_abs(rl1, "1")
        if k and p1:
            tr = same_net(g, "+12V_PROT", (k[0], k[1]), (p1[0], p1[1]))
            print(f"  D20.K <-> RL1.1: {'OK' if tr else 'FALTA (ilha +12V?)'}")
            if not tr:
                ok = False

    print("\n=== Pendente (nao exigido agora) ===")
    print("  U1 L22I/L23I/L22O -> GRL1/2/3")
    print("  CN3 pads 1-3 -> RL_MAIN/RL_PUMP/RL_IAC")

    print("\n=== Resultado ===")
    if ok:
        print("  MOD9 bloco OK (3 canais internos). Pode seguir MOD10 CAN.")
        return 0
    print("  MOD9 com ilhas — ver FALTA acima.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
