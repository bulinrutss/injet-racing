"""Pinout STM32F4VE Ver V33 — só headers laterais 2×24 (silk inferior).

Orientação: topo = USART/SWD (como na foto).
  J2 esq. (LO|LI): 3V3 2×2 · BT · GND 2×2 · GPIO
  J3 dir. (RO|RI): 5V 2×2 · 3V3 2×2 · GND · GPIO
LO/RO = coluna exterior · LI/RI = coluna interior (par silk esq|dir).

PCB prodv6 (2026-08-11): U1 @ (60.46, 107.94) — nets nos pads = roteamento 1-face;
pads sem net ECU ficam NC no header (trilha passa por outro pad).
"""

BB_PITCH = 2.54
BB_COL_LO = 0.0
BB_COL_LI = 2.54
BB_COL_RO = 50.0
BB_COL_RI = 52.54
BB_NROWS = 24

LEFT_3V3_ROWS = (0, 1)
LEFT_GND_ROWS = (3, 4)
RIGHT_5V_ROWS = (0, 1)
RIGHT_3V3_ROWS = (2, 3)
RIGHT_GND_ROW = 4
VREF_ROW = 10
VREF_COL = BB_COL_RO  # UR+ coluna ext dir.

U1_AT_PCB = (60.46, 107.94)

JL32_LEFT: list[tuple[str, str]] = [
    ("3V3", "3V3"), ("3V3", "3V3"),
    ("BT1", "BT0"), ("GND", "GND"), ("GND", "GND"),
    ("PE0", "PE1"), ("PB8", "PB9"), ("PB6", "PB7"), ("PB3", "PB5"),
    ("PD6", "PD7"), ("PD4", "PD5"), ("PD2", "PD3"), ("PD0", "PD1"),
    ("PC11", "PC12"), ("PA15", "PC10"), ("PA11", "PA12"), ("PA9", "PA10"),
    ("PC9", "PA8"), ("PC7", "PC8"), ("PD15", "PC6"), ("PD13", "PD14"),
    ("PD11", "PD12"), ("PD9", "PD10"), ("PB15", "PD8"),
]

JL32_RIGHT: list[tuple[str, str]] = [
    ("5V", "5V"), ("5V", "5V"),
    ("3V3", "3V3"), ("3V3", "3V3"),
    ("GND", "GND"),
    ("PE3", "PE2"), ("PE5", "PE4"), ("PC13", "PE6"), ("PC1", "PC0"),
    ("PC3", "PC2"), ("UR+", "UR-"), ("PA1", "PA0"), ("PA3", "PA2"),
    ("PA5", "PA4"), ("PA7", "PA6"), ("PC5", "PC4"), ("PB1", "PB0"),
    ("PE8", "PE7"), ("PE10", "PE9"), ("PE12", "PE11"), ("PE14", "PE13"),
    ("PB10", "PE15"), ("PB12", "PB11"), ("PB14", "PB13"),
]


def pad_gpio(pad: str) -> str:
    """GPIO do STM32 para pad do socket U1 (ex.: L12O -> PD0)."""
    row = int(pad[1:-1])
    col = pad[-1]
    if pad[0] == "L":
        lo, li = JL32_LEFT[row]
        return lo if col == "O" else li
    ro, ri = JL32_RIGHT[row]
    return ro if col == "O" else ri


def u1_pad_xy(pad: str) -> tuple[float, float]:
    """Posição absoluta mm do pad U1 no .kicad_pcb."""
    row = int(pad[1:-1])
    col = BB_COL_LO if pad[-1] == "O" else BB_COL_LI
    if pad[0] == "R":
        col = BB_COL_RO if pad[-1] == "O" else BB_COL_RI
    ox, oy = U1_AT_PCB
    return (ox + col, oy - row * BB_PITCH)


# --- Pads com net ECU no .kicad_pcb (2026-08-11) ---

U1_SENS_PAD: dict[str, str] = {
    "IAT": "L12O",   # PD0
    "CLT": "L16O",   # PA9
    "MAP": "L17O",   # PC9
    "TPS": "L18I",   # PC8  (+ L18O=PC7 trilha bypass)
    "VBAT": "L17I",  # PA8  (+ L20I/L20O trilha bypass)
}

U1_RPM_PAD = "R17O"  # PE8

U1_REL_PAD: dict[str, str] = {
    "GRL1": "L22I",  # PD10
    "GRL2": "L23I",  # PD8
    "GRL3": "L22O",  # PD9
}

U1_CAN_PAD: dict[str, str] = {
    "CAN_RX": "L6O",   # PB8
    "CAN_TX": "L6I",   # PB9
}

U1_LAMBDA_PAD: dict[str, str] = {
    "VM": "R13I",        # PA4 DAC
    "IP": "R13O",        # PA5 ADC (+ R12I/R12O trilha IP)
    "UN": "R14I",        # PA6
    "RI_PULSE": "R5I",   # PE2
}

U1_HEAT_PAD: dict[str, str] = {
    "GHEAT": "R16I",  # PB0 PWM
}

U1_INJ_PAD: dict[str, str] = {
    "GINJ1": "R18I",  # PE9
    "GINJ2": "R19I",  # PE11
    "GINJ3": "R20I",  # PE13
    "GINJ4": "R21I",  # PE15
}

# Pads só trilha (sem GPIO ECU no furo original)
U1_TRACE_BYPASS: dict[str, str] = {
    "TPS": "L18O",       # PC7 — furo NC (trilha TPS)
    "VBAT": "L20I",      # PD14 — furo NC
    "VBAT2": "L20O",     # PD13 — furo NC
    "IP": "R12O",        # PA3 — trilha paralela IP
}

ECU_GPIO_NET: dict[str, str] = {
    "5V": "+5V",
    "3V3": "+3V3",
    "GND": "GND",
    "UR+": "VREF+",
    "PD0": "IAT",
    "PA9": "CLT",
    "PC9": "MAP",
    "PA8": "VBAT",
    "PC8": "TPS",
    "PA4": "VM",
    "PA5": "IP",
    "PA6": "UN",
    "PE2": "RI_PULSE",
    "PE8": "RPM_IN",
    "PB8": "CAN_RX",
    "PB9": "CAN_TX",
    "PE9": "GINJ1",
    "PE11": "GINJ2",
    "PE13": "GINJ3",
    "PE15": "GINJ4",
    "PD10": "GRL1",
    "PD8": "GRL2",
    "PD9": "GRL3",
    "PB0": "GHEAT",
}


def gpio_net(name: str) -> str:
    return ECU_GPIO_NET.get(name, "")
