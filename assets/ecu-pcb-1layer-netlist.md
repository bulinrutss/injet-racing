# Netlist PCB 1-layer — INJET RACING ECU

> Gerado com o layout `ecu-pcb-1layer-*`. Placa **200×100 mm**, cobre 1 face.

## Conectores

### CN1 — ATX 24 pinos (igual placa-mãe ↔ fonte)

| Pino ATX | Sinal ECU |
|---:|---|
| 1 | `+12V_IGN` |
| 2 | `+12V_BAT` |
| 3 | `GND_P` |
| 4 | `GND_P` |
| 5 | `GND_S` |
| 6 | `+5V` |
| 7 | `+3V3` |
| 8 | `IAT` |
| 9 | `CLT` |
| 10 | `MAP` |
| 11 | `TPS` |
| 12 | `RPM` |
| 13 | `INJ1` |
| 14 | `INJ2` |
| 15 | `INJ3` |
| 16 | `INJ4` |
| 17 | `RL2` |
| 18 | `RL1` |
| 19 | `RL3` |
| 20 | `CANH` |
| 21 | `CANL` |
| 22 | `TACHO` |
| 23 | `START` |
| 24 | `SHIELD` |

### CN2 — PCIe 6 pinos (igual placa de vídeo)

| Pino | Sinal LSU 4.2 |
|---:|---|
| 1 | **H+** aquecedor (+12V_PROT) |
| 2 | **H−** aquecedor (dreno QHEAT) |
| 3 | **IP** pump current |
| 4 | **VM** terra virtual |
| 5 | **UN** Nernst |
| 6 | NC (não usado — Rcal fica no chicote da sonda) |

## Módulos na placa

1. POWER — IRF9540, TVS, bulk, buck 5V, LDO 3V3
2. INJ — 4× IRLZ44N + flyback + gate
3. HEAT — IRLZ44N aquecedor λ
4. RELAY DRV — 3× 2N7000 + flyback
5. STM32F407 Black Board
6. SENSORS — pull-ups / divisores IAT CLT MAP TPS
7. RPM — PC817 + 2×10k 2W
8. CAN — módulo SN65HVD230
9. LAMBDA — MCP6004 (topo) + **AD8628 SMD embaixo** + shunt 61R9 + R_ESR 6k8
10. CN1 ATX-24 + CN2 PCIe-6

## Contagem

- Pads: **250**
- Segmentos de trilha: **173**
- Nets distintos: **45**
