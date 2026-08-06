#!/usr/bin/env python3
"""
INJET RACING ECU — KiCad prodv4 (patch do prodv3 editado pelo usuário)

Parte de kicad/injet-racing-prodv3.kicad_pcb (layout KiCad 10 salvo),
atribui nets nos pads, corrige SWD, fecha gaps do DRC.rpt e grava prodv4.

Uso: python _gen_kicad_prodv4.py
"""
from __future__ import annotations

import importlib.util
import json
import math
import sys
import uuid
from pathlib import Path
from typing import Any

from sexpdata import Symbol, dumps, loads

ROOT = Path(__file__).resolve().parent
SRC_PCB = ROOT / "injet-racing-prodv3.kicad_pcb"
PROJECT = "injet-racing-prodv4"
GENERATOR = "injet-racing-gen"
GENERATOR_VERSION = "1.1-prodv4-patch"

S = Symbol


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


pcb_nets = _load_module("pcb_prodv4", ROOT.parent / "assets" / "_gen_pcb_prodv4.py")
pcb_v2 = _load_module("pcb_prodv2", ROOT.parent / "assets" / "_gen_pcb_prodv2.py")

REF_TO_PREFIX: dict[str, str] = {
    "CN1": "CN1",
    "CN2": "CN2",
    "U1": "MCU",
    "U2": "BUCK",
    "U3": "LDO",
    "U4": "U6004",
    "U5": "U8628",
    "U6": "CAN",
    "U7": "U817",
    "U8": "U8",
    "Q1": "QREV",
    "Q10": "QINJ1",
    "Q11": "QINJ2",
    "Q12": "QINJ3",
    "Q13": "QINJ4",
    "Q30": "QHEAT",
    "Q20": "QRL1",
    "Q21": "QRL2",
    "Q22": "QRL3",
    "J1": "SWD",
}


def _is_sym(node: Any, name: str) -> bool:
    return isinstance(node, list) and len(node) >= 1 and node[0] == S(name)


def _uid() -> str:
    return str(uuid.uuid4())


def _net_name(node: list | None) -> str | None:
    if node is None:
        return None
    if len(node) == 2:
        return str(node[1])
    if len(node) >= 3:
        return str(node[2])
    return ""


def _set_net(node: list, net: str) -> None:
    for i, sub in enumerate(node):
        if _is_sym(sub, "net"):
            if len(sub) == 2:
                node[i] = [S("net"), net]
            else:
                node[i] = [S("net"), sub[1], net]
            return
    insert_at = len(node)
    for i, sub in enumerate(node):
        if _is_sym(sub, "uuid"):
            insert_at = i
            break
    node.insert(insert_at, [S("net"), net])


def _get_fp_ref(fp: list) -> str:
    for sub in fp:
        if _is_sym(sub, "property") and len(sub) > 2 and sub[1] == "Reference":
            return str(sub[2])
    return ""


def _get_fp_lib_name(fp: list) -> str:
    if len(fp) > 1:
        return str(fp[1])
    return ""


def _pad_layout_key(ref: str, pin: str, fp_lib: str) -> str:
    prefix = REF_TO_PREFIX.get(ref)
    if not prefix:
        if ref and ref[0] in "RCDL":
            prefix = ref
        else:
            prefix = fp_lib.split(":", 1)[-1] if ":" in fp_lib else ref
    return f"{prefix}.{pin}"


