#!/usr/bin/env python3
"""
INJET RACING ECU — KiCad produção (esquemático plano + PCB 1-layer roteado)

Gera projeto separado do hierárquico didático:
  injet-racing-prod.kicad_pro / .kicad_sch / .kicad_pcb

- Esquemático: folha única A0, todos os blocos ligados (global labels)
- PCB: 200×100 mm, cobre B.Cu, trilhas do layout ecu-pcb-1layer (0 jumpers)

Uso: python _gen_kicad_prod.py
"""
from __future__ import annotations

import importlib.util
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
PROJECT = "injet-racing-prod"
KICAD_PCB_VERSION = 20241229
GENERATOR = "injet-racing-gen"
GENERATOR_VERSION = "1.1-prod"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


gen = _load_module("gen_ecu", ROOT / "_gen_kicad_ecu.py")
pcb_layout = _load_module("pcb1", ROOT.parent / "assets" / "_gen_pcb_1layer.py")
sch_complete = _load_module("sch_prod", ROOT / "_schematic_prod_complete.py")

S = gen.S
uid = gen.uid
fmt = gen.fmt
SchDoc = gen.SchDoc
build_lib_symbols = gen.build_lib_symbols
label_global = gen.label_global
wire_h = gen.wire_h
wire_v = gen.wire_v
text_note = gen.text_note


# ---------------------------------------------------------------------------
# Transformação S-exp (offset + hier → global)
# ---------------------------------------------------------------------------

def _is_sym(node: Any, name: str) -> bool:
    return isinstance(node, list) and len(node) >= 1 and node[0] == S(name)


def shift_item(item: list, dx: float, dy: float) -> list:
    """Desloca coordenadas at/xy/start/end dentro de um item."""

    def walk(node: Any) -> Any:
        if not isinstance(node, list):
            return node
        if _is_sym(node, "at"):
            if len(node) == 3:
                return [S("at"), node[1] + dx, node[2] + dy]
            if len(node) >= 4:
                return [S("at"), node[1] + dx, node[2] + dy, *node[3:]]
        if _is_sym(node, "xy"):
            return [S("xy"), node[1] + dx, node[2] + dy]
        if _is_sym(node, "start"):
            return [S("start"), node[1] + dx, node[2] + dy]
        if _is_sym(node, "end"):
            return [S("end"), node[1] + dx, node[2] + dy]
        if _is_sym(node, "pts"):
            return [S("pts"), *[walk(c) for c in node[1:]]]
        return [walk(c) for c in node]

    return walk(item)


def hier_to_global_item(item: list) -> list:
    """Converte hierarchical_label → global_label (KiCad 10)."""
    if not _is_sym(item, "hierarchical_label"):
        return item
    text = item[1]
    shape, x, y, rot = "passive", 0.0, 0.0, 0
    for sub in item[2:]:
        if _is_sym(sub, "shape"):
            shape = str(sub[1])
        elif _is_sym(sub, "at"):
            x, y = float(sub[1]), float(sub[2])
            if len(sub) >= 4:
                rot = int(float(sub[3]))
    return label_global(str(text), x, y, shape, rot)


def merge_sheet(doc: SchDoc, dx: float, dy: float) -> list:
    out = []
    for item in doc.items:
        shifted = shift_item(item, dx, dy)
        if _is_sym(shifted, "hierarchical_label"):
            shifted = hier_to_global_item(shifted)
        out.append(shifted)
    return out


def build_flat_schematic() -> SchDoc:
    """Esquemático plano completo — CN1 ATX-24 + CN2 PCIe-6, tudo ligado com fios."""
    old_proj = gen.PROJECT
    gen.PROJECT = PROJECT
    try:
        return sch_complete.build_complete_schematic(gen)
    finally:
        gen.PROJECT = old_proj


# ---------------------------------------------------------------------------
# PCB 1-layer — trilhas do layout fenolite
# ---------------------------------------------------------------------------

BOARD_W = pcb_layout.W
BOARD_H = pcb_layout.H
COPPER_LAYER = "B.Cu"


def L(name: str) -> str:
    """Nome de camada/footprint/rede — string literal (KiCad 10 exige aspas)."""
    return name


