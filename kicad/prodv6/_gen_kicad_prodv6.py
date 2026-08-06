#!/usr/bin/env python3
"""ProdV6 — PCB rebuild por passos (checklist CHECKLIST.md)."""
from __future__ import annotations

import json
import importlib.util
import sys
import uuid
from pathlib import Path
from typing import Any

from sexpdata import Symbol

ROOT = Path(__file__).resolve().parent
KICAD_ROOT = ROOT.parent
PROJECT = "injet-racing-prodv6"
GENERATOR = "injet-racing-gen"
GENERATOR_VERSION = "1.6-prodv6-step4-buck"
BOARD_W, BOARD_H = 240.0, 160.0
S = Symbol


def _load_v2():
    spec = importlib.util.spec_from_file_location(
        "pcb_v2", KICAD_ROOT.parent / "assets" / "_gen_pcb_prodv2.py"
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules["pcb_v2"] = mod
    spec.loader.exec_module(mod)
    return mod


pcb_v2 = _load_v2()
CN1_NETS = dict(pcb_v2.CN1_PAD_NETS)
CN1_NETS[1] = "+12V_BAT"
CN1_NETS[2] = "+12V_BAT"
CN2_NETS = pcb_v2.CN2_PAD_NETS


def _load_layout():
    spec = importlib.util.spec_from_file_location(
        "prodv6_layout", ROOT / "prodv6_layout.py"
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules["prodv6_layout"] = mod
    spec.loader.exec_module(mod)
    return mod


layout = _load_layout()

# Posições (mm) — mesma lógica prodv2/v5
CN1_AT = (12.0, 8.0)
CN2_AT = (200.0, 8.0)
MOUNT_HOLES = [(6.0, 6.0), (234.0, 6.0), (6.0, 154.0), (234.0, 154.0)]


def _uid() -> str:
    return str(uuid.uuid4())


def _fmt_atom(val: Any) -> str:
    if isinstance(val, Symbol):
        return str(val)
    if isinstance(val, float):
        return f"{val:g}"
    from sexpdata import dumps
    return dumps([val])[1:-1]


def fmt_pcb(node: Any, depth: int = 0) -> str:
    tab = "\t"
    pad = tab * depth
    if not isinstance(node, list):
        return _fmt_atom(node)
    if not node:
        return f"{pad}()"
    head = _fmt_atom(node[0])
    inline, nested = [], []
    for child in node[1:]:
        (nested if isinstance(child, list) else inline).append(child)
    if not nested:
        return f"{pad}({head} {' '.join(_fmt_atom(c) for c in inline)})"
    first = head + (" " + " ".join(_fmt_atom(c) for c in inline) if inline else "")
    lines = [f"{pad}({first}"]
    for child in nested:
        lines.append(fmt_pcb(child, depth + 1))
    lines.append(f"{pad})")
    return "\n".join(lines)


def _prop(key: str, val: str, layer: str = "F.SilkS", hide: bool = False) -> list:
    p = [
        S("property"), key, val,
        [S("at"), 0, -3 if key == "Reference" else 3, 0],
        [S("layer"), layer],
        [S("uuid"), _uid()],
        [S("effects"), [S("font"), [S("size"), 1, 1]]],
    ]
    if hide:
        p.insert(4, [S("hide"), S("yes")])
    return p


def _pad(num: str, x: float, y: float, net: str, od: float = 2.15, drill: float = 1.1) -> list:
    el = [
        S("pad"), num, S("thru_hole"), S("circle"),
        [S("at"), x, y],
        [S("size"), od, od],
        [S("drill"), drill],
        [S("layers"), "*.Cu", "*.Mask"],
        [S("remove_unused_layers"), S("no")],
        [S("uuid"), _uid()],
    ]
    if net:
        el.insert(-1, [S("net"), net])
    return el


def _fp_line(x1, y1, x2, y2, layer="F.SilkS", w=0.12) -> list:
    return [
        S("fp_line"),
        [S("start"), x1, y1], [S("end"), x2, y2],
        [S("stroke"), [S("width"), w], [S("type"), S("solid")]],
        [S("layer"), layer],
        [S("uuid"), _uid()],
    ]


def _fp_rect(x1, y1, x2, y2, layer="F.CrtYd") -> list:
    return [
        S("fp_rect"),
        [S("start"), x1, y1], [S("end"), x2, y2],
        [S("stroke"), [S("width"), 0.05], [S("type"), S("solid")]],
        [S("layer"), layer],
        [S("fill"), S("no")],
        [S("uuid"), _uid()],
    ]


def _footprint(name: str, ref: str, val: str, ox: float, oy: float, extras: list) -> list:
    return [
        S("footprint"), name,
        [S("layer"), "F.Cu"],
        [S("uuid"), _uid()],
        [S("at"), ox, oy],
        _prop("Reference", ref, hide=(ref == "H")),
        _prop("Value", val, "F.Fab"),
        _prop("Datasheet", "", hide=True),
        _prop("Description", "", hide=True),
        [S("duplicate_pad_numbers_are_jumpers"), S("no")],
        *extras,
        [S("embedded_fonts"), S("no")],
    ]


def _segment(x1, y1, x2, y2, net: str, layer: str = "F.Cu", width: float = 0.8) -> list:
    return [
        S("segment"),
        [S("start"), x1, y1], [S("end"), x2, y2],
        [S("width"), width],
        [S("layer"), layer],
        [S("net"), net],
        [S("uuid"), _uid()],
    ]


def _cn1_footprint() -> list:
    pads_top = [(i, (i - 1) * 4, 6) for i in range(1, 13)]
    pads_bot = [(i, (i - 13) * 4, 0) for i in range(13, 25)]
    extras = [_fp_rect(-1, -1, 47, 7)]
    for pin, x, y in pads_top + pads_bot:
        extras.append(_pad(str(pin), x, y, CN1_NETS[pin]))
    return _footprint("Injet:CN1", "CN1", "ATX-24", *CN1_AT, extras)


def _cn2_footprint() -> list:
    layout = [(1, 0, 6), (2, 4, 6), (3, 8, 6), (4, 0, 0), (5, 4, 0), (6, 8, 0)]
    extras = [_fp_rect(-1, -1, 11, 7)]
    for pin, x, y in layout:
        extras.append(_pad(str(pin), x, y, CN2_NETS.get(pin, "")))
    return _footprint("Injet:CN2", "CN2", "PCIe-6", *CN2_AT, extras)


def _patch_sch_remove_swd(text: str) -> str:
    import re
    text = re.sub(
        r'\t\(text "CN3 SWD \(interno gravação\)"[\s\S]*?\t\)\n',
        "",
        text,
    )
    for at in ("220 35", "228 35", "236 35", "244 35"):
        text = re.sub(
            rf'\t\(label "[^"]+"\s*\n\t\t\(at {re.escape(at)}[\s\S]*?\t\)\n',
            "",
            text,
        )
    note = '\t(text "Gravacao: USB/SWD da Black Board STM32 (sem CN3 na ECU)"\n'
    note += '\t\t(at 215 27 0)\n\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1.2 1.2)\n\t\t\t)\n\t\t)\n'
    note += '\t\t(uuid "prodv6-no-swd-note")\n\t)\n'
    return text.replace(
        '\t(text "Condicionamento sensores',
        note + '\t(text "Condicionamento sensores',
        1,
    )


def _write_sch() -> None:
    src = KICAD_ROOT / "injet-racing-prodv5.kicad_sch"
    text = src.read_text(encoding="utf-8")
    text = text.replace("injet-racing-prodv5", PROJECT)
    text = text.replace("ProdV5-JL32", "ProdV6-rebuild")
    text = _patch_sch_remove_swd(text)
    (ROOT / f"{PROJECT}.kicad_sch").write_text(text, encoding="utf-8")


def _mount_hole(x: float, y: float) -> list:
    return _footprint(
        "MountingHole:MountingHole_3.2mm_M3", "H", "MountingHole", x, y,
        [[
            S("pad"), "", S("np_thru_hole"), S("circle"),
            [S("at"), 0, 0], [S("size"), 6.4, 6.4], [S("drill"), 3.2],
            [S("layers"), "*.Cu", "*.Mask"],
            [S("uuid"), _uid()],
        ]],
    )


def _edge_cuts() -> list:
    m = 0.5
    lines = [
        (m, m, BOARD_W - m, m),
        (BOARD_W - m, m, BOARD_W - m, BOARD_H - m),
        (BOARD_W - m, BOARD_H - m, m, BOARD_H - m),
        (m, BOARD_H - m, m, m),
    ]
    out = []
    for x1, y1, x2, y2 in lines:
        out.append([
            S("gr_line"),
            [S("start"), x1, y1], [S("end"), x2, y2],
            [S("stroke"), [S("width"), 0.1], [S("type"), S("solid")]],
            [S("layer"), "Edge.Cuts"],
            [S("uuid"), _uid()],
        ])
    return out


def _gnd_zone(layer: str) -> list:
    inset = 1.0
    return [
        S("zone"),
        [S("net"), "GND"],
        [S("layer"), layer],
        [S("uuid"), _uid()],
        [S("hatch"), S("edge"), 0.508],
        [S("connect_pads"),
         [S("clearance"), 0.5]],
        [S("min_thickness"), 0.254],
        [S("filled_areas_thickness"), S("no")],
        [S("fill"), S("yes"),
         [S("thermal_gap"), 0.254],
         [S("thermal_bridge_width"), 0.5],
         [S("island_removal_mode"), 0]],
        [S("polygon"),
         [S("pts"),
          [S("xy"), inset, inset],
          [S("xy"), BOARD_W - inset, inset],
          [S("xy"), BOARD_W - inset, BOARD_H - inset],
          [S("xy"), inset, BOARD_H - inset]]],
    ]


def _board_text() -> list:
    return [
        [
            S("gr_text"), "ProdV6 step4 - MOD4 buck +5V",
            [S("at"), 120, 155],
            [S("layer"), "Dwgs.User"],
            [S("uuid"), _uid()],
            [S("effects"), [S("font"), [S("size"), 1.5, 1.5]], [S("justify"), S("left")]],
        ],
        [
            S("gr_text"), "KiCad: tecla B = preencher zones",
            [S("at"), 120, 152],
            [S("layer"), "Dwgs.User"],
            [S("uuid"), _uid()],
            [S("effects"), [S("font"), [S("size"), 1.2, 1.2]], [S("justify"), S("left")]],
        ],
    ]


def _pcb_layers() -> list:
    rows = [
        [0, "F.Cu", S("signal")],
        [2, "B.Cu", S("signal")],
        [5, "F.SilkS", S("user"), "F.Silkscreen"],
        [7, "B.SilkS", S("user"), "B.Silkscreen"],
        [1, "F.Mask", S("user")],
        [3, "B.Mask", S("user")],
        [17, "Dwgs.User", S("user"), "User.Drawings"],
        [25, "Edge.Cuts", S("user")],
        [31, "F.CrtYd", S("user"), "F.Courtyard"],
        [29, "B.CrtYd", S("user"), "B.Courtyard"],
        [35, "F.Fab", S("user")],
        [33, "B.Fab", S("user")],
    ]
    return [S("layers"), *rows]


def build_pcb() -> list:
    fps = [_cn1_footprint(), _cn2_footprint()]
    fps.extend(layout.power_footprints())
    fps.extend(layout.buck_footprints())
    for x, y in MOUNT_HOLES:
        fps.append(_mount_hole(x, y))
    return [
        S("kicad_pcb"),
        [S("version"), 20260206],
        [S("generator"), GENERATOR],
        [S("generator_version"), GENERATOR_VERSION],
        [S("general"), [S("thickness"), 1.6], [S("legacy_teardrops"), S("no")]],
        [S("paper"), "A4"],
        _pcb_layers(),
        [S("setup"),
         [S("pad_to_mask_clearance"), 0],
         [S("pcbplotparams"),
          [S("layerselection"), 0], [S("mode"), 1], [S("useauxorigin"), S("no")],
          [S("outputformat"), 1], [S("outputdirectory"), ""]]],
        *fps,
        *layout.power_traces(),
        *layout.buck_traces(),
        _gnd_zone("B.Cu"),
        _gnd_zone("F.Cu"),
        *_edge_cuts(),
        *layout.zone_markers(),
        *layout.mod_io_markers(),
        *_board_text(),
    ]


def _write_pro() -> None:
    src = KICAD_ROOT / "injet-racing-prodv5.kicad_pro"
    if src.exists():
        data = json.loads(src.read_text(encoding="utf-8"))
    else:
        data = {"meta": {"filename": f"{PROJECT}.kicad_pro", "version": 1}, "sheets": [["", f"{PROJECT}.kicad_sch"]]}
    data.setdefault("meta", {})["filename"] = f"{PROJECT}.kicad_pro"
    if "sheets" in data and data["sheets"]:
        data["sheets"][0][1] = f"{PROJECT}.kicad_sch"
    (ROOT / f"{PROJECT}.kicad_pro").write_text(json.dumps(data, indent=2), encoding="utf-8")


def main() -> None:
    pcb_path = ROOT / f"{PROJECT}.kicad_pcb"
    pcb_path.write_text(fmt_pcb(build_pcb()) + "\n", encoding="utf-8")
    _write_pro()
    _write_sch()
    print(f"  {pcb_path.name}: passo 3 — MOD3 +12V_PROT (Q1 F1 R1 D1 D2 C1 C2)")
    print(f"  Zonas reservadas: MOD4–MOD11 (Dwgs.User)")
    print(f"  CN1 @ {CN1_AT}, CN2 @ {CN2_AT} (sem J1 SWD — grava na Black Board)")
    print(f"  {PROJECT}.kicad_pro / .kicad_sch")
    print(f"  Abrir: {ROOT / (PROJECT + '.kicad_pro')}")


if __name__ == "__main__":
    main()
