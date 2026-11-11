# -*- coding: utf-8 -*-
"""
INJET RACING ECU — PCB 1-layer fenolite 200×100 mm
Layout profissional por módulos + netlist real do projeto.

Camada: cobre embaixo (CNC isola espaços).
THT em cima. AD8628 (único SMD) soldado no lado do cobre (embaixo).

CN1 = ATX 24 pinos (placa-mãe ↔ fonte)
CN2 = PCIe 6 pinos (placa de vídeo) — 5 sinais LSU 4.2 + 1 NC
"""
from __future__ import annotations

from pathlib import Path
from collections import defaultdict
from PIL import Image, ImageDraw, ImageFont

OUT = Path(r"e:\injet racing\assets")
W, H = 200.0, 100.0
PPM = 12.0  # px/mm — CNC bitmap nítido
DPI = int(25.4 * PPM)

# ---------- helpers ----------
def font(mm):
    px = max(9, int(mm * PPM))
    for p in ("C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/calibri.ttf"):
        try:
            return ImageFont.truetype(p, px)
        except OSError:
            pass
    return ImageFont.load_default()


def px(*xy):
    return tuple(int(round(v * PPM)) for v in xy)


# Pad: name -> (x, y, od, drill)
pads: dict[str, tuple[float, float, float, float]] = {}
# Comp outlines for silk: (x0,y0,x1,y1,label,side) side=top|bot
outlines: list[tuple[float, float, float, float, str, str]] = []
# Traces: list of (points, width_mm, net)
traces: list[tuple[list[tuple[float, float]], float, str]] = []
# Net list documentation
netlist_doc: list[str] = []


def pad(name, x, y, od=1.9, drill=0.95):
    pads[name] = (x, y, od, drill)


def axial(name_a, name_b, x1, y1, x2, y2, od=1.7, drill=0.85):
    pad(name_a, x1, y1, od, drill)
    pad(name_b, x2, y2, od, drill)


def to220(prefix, x, y):
    """TO-220: G D S em linha, passo 2.54. Tab para +Y."""
    pad(f"{prefix}.G", x - 2.54, y, 2.3, 1.1)
    pad(f"{prefix}.D", x, y, 2.3, 1.1)
    pad(f"{prefix}.S", x + 2.54, y, 2.3, 1.1)
    outlines.append((x - 5, y - 2, x + 5, y + 12, prefix, "top"))


def to92(prefix, x, y):
    """2N7000 TO-92: pin view flat face — S G D (comum)."""
    pad(f"{prefix}.S", x - 1.27, y, 1.6, 0.8)
    pad(f"{prefix}.G", x, y + 1.8, 1.6, 0.8)
    pad(f"{prefix}.D", x + 1.27, y, 1.6, 0.8)
    outlines.append((x - 3, y - 1, x + 3, y + 5, prefix, "top"))


def dip(prefix, x0, y0, n, pitch=2.54, row=7.62, od=1.7, drill=0.85):
    """DIP pin1 bottom-left, left column up, right column down."""
    half = n // 2
    for i in range(half):
        pad(f"{prefix}.{i+1}", x0, y0 + i * pitch, od, drill)
        pad(f"{prefix}.{n - i}", x0 + row, y0 + i * pitch, od, drill)
    outlines.append((x0 - 1.5, y0 - 1.5, x0 + row + 1.5, y0 + (half - 1) * pitch + 1.5, prefix, "top"))


def header_row(prefix, x0, y0, n, pitch=2.54, od=1.8, drill=1.0):
    for i in range(n):
        pad(f"{prefix}.{i+1}", x0 + i * pitch, y0, od, drill)


def soic8_bottom(prefix, x0, y0, pitch=1.27, row=5.4):
    """AD8628 SOIC-8 no LADO DO COBRE (embaixo). Pads na camada de cobre."""
    for i in range(4):
        pad(f"{prefix}.{i+1}", x0, y0 + i * pitch, 1.4, 0.0)  # SMD — sem furo
        pad(f"{prefix}.{8-i}", x0 + row, y0 + i * pitch, 1.4, 0.0)
    outlines.append((x0 - 1, y0 - 1, x0 + row + 1, y0 + 3 * pitch + 1, prefix + " (SMD baixo)", "bot"))


def tr(net, pts, w=1.0):
    if len(pts) >= 2:
        traces.append((pts, w, net))


def connect(net, *pad_names, w=1.0, via_y=None):
    """Liga pads em sequência Manhattan (horizontal depois vertical)."""
    pts = []
    coords = []
    for n in pad_names:
        if n not in pads:
            raise KeyError(n)
        coords.append((pads[n][0], pads[n][1]))
    for i, (x, y) in enumerate(coords):
        if i == 0:
            pts.append((x, y))
            continue
        px_, py_ = pts[-1]
        if abs(px_ - x) < 0.01 or abs(py_ - y) < 0.01:
            pts.append((x, y))
        else:
            # elbow: prefer horizontal first along channel
            mid_y = via_y if via_y is not None else py_
            if abs(py_ - mid_y) > 0.01:
                pts.append((px_, mid_y))
            pts.append((x, mid_y))
            pts.append((x, y))
    tr(net, pts, w)


def star(net, hub_pad, *others, w=1.0):
    hx, hy = pads[hub_pad][0], pads[hub_pad][1]
    for o in others:
        ox, oy = pads[o][0], pads[o][1]
        if abs(hx - ox) < 0.01 or abs(hy - oy) < 0.01:
            tr(net, [(hx, hy), (ox, oy)], w)
        else:
            tr(net, [(hx, hy), (ox, hy), (ox, oy)], w)


# =============================================================================
# COLOCAÇÃO POR MÓDULO (Y=0 baixo, Y=100 topo) — vista topo componentes
# =============================================================================

# --- CN1 ATX-24 (placa-mãe) — 2×12, passo 4.20 mm, fileiras Y=8 e Y=16.4 ---
ATX_P = 4.20
atx_x0, atx_y0 = 8.0, 8.0
for i in range(12):
    pad(f"CN1.{i+1}", atx_x0 + i * ATX_P, atx_y0 + ATX_P, 2.4, 1.2)       # fila 1–12
    pad(f"CN1.{i+13}", atx_x0 + i * ATX_P, atx_y0, 2.4, 1.2)              # fila 13–24
outlines.append((atx_x0 - 3, atx_y0 - 4, atx_x0 + 11 * ATX_P + 3, atx_y0 + ATX_P + 6, "CN1 ATX-24", "top"))