def fmt_atom(val: Any) -> str:
    from sexpdata import Symbol
    import sexpdata
    if isinstance(val, Symbol):
        return str(val)
    return sexpdata.dumps([val])[1:-1]


def fmt_pcb(node: Any, depth: int = 0) -> str:
    """Formata S-exp PCB com aspas corretas (KiCad 10)."""
    tab = "\t"
    pad = tab * depth
    if not isinstance(node, list):
        return fmt_atom(node)
    if not node:
        return f"{pad}()"
    head = fmt_atom(node[0])
    inline: list[Any] = []
    nested: list[list] = []
    for child in node[1:]:
        (nested if isinstance(child, list) else inline).append(child)
    if not nested:
        parts = [head] + [fmt_atom(c) for c in inline]
        return f"{pad}({' '.join(parts)})"
    first = head + (" " + " ".join(fmt_atom(c) for c in inline) if inline else "")
    lines = [f"{pad}({first}"]
    for child in nested:
        lines.append(fmt_pcb(child, depth + 1))
    lines.append(f"{pad})")
    return "\n".join(lines)


# Tabela de camadas KiCad 10 (IDs canônicos, nomes entre aspas)
PCB_LAYERS: list[list] = [
    [0, L("F.Cu"), S("signal")],
    [2, L("B.Cu"), S("signal")],
    [9, L("F.Adhes"), S("user"), L("F.Adhesive")],
    [11, L("B.Adhes"), S("user"), L("B.Adhesive")],
    [13, L("F.Paste"), S("user")],
    [15, L("B.Paste"), S("user")],
    [5, L("F.SilkS"), S("user"), L("F.Silkscreen")],
    [7, L("B.SilkS"), S("user"), L("B.Silkscreen")],
    [1, L("F.Mask"), S("user")],
    [3, L("B.Mask"), S("user")],
    [17, L("Dwgs.User"), S("user"), L("User.Drawings")],
    [19, L("Cmts.User"), S("user"), L("User.Comments")],
    [21, L("Eco1.User"), S("user"), L("User.Eco1")],
    [23, L("Eco2.User"), S("user"), L("User.Eco2")],
    [25, L("Edge.Cuts"), S("user")],
    [27, L("Margin"), S("user")],
    [31, L("F.CrtYd"), S("user"), L("F.Courtyard")],
    [29, L("B.CrtYd"), S("user"), L("B.Courtyard")],
    [35, L("F.Fab"), S("user")],
    [33, L("B.Fab"), S("user")],
]


def assign_pad_nets(pads: dict, traces: list, tol: float = 0.35) -> dict[str, str]:
    pad_net: dict[str, str] = {}
    for pts, _w, net in traces:
        for x, y in pts:
            for pname, (px, py, _od, _dr) in pads.items():
                if math.hypot(px - x, py - y) <= tol:
                    if pname in pad_net and pad_net[pname] != net:
                        # Prefer power nets on conflict
                        priority = {"GND": 0, "+12V_PROT": 1, "+5V": 2, "+3V3": 3}
                        if priority.get(net, 99) < priority.get(pad_net[pname], 99):
                            pad_net[pname] = net
                    else:
                        pad_net[pname] = net
    return pad_net


def group_pads(pads: dict) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = defaultdict(list)
    for name in sorted(pads):
        prefix = name.rsplit(".", 1)[0] if "." in name else name
        groups[prefix].append(name)
    return groups


REF_MAP = {
    "CN1": ("CN1", "ATX-24"),
    "CN2": ("CN2", "PCIe-6 λ"),
    "QREV": ("Q1", "IRF9540"),
    "BUCK": ("U2", "MP1584"),
    "LDO": ("U3", "LDO 3V3"),
    "QINJ1": ("Q10", "IRLZ44N"),
    "QINJ2": ("Q11", "IRLZ44N"),
    "QINJ3": ("Q12", "IRLZ44N"),
    "QINJ4": ("Q13", "IRLZ44N"),
    "QHEAT": ("Q30", "IRLZ44N"),
    "QRL1": ("Q20", "2N7000"),
    "QRL2": ("Q21", "2N7000"),
    "QRL3": ("Q22", "2N7000"),
    "MCU": ("U1", "STM32F407 Black Board"),
    "SWD": ("J1", "SWD 4p"),
    "U817": ("U7", "PC817"),
    "CAN": ("U6", "SN65HVD230"),
    "U6004": ("U4", "MCP6004"),
    "U8628": ("U5", "AD8628"),
}