def _build_pad_net_map() -> dict[str, str]:
    out: dict[str, str] = dict(pcb_nets.STATIC_PAD_NETS)
    for i, net in pcb_v2.CN1_PAD_NETS.items():
        out[f"CN1.{i}"] = net
    for i, net in pcb_v2.CN2_PAD_NETS.items():
        if net:
            out[f"CN2.{i}"] = net

    gnd_exact = {
        "BUCK.GND", "LDO.GND", "CAN.GND", "U817.2", "U817.3", "U8628.4", "U6004.4",
        "SWD.4", "MCU.R2", "R1.B", "D2.K", "C1.B", "C2.B", "C3.B", "C4.B",
        "C10.B", "C11.B", "C12.B", "C13.B", "C20.B", "C30.B", "C31.B", "C32.B", "C33.B",
        "R43.B", "U8.GND", "QREV.S",
    }
    for key in gnd_exact:
        out[key] = "GND"
    for prefix in ("QINJ1", "QINJ2", "QINJ3", "QINJ4", "QHEAT", "QRL1", "QRL2", "QRL3"):
        out[f"{prefix}.S"] = "GND"
    for n in range(1, 40):
        out.setdefault(f"C{n}.B", "GND")

    extras = {
        "R40.B": "IAT", "R41.B": "CLT", "R42.B": "MAP", "R53.B": "TPS",
        "R50.B": "IAT", "R51.B": "CLT", "R52.B": "MAP", "R54.B": "TPS",
        "R10.B": "GINJ1", "R11.B": "GINJ2", "R12.B": "GINJ3", "R13.B": "GINJ4",
        "R30.B": "GRL1", "R31.B": "GRL2", "R32.B": "GRL3",
        "R61.B": "RPM_IN", "R62.B": "RPM_OUT",
        "R76.A": "VM", "R77.A": "VM", "R78.B": "RI_PULSE",
        "R20.A": "GINJ1", "R21.A": "GINJ2", "R22.A": "GINJ3", "R23.A": "GINJ4",
        "R25.A": "GHEAT", "R15.B": "GHEAT",
        "D10.A": "INJ1", "D11.A": "INJ2", "D12.A": "INJ3", "D13.A": "INJ4",
        "D14.A": "INJ1", "D20.A": "RL1", "D21.A": "RL2", "D22.A": "RL3",
        "QINJ1.G": "GINJ1", "QINJ2.G": "GINJ2", "QINJ3.G": "GINJ3", "QINJ4.G": "GINJ4",
        "QINJ1.D": "INJ1", "QINJ2.D": "INJ2", "QINJ3.D": "INJ3", "QINJ4.D": "INJ4",
        "QHEAT.G": "GHEAT", "QRL1.G": "GRL1", "QRL2.G": "GRL2", "QRL3.G": "GRL3",
        "QREV.D": "+12V_PROT", "QREV.S": "GND",
        "BUCK.VIN": "+12V_IN", "BUCK.GND": "GND",
        "LDO.GND": "GND",
        "U817.1": "RI_PULSE", "U817.4": "RPM_OUT",
        "U6004.1": "DAC_VM", "U8628.2": "DAC_VM", "U8628.5": "DAC_VM",
        "CAN.GND": "GND",
    }
    out.update(extras)
    return out


PAD_NET_MAP = _build_pad_net_map()


def _assign_pad_nets(tree: list) -> tuple[int, int]:
    assigned = updated = 0
    for item in tree:
        if not _is_sym(item, "footprint"):
            continue
        ref = _get_fp_ref(item)
        lib = _get_fp_lib_name(item)
        for sub in item:
            if not _is_sym(sub, "pad"):
                continue
            pin = str(sub[1])
            key = _pad_layout_key(ref, pin, lib)
            want = PAD_NET_MAP.get(key)
            if not want:
                continue
            cur = None
            for psub in sub:
                if _is_sym(psub, "net"):
                    cur = _net_name(psub)
            if cur is None or cur == "":
                _set_net(sub, want)
                assigned += 1
            elif cur != want and key.startswith("MCU."):
                _set_net(sub, want)
                updated += 1
    return assigned, updated


def _point_key(x: float, y: float, layer: str) -> tuple[int, int, str]:
    return (round(x * 100), round(y * 100), layer)


def _read_xy(node: list) -> tuple[float, float]:
    return float(node[1]), float(node[2])


def _read_segment(item: list) -> tuple[tuple[float, float], tuple[float, float], str, str, list]:
    start = end = (0.0, 0.0)
    layer = ""
    net = ""
    for sub in item:
        if _is_sym(sub, "start"):
            start = _read_xy(sub)
        elif _is_sym(sub, "end"):
            end = _read_xy(sub)
        elif _is_sym(sub, "layer"):
            layer = str(sub[1])
        elif _is_sym(sub, "net"):
            net = _net_name(sub) or ""
    return start, end, layer, net, item


