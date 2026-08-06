# -*- coding: utf-8 -*-
"""
INJET RACING — PCB 1-LAYER SEM CURTO (barramentos + corredores)
200×100 mm | cobre 1 face | THT topo | AD8628 SMD no cobre

Estratégia clássica 1-layer:
  • GND  = faixa contínua em Y baixo
  • +12V = faixa contínua em Y alto
  • +5V / +3V3 = faixas horizontais dedicadas
  • Sinais = corredores horizontais exclusivos (1 net por faixa Y)
  • Descida vertical só na coluna do pad (não atravessa outro corredor ocupado)
  • Jumper (fio TOPO) só se corredor esgotado
"""
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(r"e:\injet racing\assets")
W, H = 200.0, 100.0
PPM = 12.0
DPI = int(25.4 * PPM)

pads: dict[str, tuple[float, float, float, float]] = {}
outlines: list[tuple] = []
traces: list[tuple] = []  # (pts, w, net)
jumpers: list[tuple] = []  # (x1,y1,x2,y2,net) fio TOPO
# Ocupação de corredores horizontais: y_mm -> net|None  (faixas de sinal)
# Para cada coluna X, segmentos Y ocupados por net
seg_occ: list[tuple[float, float, float, float, str]] = []  # x1,y1,x2,y2,net axis-aligned


def font(mm):
    try:
        return ImageFont.truetype("C:/Windows/Fonts/arial.ttf", max(9, int(mm * PPM)))
    except OSError:
        return ImageFont.load_default()


def px(*a):
    return tuple(int(round(v * PPM)) for v in a)


def pad(n, x, y, od=1.9, drill=0.95):
    pads[n] = (x, y, od, drill)


def axial(a, b, x1, y1, x2, y2, od=1.7, dr=0.85):
    pad(a, x1, y1, od, dr)
    pad(b, x2, y2, od, dr)


def to220(p, x, y):
    pad(f"{p}.G", x - 2.54, y, 2.3, 1.1)
    pad(f"{p}.D", x, y, 2.3, 1.1)
    pad(f"{p}.S", x + 2.54, y, 2.3, 1.1)
    outlines.append((x - 5, y - 1, x + 5, y + 10, p, "top"))


def to92(p, x, y):
    pad(f"{p}.S", x - 1.27, y, 1.6, 0.8)
    pad(f"{p}.G", x, y + 1.8, 1.6, 0.8)
    pad(f"{p}.D", x + 1.27, y, 1.6, 0.8)
    outlines.append((x - 3, y - 1, x + 3, y + 5, p, "top"))


def dip(p, x0, y0, n, pitch=2.54, row=7.62):
    h = n // 2
    for i in range(h):
        pad(f"{p}.{i+1}", x0, y0 + i * pitch, 1.7, 0.85)
        pad(f"{p}.{n-i}", x0 + row, y0 + i * pitch, 1.7, 0.85)
    outlines.append((x0 - 1, y0 - 1, x0 + row + 1, y0 + (h - 1) * pitch + 1, p, "top"))


def soic8(p, x0, y0):
    for i in range(4):
        pad(f"{p}.{i+1}", x0, y0 + i * 1.27, 1.3, 0.0)
        pad(f"{p}.{8-i}", x0 + 5.4, y0 + i * 1.27, 1.3, 0.0)
    outlines.append((x0 - 1, y0 - 1, x0 + 6.4, y0 + 4.8, p + " SMD↓", "bot"))


def overlaps(a1, a2, b1, b2, gap=0.55):
    lo1, hi1 = min(a1, a2), max(a1, a2)
    lo2, hi2 = min(b1, b2), max(b1, b2)
    return not (hi1 + gap < lo2 or hi2 + gap < lo1)


