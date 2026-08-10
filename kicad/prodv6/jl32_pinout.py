"""Pinout STM32F4VE Ver V33 — só headers laterais 2×24 (silk inferior).

Orientação: topo = USART/SWD (como na foto).
  J2 esq. (LO|LI): 3V3 2×2 · BT · GND 2×2 · GPIO
  J3 dir. (RO|RI): 5V 2×2 · 3V3 2×2 · GND · GPIO
LO/RO = coluna exterior · LI/RI = coluna interior (par silk esq|dir).
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

# Sensores ADC — J2 esquerda (U1 @ 86,108 no prodv6 PCB)
U1_RPM_PAD = "R17O"  # PE8 @ (136, 64.82)

U1_SENS_PAD: dict[str, str] = {
    "IAT": "L12O",   # PC11 ADC1_IN11
    "CLT": "L16O",   # PC9  ADC1_IN9
    "MAP": "L17O",   # PC7  ADC1_IN7
    "TPS": "L18I",   # PC6  ADC1_IN6
    "VBAT": "L17I",  # PC8  ADC1_IN8
}

# Gate relés — J2 esquerda (U1 @ 86,108) — nets GRL* no MCU, RL* bobina
U1_REL_PAD: dict[str, str] = {
    "GRL1": "L22I",  # PD10 RL_MAIN @ (88.54, 52.12)
    "GRL2": "L23I",  # PD8  RL_PUMP  @ (88.54, 49.58)
    "GRL3": "L22O",  # PD9  RL_IAC   @ (86.00, 52.12)
}

# CAN — J2 esquerda row6 (U1 @ 86,108)
U1_CAN_PAD: dict[str, str] = {
    "CAN_RX": "L6O",  # PB8  @ (86.00, 92.76)
    "CAN_TX": "L6I",  # PB9  @ (88.54, 92.76)
}

# Lambda — J3 direita rows 13–14 (U1 @ 86,108)
U1_LAMBDA_PAD: dict[str, str] = {
    "VM": "R13I",  # PA4 DAC  @ (138.54, 74.98)
    "IP": "R13O",  # PA5 ADC  @ (136.00, 74.98)
    "UN": "R14I",  # PA6 ADC  @ (138.54, 77.52)
}

# Aquecedor λ — J2 esquerda row21 (U1 @ 86,108)
U1_HEAT_PAD: dict[str, str] = {
    "GHEAT": "L21I",  # PD12 PWM @ (88.54, 54.66)
}

# Gate drivers injetores — J3 direita (U1 @ 86,108)
U1_INJ_PAD: dict[str, str] = {
    "GINJ1": "R18I",  # PE9  @ (138.54, 62.28)
    "GINJ2": "R19I",  # PE11 @ (138.54, 59.74)
    "GINJ3": "R20I",  # PE13 @ (138.54, 57.20)
    "GINJ4": "R21I",  # PE15 @ (138.54, 54.66)
}

ECU_GPIO_NET: dict[str, str] = {
    "5V": "+5V",
    "3V3": "+3V3",
    "GND": "GND",
    "UR+": "VREF+",
    "PC11": "IAT",
    "PC9": "CLT",
    "PC7": "MAP",
    "PC8": "VBAT",
    "PC6": "TPS",
    "PA4": "VM",
    "PA5": "IP",
    "PA6": "UN",
    "PE8": "RPM_IN",  # R17O — U1 @ (86,108)
    "PB8": "CAN_RX",
    "PB9": "CAN_TX",
    "PE9": "GINJ1",
    "PE11": "GINJ2",
    "PE13": "GINJ3",
    "PE15": "GINJ4",
    "PD10": "GRL1",
    "PD8": "GRL2",
    "PD9": "GRL3",
    "PD12": "GHEAT",
}


def gpio_net(name: str) -> str:
    return ECU_GPIO_NET.get(name, "")