def net_ref(net_ids: dict[str, int], net_name: str) -> list:
    """Referência de net em pad/via KiCad 10: (net <id> \"<nome>\")."""
    name = net_name or ""
    return [S("net"), net_ids.get(name, 0), name]


def net_id_ref(net_ids: dict[str, int], net_name: str) -> list:
    """Referência de net em segment/track KiCad 10: (net <id>)."""
    return [S("net"), net_ids.get(net_name or "", 0)]


def fp_ref(prefix: str) -> tuple[str, str]:
    if prefix in REF_MAP:
        return REF_MAP[prefix]
    return (prefix, prefix)


def make_footprint(
    prefix: str,
    pad_names: list[str],
    pads: dict,
    pad_net: dict[str, str],
    net_ids: dict[str, int],
) -> list:
    xs = [pads[p][0] for p in pad_names]
    ys = [pads[p][1] for p in pad_names]
    ox, oy = min(xs), min(ys)
    ref, val = fp_ref(prefix)
    fp_uuid = uid()
    pad_els = []
    for pname in sorted(pad_names, key=lambda n: pads[n][0]):
        x, y, od, drill = pads[pname]
        pin = pname.split(".")[-1]
        net_name = pad_net.get(pname, "")
        net_id = net_ids.get(net_name, 0)
        rx, ry = x - ox, y - oy
        if drill > 0:
            pad_els.append([
                S("pad"), pin, S("thru_hole"), S("circle"),
                [S("at"), rx, ry],
                [S("size"), od, od],
                [S("drill"), drill],
                [S("layers"), L("*.Cu"), L("*.Mask")],
                net_ref(net_ids, net_name),
                [S("uuid"), uid()],
            ])
        else:
            pad_els.append([
                S("pad"), pin, S("smd"), S("rect"),
                [S("at"), rx, ry],
                [S("size"), od, od],
                [S("layers"), L(COPPER_LAYER), L(COPPER_LAYER)],
                net_ref(net_ids, net_name),
                [S("uuid"), uid()],
            ])
    return [
        S("footprint"), L(f"Injet:{prefix}"),
        [S("layer"), L("F.Cu")],
        [S("uuid"), fp_uuid],
        [S("at"), ox, oy],
        [S("property"), "Reference", ref,
         [S("at"), 0, -3],
         [S("layer"), L("F.SilkS")],
         [S("uuid"), uid()],
         [S("effects"), [S("font"), [S("size"), 1, 1]]]],
        [S("property"), "Value", val,
         [S("at"), 0, 3],
         [S("layer"), L("F.Fab")],
         [S("uuid"), uid()],
         [S("effects"), [S("font"), [S("size"), 1, 1]]]],
        *pad_els,
    ]


