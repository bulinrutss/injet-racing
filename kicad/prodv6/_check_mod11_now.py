#!/usr/bin/env python3
"""Checagem MOD11 — lambda MCP6004 + OPA388IDR (PCB 2026-08-11)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from _check_mod6_now import fp_pad, parse_graph, rot_pt  # noqa: E402
from _review_routes import _pt_key  # noqa: E402
import jl32_pinout as jl  # noqa: E402

PCB = ROOT / "injet-racing-prodv6.kicad_pcb"

U4_PADS = {"1": "VM", "2": "VM", "3": "VM", "4": "GND", "5": "UN", "6": "UN", "7": "UN", "14": "+5V"}
U5_PADS = {"2": "IP", "3": "VM", "4": "GND", "6": "IP", "7": "+5V"}

PASSIVE_NETS = {
    "R70": ("A", "IP", "B", "VM"),
    "R71": ("A", "UN", "B", "RI_PULSE"),
    "R76": ("A", "+3V3", "B", "VM"),
    "R77": ("A", "VM", "B", "GND"),
    "R78": ("A", "UN", "B", "RI_PULSE"),
    "C30": ("A", "IP", "B", "GND"),
    "C31": ("A", "UN", "B", "GND"),
    "C32": ("A", "+5V", "B", "GND"),
    "C33": ("A", "+5V", "B", "GND"),
}

CN2_NETS = {1: "+12V_PROT", 2: "H-", 4: "IP", 5: "VM", 6: "UN"}  # pad3 NC


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


def pad_net(block: str, pad: str) -> str | None:
    pm = re.search(rf'\(pad\s+"{re.escape(pad)}"[\s\S]*?\(net\s+"([^"]+)"\)', block)
    return pm.group(1) if pm else None


def cn2_pad(n: int, text: str) -> tuple[float, float] | None:
    blk = fp_block(text, "CN2")
    if not blk:
        return None
    at_m = re.search(r"\(at\s+([\d.-]+)\s+([\d.-]+)(?:\s+([\d.-]+))?", blk)
    if not at_m:
        return None
    ox, oy = float(at_m.group(1)), float(at_m.group(2))
    rot = float(at_m.group(3)) if at_m.group(3) else 0.0
    pm = re.search(rf'\(pad\s+"{n}"[\s\S]*?\(at\s+([\d.-]+)\s+([\d.-]+)', blk)
    if not pm:
        return None
    return rot_pt(ox, oy, rot, float(pm.group(1)), float(pm.group(2)))


def same_net(g, net: str, a: tuple[float, float], b: tuple[float, float]) -> bool:
    return g.connected(net, _pt_key(*a), _pt_key(*b))


def main() -> int:
    text = PCB.read_text(encoding="utf-8")
    g = parse_graph(text)
    ok = True

    print(f"PCB MOD11 — lambda\n=== Posicoes ===")
    for ref in ["U4", "U5", "CN2", "R70", "R71", "R76", "R77", "R78", "C30", "C31", "C32", "C33"]:
        print(f"  {ref}: {fp_positions(text).get(ref, 'AUSENTE')}")

    print("\n=== U4 MCP6004 ===")
    u4 = fp_block(text, "U4")
    if not u4:
        ok = False
    else:
        for pad, want in U4_PADS.items():
            net = pad_net(u4, pad)
            mark = "OK" if net == want else f"ERR ({net})"
            print(f"  U4.{pad} -> {want}: {mark}")
            if net != want:
                ok = False

    print("\n=== U5 OPA388IDR B.Cu ===")
    u5 = fp_block(text, "U5")
    if not u5:
        ok = False
    else:
        for pad, want in U5_PADS.items():
            net = pad_net(u5, pad)
            mark = "OK" if net == want else f"ERR ({net})"
            print(f"  U5.{pad} -> {want}: {mark}")
            if net != want:
                ok = False

    print("\n=== Passivos ===")
    for ref, spec in PASSIVE_NETS.items():
        blk = fp_block(text, ref)
        if not blk:
            print(f"  FALTA {ref}")
            ok = False
            continue
        for i in range(0, len(spec), 2):
            pad, want = spec[i], spec[i + 1]
            net = pad_net(blk, pad)
            mark = "OK" if net == want else f"ERR ({net})"
            print(f"  {ref}.{pad} -> {want}: {mark}")
            if net != want:
                ok = False

    print("\n=== CN2 ===")
    cn2 = fp_block(text, "CN2")
    for pin, want in CN2_NETS.items():
        net = pad_net(cn2, str(pin)) if cn2 else None
        mark = "OK" if net == want else f"ERR ({net})"
        print(f"  CN2-{pin} -> {want}: {mark}")
        if net != want:
            ok = False

    print("\n=== U1 pads lambda ===")
    u1 = fp_block(text, "U1")
    u1_map = {
        "VM": jl.U1_LAMBDA_PAD["VM"],
        "IP": jl.U1_LAMBDA_PAD["IP"],
        "UN": jl.U1_LAMBDA_PAD["UN"],
        "RI_PULSE": jl.U1_LAMBDA_PAD["RI_PULSE"],
    }
    u1_pts = {}
    for net, pad in u1_map.items():
        pn = pad_net(u1, pad) if u1 else None
        pt = jl.u1_pad_xy(pad)
        u1_pts[net] = pt
        mark = "OK" if pn == net else f"ERR ({pn})"
        print(f"  {pad} {net} @ {pt}: {mark}")
        if pn != net:
            ok = False
    bypass = pad_net(u1, jl.U1_TRACE_BYPASS["IP"]) if u1 else None
    print(f"  {jl.U1_TRACE_BYPASS['IP']} IP trilha bypass: {bypass or 'NC'}")

    print("\n=== Conectividade ===")
    u4_vm = fp_pad(text, "U4", "1") or fp_pad(text, "U4", "2")
    cn2_vm = cn2_pad(5, text)
    vm_ok = u4_vm and cn2_vm and same_net(g, "VM", u4_vm, cn2_vm)
    vm_mcu = same_net(g, "VM", u1_pts["VM"], u4_vm) if u4_vm else False
    print(f"  R13I -> U4 VM -> CN2-5: {'OK' if vm_mcu and vm_ok else 'FALHA'}")

    u5_ip = fp_pad(text, "U5", "6")
    cn2_ip = cn2_pad(4, text)
    ip_ok = cn2_ip and same_net(g, "IP", u1_pts["IP"], cn2_ip)
    print(f"  R13O -> IP -> CN2-4: {'OK' if ip_ok else 'FALHA'}")

    u4_un = fp_pad(text, "U4", "5")
    cn2_un = cn2_pad(6, text)
    un_ok = u4_un and cn2_un and same_net(g, "UN", u1_pts["UN"], cn2_un)
    print(f"  R14I -> U4 UN -> CN2-6: {'OK' if un_ok else 'FALHA'}")

    r71b = fp_pad(text, "R71", "B")
    r78b = fp_pad(text, "R78", "B")
    ri_ok = r71b and same_net(g, "RI_PULSE", u1_pts["RI_PULSE"], r71b)
    ri78 = r78b and r71b and same_net(g, "RI_PULSE", r78b, r71b)
    print(f"  R5I -> R71 (RI_PULSE): {'OK' if ri_ok else 'FALHA'}")
    print(f"  R78 -> R71 RI_PULSE: {'OK' if ri78 else 'FALHA (ilha?)'}")

    r70a = fp_pad(text, "R70", "A")
    r70b = fp_pad(text, "R70", "B")
    r70_ip = r70a and same_net(g, "IP", r70a, u1_pts["IP"])
    r70_vm = r70b and same_net(g, "VM", r70b, u4_vm)
    print(f"  R70 shunt IP-VM: IP-side={'OK' if r70_ip else 'FALHA'} VM-side={'OK' if r70_vm else 'FALHA'}")

    core = vm_mcu and vm_ok and ip_ok and un_ok and ri_ok
    if not core or not r70_ip or not ri78:
        ok = False

    print("\n=== Resultado ===")
    if ok:
        print("  MOD11 completo.")
        return 0
    print("  MOD11 com pendencias.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