def seg_conflicts(x1, y1, x2, y2, net, w):
    """Conflito se segmento intersecta outro net (eixos alinhados)."""
    gap = w / 2 + 0.45
    horiz = abs(y1 - y2) < 0.01
    for ox1, oy1, ox2, oy2, onet in seg_occ:
        if onet == net:
            continue
        oh = abs(oy1 - oy2) < 0.01
        if horiz and oh:
            # paralelos horizontais
            if abs(y1 - oy1) < gap and overlaps(x1, x2, ox1, ox2, gap):
                return True
        elif not horiz and not oh:
            if abs(x1 - ox1) < gap and overlaps(y1, y2, oy1, oy2, gap):
                return True
        elif horiz and not oh:
            # H cruzando V
            if overlaps(x1, x2, ox1, ox1, 0) and overlaps(oy1, oy2, y1, y1, 0):
                if onet != net:
                    return True
        elif not horiz and oh:
            if overlaps(y1, y2, oy1, oy1, 0) and overlaps(ox1, ox2, x1, x1, 0):
                if onet != net:
                    return True
    return False


def add_seg(x1, y1, x2, y2, net, w):
    if abs(x1 - x2) < 0.01 and abs(y1 - y2) < 0.01:
        return True
    if seg_conflicts(x1, y1, x2, y2, net, w):
        return False
    seg_occ.append((x1, y1, x2, y2, net))
    return True


def commit_path(pts, net, w):
    for i in range(len(pts) - 1):
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]
        if not add_seg(x1, y1, x2, y2, net, w):
            return False
    traces.append((pts, w, net))
    return True


def try_path(pts, net, w):
    """Tenta sem gravar; se ok, grava."""
    # dry-run
    saved = len(seg_occ)
    ok = True
    for i in range(len(pts) - 1):
        if not add_seg(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], net, w):
            ok = False
            break
    if not ok:
        del seg_occ[saved:]
        return False
    traces.append((pts, w, net))
    return True


def route_manhattan(net, ax, ay, bx, by, w, via_ys):
    """Tenta L e Z com via_ys candidatos (corredores livres)."""
    candidates = []
    # direto H-V
    candidates.append([(ax, ay), (bx, ay), (bx, by)])
    candidates.append([(ax, ay), (ax, by), (bx, by)])
    for vy in via_ys:
        candidates.append([(ax, ay), (ax, vy), (bx, vy), (bx, by)])
        candidates.append([(ax, ay), (bx, vy), (bx, by)])  # se ay==vy degenera
    # perimeter escapes
    for vy in (3.0, 97.0):
        candidates.append([(ax, ay), (ax, vy), (bx, vy), (bx, by)])
    for vx in (3.0, 197.0):
        candidates.append([(ax, ay), (vx, ay), (vx, by), (bx, by)])

    for pts in candidates:
        # limpa pontos duplicados
        clean = [pts[0]]
        for p in pts[1:]:
            if abs(p[0] - clean[-1][0]) > 0.01 or abs(p[1] - clean[-1][1]) > 0.01:
                clean.append(p)
        if len(clean) < 2:
            continue
        if try_path(clean, net, w):
            return True
    return False


def route_pads(net, a, b, w, vias):
    if a not in pads or b not in pads:
        print("skip missing", a, b)
        return False
    ax, ay = pads[a][0], pads[a][1]
    bx, by = pads[b][0], pads[b][1]
    if route_manhattan(net, ax, ay, bx, by, w, vias):
        return True
    # Jumper no TOPO: tenta aterrar cobre em pads de jumper sem poluir se falhar
    for jy2 in (20.0, 25.0, 30.0, 50.0, 55.0, 70.0, 18.0):
        for jx2 in (55.0, 75.0, 95.0, 115.0, 135.0, 155.0):
            snap = len(seg_occ)
            ntr = len(traces)
            p1 = [(ax, ay), (ax, jy2), (jx2, jy2)]
            p2 = [(bx, by), (bx, jy2 + 1.5), (jx2 + 3.0, jy2 + 1.5)]
            if try_path(p1, net, w) and try_path(p2, net, w):
                jumpers.append((jx2, jy2, jx2 + 3.0, jy2 + 1.5, net))
                pad(f"JMP{len(jumpers)}.A", jx2, jy2, 1.7, 0.9)
                pad(f"JMP{len(jumpers)}.B", jx2 + 3.0, jy2 + 1.5, 1.7, 0.9)
                return True
            del seg_occ[snap:]
            del traces[ntr:]
    # Último recurso: fio inteiro no topo (sem cobre entre A e B)
    jumpers.append((ax, ay, bx, by, net + " WIRE"))
    return False