def _propagate_segment_nets(tree: list) -> int:
    """Preenche (net \"\") em segmentos conectados a trilhas/pads com net."""
    segments: list[tuple[tuple[float, float], tuple[float, float], str, str, list]] = []
    vias: list[tuple[float, float, str, list]] = []
    pad_pts: list[tuple[float, float, str, str]] = []

    for item in tree:
        if _is_sym(item, "segment"):
            segments.append(_read_segment(item))
        elif _is_sym(item, "via"):
            x = y = 0.0
            net = ""
            for sub in item:
                if _is_sym(sub, "at"):
                    x, y = _read_xy(sub)
                elif _is_sym(sub, "net"):
                    net = _net_name(sub) or ""
            vias.append((x, y, net, item))

    for item in tree:
        if not _is_sym(item, "footprint"):
            continue
        ox = oy = 0.0
        for sub in item:
            if _is_sym(sub, "at"):
                ox, oy = _read_xy(sub)
        ref = _get_fp_ref(item)
        lib = _get_fp_lib_name(item)
        for sub in item:
            if not _is_sym(sub, "pad"):
                continue
            pin = str(sub[1])
            px = py = 0.0
            for psub in sub:
                if _is_sym(psub, "at"):
                    px, py = _read_xy(psub)
            gx, gy = ox + px, oy + py
            net = PAD_NET_MAP.get(_pad_layout_key(ref, pin, lib), "")
            for psub in sub:
                if _is_sym(psub, "net"):
                    n = _net_name(psub)
                    if n:
                        net = n
            if net:
                pad_pts.append((gx, gy, "*", net))

    parent: dict[tuple, tuple] = {}

    def find(k):
        parent.setdefault(k, k)
        if parent[k] != k:
            parent[k] = find(parent[k])
        return parent[k]

    def unite(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    def near(a, b, tol=0.05):
        return abs(a[0] - b[0]) <= tol and abs(a[1] - b[1]) <= tol

    nodes: dict[tuple, str] = {}

    for start, end, layer, net, seg in segments:
        k1 = _point_key(*start, layer)
        k2 = _point_key(*end, layer)
        unite(k1, k2)
        if net:
            nodes[k1] = net
            nodes[k2] = net

    for x, y, net, _via in vias:
        kf = _point_key(x, y, "F.Cu")
        kb = _point_key(x, y, "B.Cu")
        unite(kf, kb)
        if net:
            nodes[kf] = net
            nodes[kb] = net

    for x, y, layer, net in pad_pts:
        k = _point_key(x, y, layer if layer != "*" else "F.Cu")
        kf = _point_key(x, y, "F.Cu")
        kb = _point_key(x, y, "B.Cu")
        unite(k, kf)
        unite(k, kb)
        nodes[k] = net
        nodes[kf] = net
        nodes[kb] = net

    for start, end, layer, _net, _seg in segments:
        for px, py, _l, pnet in pad_pts:
            if near(start, (px, py)) or near(end, (px, py)):
                k1 = _point_key(*start, layer)
                kp = _point_key(px, py, layer)
                unite(k1, kp)
                nodes[kp] = pnet

    comp_net: dict[tuple, str] = {}

    def comp_root(k):
        return find(k)

    for k, net in nodes.items():
        r = comp_root(k)
        if net:
            comp_net[r] = net

    changed = 0
    for start, end, layer, net, seg in segments:
        if net:
            continue
        k1 = _point_key(*start, layer)
        inferred = comp_net.get(comp_root(k1), "")
        if not inferred:
            # heurística: trilhas vazias perto de GINJ3 em B.Cu
            if layer == "B.Cu" and abs(start[1] - 96.98) < 1:
                inferred = "GINJ3"
        if inferred:
            for sub in seg:
                if _is_sym(sub, "net"):
                    if len(sub) == 2:
                        sub[1] = inferred
                    elif len(sub) >= 3:
                        sub[2] = inferred
                    changed += 1
                    break
            else:
                _set_net(seg, inferred)
                changed += 1
    return changed


def _segment_exists(tree: list, x1: float, y1: float, x2: float, y2: float, layer: str, tol: float = 0.08) -> bool:
    for item in tree:
        if not _is_sym(item, "segment"):
            continue
        ly = ""
        s = e = None
        for sub in item:
            if _is_sym(sub, "layer"):
                ly = str(sub[1])
            elif _is_sym(sub, "start"):
                s = _read_xy(sub)
            elif _is_sym(sub, "end"):
                e = _read_xy(sub)
        if ly != layer or s is None or e is None:
            continue
        if (abs(s[0] - x1) <= tol and abs(s[1] - y1) <= tol and abs(e[0] - x2) <= tol and abs(e[1] - y2) <= tol):
            return True
        if (abs(s[0] - x2) <= tol and abs(s[1] - y2) <= tol and abs(e[0] - x1) <= tol and abs(e[1] - y1) <= tol):
            return True
    return False


def _via_exists(tree: list, x: float, y: float, tol: float = 0.08) -> bool:
    for item in tree:
        if not _is_sym(item, "via"):
            continue
        for sub in item:
            if _is_sym(sub, "at"):
                vx, vy = _read_xy(sub)
                if abs(vx - x) <= tol and abs(vy - y) <= tol:
                    return True
    return False


def _trace_width(net: str) -> float:
    if net in ("+12V_PROT", "+12V_IN", "+12V"):
        return 1.2
    if net in ("+5V", "+3V3"):
        return 1.0
    if net == "GND":
        return 0.8
    return 0.75


def _make_segment(x1: float, y1: float, x2: float, y2: float, layer: str, net: str) -> list:
    return [
        S("segment"),
        [S("start"), x1, y1],
        [S("end"), x2, y2],
        [S("width"), _trace_width(net)],
        [S("layer"), layer],
        [S("net"), net],
        [S("uuid"), _uid()],
    ]


def _make_via(x: float, y: float, net: str) -> list:
    return [
        S("via"),
        [S("at"), x, y],
        [S("size"), 0.8],
        [S("drill"), 0.4],
        [S("layers"), "F.Cu", "B.Cu"],
        [S("net"), net],
        [S("uuid"), _uid()],
    ]


# Trechos para fechar os 10 unconnected_items do DRC (prodv3, 2026-08-06)
V4_DRC_CONNECTS: list[tuple[str, list[tuple[float, float]], str]] = [
    ("B.Cu", [(200, 28), (200, 157)], "+12V_PROT"),
    ("B.Cu", [(56, 14), (56, 74), (54, 74)], "RPM_IN"),
    ("B.Cu", [(100, 130), (94, 130)], "VBAT"),
    ("B.Cu", [(100, 130), (100, 126)], "VBAT"),
    ("F.Cu", [(116, 70), (116, 104), (168, 104)], "+3V3"),
    ("B.Cu", [(32, 14), (32, 142), (150, 142), (164, 50)], "+5V"),
    ("F.Cu", [(200, 60), (208, 60), (208, 14)], "IP"),
    ("F.Cu", [(192, 66), (204, 66), (204, 8)], "UN"),
    ("B.Cu", [(202, 46.54), (202, 8), (200, 8)], "VM"),
]


def _add_path_segments(tree: list, layer: str, path: list[tuple[float, float]], net: str) -> int:
    added = 0
    for i in range(len(path) - 1):
        x1, y1 = path[i]
        x2, y2 = path[i + 1]
        if abs(x1 - x2) < 0.01 and abs(y1 - y2) < 0.01:
            if not _via_exists(tree, x1, y1):
                tree.append(_make_via(x1, y1, net))
                added += 1
            continue
        if not _segment_exists(tree, x1, y1, x2, y2, layer):
            tree.append(_make_segment(x1, y1, x2, y2, layer, net))
            added += 1
    return added


def _add_drc_connects(tree: list) -> int:
    added = 0
    if not _via_exists(tree, 200, 28):
        tree.append(_make_via(200, 28, "+12V_PROT"))
        added += 1
    for layer, path, net in V4_DRC_CONNECTS:
        if len(path) == 1:
            continue
        added += _add_path_segments(tree, layer, path, net)
    return added


def _fix_swd_colocated_vias(tree: list) -> int:
    """Separa SWDIO/SWCLK: SWCLK via em (130,78.92), trilha B.Cu alinhada."""
    fixes = 0
    swclk_via = None
    swclk_b_seg = None
    for item in tree:
        if _is_sym(item, "via"):
            x = y = 0.0
            net = ""
            for sub in item:
                if _is_sym(sub, "at"):
                    x, y = _read_xy(sub)
                elif _is_sym(sub, "net"):
                    net = _net_name(sub) or ""
            if net == "SWCLK" and abs(x - 128) < 0.1 and abs(y - 80) < 0.1:
                swclk_via = item
        elif _is_sym(item, "segment"):
            start, end, layer, net, _seg = _read_segment(item)
            if net == "SWCLK" and layer == "B.Cu" and abs(start[0] - 128) < 0.1 and abs(start[1] - 80) < 0.1:
                swclk_b_seg = item

    if swclk_via:
        for sub in swclk_via:
            if _is_sym(sub, "at"):
                sub[1] = 130.0
                sub[2] = 78.92
                fixes += 1
    if swclk_b_seg:
        for sub in swclk_b_seg:
            if _is_sym(sub, "start"):
                sub[1] = 130.0
                sub[2] = 78.92
                fixes += 1
    if swclk_via and not _segment_exists(tree, 130, 78.92, 130, 79, "F.Cu"):
        tree.append(_make_segment(130, 78.92, 130, 79, "F.Cu", "SWCLK"))
        fixes += 1
    return fixes


def _update_generator_meta(tree: list) -> None:
    for i, sub in enumerate(tree):
        if _is_sym(sub, "generator"):
            tree[i] = [S("generator"), GENERATOR]
        elif _is_sym(sub, "generator_version"):
            tree[i] = [S("generator_version"), GENERATOR_VERSION]


def _fmt_atom(val: Any) -> str:
    if isinstance(val, Symbol):
        return str(val)
    if isinstance(val, float):
        s = f"{val:g}"
        return s
    return dumps([val])[1:-1]


def fmt_pcb(node: Any, depth: int = 0) -> str:
    tab = "\t"
    pad = tab * depth
    if not isinstance(node, list):
        return _fmt_atom(node)
    if not node:
        return f"{pad}()"
    head = _fmt_atom(node[0])
    inline: list[Any] = []
    nested: list[list] = []
    for child in node[1:]:
        (nested if isinstance(child, list) else inline).append(child)
    if not nested:
        parts = [head] + [_fmt_atom(c) for c in inline]
        return f"{pad}({' '.join(parts)})"
    first = head + (" " + " ".join(_fmt_atom(c) for c in inline) if inline else "")
    lines = [f"{pad}({first}"]
    for child in nested:
        lines.append(fmt_pcb(child, depth + 1))
    lines.append(f"{pad})")
    return "\n".join(lines)


def _copy_project_files() -> None:
    src_pro = ROOT / "injet-racing-prodv3.kicad_pro"
    src_sch = ROOT / "injet-racing-prodv3.kicad_sch"
    dst_pro = ROOT / f"{PROJECT}.kicad_pro"
    dst_sch = ROOT / f"{PROJECT}.kicad_sch"

    if src_pro.exists():
        data = json.loads(src_pro.read_text(encoding="utf-8"))
        data.setdefault("meta", {})["filename"] = f"{PROJECT}.kicad_pro"
        if "sheets" in data and data["sheets"]:
            data["sheets"][0][1] = f"{PROJECT}.kicad_sch"
        dst_pro.write_text(json.dumps(data, indent=2), encoding="utf-8")

    if src_sch.exists():
        text = src_sch.read_text(encoding="utf-8")
        text = text.replace("injet-racing-prodv3", PROJECT)
        text = text.replace("ProdV3-2L", "ProdV4-2L")
        dst_sch.write_text(text, encoding="utf-8")


def _count_pads(tree: list) -> tuple[int, int]:
    with_net = without = 0
    for item in tree:
        if not _is_sym(item, "footprint"):
            continue
        for sub in item:
            if not _is_sym(sub, "pad"):
                continue
            net = None
            for psub in sub:
                if _is_sym(psub, "net"):
                    net = _net_name(psub)
            if net:
                with_net += 1
            else:
                without += 1
    return with_net, without


def main() -> None:
    if not SRC_PCB.exists():
        raise SystemExit(f"Base não encontrada: {SRC_PCB}")

    print(f"Lendo base: {SRC_PCB.name}")
    tree = loads(SRC_PCB.read_text(encoding="utf-8"))
    if not isinstance(tree, list) or tree[0] != S("kicad_pcb"):
        raise SystemExit("Arquivo KiCad inválido")

    n_seg_before = sum(1 for x in tree if _is_sym(x, "segment"))
    n_via_before = sum(1 for x in tree if _is_sym(x, "via"))
    w0, wo0 = _count_pads(tree)

    assigned, updated = _assign_pad_nets(tree)
    propagated = _propagate_segment_nets(tree)
    swd_fixes = _fix_swd_colocated_vias(tree)
    added_segs = _add_drc_connects(tree)
    _update_generator_meta(tree)

    dst = ROOT / f"{PROJECT}.kicad_pcb"
    dst.write_text(fmt_pcb(tree) + "\n", encoding="utf-8")
    _copy_project_files()

    n_seg = sum(1 for x in tree if _is_sym(x, "segment"))
    n_via = sum(1 for x in tree if _is_sym(x, "via"))
    w1, wo1 = _count_pads(tree)

    print(f"  wrote {dst.name} ({dst.stat().st_size // 1024} KB)")
    print(f"  pads: {w0} com net -> {w1} (+{assigned} novos, {updated} MCU corrigidos, {wo1} sem net)")
    print(f"  segmentos: {n_seg_before} -> {n_seg} (+{n_seg - n_seg_before}, DRC stubs ~{added_segs})")
    print(f"  vias: {n_via_before} -> {n_via}")
    print(f"  segment nets propagados: {propagated}, SWD fixes: {swd_fixes}")
    print(f"  wrote {PROJECT}.kicad_pro / .kicad_sch")
    print(f"\nAbrir no KiCad: {PROJECT}.kicad_pro")
    print("Rodar DRC de novo e comparar com DRC.rpt anterior.")


if __name__ == "__main__":
    main()
