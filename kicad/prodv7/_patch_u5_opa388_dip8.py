"""prodv7 — U5 SOIC B.Cu → OPA388IDR DIP-8 THT F.Cu (adaptador SOIC8-DIP)."""
from __future__ import annotations

import re
import uuid
from pathlib import Path

PCB = Path(__file__).resolve().parent / "injet-racing-prodv7.kicad_pcb"

# Preserva UUIDs dos pads para não quebrar trilhas existentes.
PAD_UUID = {
    "1": "4a791d80-1581-4f8e-b557-99910cd11f22",
    "2": "9cefd71a-64f0-41d4-aa5d-07aa42c288ea",
    "3": "7f497cab-4f0b-46fa-a0bf-5002dbc7f778",
    "4": "f48bb430-5edf-49b0-bf40-78ae04d94515",
    "5": "eb90fe9e-1048-4756-bbed-ba3c882c2ea1",
    "6": "33721b71-c0aa-434f-9f1d-e8eccbbfa947",
    "7": "86a0e181-f375-4847-a300-798ed3c2a1b9",
    "8": "981e2319-5e5e-4c0f-ba8d-f68e3987699e",
}

PAD_NET = {
    "2": "IP",
    "3": "VM",
    "4": "GND",
    "6": "IP",
    "7": "+5V",
}

PAD_AT = {
    "1": (0, 0),
    "2": (0, 2.54),
    "3": (0, 5.08),
    "4": (0, 7.62),
    "5": (7.62, 7.62),
    "6": (7.62, 5.08),
    "7": (7.62, 2.54),
    "8": (7.62, 0),
}


def _uid() -> str:
    return str(uuid.uuid4())


def _pad(num: str) -> str:
    x, y = PAD_AT[num]
    net = PAD_NET.get(num, "")
    net_line = f'\n\t\t\t(net "{net}")' if net else ""
    return f"""\t\t(pad "{num}" thru_hole circle
\t\t\t(at {x} {y})
\t\t\t(size 1.55 1.55)
\t\t\t(drill 0.85)
\t\t\t(layers "*.Cu" "*.Mask")
\t\t\t(remove_unused_layers no){net_line}
\t\t\t(uuid "{PAD_UUID[num]}")
\t\t)"""


def _fp_line(x1: float, y1: float, x2: float, y2: float, layer: str, w: float) -> str:
    return f"""\t\t(fp_line
\t\t\t(start {x1} {y1})
\t\t\t(end {x2} {y2})
\t\t\t(stroke
\t\t\t\t(width {w})
\t\t\t\t(type solid)
\t\t\t)
\t\t\t(layer "{layer}")
\t\t\t(uuid "{_uid()}")
\t\t)"""


def _fp_circle(cx: float, cy: float, layer: str) -> str:
    return f"""\t\t(fp_circle
\t\t\t(center {cx} {cy})
\t\t\t(end {cx + 1} {cy})
\t\t\t(stroke
\t\t\t\t(width 0.05)
\t\t\t\t(type solid)
\t\t\t)
\t\t\t(fill no)
\t\t\t(layer "{layer}")
\t\t\t(uuid "{_uid()}")
\t\t)"""


def build_footprint(at_x: float, at_y: float) -> str:
    lines = [
        '\t(footprint "Injet:U388"',
        '\t\t(layer "F.Cu")',
        '\t\t(uuid "735ddf39-ada7-4986-b87d-f6108d0cc771")',
        f"\t\t(at {at_x} {at_y})",
        '\t\t(property "Reference" "U5"',
        "\t\t\t(at 3.81 -2 0)",
        '\t\t\t(layer "F.SilkS")',
        '\t\t\t(uuid "1bf97a9e-2410-47cb-9c33-4ad0f9dc58da")',
        "\t\t\t(effects",
        "\t\t\t\t(font",
        "\t\t\t\t\t(size 1 1)",
        "\t\t\t\t)",
        "\t\t\t)",
        "\t\t)",
        '\t\t(property "Value" "OPA388IDR"',
        "\t\t\t(at 3.81 9.5 0)",
        '\t\t\t(layer "F.Fab")',
        '\t\t\t(uuid "6b55afc5-55d5-42bf-b83f-ec28680a6a31")',
        "\t\t\t(effects",
        "\t\t\t\t(font",
        "\t\t\t\t\t(size 1 1)",
        "\t\t\t\t)",
        "\t\t\t)",
        "\t\t)",
        '\t\t(property "Datasheet" ""',
        "\t\t\t(at 0 3 0)",
        '\t\t\t(layer "F.SilkS")',
        "\t\t\t(hide yes)",
        '\t\t\t(uuid "314e4df9-4987-484b-a51b-a26e771fca62")',
        "\t\t\t(effects",
        "\t\t\t\t(font",
        "\t\t\t\t\t(size 1 1)",
        "\t\t\t\t)",
        "\t\t\t)",
        "\t\t)",
        '\t\t(property "Description" "Zero-drift Ip · SOIC8 on DIP-8 adapter"',
        "\t\t\t(at 0 3 0)",
        '\t\t\t(layer "F.SilkS")',
        "\t\t\t(hide yes)",
        '\t\t\t(uuid "367391d8-c979-4037-9a81-4b73427d5cd5")',
        "\t\t\t(effects",
        "\t\t\t\t(font",
        "\t\t\t\t\t(size 1 1)",
        "\t\t\t\t)",
        "\t\t\t)",
        "\t\t)",
        "\t\t(duplicate_pad_numbers_are_jumpers no)",
    ]
    for layer, w in (("F.CrtYd", 0.05), ("F.Fab", 0.1)):
        lines += [
            _fp_line(0, -1, 7.62, -1, layer, w),
            _fp_line(7.62, -1, 7.62, 8.62, layer, w),
            _fp_line(7.62, 8.62, 0, 8.62, layer, w),
            _fp_line(0, 8.62, 0, -1, layer, w),
        ]
    for layer in ("F.CrtYd", "F.Fab"):
        lines += [
            _fp_circle(0, 0, layer),
            _fp_circle(0, 7.62, layer),
            _fp_circle(7.62, 0, layer),
            _fp_circle(7.62, 7.62, layer),
        ]
    for n in "12345678":
        lines.append(_pad(n))
    lines += ["\t\t(embedded_fonts no)", "\t)"]
    return "\n".join(lines)


def main() -> None:
    text = PCB.read_text(encoding="utf-8")
    m = re.search(
        r'\t\(footprint "Injet:U8628".*?\t\(footprint "Injet:U8"',
        text,
        re.DOTALL,
    )
    if not m:
        raise SystemExit("U5 footprint Injet:U8628 not found")

    old = m.group(0)
    at_m = re.search(r"\(at ([\d.]+) ([\d.]+)", old)
    if not at_m:
        raise SystemExit("U5 position not found")
    at_x, at_y = float(at_m.group(1)), float(at_m.group(2))

    new_fp = build_footprint(at_x, at_y) + '\n\t(footprint "Injet:U8"'
    patched = text[: m.start()] + new_fp + text[m.end() :]
    PCB.write_text(patched, encoding="utf-8")
    print(f"OK - U5 @ ({at_x}, {at_y}) -> Injet:U388 OPA388IDR DIP-8 F.Cu")


if __name__ == "__main__":
    main()