def build_pcb_sexp() -> list:
    pads = pcb_layout.pads
    traces = pcb_layout.traces
    pad_net = assign_pad_nets(pads, traces)

    all_nets = sorted({n for n in pad_net.values()} | {net for _, _, net in traces})
    if "" not in all_nets:
        all_nets = [""] + all_nets
    net_ids = {name: i for i, name in enumerate(all_nets)}

    segments = []
    for pts, width, net in traces:
        for i in range(len(pts) - 1):
            x1, y1 = pts[i]
            x2, y2 = pts[i + 1]
            segments.append([
                S("segment"),
                [S("start"), x1, y1],
                [S("end"), x2, y2],
                [S("width"), width],
                [S("layer"), L(COPPER_LAYER)],
                net_id_ref(net_ids, net),
                [S("uuid"), uid()],
            ])

    footprints = []
    for prefix, pnames in sorted(group_pads(pads).items()):
        footprints.append(make_footprint(prefix, pnames, pads, pad_net, net_ids))

    margin = 0.5
    edge = [
        [S("gr_line"), [S("start"), margin, margin], [S("end"), BOARD_W - margin, margin],
         [S("stroke"), [S("width"), 0.1], [S("type"), S("solid")]], [S("layer"), L("Edge.Cuts")], [S("uuid"), uid()]],
        [S("gr_line"), [S("start"), BOARD_W - margin, margin], [S("end"), BOARD_W - margin, BOARD_H - margin],
         [S("stroke"), [S("width"), 0.1], [S("type"), S("solid")]], [S("layer"), L("Edge.Cuts")], [S("uuid"), uid()]],
        [S("gr_line"), [S("start"), BOARD_W - margin, BOARD_H - margin], [S("end"), margin, BOARD_H - margin],
         [S("stroke"), [S("width"), 0.1], [S("type"), S("solid")]], [S("layer"), L("Edge.Cuts")], [S("uuid"), uid()]],
        [S("gr_line"), [S("start"), margin, BOARD_H - margin], [S("end"), margin, margin],
         [S("stroke"), [S("width"), 0.1], [S("type"), S("solid")]], [S("layer"), L("Edge.Cuts")], [S("uuid"), uid()]],
    ]

    # Furos M3 nos cantos
    for x, y in [(4, 4), (196, 4), (4, 96), (196, 96)]:
        footprints.append([
            S("footprint"), L("MountingHole:MountingHole_3.2mm_M3"),
            [S("layer"), L("F.Cu")], [S("uuid"), uid()], [S("at"), x, y],
            [S("property"), "Reference", "H",
             [S("at"), 0, 0],
             [S("layer"), L("F.SilkS")],
             [S("hide"), S("yes")],
             [S("uuid"), uid()],
             [S("effects"), [S("font"), [S("size"), 1, 1]]]],
            [S("pad"), "", S("np_thru_hole"), S("circle"),
             [S("at"), 0, 0], [S("size"), 6.4, 6.4], [S("drill"), 3.2],
             [S("layers"), L("*.Cu"), L("*.Mask")], net_ref(net_ids, ""), [S("uuid"), uid()]],
        ])

    net_decls = [[S("net"), i, name] for name, i in sorted(net_ids.items(), key=lambda x: x[1])]

    return [
        S("kicad_pcb"),
        [S("version"), KICAD_PCB_VERSION],
        [S("generator"), GENERATOR],
        [S("generator_version"), GENERATOR_VERSION],
        [S("general"), [S("thickness"), 1.6], [S("legacy_teardrops"), S("no")]],
        [S("paper"), "A4"],
        [S("layers"), *PCB_LAYERS],
        [S("setup"),
         [S("pad_to_mask_clearance"), 0],
         [S("allow_soldermask_bridges_in_footprints"), S("no")],
         [S("pcbplotparams"),
          [S("layerselection"), 0x80000],
          [S("plot_on_all_layers_selection"), 0x0000000],
          [S("disableapertmacros"), S("no")],
          [S("usegerberattributes"), S("yes")],
          [S("usegerberadvancedattributes"), S("yes")],
          [S("creategerberjobfile"), S("yes")],
          [S("svguseinch"), S("no")],
          [S("svgprecision"), 6],
          [S("excludeedgelayer"), S("yes")],
          [S("plotframeref"), S("no")],
          [S("viasonmask"), S("no")],
          [S("mode"), 1],
          [S("useauxorigin"), S("no")],
          [S("hpglpennumber"), 1],
          [S("hpglpenspeed"), 20],
          [S("hpglpendiameter"), 15.0],
          [S("pdf_front_fp_property_popups"), S("yes")],
          [S("pdf_back_fp_property_popups"), S("yes")],
          [S("dxfpolygonmode"), S("yes")],
          [S("dxfimperialunits"), S("yes")],
          [S("dxfusepcbnewfont"), S("yes")],
          [S("psnegative"), S("no")],
          [S("psa4output"), S("no")],
          [S("plotreference"), S("yes")],
          [S("plotvalue"), S("yes")],
          [S("plotfingerprint"), S("no")],
          [S("plotinvisibletext"), S("no")],
          [S("sketchpadsonfab"), S("no")],
          [S("subtractmaskfromsilk"), S("no")],
          [S("outputformat"), 1],
          [S("mirror"), S("no")],
          [S("drillshape"), 1],
          [S("scaleselection"), 1],
          [S("outputdirectory"), ""],
         ],
        ],
        *net_decls,
        *footprints,
        *segments,
        *edge,
    ]


