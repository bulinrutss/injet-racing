"""
Esquemático produção INJET RACING — folha única, circuito completo com fios.

CN1 = ATX 24 pinos (placa-mãe PC) — chicote motor
CN2 = PCIe 6 pinos (placa de vídeo) — sonda lambda LSU 4.2
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from _gen_kicad_ecu import SchDoc

# Pinagem CN1 — modulo/esquema-eletrico.md §9.1
CN1_NETS: dict[int, str] = {
    1: "+12V_IGN", 2: "+12V_BAT", 3: "GND", 4: "GND", 5: "GND_SIG",
    6: "+5V", 7: "+3V3", 8: "IAT", 9: "CLT", 10: "MAP", 11: "TPS", 12: "RPM_IN",
    13: "INJ1", 14: "INJ2", 15: "INJ3", 16: "INJ4",
    17: "RL_PUMP", 18: "RL_MAIN", 19: "RL_IAC",
    20: "CANH", 21: "CANL", 22: "TACHO", 23: "START", 24: "SHIELD",
}

CN2_NETS: dict[int, str] = {
    1: "+12V_PROT", 2: "H_MINUS", 3: "IP", 4: "VM", 5: "UN", 6: "NC",
}


def cn1_pin_xy(cx: float, cy: float, pin: int) -> tuple[float, float]:
    """Posição do pino Pn do símbolo CN_ATX24 (coluna esquerda)."""
    return cx - 5.08, cy + 30.48 - (pin - 1) * 2.54


def cn2_pin_xy(cx: float, cy: float, pin: int) -> tuple[float, float]:
    """PCIe-6: P1-P3 fila superior, P4-P6 fila inferior."""
    row = 0 if pin <= 3 else 1
    col = (pin - 1) if pin <= 3 else (pin - 4)
    return cx - 5.08 + col * 2.54, cy + 7.62 - row * 2.54


def stub_to_net(d: "SchDoc", x0: float, y0: float, x1: float, net: str, gen) -> None:
    """Trilha horizontal do conector + label local."""
    if abs(x0 - x1) > 0.1:
        d.add(gen.wire_h(x0, x1, y0))
    d.add(gen.label_local(net, x1 + 1.27, y0))


def build_complete_schematic(gen) -> "SchDoc":
    d = gen.SchDoc("INJET RACING ECU — Produção (CN1 ATX-24 + CN2 PCIe-6)", "1")
    d.add(gen.text_note(
        "Circuito completo Fase 1 · CN1=chicote ATX-24 · CN2=lambda PCIe-6 · PCB 200×100 mm 1-layer\n"
        "Black Board STM32F407 · buck MP1584 · +3V3 da Black Board (sem LDO extra) · LSU 4.2 DIY",
        15, 8, 2.0,
    ))

    # =========================================================================
    # CN1 — ATX 24 pinos (borda esquerda)
    # =========================================================================
    cn1_x, cn1_y = 45.0, 145.0
    d.sym("Injet:CN_ATX24", "CN1", "ATX-24 chicote", cn1_x, cn1_y,
          fp="Connector_PinHeader_2.54mm:PinHeader_2x12_P2.54mm")
    d.add(gen.text_note("CN1 — conector placa-mãe PC (2×12 passo 4,2 mm)", cn1_x - 5, cn1_y + 38, 1.3))

    bus_x = 78.0
    for pin, net in CN1_NETS.items():
        px, py = cn1_pin_xy(cn1_x, cn1_y, pin)
        if net in ("TACHO", "START", "NC"):
            d.add(gen.wire_h(px, bus_x, py), gen.no_connect(bus_x, py))
            d.add(gen.label_local(f"P{pin}:{net}", bus_x + 2, py, 0))
        elif net == "SHIELD":
            stub_to_net(d, px, py, bus_x, "GND", gen)
        else:
            stub_to_net(d, px, py, bus_x, net, gen)

    # Barras de alimentação (ligam blocos internos aos stubs CN1)
    d.add(
        gen.wire_v(95, 40, 320),
        gen.label_global("+12V_BAT", 95, 45, "input"),
        gen.label_global("+12V_IGN", 95, 55, "input"),
        gen.label_global("+12V_PROT", 95, 200, "output"),
        gen.label_global("+5V", 95, 260, "output"),
        gen.label_global("+3V3", 95, 280, "output"),
        gen.label_global("GND", 95, 300, "passive"),
        gen.label_global("GND_SIG", 95, 310, "passive"),
    )

    # =========================================================================
    # POWER — CN1.2 → F1 → Q1 → +12V_PROT → MP1584 → +5V
    # =========================================================================
    px, py = 120, 50
    d.add(gen.label_local("+12V_BAT", bus_x, cn1_pin_xy(cn1_x, cn1_y, 2)[1]))
    d.add(gen.wire_h(bus_x, px - 10, cn1_pin_xy(cn1_x, cn1_y, 2)[1]),
          gen.wire_h(px - 10, px - 10, py), gen.wire_h(px - 10, px - 7.5, py))

    d.sym("Device:Fuse", "F1", "5A", px, py)
    d.add(gen.wire_h(px - 7.5, px + 7.5, py), gen.wire_h(px + 7.5, px + 20, py))

    d.sym("Device:Q_PMOS", "Q1", "IRF9540", px + 30, py)
    d.add(gen.wire_h(px + 20, px + 22.5, py), gen.wire_h(px + 37.5, px + 55, py))
    gen.place_r(d, "R1", "100k", px + 30, py + 15)
    gen.place_d(d, "D1", "15V Zener", px + 40, py + 15)
    d.add(gen.wire_v(px + 30, py + 7.5, py + 12.5), gen.wire_h(px + 30, px + 40, py + 17.5),
          gen.wire_v(px + 40, py + 12.5, py + 17.5), gen.wire_h(px + 40, px + 55, py + 17.5))
    gen.place_gnd(d, px + 55, py + 17.5)

    d.add(gen.label_global("+12V_PROT", px + 58, py, "output"),
          gen.wire_h(px + 55, px + 65, py))

    gen.place_d(d, "D2", "TVS 33V", px + 75, py + 10)
    gen.place_c(d, "C1", "220uF", px + 75, py - 5)
    gen.place_c(d, "C2", "100nF", px + 90, py - 5)
    d.add(gen.wire_h(px + 65, px + 72.5, py), gen.wire_v(px + 75, py, py - 7.5),
          gen.wire_v(px + 75, py + 7.5, py + 10), gen.wire_h(px + 65, px + 95, py))
    gen.place_gnd(d, px + 75, py + 10)
    gen.place_gnd(d, px + 90, py - 5)

    d.sym("Injet:MP1584", "U2", "MP1584", px + 115, py)
    d.add(gen.wire_h(px + 95, px + 102.5, py), gen.wire_h(px + 95, px + 102.5, py - 12),
          gen.wire_h(px + 127.5, px + 145, py - 12))
    gen.place_c(d, "C3", "100uF", px + 105, py - 12)
    gen.place_c(d, "C4", "100nF", px + 120, py - 12)
    gen.place_c(d, "C5", "220uF", px + 135, py - 12)
    gen.place_c(d, "C6", "100nF", px + 150, py - 12)
    d.add(gen.wire_v(px + 115, py - 7.5, py - 12), gen.wire_h(px + 105, px + 155, py - 12))
    gen.place_gnd(d, px + 130, py - 12)

    d.add(gen.label_global("+5V", px + 148, py - 12, "output"),
          gen.wire_h(px + 145, px + 155, py - 12))

    d.add(gen.text_note("+12V_IGN (CN1-1) acorda ECU — ligar à mesma barra +12V_BAT ou relé ignição", px, py + 28, 1.2))

    # =========================================================================
    # MCU — Black Board + REF3033 + barra +3V3
    # =========================================================================
    mx, my = 210, 90
    d.sym("Injet:BLACK_BOARD", "U1", "STM32F407 Black Board", mx, my)
    d.add(gen.wire_h(px + 155, mx - 20, py - 12), gen.wire_v(mx - 20, py - 12, my + 15),
          gen.wire_h(mx - 20, mx - 12.5, my + 15))
    d.add(gen.wire_h(mx - 20, mx - 12.5, my - 5), gen.wire_v(mx - 20, my - 5, my - 10))
    gen.place_v5(d, mx - 25, my + 15)
    gen.place_gnd(d, mx - 25, my - 10)

    d.sym("Injet:REF3033", "U8", "REF3033", mx, my - 35)
    gen.place_c(d, "C10", "100nF", mx - 15, my - 35)
    gen.place_c(d, "C11", "10uF", mx + 15, my - 35)
    d.add(gen.wire_h(mx - 20, mx - 7.5, my - 35), gen.wire_h(mx - 7.5, mx + 7.5, my - 35),
          gen.wire_h(mx + 7.5, mx + 25, my - 35))
    gen.place_gnd(d, mx, my - 28)
    d.add(gen.label_local("VREF+", mx + 28, my - 35))

    gen.place_c(d, "C12", "10uF", mx + 35, my + 5)
    gen.place_c(d, "C13", "100nF", mx + 50, my + 5)
    d.add(gen.wire_h(mx + 20, mx + 32.5, my + 15), gen.wire_h(mx + 32.5, mx + 55, my + 5))
    gen.place_v33(d, mx + 35, my + 5)
    d.add(gen.label_global("+3V3", mx + 58, my + 5, "output"), gen.wire_h(mx + 55, mx + 65, my + 5))

    # GPIO → nets (fio + label para drivers/sensores)
    gpio_map = [
        ("PA0", "IAT"), ("PA1", "CLT"), ("PA2", "MAP"), ("PA3", "TPS"),
        ("PA4", "VM"), ("PA5", "IP"), ("PA6", "UN"), ("PC0", "RI_PULSE"), ("PC1", "VBAT"),
        ("PB0", "RPM_OUT"), ("PB8", "CAN_RX"), ("PB9", "CAN_TX"),
        ("PE9", "GINJ1"), ("PE11", "GINJ2"), ("PE13", "GINJ3"), ("PE14", "GINJ4"),
        ("PD8", "GRL1"), ("PD9", "GRL2"), ("PD10", "GRL3"), ("PD12", "GHEAT"),
    ]
    gx = mx + 45
    for i, (mcu, net) in enumerate(gpio_map):
        gy = my + 25 - i * 4.5
        d.add(gen.wire_h(mx + 20, gx, my + 15.24 - i * 2.54 if i < 20 else gy),
              gen.label_local(net, gx + 2, gy))

    # SWD: gravação só via USB/SWD da Black Board (sem CN3 na ECU)

    # =========================================================================
    # SENSORES — IAT CLT MAP TPS VBat → MCU + CN1
    # =========================================================================
    sx, sy = 320, 70
    d.add(gen.text_note("Condicionamento sensores → CN1 p6/p7/p8-11", sx, sy - 15, 1.3))

    def sensor_ntc(ref_r: str, ref_c: str, ref_s: str, net: str, y: float, mcu_net: str) -> None:
        gen.place_r(d, ref_r, "2.26k", sx, y)
        gen.place_c(d, ref_c, "100nF", sx + 25, y)
        gen.place_r(d, ref_s, "1k", sx + 45, y)
        d.add(gen.label_global("+3V3", sx - 8, y, "passive"), gen.wire_h(sx - 8, sx - 3.5, y))
        d.add(gen.wire_h(sx - 3.5, sx + 2.5, y), gen.wire_h(sx + 2.5, sx + 22.5, y),
              gen.wire_h(sx + 27.5, sx + 42.5, y), gen.wire_h(sx + 47.5, sx + 60, y))
        d.add(gen.label_local(mcu_net, sx + 62, y), gen.label_local(net, sx + 62, y + 4))
        gen.place_gnd(d, sx + 25, y)

    sensor_ntc("R10", "C20", "R18", "IAT", sy, "IAT")
    sensor_ntc("R11", "C21", "R19", "CLT", sy + 18, "CLT")

    # MAP divisor
    y = sy + 36
    gen.place_r(d, "R12", "10k", sx, y)
    gen.place_r(d, "R13", "18k", sx + 15, y + 8)
    gen.place_c(d, "C22", "100nF", sx + 25, y)
    gen.place_r(d, "R16", "1k", sx + 45, y)
    d.add(gen.label_global("+5V", sx - 8, y, "passive"), gen.wire_h(sx - 8, sx - 3.5, y))
    d.add(gen.wire_h(sx - 3.5, sx + 2.5, y), gen.wire_v(sx + 15, y, y + 5.5),
          gen.wire_h(sx + 15, sx + 15, y + 8), gen.wire_h(sx + 2.5, sx + 47.5, y))
    gen.place_gnd(d, sx + 15, y + 8)
    d.add(gen.label_local("MAP", sx + 62, y))

    # TPS
    y = sy + 54
    gen.place_c(d, "C23", "100nF", sx + 25, y)
    gen.place_r(d, "R17", "1k", sx + 45, y)
    d.add(gen.label_global("+3V3", sx - 8, y, "passive"), gen.wire_h(sx - 8, sx + 42.5, y))
    gen.place_gnd(d, sx + 10, y + 8)
    d.add(gen.label_local("TPS", sx + 62, y))

    # VBat
    y = sy + 72
    gen.place_r(d, "R14", "100k 1%", sx, y)
    gen.place_r(d, "R15", "10k 1%", sx + 15, y + 8)
    gen.place_c(d, "C24", "100nF", sx + 25, y)
    d.add(gen.label_global("+12V_PROT", sx - 8, y, "passive"), gen.wire_h(sx - 8, sx - 3.5, y))
    d.add(gen.wire_h(sx - 3.5, sx + 2.5, y), gen.wire_v(sx + 15, y, y + 5.5), gen.wire_h(sx + 15, sx + 15, y + 8))
    gen.place_gnd(d, sx + 15, y + 8)
    d.add(gen.label_local("VBAT", sx + 62, y))

    # MAP +5V → CN1-6, +3V3 → CN1-7 (labels globais já ligam)

    # =========================================================================
    # RPM — PC817 → CN1-12
    # =========================================================================
    rx, ry = 320, 175
    d.sym("Injet:PC817", "U7", "PC817", rx, ry)
    gen.place_r(d, "R20", "10k 2W", rx - 25, ry + 10)
    gen.place_r(d, "R21", "10k 2W", rx - 15, ry + 10)
    gen.place_r(d, "R22", "4k7", rx + 25, ry + 5)
    gen.place_d(d, "D3", "1N4148", rx - 5, ry - 5)
    gen.place_c(d, "C25", "1nF", rx + 35, ry)
    d.add(gen.label_global("RPM_IN", rx - 35, ry + 10, "input"),
          gen.wire_h(rx - 35, rx - 27.5, ry + 10), gen.wire_h(rx - 12.5, rx - 7.5, ry + 10))
    d.add(gen.wire_h(rx - 7.5, rx - 5, ry - 5), gen.wire_h(rx + 7.5, rx + 30, ry + 5))
    d.add(gen.label_global("RPM_OUT", rx + 42, ry, "output"), gen.wire_h(rx + 37.5, rx + 42, ry))
    gen.place_gnd(d, rx - 5, ry - 5)
    gen.place_v33(d, rx - 35, ry + 20)
    gen.place_gnd(d, rx - 35, ry - 5)

    # =========================================================================
    # INJETORES 4× — CN1 p13-16
    # =========================================================================
    ix = 120
    for i in range(4):
        y = 175 - i * 22
        q, rg, rd, df = f"Q{10+i}", f"R{30+i}", f"R{40+i}", f"D{10+i}"
        d.add(gen.label_global(f"GINJ{i+1}", ix - 15, y, "input"),
              gen.wire_h(ix - 15, ix - 5, y))
        d.sym("Device:Q_NMOS", q, "IRLZ44N", ix + 10, y)
        gen.place_r(d, rg, "100R", ix - 5, y)
        gen.place_r(d, rd, "10k", ix + 10, y + 12)
        gen.place_d(d, df, "1N4007", ix + 25, y - 8)
        d.add(gen.wire_h(ix - 2.5, ix + 7.5, y), gen.wire_v(ix + 10, y + 7.5, y + 9.5),
              gen.wire_h(ix + 10, ix + 10, y + 12), gen.wire_h(ix + 25, ix + 30, y - 8))
        gen.place_gnd(d, ix + 10, y + 12)
        d.add(gen.label_global(f"INJ{i+1}", ix + 32, y, "output"),
              gen.wire_h(ix + 12.5, ix + 40, y))
        d.add(gen.label_global("+12V_PROT", ix + 32, y + 5, "passive"),
              gen.wire_h(ix + 30, ix + 40, y + 5), gen.wire_v(ix + 30, y - 8, y + 5))

    # =========================================================================
    # RELÉS 3× — CN1 p17-19
    # =========================================================================
    rlx = 210
    relays = [("GRL1", "RL_MAIN", "RL1", "Q20", 0), ("GRL2", "RL_PUMP", "RL2", "Q21", 1), ("GRL3", "RL_IAC", "RL3", "Q22", 2)]
    for gnet, cnet, rl, q, idx in relays:
        y = 175 - idx * 22
        d.add(gen.label_global(gnet, rlx - 15, y, "input"), gen.wire_h(rlx - 15, rlx - 5, y))
        d.sym("Device:Q_NMOS", q, "2N7000", rlx + 10, y)
        d.sym("Injet:Relay", rl, f"12V 30A", rlx + 35, y)
        gen.place_r(d, f"R{50+idx}", "1k", rlx - 5, y)
        gen.place_r(d, f"R{55+idx}", "10k", rlx + 10, y + 12)
        gen.place_d(d, f"D{20+idx}", "1N4007", rlx + 22, y - 6)
        d.add(gen.wire_h(rlx - 2.5, rlx + 7.5, y), gen.wire_h(rlx + 12.5, rlx + 30, y))
        gen.place_gnd(d, rlx + 10, y + 12)
        d.add(gen.label_global(cnet, rlx + 48, y, "output"), gen.wire_h(rlx + 42.5, rlx + 55, y))

    # =========================================================================
    # CAN — CN1 p20-21
    # =========================================================================
    cx, cy = 320, 240
    d.sym("Injet:SN65HVD230", "U6", "SN65HVD230", cx, cy)
    gen.place_c(d, "C40", "100nF", cx - 20, cy + 8)
    gen.place_c(d, "C41", "10uF", cx - 20, cy + 3)
    d.add(gen.label_global("CAN_TX", cx - 28, cy + 5, "input"),
          gen.wire_h(cx - 28, cx - 12.5, cy + 5))
    d.add(gen.label_global("CAN_RX", cx - 28, cy - 2, "output"),
          gen.wire_h(cx - 28, cx - 12.5, cy - 2))
    gen.place_v33(d, cx - 28, cy + 15)
    gen.place_gnd(d, cx - 28, cy - 10)
    d.add(gen.label_global("CANH", cx + 25, cy + 5, "bidirectional"),
          gen.wire_h(cx + 12.5, cx + 35, cy + 5))
    d.add(gen.label_global("CANL", cx + 25, cy - 2, "bidirectional"),
          gen.wire_h(cx + 12.5, cx + 35, cy - 2))

    # =========================================================================
    # LAMBDA + CN2 PCIe-6
    # =========================================================================
    cn2_x, cn2_y = 45.0, 285.0
    d.sym("Injet:CN_PCIE6", "CN2", "PCIe-6 Lambda", cn2_x, cn2_y,
          fp="Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm")
    d.add(gen.text_note("CN2 — conector GPU PCIe-6 (LSU 4.2 wideband)", cn2_x - 5, cn2_y + 12, 1.3))

    for pin, net in CN2_NETS.items():
        px, py = cn2_pin_xy(cn2_x, cn2_y, pin)
        if net == "NC":
            d.add(gen.wire_h(px, bus_x, py), gen.no_connect(bus_x, py))
        else:
            stub_to_net(d, px, py, bus_x, net, gen)

    lx, ly = 120, 270
    d.sym("Injet:MCP6004", "U4", "MCP6004", lx, ly)
    d.sym("Injet:AD8628", "U5", "AD8628", lx + 45, ly)
    gen.place_r(d, "R70", "61R9 1%", lx + 75, ly - 5)
    gen.place_r(d, "R71", "6k8 1%", lx + 75, ly - 15)
    gen.place_r(d, "R76", "10k", lx - 15, ly + 10)
    gen.place_r(d, "R77", "10k", lx - 15, ly + 5)
    gen.place_r(d, "R78", "1k", lx - 15, ly - 5)
    gen.place_c(d, "C30", "220nF", lx + 90, ly - 5)
    gen.place_c(d, "C31", "220nF", lx + 90, ly - 15)
    gen.place_c(d, "C32", "100nF", lx - 25, ly + 10)
    gen.place_c(d, "C33", "10uF", lx - 25, ly + 5)
    gen.place_v5(d, lx - 25, ly + 15)
    gen.place_gnd(d, lx - 25, ly - 15)

    d.add(gen.label_global("VM", lx + 15, ly + 8, "passive"),
          gen.wire_h(lx + 5, lx + 20, ly + 8))
    d.add(gen.label_global("IP", lx + 70, ly - 5, "passive"),
          gen.wire_h(lx + 60, lx + 80, ly - 5))
    d.add(gen.label_global("UN", lx + 70, ly - 15, "passive"),
          gen.wire_h(lx + 60, lx + 80, ly - 15))

    # Aquecedor
    d.sym("Device:Q_NMOS", "Q30", "IRLZ44N", lx + 110, ly)
    gen.place_r(d, "R80", "100R", lx + 95, ly)
    gen.place_r(d, "R81", "10k", lx + 110, ly + 12)
    gen.place_d(d, "D30", "1N4007", lx + 125, ly - 8)
    d.add(gen.label_global("GHEAT", lx + 88, ly, "input"), gen.wire_h(lx + 88, lx + 92.5, ly))
    d.add(gen.label_global("H_MINUS", lx + 135, ly, "output"), gen.wire_h(lx + 112.5, lx + 145, ly))
    d.add(gen.label_global("+12V_PROT", lx + 135, ly + 8, "passive"),
          gen.wire_h(lx + 130, lx + 145, ly + 8), gen.wire_v(lx + 130, ly - 8, ly + 8))
    gen.place_gnd(d, lx + 110, ly + 12)

    d.add(gen.text_note(
        "CN2: 1=H+ (+12V_PROT)  2=H- (Q30)  3=IP  4=VM (PA4 DAC)  5=UN (PA6)  6=NC",
        lx, ly - 25, 1.2,
    ))

    # Tabela pinagem CN1
    tbl = "CN1: 1=+12V_IGN 2=+12V_BAT 3-4=GND 5=GND_SIG 6=+5V 7=+3V3 8=IAT 9=CLT 10=MAP 11=TPS 12=RPM"
    d.add(gen.text_note(tbl, 15, 330, 1.15))
    tbl2 = "13-16=INJ1-4  17=bomba 18=main 19=IAC  20=CANH 21=CANL  22=TACHO 23=START 24=SHIELD"
    d.add(gen.text_note(tbl2, 15, 336, 1.15))

    return d