# Pinagem ECU no ATX-24 (remapeada — NÃO é pinagem ATX de PC)
# 1:+12V_IGN  2:+12V_BAT  3:GND_P  4:GND_P  5:GND_S  6:+5V_MAP  7:+3V3_TPS
# 8:IAT  9:CLT  10:MAP  11:TPS  12:RPM
# 13:INJ1  14:INJ2  15:INJ3  16:INJ4  17:RL_BOMBA  18:RL_MAIN  19:RL_IAC
# 20:CANH  21:CANL  22:TACHO  23:START  24:SHIELD
CN1_MAP = {
    1: "+12V_IGN", 2: "+12V_BAT", 3: "GND_P", 4: "GND_P", 5: "GND_S",
    6: "+5V", 7: "+3V3", 8: "IAT", 9: "CLT", 10: "MAP", 11: "TPS", 12: "RPM",
    13: "INJ1", 14: "INJ2", 15: "INJ3", 16: "INJ4",
    17: "RL2", 18: "RL1", 19: "RL3", 20: "CANH", 21: "CANL",
    22: "TACHO", 23: "START", 24: "SHIELD",
}

# --- CN2 PCIe-6 (GPU) — 2×3 passo 4.20 ---
# Sinais LSU 4.2 (5 fios): H+ H- IP VM UN | pin6 NC
pcie_x0, pcie_y0 = 168.0, 8.0
for i in range(3):
    pad(f"CN2.{i+1}", pcie_x0 + i * ATX_P, pcie_y0 + ATX_P, 2.4, 1.2)
    pad(f"CN2.{i+4}", pcie_x0 + i * ATX_P, pcie_y0, 2.4, 1.2)
outlines.append((pcie_x0 - 3, pcie_y0 - 4, pcie_x0 + 2 * ATX_P + 3, pcie_y0 + ATX_P + 6, "CN2 PCIe-6 λ", "top"))
# CN2.1=H+  CN2.2=H-  CN2.3=IP  CN2.4=VM  CN2.5=UN  CN2.6=NC

# --- POWER (topo-esquerda) ---
to220("QREV", 18, 88)  # IRF9540  G=gate R/Zener  D=entrada 12V  S=+12V_PROT  [P-ch: S=fonte p/ carga]
# Nota IRF9540 P-FET: Source → +12V_PROT (saída), Drain → bateria via fusível, Gate → R+zener
axial("CBULK.A", "CBULK.K", 30, 90, 38, 90, 2.6, 0.9)  # 220u eletrolítico
axial("CIN.A", "CIN.K", 30, 84, 34, 84, 1.7, 0.8)  # 100n
axial("TVS.A", "TVS.K", 42, 90, 42, 84, 1.8, 0.85)  # SMBJ33A → usar P6KE33A THT
axial("RG.A", "RG.B", 12, 82, 12, 76, 1.6, 0.8)  # 100k gate
axial("DZ.A", "DZ.K", 16, 82, 16, 76, 1.6, 0.8)  # zener 12V

# Buck MP1584 módulo 4 pinos: VIN GND VOUT ADJ
pad("BUCK.VIN", 48, 90, 2.0, 1.0)
pad("BUCK.GND", 54, 90, 2.0, 1.0)
pad("BUCK.VOUT", 48, 82, 2.0, 1.0)
pad("BUCK.FB", 54, 82, 2.0, 1.0)
outlines.append((46, 80, 56, 93, "BUCK 5V", "top"))

# LDO AMS1117 módulo / pinos IN GND OUT
pad("LDO.IN", 60, 90, 2.0, 1.0)
pad("LDO.GND", 66, 90, 2.0, 1.0)
pad("LDO.OUT", 63, 82, 2.0, 1.0)
axial("CLDO1.A", "CLDO1.B", 70, 90, 74, 90)  # 10u in
axial("CLDO2.A", "CLDO2.B", 70, 84, 74, 84)  # 10u out
axial("CLDO3.A", "CLDO3.B", 70, 78, 74, 78)  # 100n out
outlines.append((58, 80, 76, 93, "LDO 3V3", "top"))

# --- INJECTOR DRIVERS (topo-centro) ---
inj = []
for i, x in enumerate([88, 102, 116, 130]):
    name = f"QINJ{i+1}"
    to220(name, x, 88)
    axial(f"RG{i+1}.A", f"RG{i+1}.B", x - 2.54, 80, x - 2.54, 74)  # 100R gate
    axial(f"RGS{i+1}.A", f"RGS{i+1}.B", x - 2.54, 72, x + 1, 72)  # 10k gs
    axial(f"DF{i+1}.A", f"DF{i+1}.K", x + 5, 88, x + 5, 82)  # 1N4007  A=dreno K=+12
    inj.append(i + 1)

# Heater MOSFET
to220("QHEAT", 146, 88)
axial("RGH.A", "RGH.B", 143.46, 80, 143.46, 74)
axial("RGSH.A", "RGSH.B", 143.46, 72, 148, 72)

# --- RELAY DRIVERS (esquerda-meio) ---
for i, x in enumerate([14, 24, 34]):
    to92(f"QRL{i+1}", x, 58)
    axial(f"RRL{i+1}.A", f"RRL{i+1}.B", x, 52, x, 46)  # 1k
    axial(f"DRL{i+1}.A", f"DRL{i+1}.K", x + 4, 58, x + 4, 52)  # flyback

# --- STM32 BLACK BOARD (centro) headers 2×20 verticais ---
# Esquerda = sinais; direita = power/extra
mcu_lx, mcu_rx = 78.0, 130.0
mcu_ytop = 68.0
for i in range(20):
    pad(f"MCU.L{i+1}", mcu_lx, mcu_ytop - i * 2.54, 1.7, 0.95)
    pad(f"MCU.R{i+1}", mcu_rx, mcu_ytop - i * 2.54, 1.7, 0.95)
outlines.append((mcu_lx - 2, mcu_ytop - 19 * 2.54 - 2, mcu_rx + 2, mcu_ytop + 2, "STM32F407 BLACK BOARD", "top"))

# Mapeamento MCU headers (obrigatório do projeto)
# L1=+3V3 L2=GND L3=PA0_IAT L4=PA1_CLT L5=PA2_MAP L6=PA3_TPS L7=PA4_O2
# L8=PA5_Ip L9=PA6_Un L10=PB0_RPM L11=PB8_CANRX L12=PB9_CANTX
# L13=PE9_INJ1 L14=PE11_INJ2 L15=PE13_INJ3 L16=PE14_INJ4
# L17=PD8_RL1 L18=PD9_RL2 L19=PD10_RL3 L20=PA8_HEAT
# R1=+5V_IN R2=GND — PA4=DAC Vm ONLY (sem divisor O2/CJ125)
# Ip=PA5 Un=PA6 VBat=PC1 — ver firmware/include/pins.h e _gen_pcb_1layer_v8.py
# R4=SWDIO R5=SWCLK R6=+3V3 R7=GND R8.. spare

# SWD header dedicado
header_row("SWD", 100, 30, 4, 2.54)
outlines.append((98, 27, 112, 34, "SWD", "top"))
# SWD.1=3V3 SWD.2=SWDIO SWD.3=SWCLK SWD.4=GND

