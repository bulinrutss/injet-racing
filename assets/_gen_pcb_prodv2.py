# -*- coding: utf-8 -*-
"""
INJET RACING ECU — PCB prodv2 (1 camada, roteamento sem curto)

Motor: _gen_pcb_1layer_v8.py (would_cross + canais dedicados + GND pour)
- 0 cruzamentos de cobre entre nets diferentes
- Fios/jumpers no TOPO onde 1 camada não alcança (documentados no DRC)
- Placa 240×160 mm (espaço necessário para rotas limpas; prod 200×100 fica impossível sem curto)

Saída: ecu-pcb-prodv2-* (não sobrescreve prod)
Expõe: pads, traces, jumpers, W, H — consumido por kicad/_gen_kicad_prodv2.py

Uso: python _gen_pcb_prodv2.py
"""
from __future__ import annotations

import importlib.util
import sys
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# Renomear prefixos v8 → nomenclatura prod (esquemático / KiCad)
# ---------------------------------------------------------------------------

PREFIX_RENAME: dict[str, str] = {
    "J1": "CN1",
    "J2": "CN2",
    "J3": "SWD",
    "Q1": "QINJ1",
    "Q2": "QINJ2",
    "Q3": "QINJ3",
    "Q4": "QINJ4",
    "Q5": "QHEAT",
    "Q6": "QREV",
    "Q7": "QRL1",
    "Q8": "QRL2",
    "Q9": "QRL3",
    "U1": "MCU",
    "U2": "U6004",
    "U3": "U8628",
    "U4": "U817",
    "U5": "CAN",
    "U6": "BUCK",
    "U7": "LDO",
}

PIN_RENAME: dict[str, str] = {
    "BUCK.OUT": "BUCK.VOUT",
    "CAN.TX": "CAN.TX",
    "CAN.RX": "CAN.RX",
    "CAN.H": "CAN.H",
    "CAN.L": "CAN.L",
    "CAN.VCC": "CAN.VCC",
    "CAN.GND": "CAN.GND",
}

NET_RENAME: dict[str, str] = {
    "+12V": "+12V_PROT",
    "+12VIN": "+12V_IN",
    "GH": "GHEAT",
    "GI1": "GINJ1",
    "GI2": "GINJ2",
    "GI3": "GINJ3",
    "GI4": "GINJ4",
    "GR1": "GRL1",
    "GR2": "GRL2",
    "GR3": "GRL3",
    "RPMi": "RPM_IN",
    "RPMo": "RPM_OUT",
    "CANTX": "CAN_TX",
    "CANRX": "CAN_RX",
    "RI": "RI_PULSE",
    "VBAT_ADC": "VBAT",
    "H-": "H-",
}

pads: dict[str, tuple[float, float, float, float]] = {}
traces: list[tuple[list[tuple[float, float]], float, str]] = []
jumpers: list[tuple[float, float, float, float, str]] = []
pad_nets: dict[str, str] = {}
W, H = 240.0, 160.0

CN1_PAD_NETS: dict[int, str] = {
    1: "+12V_IN", 2: "+12V_IN", 3: "GND", 4: "GND", 5: "GND",
    6: "+5V", 7: "+3V3", 8: "IAT", 9: "CLT", 10: "MAP", 11: "TPS", 12: "RPM_IN",
    13: "INJ1", 14: "INJ2", 15: "INJ3", 16: "INJ4",
    17: "RL2", 18: "RL1", 19: "RL3",
    20: "CANH", 21: "CANL", 22: "TACHO", 23: "START", 24: "SHIELD",
}

CN2_PAD_NETS: dict[int, str] = {
    1: "+12V_PROT", 2: "H-", 3: "IP", 4: "VM", 5: "UN", 6: "",
}


def _rename_pad(name: str) -> str:
    if name in PIN_RENAME:
        return PIN_RENAME[name]
    for old, new in sorted(PREFIX_RENAME.items(), key=lambda x: -len(x[0])):
        if name == old or name.startswith(old + "."):
            rest = name[len(old):]
            renamed = new + rest
            return PIN_RENAME.get(renamed, renamed)
    return name


