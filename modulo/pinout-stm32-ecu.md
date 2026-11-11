# Pinout ECU → Black Board (STM32F4VE V33)

**Fonte:** `injet-racing-prodv6.kicad_pcb` · U1 @ **(60.46, 107.94)** · `jl32_pinout.py` · `pins.h`

Pad com trilha de bypass = furo **NC** no STM (net só na trilha).

---

## Alimentação

| Net | Pad U1 |
|-----|--------|
| +5V | R0/R1 O/I |
| +3V3 | L0/L1, R2/R3 O/I |
| GND | L3/L4, R4 O/I |
| VREF+ | R10 O/I |

---

## Sensores (MOD6)

| Net | Pad | MCU |
|-----|-----|-----|
| IAT | L12O | PD0 |
| CLT | L16O | PA9 |
| MAP | L17O | PC9 |
| TPS | L18I | PC8 |
| VBAT | L17I | PA8 |

Bypass trilha: **L18O** (PC7), **L20I/L20O** (PD14/PD13) — NC no header.

---

## Lambda / RPM / aquecedor

| Net | Pad | MCU |
|-----|-----|-----|
| VM | R13I | PA4 |
| IP | R13O | PA5 |
| UN | R14I | PA6 |
| RI_PULSE | R5I | PE2 |
| RPM_IN | R17O | PE8 |
| GHEAT | R16I | PB0 |

Bypass: **R12O** (IP trilha).

---

## Injetores / relés / CAN

| Net | Pad | MCU |
|-----|-----|-----|
| GINJ1–4 | R18I–R21I | PE9/11/13/15 |
| GRL1/2/3 | L22I/L23I/L22O | PD10/8/9 |
| CAN_TX/RX | L6I/L6O | PB9/PB8 |

---

## Fora do header

SWD na Black Board · INJ/RL/+12V via CN1/CN2/CN3