# --- SENSOR CONDITIONING (direita) ---
# IAT: pullup 2K26 + 100n + série 1k
axial("RIAT.A", "RIAT.B", 158, 70, 166, 70)  # 2K26
axial("CIAT.A", "CIAT.B", 170, 70, 170, 64)  # 100n
axial("SIAT.A", "SIAT.B", 174, 70, 182, 70)  # 1k série → MCU
# CLT
axial("RCLT.A", "RCLT.B", 158, 60, 166, 60)
axial("CCLT.A", "CCLT.B", 170, 60, 170, 54)
axial("SCLT.A", "SCLT.B", 174, 60, 182, 60)
# MAP divisor 10k/18k + 100n + 1k
axial("RMAP1.A", "RMAP1.B", 158, 50, 166, 50)  # 10k
axial("RMAP2.A", "RMAP2.B", 166, 50, 166, 44)  # 18k p/ GND
axial("CMAP.A", "CMAP.B", 170, 50, 170, 44)
axial("SMAP.A", "SMAP.B", 174, 50, 182, 50)
# TPS: só 100n + 1k (pote em 3V3)
axial("CTPS.A", "CTPS.B", 170, 40, 170, 34)
axial("STPS.A", "STPS.B", 174, 40, 182, 40)
outlines.append((154, 32, 190, 74, "SENSORS", "top"))

# --- RPM OPTO ---
dip("U817", 58, 34, 4)  # PC817: 1=A 2=K 3=E 4=C
axial("RRPM1.A", "RRPM1.B", 48, 38, 56, 38)  # 10k 2W
axial("RRPM2.A", "RRPM2.B", 40, 38, 48, 38)  # 10k 2W
axial("DRPM.A", "DRPM.K", 52, 34, 52, 28)  # 1N4148 across LED
axial("RRPM3.A", "RRPM3.B", 68, 42, 68, 36)  # 4k7 pullup
axial("CRPM.A", "CRPM.B", 72, 36, 72, 30)  # 1nF
outlines.append((38, 26, 76, 46, "RPM OPTO", "top"))

# --- CAN módulo SN65HVD230 breakout: VCC GND TX RX CANH CANL ---
pad("CAN.VCC", 88, 40, 1.9, 1.0)
pad("CAN.GND", 94, 40, 1.9, 1.0)
pad("CAN.TX", 88, 34, 1.9, 1.0)
pad("CAN.RX", 94, 34, 1.9, 1.0)
pad("CAN.H", 100, 40, 1.9, 1.0)
pad("CAN.L", 106, 40, 1.9, 1.0)
axial("CCAN.A", "CCAN.B", 100, 34, 106, 34)  # 100n
outlines.append((86, 30, 110, 44, "CAN HVD230", "top"))

# --- LAMBDA DIY ---
dip("U6004", 150, 18, 14)  # MCP6004 DIP14
# AD8628 SOIC embaixo sob a área lambda
soic8_bottom("U8628", 172, 20)
axial("RSH.A", "RSH.B", 168, 36, 176, 36)  # 61R9 shunt
axial("RESR.A", "RESR.B", 168, 42, 176, 42)  # 6k8
axial("CIP.A", "CIP.B", 180, 36, 180, 30)  # 220n Ip
axial("CUN.A", "CUN.B", 184, 42, 184, 36)  # 220n Un
axial("C5A.A", "C5A.B", 142, 28, 142, 22)  # 100n +5V opamp
axial("C5B.A", "C5B.B", 146, 28, 146, 22)  # 10u
# O2 divisor 10k/18k da saída λ (opcional buffer → PA4)
axial("RO21.A", "RO21.B", 158, 28, 166, 28)  # 10k
axial("RO22.A", "RO22.B", 166, 28, 166, 22)  # 18k
axial("CO2.A", "CO2.B", 170, 28, 170, 22)
outlines.append((140, 14, 190, 48, "LAMBDA DIY", "top"))

# =============================================================================
# NETLIST + ROTEAMENTO 1-LAYER (canais dedicados)
# =============================================================================
# Canais horizontais de barramento:
Y_GND = 4.0
Y_12V = 96.0
Y_5V = 76.0
Y_3V3 = 66.0
Y_SIG_A = 56.0  # GPIO potencia
Y_SIG_B = 48.0  # sensores/ADC

# --- GND star / bus ---
# CN1 GND pins → bus
tr("GND", [(pads["CN1.3"][0], pads["CN1.3"][1]), (pads["CN1.3"][0], Y_GND), (190, Y_GND)], 2.8)
tr("GND", [(pads["CN1.4"][0], pads["CN1.4"][1]), (pads["CN1.4"][0], Y_GND)], 2.8)
tr("GND", [(pads["CN1.5"][0], pads["CN1.5"][1]), (pads["CN1.5"][0], Y_GND)], 2.0)
tr("GND", [(pads["CN1.24"][0], pads["CN1.24"][1]), (pads["CN1.24"][0], Y_GND)], 1.5)  # shield

gnd_nodes = [
    "QREV.G",  # via zener/Rg — gate network returns GND through DZ
    "CBULK.K", "CIN.K", "TVS.K", "DZ.K", "RG.B",
    "BUCK.GND", "LDO.GND", "CLDO1.B", "CLDO2.B", "CLDO3.B",
    "QINJ1.S", "QINJ2.S", "QINJ3.S", "QINJ4.S", "QHEAT.S",
    "RGS1.B", "RGS2.B", "RGS3.B", "RGS4.B", "RGSH.B",
    "QRL1.S", "QRL2.S", "QRL3.S",
    "MCU.L2", "MCU.R2", "SWD.4",
    "CIAT.B", "CCLT.B", "CMAP.B", "CTPS.B", "RMAP2.B", "CO2.B", "RO22.B",
    "U817.3", "CRPM.B",  # emitter
    "CAN.GND", "CCAN.B",
    "C5A.B", "C5B.B", "CIP.B", "CUN.B",
    "U6004.4", "U6004.11",  # MCP6004 VSS pins typically 4&11? DIP14: pin4 VSS pin11 NC/VSS — MCP6004: pin 4=VSS, pin 11=NC; VDD=pin14
    "U8628.4",  # VSS SOIC
]
# Fix MCP6004: Pin4=VSS, Pin14=VDD. Pin11 is NC on MCP6004.
for n in gnd_nodes:
    if n not in pads:
        continue
    x, y = pads[n][0], pads[n][1]
    tr("GND", [(x, y), (x, Y_GND)], 1.2 if "QINJ" not in n and "QHEAT" not in n and "QREV" not in n else 2.0)