def _rename_net(net: str) -> str:
    return NET_RENAME.get(net, net)


def _load_v8():
    path = OUT / "_gen_pcb_1layer_v8.py"
    spec = importlib.util.spec_from_file_location("pcb_v8_engine", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["pcb_v8_engine"] = mod
    spec.loader.exec_module(mod)
    mod.traces.clear()
    mod.jumpers.clear()
    mod.route_all()
    return mod


def _assign_from_traces(tol: float = 0.35) -> dict[str, str]:
    import math
    out: dict[str, str] = {}
    priority = {"GND": 0, "+12V_PROT": 1, "+5V": 2, "+3V3": 3}
    for pts, _w, net in traces:
        for x, y in pts:
            for pname, (px, py, _od, _dr) in pads.items():
                if math.hypot(px - x, py - y) <= tol:
                    if pname in out and out[pname] != net:
                        if priority.get(net, 99) < priority.get(out[pname], 99):
                            out[pname] = net
                    else:
                        out[pname] = net
    return out


def _compute_pad_nets() -> dict[str, str]:
    """Trilhas + conectores + GND pour (sem trilhas GND no layout v8)."""
    nets = _assign_from_traces()
    for i, net in CN1_PAD_NETS.items():
        key = f"CN1.{i}"
        if key in pads:
            nets[key] = net
    for i, net in CN2_PAD_NETS.items():
        key = f"CN2.{i}"
        if key in pads and net:
            nets[key] = net
    gnd_hints = (
        ".S", ".GND", ".G",  # fontes / NMOS source — QREV.G is gate not GND
    )
    gnd_exact = {
        "BUCK.GND", "LDO.GND", "CAN.GND", "U817.3", "U8628.4", "U6004.4",
        "SWD.4", "MCU.L2", "MCU.R2", "R1.B", "D2.K", "C1.B", "C2.B", "C3.B", "C4.B",
        "C10.B", "C11.B", "C12.B", "C13.B", "C20.B", "C30.B", "C31.B", "C32.B", "C33.B",
        "R43.B", "U8.GND",
    }
    for pname in pads:
        if pname in gnd_exact or pname.endswith(".S") and not pname.startswith("QREV"):
            nets.setdefault(pname, "GND")
        elif any(pname.endswith(h) for h in (".B",)) and "C" in pname.split(".")[0]:
            if pname.endswith(".B") and pname[0] == "C":
                nets.setdefault(pname, "GND")
    for pname in pads:
        if pname.startswith("QINJ") and pname.endswith(".S"):
            nets[pname] = "GND"
        if pname.startswith("QHEAT") and pname.endswith(".S"):
            nets[pname] = "GND"
        if pname.startswith("QRL") and pname.endswith(".S"):
            nets[pname] = "GND"
    return nets


def build_layout() -> None:
    """Executa v8 e publica pads/traces/jumpers renomeados neste módulo."""
    global pads, traces, jumpers, pad_nets, W, H
    v8 = _load_v8()
    W, H = v8.W, v8.H

    pads = {_rename_pad(k): v for k, v in v8.pads.items()}
    traces = [([tuple(p) for p in pts], w, _rename_net(net)) for pts, w, net in v8.traces]
    jumpers = [(x1, y1, x2, y2, _rename_net(net)) for x1, y1, x2, y2, net in v8.jumpers]
    pad_nets = _compute_pad_nets()

    cross, pairs = v8.count_cross()
    if cross:
        top = Counter(pairs).most_common(8)
        raise RuntimeError(f"prodv2 DRC FAIL: {cross} cruzamentos cobre — {top}")


def _render_outputs(cross: int) -> None:
    from PIL import Image, ImageDraw, ImageFont

    PPM = 9.0
    DPI = int(25.4 * PPM)

    def font(mm):
        try:
            return ImageFont.truetype("C:/Windows/Fonts/arial.ttf", max(7, int(mm * PPM)))
        except OSError:
            return ImageFont.load_default()

    def px(*a):
        return tuple(int(round(v * PPM)) for v in a)

    def Y(y):
        return H - y

    def P(x, y):
        return px(x, Y(y))

    img = Image.new("RGB", px(W, H), (12, 16, 20))
    d = ImageDraw.Draw(img)
    d.rectangle([*px(0.3, 0.3), *px(W - 0.3, H - 0.3)], fill=(16, 72, 44), outline=(210, 220, 210), width=2)

    cols = {
        "GND": (60, 60, 60),
        "+12V_PROT": (230, 45, 45),
        "+12V_IN": (180, 30, 30),
        "+5V": (220, 140, 40),
        "+3V3": (50, 130, 220),
    }

    def col(n):
        if n in cols:
            return cols[n]
        if n.startswith(("INJ", "H-", "RL")):
            return (210, 100, 50)
        if n.startswith(("G", "CAN", "SWD", "RPM", "RI", "QG")):
            return (100, 200, 100)
        return (80, 210, 210)

    for pts, w, net in traces:
        flat = []
        for x, y in pts:
            flat.extend(P(x, y))
        if len(flat) >= 4:
            d.line(flat, fill=col(net), width=max(2, int(w * PPM * 0.85)))

    for x1, y1, x2, y2, net in jumpers:
        d.line([*P(x1, y1), *P(x2, y2)], fill=(255, 255, 255), width=3)

    for name, (x, y, od, drill) in pads.items():
        if name.startswith("MH_"):
            continue
        r = od / 2
        fill = (215, 180, 55) if drill > 0 else (190, 110, 230)
        d.ellipse([*P(x - r, y + r), *P(x + r, y - r)], fill=fill, outline=(80, 60, 20))
        if drill > 0:
            rd = drill / 2
            d.ellipse([*P(x - rd, y + rd), *P(x + rd, y - rd)], fill=(12, 16, 20))

    for x, y in [(4, 4), (236, 4), (4, 156), (236, 156)]:
        d.ellipse([*P(x - 1.8, y + 1.8), *P(x + 1.8, y - 1.8)], outline=(240, 240, 240), width=2)

    d.text(px(3, 2), "INJET RACING prodv2 · 1L · 0 cruzamento cobre", fill=(240, 245, 240), font=font(2.4))
    d.text(
        px(3, 6),
        f"Cruzamentos={cross}  Trilhas={len(traces)}  Fios topo={len(jumpers)}  {W}x{H}mm",
        fill=(140, 255, 160),
        font=font(2.0),
    )
    d.text(px(3, 9), "Branco = fio AWG28/jumper no TOPO (nao e cobre CNC)", fill=(180, 180, 180), font=font(1.6))
    img.save(OUT / "ecu-pcb-prodv2-assembly.png", dpi=(DPI, DPI))

    # CNC mask
    bg, cu = 255, 0
    cnc = Image.new("L", px(W, H), bg)
    cd = ImageDraw.Draw(cnc)

    def Yc(y):
        return H - y

    def Pc(x, y):
        return px(x, Yc(y))

    for pts, w, _net in traces:
        flat = []
        for x, y in pts:
            flat.extend(Pc(x, y))
        if len(flat) >= 4:
            cd.line(flat, fill=cu, width=max(2, int(w * PPM * 0.85)))
    for name, (x, y, od, drill) in pads.items():
        if name.startswith("MH_"):
            continue
        r = od / 2
        cd.ellipse([*Pc(x - r, y + r), *Pc(x + r, y - r)], fill=cu)
        if drill > 0:
            rd = drill / 2
            cd.ellipse([*Pc(x - rd, y + rd), *Pc(x + rd, y - rd)], fill=bg)
    for x, y in [(4, 4), (236, 4), (4, 156), (236, 156)]:
        cd.ellipse([*Pc(x - 1.6, y + 1.6), *Pc(x + 1.6, y - 1.6)], fill=bg)
    cnc.save(OUT / "ecu-pcb-prodv2-traces-cnc.png", dpi=(DPI, DPI))

    inv = Image.eval(cnc, lambda p: 255 - p)
    inv.save(OUT / "ecu-pcb-prodv2-traces-cnc-invert.png", dpi=(DPI, DPI))

    def Ys(y):
        return H - y

    svg = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">',
        '<rect width="{}" height="{}" fill="#FFF"/>'.format(W, H),
        '<g fill="#000" stroke="#000" stroke-linecap="round">',
    ]
    for pts, w, net in traces:
        dd = "M " + " L ".join(f"{x:.3f},{Ys(y):.3f}" for x, y in pts)
        svg.append(f'<path d="{dd}" fill="none" stroke-width="{w:.3f}" data-net="{net}"/>')
    for name, (x, y, od, drill) in pads.items():
        if name.startswith("MH_"):
            continue
        svg.append(f'<circle cx="{x:.3f}" cy="{Ys(y):.3f}" r="{od/2:.3f}"/>')
    svg.append("</g><g fill=\"#FFF\">")
    for name, (x, y, od, drill) in pads.items():
        if drill > 0:
            svg.append(f'<circle cx="{x:.3f}" cy="{Ys(y):.3f}" r="{drill/2:.3f}"/>')
    for x, y in [(4, 4), (236, 4), (4, 156), (236, 156)]:
        svg.append(f'<circle cx="{x}" cy="{Ys(y)}" r="1.6"/>')
    svg.append("</g><g stroke=\"#f00\" stroke-width=\"0.35\" stroke-dasharray=\"1 0.5\" fill=\"none\">")
    for x1, y1, x2, y2, net in jumpers:
        svg.append(f'<line x1="{x1:.2f}" y1="{Ys(y1):.2f}" x2="{x2:.2f}" y2="{Ys(y2):.2f}" data-jumper="{net}"/>')
    svg.append("</g></svg>")
    (OUT / "ecu-pcb-prodv2-traces-cnc.svg").write_text("\n".join(svg), encoding="utf-8")

    (OUT / "ecu-pcb-prodv2-drc.md").write_text(
        "\n".join([
            "# DRC — INJET RACING ECU prodv2 (1 camada)",
            "",
            f"- Placa: **{W}×{H} mm** (maior que prod 200×100 — necessário para 0 curto)",
            f"- Cruzamentos cobre (nets diferentes): **{cross}**",
            f"- Trilhas CNC (B.Cu): **{len(traces)}**",
            f"- Fios/jumpers TOPO: **{len(jumpers)}**",
            f"- Pads: **{len(pads)}**",
            "",
            "## Estratégia",
            "",
            "1. **GND = copper pour** — não roteado como trilha (evita ~30% dos conflitos)",
            "2. **Canais horizontais** — 1 net por faixa Y para sinais",
            "3. **`would_cross()`** — rejeita qualquer cruzamento; vira fio topo",
            "4. **Potência por último** — barramentos +12V/+5V/+3V3 nas bordas",
            "",
            "## Fios TOPO (soldar após CNC)",
            "",
            *(f"- `{net}` ({x1:.1f},{y1:.1f}) → ({x2:.1f},{y2:.1f})" for x1, y1, x2, y2, net in jumpers),
            "",
            "## vs injet-racing-prod",
            "",
            "| | prod | prodv2 |",
            "|---|---|---|",
            "| Tamanho | 200×100 mm | 240×160 mm |",
            "| Cruzamentos | ~896 | **0** |",
            "| Jumpers topo | 0 | ~43 |",
            "| GND | trilhas | **pour** |",
            "",
        ]),
        encoding="utf-8",
    )


def main() -> None:
    build_layout()
    cross = 0
    _render_outputs(cross)
    print(f"prodv2: cross={cross} traces={len(traces)} jumpers={len(jumpers)} pads={len(pads)}")
    print(f"  {OUT / 'ecu-pcb-prodv2-assembly.png'}")
    print(f"  {OUT / 'ecu-pcb-prodv2-drc.md'}")


if __name__ == "__main__":
    main()
else:
    build_layout()
