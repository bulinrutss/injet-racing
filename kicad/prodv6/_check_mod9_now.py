#!/usr/bin/env python3
"""Checagem MOD9 — drivers on-board; RL1-3/CN3 = relé externo (ignorar footprint RL)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from _check_mod6_now import parse_graph, rot_pt, fp_pad  # noqa: E402
from _review_routes import _pt_key  # noqa: E402
import jl32_pinout as jl  # noqa: E402

PCB = ROOT / "injet-racing-prodv6.kicad_pcb"
EXTERNAL_Y = 200.0  # RL/CN3 abaixo disso = fora da placa montada

CHANNELS = [
    ("RL1", "GRL1", "RL_MAIN", "L22I", "Q20", "R50", "R55", "D20", 3),
    ("RL2", "GRL2", "RL_PUMP", "L23I", "Q21", "R51", "R56", "D21", 2),
    ("RL3", "GRL3", "RL_IAC", "L22O", "Q22", "R52", "R57", "D22", 1),
]


def fp_positions(text: str) -> dict[str, tuple[float, float, float]]:
    out: dict[str, tuple[float, float, float]] = {}
    for fp in re.finditer(r"\(footprint[\s\S]*?\n\t\)", text):
        block = fp.group(0)
        ref_m = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', block)
        at_m = re.search(r"\(at\s+([\d.-]+)\s+([\d.-]+)(?:\s+([\d.-]+))?", block)
        if ref_m and at_m:
            rot = float(at_m.group(3)) if at_m.group(3) else 0.0
            out[ref_m.group(1)] = (float(at_m.group(1)), float(at_m.group(2)), rot)
    return out


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
    pm = re.search(
        rf'\(pad\s+"{re.escape(pad)}"[\s\S]*?\(at\s+([\d.-]+)\s+([\d.-]+)[\s\S]*?\(net\s+"([^"]+)"\)',
        block,
    )
    if not pm:
        return None
    px, py, net = float(pm.group(1)), float(pm.group(2)), pm.group(3)
    return (*rot_pt(ox, oy, rot, px, py), net)


def cn3_pad(n: int) -> tuple[float, float] | None:
    blk = fp_block(PCB.read_text(encoding="utf-8"), "CN3")
    if not blk:
        return None
    at_m = re.search(r"\(at\s+([\d.-]+)\s+([\d.-]+)", blk)
    if not at_m:
        return None
    ox, oy = float(at_m.group(1)), float(at_m.group(2))
    pm = re.search(rf'\(pad\s+"{n}"[\s\S]*?\(at\s+([\d.-]+)\s+([\d.-]+)', blk)
    if not pm:
        return None
    return (ox + float(pm.group(1)), oy + float(pm.group(2)))


def same_net(g, net: str, a: tuple[float, float], b: tuple[float, float]) -> bool:
    return g.connected(net, _pt_key(*a), _pt_key(*b))


def main() -> int:
    text = PCB.read_text(encoding="utf-8")
    g = parse_graph(text)
    fps = fp_positions(text)
    ok = True

    print("PCB MOD9 — drivers on-board · RL1-3 NAO montados · CN3 = chicote cargas\n")

    for rl in ["RL1", "RL2", "RL3"]:
        if rl in fps and fps[rl][1] >= EXTERNAL_Y:
            print(f"  {rl} @ y={fps[rl][1]:.1f} — externo (nao montar)")

    if "CN3" in fps:
        print(f"  CN3 @ {fps['CN3'][:2]} — conector PCIe-6 cargas\n")

    print("=== U1 pads GRL ===")
    u1 = fp_block(text, "U1")
    for grl, pad in jl.U1_REL_PAD.items():
        net = re.search(rf'pad "{pad}"[\s\S]*?net "([^"]+)"', u1 or "")
        n = net.group(1) if net else "?"
        pt = jl.u1_pad_xy(pad)
        mark = "OK" if n == grl else f"ERR ({n})"
        print(f"  {pad} {grl} @ {pt}: {mark}")
        if n != grl:
            ok = False

    print("\n=== Por canal (driver only) ===")
    for coil, grl, out_net, u1_pad, q, rg, rpd, d, cn3_n in CHANNELS:
        print(f"\n  --- {coil} / {grl} / {u1_pad} -> CN3-{cn3_n} {out_net} ---")
        qb, rgb, rpdb, db = fp_block(text, q), fp_block(text, rg), fp_block(text, rpd), fp_block(text, d)
        if not all([qb, rgb, rpdb, db]):
            print("    FALTA footprint driver")
            ok = False
            continue

        qg, qd, qs = pad_abs(qb, "G"), pad_abs(qb, "D"), pad_abs(qb, "S")
        rga, rgb_b = pad_abs(rgb, "A"), pad_abs(rgb, "B")
        rpda, rpdb_b = pad_abs(rpdb, "A"), pad_abs(rpdb, "B")
        da, dk = pad_abs(db, "A"), pad_abs(db, "K")
        u1_pt = jl.u1_pad_xy(u1_pad)

        mcu = rga and same_net(g, grl, u1_pt, (rga[0], rga[1]))
        gate = (
            rgb_b and rpda and qg
            and same_net(g, grl, (rgb_b[0], rgb_b[1]), (qg[0], qg[1]))
            and same_net(g, grl, (rpda[0], rpda[1]), (qg[0], qg[1]))
        )
        gnd = qs and qs[2] == "GND" and rpdb_b and rpdb_b[2] == "GND"
        drain = qd and da and same_net(g, coil, (qd[0], qd[1]), (da[0], da[1]))
        fly = dk and dk[2] == "+12V_PROT"

        cn3_pt = cn3_pad(cn3_n)
        cn_ok = cn3_pt and same_net(g, out_net, cn3_pt, cn3_pt)

        # out_net must exist on CN3 pad (graph has at least pad node)
        cn3_blk = fp_block(text, "CN3")
        cn_net = pad_abs(cn3_blk, str(cn3_n))[2] if cn3_blk else None
        cn_net_ok = cn_net == out_net

        print(f"    {u1_pad} -> {rg}.A: {'OK' if mcu else 'FALHA'}")
        print(f"    gate {rg}.B = {rpd}.A = {q}.G: {'OK' if gate else 'FALHA'}")
        print(f"    {q}.S + {rpd}.B -> GND: {'OK' if gnd else 'FALHA'}")
        print(f"    {q}.D = {d}.A net {coil}: {'OK' if drain else 'FALHA'}")
        print(f"    {d}.K -> +12V_PROT: {'OK' if fly else 'FALHA'}")
        print(f"    CN3-{cn3_n} net {out_net}: {'OK' if cn_net_ok else 'FALHA'}")
        print(f"    bobina ext: +12V_PROT + net {coil} no {q}.D (sem RL on-board)")

        if not all([mcu, gate, gnd, drain, fly, cn_net_ok]):
            ok = False

    print("\n=== Resultado ===")
    if ok:
        print("  MOD9 OK — drivers + CN3. Montar relé SRD no chicote externo.")
        return 0
    print("  MOD9 com pendencias.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