def bus(net, x1, x2, y, w):
    try_path([(x1, y), (x2, y)], net, w)


def stub(net, padname, bus_y, w):
    x, y = pads[padname][0], pads[padname][1]
    try_path([(x, y), (x, bus_y)], net, w)


# ===================== PLACE =====================
ATX = 4.2
for i in range(12):
    pad(f"CN1.{i+1}", 6 + i * ATX, 12, 2.2, 1.1)
    pad(f"CN1.{i+13}", 6 + i * ATX, 6.5, 2.2, 1.1)
outlines.append((3, 4, 6 + 11 * ATX + 2, 15, "CN1 ATX-24", "top"))

for i in range(3):
    pad(f"CN2.{i+1}", 176 + i * ATX, 12, 2.2, 1.1)
    pad(f"CN2.{i+4}", 176 + i * ATX, 6.5, 2.2, 1.1)
outlines.append((173, 4, 176 + 2 * ATX + 2, 15, "CN2 PCIe-6", "top"))

to220("QREV", 14, 90)
axial("CBULK.A", "CBULK.K", 26, 92, 34, 92, 2.4, 0.9)
axial("CIN.A", "CIN.K", 26, 86, 30, 86)
axial("TVS.A", "TVS.K", 38, 92, 38, 86)
axial("RG.A", "RG.B", 8, 84, 8, 78)
axial("DZ.A", "DZ.K", 12, 84, 12, 78)
pad("BUCK.VIN", 46, 92, 2.0, 1.0)
pad("BUCK.GND", 52, 92, 2.0, 1.0)
pad("BUCK.OUT", 46, 84, 2.0, 1.0)
pad("LDO.IN", 58, 92, 2.0, 1.0)
pad("LDO.GND", 64, 92, 2.0, 1.0)
pad("LDO.OUT", 61, 84, 2.0, 1.0)
axial("C5.A", "C5.B", 68, 92, 72, 92)
axial("C33.A", "C33.B", 68, 86, 72, 86)
outlines.append((44, 81, 74, 95, "POWER", "top"))

for i, x in enumerate([84, 98, 112, 126]):
    to220(f"Q{i+1}", x, 90)
    axial(f"Rg{i+1}.A", f"Rg{i+1}.B", x - 2.54, 82, x - 2.54, 76)
    axial(f"Rgs{i+1}.A", f"Rgs{i+1}.B", x - 2.54, 74, x, 74)
    axial(f"Df{i+1}.A", f"Df{i+1}.K", x + 5, 90, x + 5, 84)

to220("QH", 146, 90)
axial("Rgh.A", "Rgh.B", 143.46, 82, 143.46, 76)
axial("Rgsh.A", "Rgsh.B", 143.46, 74, 148, 74)

for i, x in enumerate([10, 20, 30]):
    to92(f"QR{i+1}", x, 58)
    axial(f"Rr{i+1}.A", f"Rr{i+1}.B", x, 52, x, 46)
    axial(f"Dr{i+1}.A", f"Dr{i+1}.K", x + 4, 58, x + 4, 52)

for i in range(20):
    pad(f"ML{i+1}", 70, 66 - i * 2.54, 1.6, 0.9)
    pad(f"MR{i+1}", 122, 66 - i * 2.54, 1.6, 0.9)
outlines.append((68, 14, 124, 68, "STM32F407", "top"))
for i in range(4):
    pad(f"SWD.{i+1}", 88 + i * 2.54, 22, 1.7, 0.95)

for n, y in [("IAT", 64), ("CLT", 56), ("MAP", 48), ("TPS", 40)]:
    if n != "TPS":
        axial(f"R{n}.A", f"R{n}.B", 148, y, 156, y)
    if n == "MAP":
        axial("Rm2.A", "Rm2.B", 156, y, 156, y - 4)
    axial(f"C{n}.A", f"C{n}.B", 160, y, 160, y - 3.5)
    axial(f"S{n}.A", f"S{n}.B", 164, y, 172, y)