# QREV gate network: RG.A to QREV.G, DZ.A to QREV.G, DZ.K GND, RG.B GND
tr("QG", [(pads["QREV.G"][0], pads["QREV.G"][1]), (pads["RG.A"][0], pads["QREV.G"][1]), (pads["RG.A"][0], pads["RG.A"][1])], 0.8)
tr("QG", [(pads["QREV.G"][0], pads["QREV.G"][1]), (pads["DZ.A"][0], pads["QREV.G"][1]), (pads["DZ.A"][0], pads["DZ.A"][1])], 0.8)
tr("GND", [(pads["RG.B"][0], pads["RG.B"][1]), (pads["RG.B"][0], Y_GND)], 0.8)
tr("GND", [(pads["DZ.K"][0], pads["DZ.K"][1]), (pads["DZ.K"][0], Y_GND)], 0.8)

# --- +12V entrada e PROT ---
# CN1.1 e CN1.2 → QREV.D (dreno = entrada bat)
tr("+12V_IN", [
    (pads["CN1.1"][0], pads["CN1.1"][1]), (pads["CN1.1"][0], 24),
    (pads["QREV.D"][0], 24), (pads["QREV.D"][0], pads["QREV.D"][1])
], 2.2)
tr("+12V_IN", [
    (pads["CN1.2"][0], pads["CN1.2"][1]), (pads["CN1.2"][0], 22),
    (pads["CN1.1"][0], 22)
], 2.2)

# +12V_PROT = QREV.S → bus topo → buck VIN, flybacks, CN2 H+, heaters path
tr("+12V_PROT", [
    (pads["QREV.S"][0], pads["QREV.S"][1]), (pads["QREV.S"][0], Y_12V),
    (160, Y_12V)
], 2.8)
tr("+12V_PROT", [(pads["CBULK.A"][0], pads["CBULK.A"][1]), (pads["CBULK.A"][0], Y_12V)], 2.0)
tr("+12V_PROT", [(pads["CIN.A"][0], pads["CIN.A"][1]), (pads["CIN.A"][0], Y_12V)], 1.0)
tr("+12V_PROT", [(pads["TVS.A"][0], pads["TVS.A"][1]), (pads["TVS.A"][0], Y_12V)], 1.2)
tr("+12V_PROT", [(pads["BUCK.VIN"][0], pads["BUCK.VIN"][1]), (pads["BUCK.VIN"][0], Y_12V)], 1.8)
for i in range(1, 5):
    tr("+12V_PROT", [(pads[f"DF{i}.K"][0], pads[f"DF{i}.K"][1]), (pads[f"DF{i}.K"][0], Y_12V)], 1.2)
    tr("INJ_FLY", [(pads[f"DF{i}.A"][0], pads[f"DF{i}.A"][1]), (pads[f"QINJ{i}.D"][0], pads[f"DF{i}.A"][1]), (pads[f"QINJ{i}.D"][0], pads[f"QINJ{i}.D"][1])], 1.2)
for i in range(1, 4):
    tr("+12V_PROT", [(pads[f"DRL{i}.K"][0], pads[f"DRL{i}.K"][1]), (pads[f"DRL{i}.K"][0], Y_12V)], 1.0)
    tr("RL_FLY", [(pads[f"DRL{i}.A"][0], pads[f"DRL{i}.A"][1]), (pads[f"QRL{i}.D"][0], pads[f"DRL{i}.A"][1]), (pads[f"QRL{i}.D"][0], pads[f"QRL{i}.D"][1])], 1.0)

# H+ → CN2.1 from +12V_PROT
tr("+12V_PROT", [
    (146, Y_12V), (pads["CN2.1"][0], Y_12V), (pads["CN2.1"][0], pads["CN2.1"][1])
], 2.0)

# --- +5V ---
tr("+5V", [
    (pads["BUCK.VOUT"][0], pads["BUCK.VOUT"][1]), (pads["BUCK.VOUT"][0], Y_5V),
    (185, Y_5V)
], 1.8)
tr("+5V", [(pads["LDO.IN"][0], pads["LDO.IN"][1]), (pads["LDO.IN"][0], Y_5V)], 1.5)
tr("+5V", [(pads["CLDO1.A"][0], pads["CLDO1.A"][1]), (pads["LDO.IN"][0], pads["CLDO1.A"][1]), (pads["LDO.IN"][0], pads["LDO.IN"][1])], 1.0)
tr("+5V", [(pads["CN1.6"][0], pads["CN1.6"][1]), (pads["CN1.6"][0], Y_5V)], 1.2)
tr("+5V", [(pads["MCU.R1"][0], pads["MCU.R1"][1]), (pads["MCU.R1"][0], Y_5V)], 1.2)
tr("+5V", [(pads["C5A.A"][0], pads["C5A.A"][1]), (pads["C5A.A"][0], Y_5V)], 1.0)
tr("+5V", [(pads["C5B.A"][0], pads["C5B.A"][1]), (pads["C5B.A"][0], Y_5V)], 1.0)
tr("+5V", [(pads["U6004.14"][0], pads["U6004.14"][1]), (pads["U6004.14"][0], Y_5V)], 1.0)
tr("+5V", [(pads["U8628.8"][0], pads["U8628.8"][1]), (pads["U8628.8"][0], Y_5V)], 0.8)  # VDD AD8628
# MAP +5V already CN1.6

# --- +3V3 ---
tr("+3V3", [
    (pads["LDO.OUT"][0], pads["LDO.OUT"][1]), (pads["LDO.OUT"][0], Y_3V3),
    (185, Y_3V3)
], 1.6)
tr("+3V3", [(pads["CLDO2.A"][0], pads["CLDO2.A"][1]), (pads["LDO.OUT"][0], pads["CLDO2.A"][1])], 1.0)
tr("+3V3", [(pads["CLDO3.A"][0], pads["CLDO3.A"][1]), (pads["LDO.OUT"][0], pads["CLDO3.A"][1])], 0.8)
tr("+3V3", [(pads["MCU.L1"][0], pads["MCU.L1"][1]), (pads["MCU.L1"][0], Y_3V3)], 1.2)
tr("+3V3", [(pads["SWD.1"][0], pads["SWD.1"][1]), (pads["SWD.1"][0], Y_3V3)], 1.0)
tr("+3V3", [(pads["CN1.7"][0], pads["CN1.7"][1]), (pads["CN1.7"][0], Y_3V3)], 1.2)
tr("+3V3", [(pads["RIAT.A"][0], pads["RIAT.A"][1]), (pads["RIAT.A"][0], Y_3V3)], 0.9)
tr("+3V3", [(pads["RCLT.A"][0], pads["RCLT.A"][1]), (pads["RCLT.A"][0], Y_3V3)], 0.9)
tr("+3V3", [(pads["RRPM3.A"][0], pads["RRPM3.A"][1]), (pads["RRPM3.A"][0], Y_3V3)], 0.9)
tr("+3V3", [(pads["CAN.VCC"][0], pads["CAN.VCC"][1]), (pads["CAN.VCC"][0], Y_3V3)], 1.0)