def write_kicad_pro(path: Path) -> None:
    data = {
        "board": {
            "design_settings": {
                "defaults": {"board_outline_line_width": 0.1, "copper_line_width": 0.2},
                "diff_pair_dimensions": [],
                "drc_exclusions": [],
                "rules": {},
                "track_widths": [0.25, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0, 2.8],
                "via_dimensions": [{"diameter": 0.8, "drill": 0.4}],
            },
            "layer_presets": [],
        },
        "boards": [],
        "cvpcb": {"equivalence_files": []},
        "libraries": {"pinned_footprint_libs": [], "pinned_symbol_libs": []},
        "meta": {"filename": f"{PROJECT}.kicad_pro", "version": 1},
        "net_settings": {
            "classes": [{"name": "Default", "track_width": 0.8, "clearance": 0.3}],
            "meta": {"version": 3},
            "net_auto_assign": True,
            "netclass_assignments": [],
        },
        "pcbnew": {
            "last_paths": {"gencad": "", "idf": "", "netlist": "", "specctra_dsn": "", "step": "", "vrml": ""},
            "page_layout_descr_file": "",
        },
        "schematic": {"legacy_lib_dir": "", "legacy_lib_list": []},
        "sheets": [["", f"{PROJECT}.kicad_sch"]],
        "text_variables": {},
    }
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def schematic_to_sexp(doc: SchDoc) -> list:
    lib = build_lib_symbols()
    return [
        S("kicad_sch"),
        [S("version"), gen.KICAD_VERSION],
        [S("generator"), GENERATOR],
        [S("generator_version"), GENERATOR_VERSION],
        [S("uuid"), doc.sheet_uuid],
        [S("paper"), S("A0")],
        [S("title_block"),
         [S("title"), doc.title],
         [S("date"), "2026-08-05"],
         [S("rev"), "Prod-1L"],
         [S("company"), "INJET RACING"],
         [S("comment"), 1, doc.page]],
        lib,
        *doc.items,
        [S("sheet_instances"), [S("path"), "/", [S("page"), doc.page]]],
        [S("embedded_fonts"), S("no")],
    ]


def main() -> None:
    sch_doc = build_flat_schematic()
    sch_path = ROOT / f"{PROJECT}.kicad_sch"
    sch_path.write_text(fmt(schematic_to_sexp(sch_doc)) + "\n", encoding="utf-8")
    print(f"  wrote {sch_path.name} ({len(sch_doc.items)} items)")

    pcb_path = ROOT / f"{PROJECT}.kicad_pcb"
    pcb_sexp = build_pcb_sexp()
    pcb_path.write_text(fmt_pcb(pcb_sexp) + "\n", encoding="utf-8")
    n_seg = sum(1 for x in pcb_sexp if isinstance(x, list) and x and x[0] == S("segment"))
    n_fp = sum(1 for x in pcb_sexp if isinstance(x, list) and x and x[0] == S("footprint"))
    print(f"  wrote {pcb_path.name} ({n_fp} footprints, {n_seg} segments, {len(pcb_layout.traces)} trace paths)")

    pro_path = ROOT / f"{PROJECT}.kicad_pro"
    write_kicad_pro(pro_path)
    print(f"  wrote {pro_path.name}")

    pad_net = assign_pad_nets(pcb_layout.pads, pcb_layout.traces)
    unassigned = [p for p in pcb_layout.pads if p not in pad_net]
    print(f"\n  PCB: {len(pcb_layout.pads)} pads, {len(pad_net)} com net, {len(unassigned)} sem net")
    print(f"  Placa: {BOARD_W}×{BOARD_H} mm · cobre {COPPER_LAYER} · 0 jumpers (só trilhas)")
    print(f"\nAbrir no KiCad: {PROJECT}.kicad_pro")


if __name__ == "__main__":
    main()