outlines.append((146, 34, 176, 68, "SENS", "top"))

dip("U817", 44, 28, 4)
axial("Rra.A", "Rra.B", 34, 32, 42, 32)
axial("Rrb.A", "Rrb.B", 26, 32, 34, 32)
axial("Drpm.A", "Drpm.K", 38, 28, 38, 23)
axial("Rrp.A", "Rrp.B", 54, 36, 54, 30)
axial("Cr.A", "Cr.B", 58, 30, 58, 25)
outlines.append((24, 20, 62, 40, "RPM", "top"))

for i, nm in enumerate(["CV", "CG", "CT", "CR", "CH", "CL"]):
    pad(f"CAN.{nm}", 88 + (i % 3) * 6, 36 - (i // 3) * 6, 1.8, 1.0)
outlines.append((86, 28, 108, 40, "CAN", "top"))

dip("U6", 132, 18, 14)
soic8("U8", 158, 20)
axial("Rsh.A", "Rsh.B", 152, 34, 160, 34)
axial("Res.A", "Res.B", 152, 40, 160, 40)
axial("Cip.A", "Cip.B", 164, 34, 164, 29)
axial("Cun.A", "Cun.B", 168, 40, 168, 35)
axial("C5a.A", "C5a.B", 128, 26, 128, 21)
axial("Ro1.A", "Ro1.B", 140, 26, 148, 26)
axial("Ro2.A", "Ro2.B", 148, 26, 148, 21)
outlines.append((126, 14, 174, 44, "LAMBDA", "top"))


SIG_Y = {
    "IAT": 63.0, "CLT": 55.0, "MAP": 47.0, "TPS": 39.0,
    "INJ1": 75.0, "INJ2": 73.5, "INJ3": 72.0, "INJ4": 70.5,
    "GI1": 69.0, "GI2": 67.5, "GI3": 61.0, "GI4": 59.5,
    "GH": 58.0, "H-": 76.5,
    "RL1": 57.0, "RL2": 54.0, "RL3": 51.0,
    "GR1": 49.5, "GR2": 45.5, "GR3": 42.5,
    "RPMi": 33.0, "RPMo": 31.0,
    "CANTX": 37.0, "CANRX": 35.0, "CANH": 29.0, "CANL": 27.0,
    "IP": 41.0, "UN": 43.0, "VM": 24.0, "O2": 26.0, "RI": 23.0,
    "SWDIO": 21.0, "SWCLK": 19.5, "QG": 80.0,
}
YGND, Y12, Y5, Y33 = 2.8, 97.0, 79.0, 71.0


def run():
    bus("GND", 4, 196, YGND, 2.4)
    bus("+12VP", 4, 196, Y12, 2.2)
    bus("+5V", 40, 190, Y5, 1.5)
    bus("+3V3", 55, 190, Y33, 1.4)

    for n in [
        "CN1.3", "CN1.4", "CN1.5", "CN1.24",
        "CBULK.K", "CIN.K", "TVS.K", "DZ.K", "RG.B", "BUCK.GND", "LDO.GND", "C5.B", "C33.B",
        "Q1.S", "Q2.S", "Q3.S", "Q4.S", "QH.S",
        "Rgs1.B", "Rgs2.B", "Rgs3.B", "Rgs4.B", "Rgsh.B",
        "QR1.S", "QR2.S", "QR3.S",
        "ML2", "MR2", "SWD.4",
        "CIAT.B", "CCLT.B", "CMAP.B", "CTPS.B", "Rm2.B",
        "U817.3", "Cr.B", "CAN.CG",
        "C5a.B", "Cip.B", "Cun.B", "U6.4", "U8.4", "Ro2.B",
    ]:
        if n in pads:
            stub("GND", n, YGND, 1.0 if not n.startswith("Q") else 1.6)

    route_pads("+12VIN", "CN1.1", "QREV.D", 1.8, [16, 18, 85])
    route_pads("+12VIN", "CN1.2", "QREV.D", 1.6, [17, 19, 86])
    route_pads("QG", "QREV.G", "RG.A", 0.7, [SIG_Y["QG"]])
    route_pads("QG", "QREV.G", "DZ.A", 0.7, [SIG_Y["QG"] + 0.8])

    for n in ["QREV.S", "CBULK.A", "CIN.A", "TVS.A", "BUCK.VIN",
              "Df1.K", "Df2.K", "Df3.K", "Df4.K", "Dr1.K", "Dr2.K", "Dr3.K", "CN2.1"]:
        stub("+12VP", n, Y12, 1.3)

    for i in range(1, 5):
        route_pads(f"INJ{i}", f"Df{i}.A", f"Q{i}.D", 1.0, [88])
    for i in range(1, 4):
        route_pads(f"RL{i}", f"Dr{i}.A", f"QR{i}.D", 0.9, [58])

    for n in ["BUCK.OUT", "LDO.IN", "C5.A", "CN1.6", "MR1", "C5a.A", "U6.14", "U8.8"]:
        stub("+5V", n, Y5, 1.1)
    for n in ["LDO.OUT", "C33.A", "ML1", "SWD.1", "CN1.7", "RIAT.A", "RCLT.A", "Rrp.A", "CAN.CV"]:
        if n in pads:
            stub("+3V3", n, Y33, 1.0)

    for i, cn in enumerate([13, 14, 15, 16], 1):
        route_pads(f"INJ{i}", f"Q{i}.D", f"CN1.{cn}", 1.3, [SIG_Y[f"INJ{i}"]])
        route_pads(f"GI{i}", f"ML{12+i}", f"Rg{i}.B", 0.75, [SIG_Y[f"GI{i}"]])
        route_pads(f"GI{i}", f"Rg{i}.A", f"Q{i}.G", 0.7, [SIG_Y[f"GI{i}"] + 0.3])
        route_pads(f"GI{i}", f"Rgs{i}.A", f"Q{i}.G", 0.65, [SIG_Y[f"GI{i}"] + 0.5])

    route_pads("GH", "ML20", "Rgh.B", 0.75, [SIG_Y["GH"]])
    route_pads("GH", "Rgh.A", "QH.G", 0.7, [SIG_Y["GH"] + 0.3])
    route_pads("GH", "Rgsh.A", "QH.G", 0.65, [SIG_Y["GH"] + 0.5])
    route_pads("H-", "QH.D", "CN2.2", 1.6, [SIG_Y["H-"]])

    rl_cn = {1: 18, 2: 17, 3: 19}
    for i in range(1, 4):
        route_pads(f"RL{i}", f"QR{i}.D", f"CN1.{rl_cn[i]}", 1.0, [SIG_Y[f"RL{i}"]])
        route_pads(f"GR{i}", f"ML{16+i}", f"Rr{i}.B", 0.7, [SIG_Y[f"GR{i}"]])
        route_pads(f"GR{i}", f"Rr{i}.A", f"QR{i}.G", 0.65, [SIG_Y[f"GR{i}"] + 0.3])

    route_pads("IAT", "CN1.8", "RIAT.B", 0.8, [SIG_Y["IAT"]])
    route_pads("IAT", "RIAT.B", "CIAT.A", 0.65, [SIG_Y["IAT"]])
    route_pads("IAT", "RIAT.B", "SIAT.A", 0.65, [SIG_Y["IAT"]])
    route_pads("IAT", "SIAT.B", "ML3", 0.8, [SIG_Y["IAT"]])

    route_pads("CLT", "CN1.9", "RCLT.B", 0.8, [SIG_Y["CLT"]])
    route_pads("CLT", "RCLT.B", "CCLT.A", 0.65, [SIG_Y["CLT"]])
    route_pads("CLT", "RCLT.B", "SCLT.A", 0.65, [SIG_Y["CLT"]])
    route_pads("CLT", "SCLT.B", "ML4", 0.8, [SIG_Y["CLT"]])

    route_pads("MAP", "CN1.10", "RMAP.B", 0.8, [SIG_Y["MAP"]])
    route_pads("MAP", "RMAP.B", "Rm2.A", 0.65, [SIG_Y["MAP"]])
    route_pads("MAP", "RMAP.B", "CMAP.A", 0.65, [SIG_Y["MAP"]])
    route_pads("MAP", "RMAP.B", "SMAP.A", 0.65, [SIG_Y["MAP"]])
    route_pads("MAP", "SMAP.B", "ML5", 0.8, [SIG_Y["MAP"]])

    route_pads("TPS", "CN1.11", "STPS.A", 0.8, [SIG_Y["TPS"]])
    route_pads("TPS", "STPS.A", "CTPS.A", 0.65, [SIG_Y["TPS"]])
    route_pads("TPS", "STPS.B", "ML6", 0.8, [SIG_Y["TPS"]])

    route_pads("RPMi", "CN1.12", "Rrb.A", 0.85, [SIG_Y["RPMi"]])
    route_pads("RPMi", "Rrb.B", "Rra.A", 0.8, [SIG_Y["RPMi"]])
    route_pads("RPMi", "Rra.B", "U817.1", 0.75, [SIG_Y["RPMi"]])
    stub("GND", "U817.2", YGND, 0.8)
    route_pads("RPMi", "Drpm.A", "U817.1", 0.6, [SIG_Y["RPMi"] + 0.5])
    route_pads("RPMi", "Drpm.K", "U817.2", 0.6, [SIG_Y["RPMi"] + 0.7])
    route_pads("RPMo", "U817.4", "Rrp.B", 0.7, [SIG_Y["RPMo"]])
    route_pads("RPMo", "U817.4", "Cr.A", 0.6, [SIG_Y["RPMo"]])
    route_pads("RPMo", "U817.4", "ML10", 0.8, [SIG_Y["RPMo"]])

    route_pads("CANTX", "ML12", "CAN.CT", 0.7, [SIG_Y["CANTX"]])
    route_pads("CANRX", "ML11", "CAN.CR", 0.7, [SIG_Y["CANRX"]])
    route_pads("CANH", "CAN.CH", "CN1.20", 0.9, [SIG_Y["CANH"]])
    route_pads("CANL", "CAN.CL", "CN1.21", 0.9, [SIG_Y["CANL"]])

    route_pads("IP", "CN2.3", "Rsh.A", 0.9, [SIG_Y["IP"]])
    route_pads("IP", "Rsh.B", "Cip.A", 0.65, [SIG_Y["IP"]])
    route_pads("IP", "Rsh.B", "ML8", 0.8, [SIG_Y["IP"]])
    route_pads("IP", "U8.6", "Rsh.A", 0.7, [SIG_Y["IP"] + 0.4])
    route_pads("IP", "U8.2", "Rsh.A", 0.65, [SIG_Y["IP"] + 0.6])

    route_pads("VM", "MR3", "U6.3", 0.7, [SIG_Y["VM"]])
    route_pads("VM", "U6.1", "U6.2", 0.6, [SIG_Y["VM"] + 0.3])
    route_pads("VM", "U6.1", "CN2.4", 0.8, [SIG_Y["VM"]])
    route_pads("VM", "U8.3", "CN2.4", 0.65, [SIG_Y["VM"] + 0.5])

    route_pads("UN", "CN2.5", "Res.A", 0.85, [SIG_Y["UN"]])
    route_pads("UN", "Res.A", "Cun.A", 0.65, [SIG_Y["UN"]])
    route_pads("UN", "Res.A", "ML9", 0.8, [SIG_Y["UN"]])
    route_pads("RI", "MR8", "Res.B", 0.7, [SIG_Y["RI"]])

    route_pads("O2", "U6.7", "Ro1.A", 0.7, [SIG_Y["O2"]])
    route_pads("O2", "Ro1.B", "Ro2.A", 0.6, [SIG_Y["O2"]])
    route_pads("O2", "Ro1.B", "ML7", 0.8, [SIG_Y["O2"]])

    route_pads("SWDIO", "SWD.2", "MR4", 0.65, [SIG_Y["SWDIO"]])
    route_pads("SWCLK", "SWD.3", "MR5", 0.65, [SIG_Y["SWCLK"]])


def count_crossings():
    segs = []
    for pts, w, net in traces:
        for i in range(len(pts) - 1):
            segs.append((pts[i], pts[i + 1], net))

    def ori(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    def hit(p1, p2, p3, p4):
        o1, o2 = ori(p1, p2, p3), ori(p1, p2, p4)
        o3, o4 = ori(p3, p4, p1), ori(p3, p4, p2)
        return o1 * o2 < -1e-9 and o3 * o4 < -1e-9

    n = 0
    for i in range(len(segs)):
        for j in range(i + 1, len(segs)):
            (a, b, n1), (c, d, n2) = segs[i], segs[j]
            if n1 == n2:
                continue
            if hit(a, b, c, d):
                n += 1
    return n


def render():
    img = Image.new("RGB", px(W, H), (12, 16, 20))
    d = ImageDraw.Draw(img)

    def Y(y):
        return H - y

    def P(x, y):
        return px(x, Y(y))

    d.rectangle([*px(0.4, 0.4), *px(W - 0.4, H - 0.4)], fill=(16, 72, 44), outline=(210, 220, 210), width=2)
    for x0, y0, x1, y1, lab, side in outlines:
        col = (255, 170, 60) if side == "bot" else (150, 205, 160)
        d.rectangle([*P(x0, y1), *P(x1, y0)], outline=col, width=2)
        d.text(P(x0 + 0.4, y1 - 0.3), lab, fill=col, font=font(1.8))

    cols = {
        "GND": (60, 60, 60), "+12VP": (230, 45, 45), "+12VIN": (180, 30, 30),
        "+5V": (220, 140, 40), "+3V3": (50, 130, 220),
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
            d.line(flat, fill=col(net), width=max(2, int(w * PPM)))

    for x1, y1, x2, y2, net in jumpers:
        d.line([*P(x1, y1), *P(x2, y2)], fill=(255, 255, 255), width=3)

    for name, (x, y, od, drill) in pads.items():
        r = od / 2
        fill = (215, 180, 55) if drill > 0 else (190, 110, 230)
        d.ellipse([*P(x - r, y + r), *P(x + r, y - r)], fill=fill, outline=(80, 60, 20))
        if drill > 0:
            rd = drill / 2
            d.ellipse([*P(x - rd, y + rd), *P(x + rd, y - rd)], fill=(12, 16, 20))

    for x, y in [(4, 4), (196, 4), (4, 96), (196, 96)]:
        d.ellipse([*P(x - 1.6, y + 1.6), *P(x + 1.6, y - 1.6)], outline=(240, 240, 240), width=2)

    cross = count_crossings()
    d.rectangle([*px(1, 1), *px(199, 11)], fill=(8, 10, 14))
    d.text(px(3, 2), "INJET RACING · 1-LAYER · SEM CRUZAMENTO DE COBRE", fill=(240, 245, 240), font=font(2.3))
    d.text(
        px(3, 6),
        f"Cruzamentos COBRE={cross}  Jumpers/fios TOPO={len(jumpers)}  Trilhas={len(traces)}",
        fill=(140, 255, 160) if cross == 0 else (255, 100, 100),
        font=font(2.0),
    )
    d.text(px(3, 9), "Branco=jumper fio no lado dos componentes (NAO e cobre). CNC = arquivo traces.", fill=(180, 180, 180), font=font(1.6))
    return img, cross


def render_cnc(inv=False):
    bg, cu = (255, 0) if not inv else (0, 255)
    img = Image.new("L", px(W, H), bg)
    d = ImageDraw.Draw(img)

    def Y(y):
        return H - y

    def P(x, y):
        return px(x, Y(y))

    for pts, w, net in traces:
        flat = []
        for x, y in pts:
            flat.extend(P(x, y))
        if len(flat) >= 4:
            d.line(flat, fill=cu, width=max(2, int(w * PPM)))
    for name, (x, y, od, drill) in pads.items():
        r = od / 2
        d.ellipse([*P(x - r, y + r), *P(x + r, y - r)], fill=cu)
        if drill > 0:
            d.ellipse([*P(x - drill / 2, y + drill / 2), *P(x + drill / 2, y - drill / 2)], fill=bg)
    for x, y in [(4, 4), (196, 4), (4, 96), (196, 96)]:
        d.ellipse([*P(x - 1.6, y + 1.6), *P(x + 1.6, y - 1.6)], fill=bg)
    return img


def write_svg(path, inv=False):
    cu, bg = ("#000", "#FFF") if not inv else ("#FFF", "#000")

    def Y(y):
        return H - y

    L = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">',
        f'<rect width="{W}" height="{H}" fill="{bg}"/>',
        f'<g fill="{cu}" stroke="{cu}" stroke-linecap="round" stroke-linejoin="round">',
    ]
    for pts, w, net in traces:
        dd = "M " + " L ".join(f"{x:.3f},{Y(y):.3f}" for x, y in pts)
        L.append(f'<path d="{dd}" fill="none" stroke-width="{w:.3f}" data-net="{net}"/>')
    for name, (x, y, od, drill) in pads.items():
        L.append(f'<circle cx="{x:.3f}" cy="{Y(y):.3f}" r="{od/2:.3f}"/>')
    L.append("</g>")
    L.append(f'<g fill="{bg}">')
    for name, (x, y, od, drill) in pads.items():
        if drill > 0:
            L.append(f'<circle cx="{x:.3f}" cy="{Y(y):.3f}" r="{drill/2:.3f}"/>')
    for x, y in [(4, 4), (196, 4), (4, 96), (196, 96)]:
        L.append(f'<circle cx="{x}" cy="{Y(y)}" r="1.6"/>')
    L.append("</g>")
    L.append('<g stroke="#f00" stroke-width="0.35" stroke-dasharray="1 0.5" fill="none">')
    for x1, y1, x2, y2, net in jumpers:
        L.append(f'<line x1="{x1:.2f}" y1="{Y(y1):.2f}" x2="{x2:.2f}" y2="{Y(y2):.2f}" data-jumper="{net}"/>')
    L.append("</g></svg>")
    path.write_text("\n".join(L), encoding="utf-8")


def main():
    run()
    img, cross = render()
    img.save(OUT / "ecu-pcb-1layer-assembly.png", dpi=(DPI, DPI))
    render_cnc(False).save(OUT / "ecu-pcb-1layer-traces-cnc.png", dpi=(DPI, DPI))
    render_cnc(True).save(OUT / "ecu-pcb-1layer-traces-cnc-invert.png", dpi=(DPI, DPI))
    write_svg(OUT / "ecu-pcb-1layer-traces-cnc.svg")
    write_svg(OUT / "ecu-pcb-1layer-traces-cnc-invert.svg", True)
    wires = [j for j in jumpers if "WIRE" in j[4]]
    (OUT / "ecu-pcb-1layer-drc.md").write_text(
        f"# DRC 1-layer\n\n- Cruzamentos cobre: **{cross}**\n"
        f"- Jumpers (ponte curta): **{len(jumpers) - len(wires)}**\n"
        f"- Fios topo (ligacao inteira): **{len(wires)}**\n"
        f"- Trilhas cobre: **{len(traces)}**\n\n"
        + ("**OK:** cobre sem cruzamento de nets diferentes.\n" if cross == 0 else "**ERRO**\n")
        + "\n## Jumpers / fios TOPO\n\n"
        + "\n".join(f"- `{n}` ({x1:.1f},{y1:.1f})->({x2:.1f},{y2:.1f})" for x1, y1, x2, y2, n in jumpers),
        encoding="utf-8",
    )
    print(f"cross={cross} jumpers={len(jumpers)} wires={len(wires)} traces={len(traces)}")


if __name__ == "__main__":
    main()