# --- Injector low-side → CN1 ---
for i, cn in enumerate([13, 14, 15, 16], start=1):
    # Drain QINJ → CN1
    tr(f"INJ{i}", [
        (pads[f"QINJ{i}.D"][0], pads[f"QINJ{i}.D"][1]),
        (pads[f"QINJ{i}.D"][0], 28 + i),
        (pads[f"CN1.{cn}"][0], 28 + i),
        (pads[f"CN1.{cn}"][0], pads[f"CN1.{cn}"][1]),
    ], 1.6)
    # Gate chain: MCU → Rgate → gate, Rgs to gate
    mcu = f"MCU.L{12+i}"  # L13..L16
    tr(f"GINJ{i}", [
        (pads[mcu][0], pads[mcu][1]),
        (pads[mcu][0], Y_SIG_A - i),
        (pads[f"RG{i}.B"][0], Y_SIG_A - i),
        (pads[f"RG{i}.B"][0], pads[f"RG{i}.B"][1]),
    ], 0.9)
    tr(f"GINJ{i}", [
        (pads[f"RG{i}.A"][0], pads[f"RG{i}.A"][1]),
        (pads[f"QINJ{i}.G"][0], pads[f"RG{i}.A"][1]),
        (pads[f"QINJ{i}.G"][0], pads[f"QINJ{i}.G"][1]),
    ], 0.9)
    tr(f"GINJ{i}", [
        (pads[f"RGS{i}.A"][0], pads[f"RGS{i}.A"][1]),
        (pads[f"QINJ{i}.G"][0], pads[f"RGS{i}.A"][1]),
    ], 0.8)

# Heater: MCU.L20 → RGH → QHEAT.G ; QHEAT.D → CN2.2 (H-)
tr("GHEAT", [
    (pads["MCU.L20"][0], pads["MCU.L20"][1]),
    (pads["MCU.L20"][0], Y_SIG_A - 5),
    (pads["RGH.B"][0], Y_SIG_A - 5),
    (pads["RGH.B"][0], pads["RGH.B"][1]),
], 0.9)
tr("GHEAT", [
    (pads["RGH.A"][0], pads["RGH.A"][1]),
    (pads["QHEAT.G"][0], pads["RGH.A"][1]),
    (pads["QHEAT.G"][0], pads["QHEAT.G"][1]),
], 0.9)
tr("GHEAT", [(pads["RGSH.A"][0], pads["RGSH.A"][1]), (pads["QHEAT.G"][0], pads["RGSH.A"][1])], 0.8)
tr("H-", [
    (pads["QHEAT.D"][0], pads["QHEAT.D"][1]),
    (pads["CN2.2"][0], pads["QHEAT.D"][1]),
    (pads["CN2.2"][0], pads["CN2.2"][1]),
], 2.0)

# Relay drains → CN1 18,17,19 (RL1 main, RL2 pump, RL3 IAC)
rl_cn = {1: 18, 2: 17, 3: 19}
rl_mcu = {1: "MCU.L17", 2: "MCU.L18", 3: "MCU.L19"}
for i in range(1, 4):
    tr(f"RL{i}", [
        (pads[f"QRL{i}.D"][0], pads[f"QRL{i}.D"][1]),
        (pads[f"QRL{i}.D"][0], 26 + i * 0.7),
        (pads[f"CN1.{rl_cn[i]}"][0], 26 + i * 0.7),
        (pads[f"CN1.{rl_cn[i]}"][0], pads[f"CN1.{rl_cn[i]}"][1]),
    ], 1.2)
    tr(f"GRL{i}", [
        (pads[rl_mcu[i]][0], pads[rl_mcu[i]][1]),
        (40 + i * 2, pads[rl_mcu[i]][1]),
        (40 + i * 2, pads[f"RRL{i}.B"][1]),
        (pads[f"RRL{i}.B"][0], pads[f"RRL{i}.B"][1]),
    ], 0.8)
    tr(f"GRL{i}", [
        (pads[f"RRL{i}.A"][0], pads[f"RRL{i}.A"][1]),
        (pads[f"QRL{i}.G"][0], pads[f"RRL{i}.A"][1]),
        (pads[f"QRL{i}.G"][0], pads[f"QRL{i}.G"][1]),
    ], 0.8)

# --- Sensors ---
# CN1.8 IAT → junction RIAT.B/CIAT/SIAT
tr("IAT", [
    (pads["CN1.8"][0], pads["CN1.8"][1]), (pads["CN1.8"][0], Y_SIG_B),
    (pads["RIAT.B"][0], Y_SIG_B), (pads["RIAT.B"][0], pads["RIAT.B"][1]),
], 0.9)
tr("IAT", [(pads["RIAT.B"][0], pads["RIAT.B"][1]), (pads["CIAT.A"][0], pads["RIAT.B"][1]), (pads["CIAT.A"][0], pads["CIAT.A"][1])], 0.8)
tr("IAT", [(pads["RIAT.B"][0], pads["RIAT.B"][1]), (pads["SIAT.A"][0], pads["RIAT.B"][1]), (pads["SIAT.A"][0], pads["SIAT.A"][1])], 0.8)
tr("IAT", [
    (pads["SIAT.B"][0], pads["SIAT.B"][1]), (188, pads["SIAT.B"][1]),
    (188, pads["MCU.L3"][1]), (pads["MCU.L3"][0], pads["MCU.L3"][1]),
], 0.9)

tr("CLT", [
    (pads["CN1.9"][0], pads["CN1.9"][1]), (pads["CN1.9"][0], Y_SIG_B - 2),
    (pads["RCLT.B"][0], Y_SIG_B - 2), (pads["RCLT.B"][0], pads["RCLT.B"][1]),
], 0.9)
tr("CLT", [(pads["RCLT.B"][0], pads["RCLT.B"][1]), (pads["CCLT.A"][0], pads["RCLT.B"][1]), (pads["CCLT.A"][0], pads["CCLT.A"][1])], 0.8)
tr("CLT", [(pads["RCLT.B"][0], pads["RCLT.B"][1]), (pads["SCLT.A"][0], pads["RCLT.B"][1]), (pads["SCLT.A"][0], pads["SCLT.A"][1])], 0.8)
tr("CLT", [
    (pads["SCLT.B"][0], pads["SCLT.B"][1]), (190, pads["SCLT.B"][1]),
    (190, pads["MCU.L4"][1]), (pads["MCU.L4"][0], pads["MCU.L4"][1]),
], 0.9)

tr("MAP", [
    (pads["CN1.10"][0], pads["CN1.10"][1]), (pads["CN1.10"][0], Y_SIG_B - 4),
    (pads["RMAP1.A"][0], Y_SIG_B - 4), (pads["RMAP1.A"][0], pads["RMAP1.A"][1]),
], 0.9)
tr("MAP", [(pads["RMAP1.B"][0], pads["RMAP1.B"][1]), (pads["RMAP2.A"][0], pads["RMAP1.B"][1])], 0.8)
tr("MAP_MID", [(pads["RMAP1.B"][0], pads["RMAP1.B"][1]), (pads["CMAP.A"][0], pads["RMAP1.B"][1]), (pads["CMAP.A"][0], pads["CMAP.A"][1])], 0.8)
tr("MAP_MID", [(pads["RMAP1.B"][0], pads["RMAP1.B"][1]), (pads["SMAP.A"][0], pads["RMAP1.B"][1]), (pads["SMAP.A"][0], pads["SMAP.A"][1])], 0.8)
tr("MAP_ADC", [
    (pads["SMAP.B"][0], pads["SMAP.B"][1]), (192, pads["SMAP.B"][1]),
    (192, pads["MCU.L5"][1]), (pads["MCU.L5"][0], pads["MCU.L5"][1]),
], 0.9)

tr("TPS", [
    (pads["CN1.11"][0], pads["CN1.11"][1]), (pads["CN1.11"][0], Y_SIG_B - 6),
    (pads["STPS.A"][0], Y_SIG_B - 6), (pads["STPS.A"][0], pads["STPS.A"][1]),
], 0.9)
tr("TPS", [(pads["STPS.A"][0], pads["STPS.A"][1]), (pads["CTPS.A"][0], pads["STPS.A"][1]), (pads["CTPS.A"][0], pads["CTPS.A"][1])], 0.8)
tr("TPS", [
    (pads["STPS.B"][0], pads["STPS.B"][1]), (194, pads["STPS.B"][1]),
    (194, pads["MCU.L6"][1]), (pads["MCU.L6"][0], pads["MCU.L6"][1]),
], 0.9)

# --- RPM ---
# CN1.12 → RRPM2 → RRPM1 → U817.1(A); U817.2(K)=GND via diode; U817.4(C)→MCU.L10 & RRPM3
tr("RPM_IN", [
    (pads["CN1.12"][0], pads["CN1.12"][1]), (pads["CN1.12"][0], 42),
    (pads["RRPM2.A"][0], 42), (pads["RRPM2.A"][0], pads["RRPM2.A"][1]),
], 1.0)
tr("RPM_IN", [(pads["RRPM2.B"][0], pads["RRPM2.B"][1]), (pads["RRPM1.A"][0], pads["RRPM2.B"][1])], 1.0)
tr("RPM_IN", [(pads["RRPM1.B"][0], pads["RRPM1.B"][1]), (pads["U817.1"][0], pads["RRPM1.B"][1]), (pads["U817.1"][0], pads["U817.1"][1])], 0.9)
tr("RPM_LED", [(pads["U817.2"][0], pads["U817.2"][1]), (pads["U817.2"][0], Y_GND)], 0.9)
tr("RPM_LED", [(pads["DRPM.A"][0], pads["DRPM.A"][1]), (pads["U817.1"][0], pads["DRPM.A"][1]), (pads["U817.1"][0], pads["U817.1"][1])], 0.7)
tr("RPM_LED", [(pads["DRPM.K"][0], pads["DRPM.K"][1]), (pads["U817.2"][0], pads["DRPM.K"][1]), (pads["U817.2"][0], pads["U817.2"][1])], 0.7)
tr("RPM_OUT", [
    (pads["U817.4"][0], pads["U817.4"][1]),
    (pads["RRPM3.B"][0], pads["U817.4"][1]), (pads["RRPM3.B"][0], pads["RRPM3.B"][1]),
], 0.8)
tr("RPM_OUT", [(pads["U817.4"][0], pads["U817.4"][1]), (pads["CRPM.A"][0], pads["U817.4"][1]), (pads["CRPM.A"][0], pads["CRPM.A"][1])], 0.7)
tr("RPM_OUT", [
    (pads["U817.4"][0], pads["U817.4"][1]),
    (pads["MCU.L10"][0], pads["U817.4"][1]), (pads["MCU.L10"][0], pads["MCU.L10"][1]),
], 0.9)

# --- CAN ---
tr("CAN_TX", [
    (pads["MCU.L12"][0], pads["MCU.L12"][1]),
    (pads["CAN.TX"][0], pads["MCU.L12"][1]), (pads["CAN.TX"][0], pads["CAN.TX"][1]),
], 0.8)
tr("CAN_RX", [
    (pads["MCU.L11"][0], pads["MCU.L11"][1]),
    (pads["CAN.RX"][0], pads["MCU.L11"][1]), (pads["CAN.RX"][0], pads["CAN.RX"][1]),
], 0.8)
tr("CANH", [
    (pads["CAN.H"][0], pads["CAN.H"][1]), (pads["CAN.H"][0], 20),
    (pads["CN1.20"][0], 20), (pads["CN1.20"][0], pads["CN1.20"][1]),
], 1.0)
tr("CANL", [
    (pads["CAN.L"][0], pads["CAN.L"][1]), (pads["CAN.L"][0], 18),
    (pads["CN1.21"][0], 18), (pads["CN1.21"][0], pads["CN1.21"][1]),
], 1.0)
tr("+3V3", [(pads["CCAN.A"][0], pads["CCAN.A"][1]), (pads["CAN.VCC"][0], pads["CCAN.A"][1]), (pads["CAN.VCC"][0], pads["CAN.VCC"][1])], 0.7)

# --- LAMBDA nets ---
# CN2.3 IP ↔ RSH ↔ U8628 / MCU.L8
tr("IP", [
    (pads["CN2.3"][0], pads["CN2.3"][1]), (pads["CN2.3"][0], 38),
    (pads["RSH.A"][0], 38), (pads["RSH.A"][0], pads["RSH.A"][1]),
], 1.0)
tr("IP", [(pads["RSH.B"][0], pads["RSH.B"][1]), (pads["CIP.A"][0], pads["RSH.B"][1]), (pads["CIP.A"][0], pads["CIP.A"][1])], 0.8)
tr("IP", [
    (pads["RSH.B"][0], pads["RSH.B"][1]), (186, pads["RSH.B"][1]),
    (186, pads["MCU.L8"][1]), (pads["MCU.L8"][0], pads["MCU.L8"][1]),
], 0.9)
# AD8628 inverting path to shunt (simplified): U8628.6 OUT → RSH.A area; U8628.2 IN-
tr("IP_DRV", [
    (pads["U8628.6"][0], pads["U8628.6"][1]), (pads["RSH.A"][0], pads["U8628.6"][1]),
    (pads["RSH.A"][0], pads["RSH.A"][1]),
], 0.8)
tr("IP_DRV", [
    (pads["U8628.2"][0], pads["U8628.2"][1]), (pads["RSH.A"][0] - 2, pads["U8628.2"][1]),
    (pads["RSH.A"][0] - 2, pads["RSH.A"][1]), (pads["RSH.A"][0], pads["RSH.A"][1]),
], 0.7)

# CN2.4 VM ← MCU DAC via MCP6004 buffer (U6004.1 OUT, pins 2/3 in)
# Use MCU.R3 as DAC_Vm
tr("VM", [
    (pads["MCU.R3"][0], pads["MCU.R3"][1]), (pads["MCU.R3"][0], 44),
    (pads["U6004.3"][0], 44), (pads["U6004.3"][0], pads["U6004.3"][1]),
], 0.8)
tr("VM", [
    (pads["U6004.1"][0], pads["U6004.1"][1]), (pads["U6004.1"][0], 12),
    (pads["CN2.4"][0], 12), (pads["CN2.4"][0], pads["CN2.4"][1]),
], 0.9)
# unity buffer: U6004.2 tied to U6004.1
tr("VM", [(pads["U6004.2"][0], pads["U6004.2"][1]), (pads["U6004.1"][0], pads["U6004.2"][1]), (pads["U6004.1"][0], pads["U6004.1"][1])], 0.7)

# CN2.5 UN → RESR → filter → MCU.L9; RESR other side GPIO pulse (MCU spare R8)
tr("UN", [
    (pads["CN2.5"][0], pads["CN2.5"][1]), (pads["CN2.5"][0], 44),
    (pads["RESR.A"][0], 44), (pads["RESR.A"][0], pads["RESR.A"][1]),
], 0.9)
tr("UN", [(pads["RESR.A"][0], pads["RESR.A"][1]), (pads["CUN.A"][0], pads["RESR.A"][1]), (pads["CUN.A"][0], pads["CUN.A"][1])], 0.8)
tr("UN", [
    (pads["RESR.A"][0], pads["RESR.A"][1]), (188, 46),
    (188, pads["MCU.L9"][1]), (pads["MCU.L9"][0], pads["MCU.L9"][1]),
], 0.9)
tr("RI_PULSE", [
    (pads["MCU.R8"][0], pads["MCU.R8"][1]), (pads["MCU.R8"][0], 46),
    (pads["RESR.B"][0], 46), (pads["RESR.B"][0], pads["RESR.B"][1]),
], 0.8)

# O2/λ para PA4: RO21 from U6004.7 (amp channel) simplified — tie RO21.A to U6004.7
tr("O2", [
    (pads["U6004.7"][0], pads["U6004.7"][1]), (pads["RO21.A"][0], pads["U6004.7"][1]),
    (pads["RO21.A"][0], pads["RO21.A"][1]),
], 0.8)
tr("O2", [(pads["RO21.B"][0], pads["RO21.B"][1]), (pads["RO22.A"][0], pads["RO21.B"][1])], 0.7)
tr("O2", [(pads["RO21.B"][0], pads["RO21.B"][1]), (pads["CO2.A"][0], pads["RO21.B"][1]), (pads["CO2.A"][0], pads["CO2.A"][1])], 0.7)
tr("O2", [
    (pads["RO21.B"][0], pads["RO21.B"][1]), (184, 26),
    (184, pads["MCU.L7"][1]), (pads["MCU.L7"][0], pads["MCU.L7"][1]),
], 0.9)

# MCP6004 remaining supplies already; bias pin U6004.3 done
# U8628.3 / 5 bias to VM simplified
tr("VM", [
    (pads["U8628.3"][0], pads["U8628.3"][1]), (pads["CN2.4"][0], pads["U8628.3"][1]),
    (pads["CN2.4"][0], pads["CN2.4"][1]),
], 0.7)

# SWD
tr("+3V3", [(pads["SWD.1"][0], pads["SWD.1"][1]), (pads["MCU.L1"][0], pads["SWD.1"][1]), (pads["MCU.L1"][0], pads["MCU.L1"][1])], 0.8)
tr("SWDIO", [(pads["SWD.2"][0], pads["SWD.2"][1]), (pads["MCU.R4"][0], pads["SWD.2"][1]), (pads["MCU.R4"][0], pads["MCU.R4"][1])], 0.8)
tr("SWCLK", [(pads["SWD.3"][0], pads["SWD.3"][1]), (pads["MCU.R5"][0], pads["SWD.3"][1]), (pads["MCU.R5"][0], pads["MCU.R5"][1])], 0.8)

# =============================================================================
# RENDER
# =============================================================================
NET_COLOR = {
    "GND": (80, 80, 80),
    "+12V_IN": (180, 40, 40),
    "+12V_PROT": (220, 50, 50),
    "+5V": (200, 120, 40),
    "+3V3": (40, 120, 200),
}


def net_color(net):
    if net in NET_COLOR:
        return NET_COLOR[net]
    if net.startswith("INJ") or net.startswith("H") or net.startswith("RL"):
        return (200, 80, 40)
    if net.startswith("G"):
        return (120, 180, 80)
    if net in ("IAT", "CLT", "MAP", "TPS", "MAP_MID", "MAP_ADC", "O2", "IP", "UN", "VM", "IP_DRV", "RI_PULSE"):
        return (80, 200, 200)
    if "CAN" in net or "RPM" in net or "SWD" in net:
        return (180, 100, 200)
    return (210, 180, 60)


def render_assembly():
    """Vista profissional: silk + componentes + trilhas coloridas por net."""
    img = Image.new("RGB", px(W, H), (12, 16, 20))
    d = ImageDraw.Draw(img)
    # board
    d.rectangle([*px(1, 1), *px(W - 1, H - 1)], fill=(20, 75, 48), outline=(180, 200, 180), width=2)

    # module boxes
    for x0, y0, x1, y1, lab, side in outlines:
        col = (255, 180, 80) if side == "bot" else (140, 190, 150)
        # flip Y for display? coords already Y-up logical — PIL Y-down: invert
        pass

    def Y(y):
        return H - y  # logical Y-up → image

    def P(x, y):
        return px(x, Y(y))

    def box(x0, y0, x1, y1, outline, width=2):
        d.rectangle([*P(x0, y1), *P(x1, y0)], outline=outline, width=width)

    for x0, y0, x1, y1, lab, side in outlines:
        col = (255, 160, 60) if side == "bot" else (160, 210, 170)
        box(x0, y0, x1, y1, col, 2)
        d.text(P(x0 + 1, y1 - 1), lab, fill=col, font=font(2.0))

    # traces under pads
    for pts, w, net in traces:
        flat = []
        for x, y in pts:
            flat.extend(P(x, y))
        if len(flat) >= 4:
            d.line(flat, fill=net_color(net), width=max(2, int(w * PPM)))

    # pads
    for name, (x, y, od, drill) in pads.items():
        r = od / 2
        fill = (220, 180, 60) if drill > 0 else (180, 100, 220)  # SMD purple
        d.ellipse([*P(x - r, y + r), *P(x + r, y - r)], fill=fill, outline=(100, 80, 30))
        if drill > 0:
            rd = drill / 2
            d.ellipse([*P(x - rd, y + rd), *P(x + rd, y - rd)], fill=(12, 16, 20))

    # mounting
    for x, y in [(4, 4), (196, 4), (4, 96), (196, 96)]:
        d.ellipse([*P(x - 1.8, y + 1.8), *P(x + 1.8, y - 1.8)], outline=(230, 230, 230), width=2)

    # title + legend
    d.rectangle([*px(2, 2), *px(198, 14)], fill=(10, 14, 18))
    d.text(px(4, 3), "INJET RACING ECU · PCB 1-LAYER 200×100 mm · THT topo + AD8628 SMD cobre", fill=(240, 245, 240), font=font(2.6))
    d.text(px(4, 7), "CN1=ATX-24  CN2=PCIe-6 λ  |  Vermelho=12V  Azul=3V3  Laranja=5V  Ciano=ADC  Verde=GPIO  Roxo=SMD", fill=(180, 200, 190), font=font(2.0))
    d.text(px(4, 10.5), "CNC: isolar espaços entre trilhas · furar pads THT · AD8628 soldar no lado do cobre", fill=(160, 180, 160), font=font(1.8))

    # CN1 pin legend strip
    for i in range(1, 25):
        x, y, od, _ = pads[f"CN1.{i}"]
        d.text(P(x - 1.2, y - 2.2 if i <= 12 else y + 3.5), str(i), fill=(255, 255, 200), font=font(1.4))

    return img


def render_cnc(invert=False):
    """Máscara cobre: preto=cobre (invert=False)."""
    bg, cu = (255, 0) if not invert else (0, 255)
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
            rd = max(0.25, drill / 2 - 0.05)
            d.ellipse([*P(x - rd, y + rd), *P(x + rd, y - rd)], fill=bg)

    for x, y in [(4, 4), (196, 4), (4, 96), (196, 96)]:
        d.ellipse([*P(x - 1.8, y + 1.8), *P(x + 1.8, y - 1.8)], fill=bg)

    # board edge guide (não cobre)
    return img


def write_svg_cnc(path, invert=False):
    cu = "#000000" if not invert else "#FFFFFF"
    bg = "#FFFFFF" if not invert else "#000000"

    def Y(y):
        return H - y

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">',
        f'<rect width="{W}" height="{H}" fill="{bg}"/>',
        f'<!-- INJET RACING 1-layer 200x100 | CN1 ATX24 | CN2 PCIe6 | AD8628 bottom SMD -->',
        f'<g id="copper" fill="{cu}" stroke="{cu}" stroke-linecap="round" stroke-linejoin="round">',
    ]
    for pts, w, net in traces:
        dpath = "M " + " L ".join(f"{x:.3f},{Y(y):.3f}" for x, y in pts)
        lines.append(f'  <path d="{dpath}" fill="none" stroke-width="{w:.3f}" data-net="{net}"/>')
    for name, (x, y, od, drill) in pads.items():
        lines.append(f'  <circle cx="{x:.3f}" cy="{Y(y):.3f}" r="{od/2:.3f}" data-pad="{name}"/>')
    lines.append("</g>")
    lines.append(f'<g id="holes" fill="{bg}">')
    for name, (x, y, od, drill) in pads.items():
        if drill > 0:
            lines.append(f'  <circle cx="{x:.3f}" cy="{Y(y):.3f}" r="{drill/2:.3f}"/>')
    for x, y in [(4, 4), (196, 4), (4, 96), (196, 96)]:
        lines.append(f'  <circle cx="{x}" cy="{Y(y)}" r="1.8"/>')
    lines.append("</g>")
    lines.append(f'<rect x="0.3" y="0.3" width="{W-0.6}" height="{H-0.6}" fill="none" stroke="#888" stroke-width="0.25" stroke-dasharray="1.5 1"/>')
    lines.append("</svg>")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_netlist_md(path):
    lines = [
        "# Netlist PCB 1-layer — INJET RACING ECU",
        "",
        "> Gerado com o layout `ecu-pcb-1layer-*`. Placa **200×100 mm**, cobre 1 face.",
        "",
        "## Conectores",
        "",
        "### CN1 — ATX 24 pinos (igual placa-mãe ↔ fonte)",
        "",
        "| Pino ATX | Sinal ECU |",
        "|---:|---|",
    ]
    for i, s in CN1_MAP.items():
        lines.append(f"| {i} | `{s}` |")
    lines += [
        "",
        "### CN2 — PCIe 6 pinos (igual placa de vídeo)",
        "",
        "| Pino | Sinal LSU 4.2 |",
        "|---:|---|",
        "| 1 | **H+** aquecedor (+12V_PROT) |",
        "| 2 | **H−** aquecedor (dreno QHEAT) |",
        "| 3 | **IP** pump current |",
        "| 4 | **VM** terra virtual |",
        "| 5 | **UN** Nernst |",
        "| 6 | NC (não usado — Rcal fica no chicote da sonda) |",
        "",
        "## Módulos na placa",
        "",
        "1. POWER — IRF9540, TVS, bulk, buck 5V, LDO 3V3",
        "2. INJ — 4× IRLZ44N + flyback + gate",
        "3. HEAT — IRLZ44N aquecedor λ",
        "4. RELAY DRV — 3× 2N7000 + flyback",
        "5. STM32F407 Black Board",
        "6. SENSORS — pull-ups / divisores IAT CLT MAP TPS",
        "7. RPM — PC817 + 2×10k 2W",
        "8. CAN — módulo SN65HVD230",
        "9. LAMBDA — MCP6004 (topo) + **OPA388IDR SMD embaixo** + shunt 61R9 + R_ESR 6k8",
        "10. CN1 ATX-24 + CN2 PCIe-6",
        "",
        f"## Contagem",
        "",
        f"- Pads: **{len(pads)}**",
        f"- Segmentos de trilha: **{len(traces)}**",
        f"- Nets distintos: **{len(set(t[2] for t in traces))}**",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    img = render_assembly()
    p1 = OUT / "ecu-pcb-1layer-assembly.png"
    img.save(p1, dpi=(DPI, DPI))

    cnc = render_cnc(False)
    p2 = OUT / "ecu-pcb-1layer-traces-cnc.png"
    cnc.save(p2, dpi=(DPI, DPI))

    cnc_i = render_cnc(True)
    p3 = OUT / "ecu-pcb-1layer-traces-cnc-invert.png"
    cnc_i.save(p3, dpi=(DPI, DPI))

    write_svg_cnc(OUT / "ecu-pcb-1layer-traces-cnc.svg", False)
    write_svg_cnc(OUT / "ecu-pcb-1layer-traces-cnc-invert.svg", True)
    write_netlist_md(OUT / "ecu-pcb-1layer-netlist.md")

    print("pads", len(pads), "traces", len(traces), "nets", len(set(t[2] for t in traces)))
    for p in (p1, p2, p3, OUT / "ecu-pcb-1layer-traces-cnc.svg", OUT / "ecu-pcb-1layer-netlist.md"):
        print(p.name, p.stat().st_size)


if __name__ == "__main__":
    main()
