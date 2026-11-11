# Lista de compra — PCB prodv7

> Extraído dos footprints de `kicad/prodv7/injet-racing-prodv7.kicad_pcb` (2026-08-17).
> Reauditado: **76 footprints** → **72 peças elétricas** + 4 furos M3.
> Só o que está na placa para soldar. Sem sensores de motor, bicos e sonda (chicote).

## Verificação (contagem PCB)

| Tipo | Qtd no PCB | Na lista |
|------|------------|----------|
| ICs / módulos | 8 (+ adaptador U5) | OK |
| MOSFET | 4 | OK |
| Diodos | 8 | OK |
| Resistores | 24 | OK |
| Capacitores | 19 | OK |
| Conectores | 3 (CN1, CN2, CN4) | OK |
| Fusível real | 1 (F1 entrada +12 V) | OK |
| Furos M3 | 4 | parafuso opcional |

## ICs e módulos

| Nome | O que é | Qtd |
|------|---------|-----|
| STM32F407VET6 Black Board | MCU (módulo pronto 3,3 V) | 1 |
| MP1584 | módulo buck +12 V → +5 V | 1 |
| MCP6002-I/P DIP-8 | op-amp dual RRIO (VM / Un) | 1 |

> **U4 no PCB prodv7 ainda é DIP-14.** A peça de compra é DIP-8 — trocar o footprint antes de soldar. Pinagem: 1–3 VM · 4 GND · 5–7 UN · 8 +5 V.
| OPA388IDR SOIC-8 | op-amp zero-drift (malha Ip) | 1 |
| Adaptador SOIC-8 → DIP-8 | soquete do U5 (OPA388) | 1 |
| REF3033 | referência 3,3 V (ADC) | 1 |
| PC817 DIP-4 | optoacoplador RPM (bobina) | 1 |
| LM393 DIP-8 | comparador pick-up VR | 1 |

## Semicondutores

| Nome | O que é | Qtd |
|------|---------|-----|
| IRF9540 TO-220 | P-MOSFET proteção reversa | 1 |
| IRLZ44N TO-220 | N-MOSFET low-side (INJ1, INJ2, aquecedor λ) | 3 |
| 1N4007 | diodo flyback (INJ1, INJ2, aquecedor) | 3 |
| 1N4148 | diodo (RPM + clamps VR) | 3 |
| Zener 15 V | clamp gate do IRF9540 | 1 |
| TVS 33 V (P6KE33A ou SMAJ33A) | surge +12 V | 1 |

## Resistores (THT, 1/4 W salvo nota)

| Nome | O que é | Qtd |
|------|---------|-----|
| 100 Ω | gate série INJ1/INJ2 + aquecedor | 3 |
| 1 kΩ | série MAP / TPS / Un (R78) | 3 |
| 4,7 kΩ | pull-up RPM + pull-up VR | 2 |
| 6,8 kΩ **1%** | R_ESR lambda (LSU 4.2) | 1 |
| 10 kΩ | PD gates, bias Vm, MAP, VBAT | 7 |
| 10 kΩ **2 W** | divisor RPM (bobina −) | 2 |
| 18 kΩ **1%** | divisor MAP | 1 |
| 47 kΩ | entrada VR | 1 |
| 61,9 Ω **1%** | shunt Ip | 1 |
| 100 kΩ | gate Q1, divisor VBAT, histerese VR | 3 |

## Capacitores

| Nome | O que é | Qtd |
|------|---------|-----|
| 220 µF 35–50 V radial | bulk +12 V e +5 V | 2 |
| 100 µF 35–50 V radial | entrada buck (+12 V_PROT) | 1 |
| 10 µF 16–25 V | +3V3, VREF+, +5 V lambda | 3 |
| 100 nF cerâmico | decouple / filtro ADC | 8 |
| 220 nF cerâmico | filtro Ip / Un | 2 |
| 10 nF cerâmico | filtro entrada VR | 1 |
| 1 nF cerâmico | filtro RPM / GPIO VR | 2 |

## Conectores e fusível

| Nome | O que é | Qtd |
|------|---------|-----|
| Header ATX 24 pinos | CN1 chicote principal | 1 |
| Header PCIe 6 pinos | CN2 lambda + CN4 pick-up VR | 2 |
| Fusível 5 A + suporte | F1 entrada +12 V (BAT → IN) | 1 |
| Headers 2,54 mm (2×24) | soquete Black Board (U1) | 2 fileiras |

## Não comprar (já no PCB como furo / silk)

- 4 furos M3 (só parafuso/espaçador se quiser prender a placa)
- Footprints extras de fusível F1/F2 com A=B na mesma net — **não** são 7 fusíveis; só **1× 5 A**

---

## Ainda sem peça no prodv7 (circuito previsto, footprint ausente)

| Falta soldar na placa | Para quê | Qtd |
|-----------------------|----------|-----|
| 2,26 kΩ **1%** | pull-up **IAT** e **CLT** | 2 |
| 100 nF | filtro ADC IAT / CLT | 2 |
| 1 kΩ (opc.) | série ADC IAT / CLT | 2 |
| IRLZ44N + 1N4007 + 100 Ω + 10 kΩ | canal **INJ3** | 1 de cada |
| IRLZ44N + 1N4007 + 100 Ω + 10 kΩ | canal **INJ4** | 1 de cada |
| 2N7000 + 1 kΩ + 10 kΩ + 1N4007 | driver **relé** (×3 canais) | 3 de cada |
| Header PCIe-6 | **CN3** relés | 1 |
| SN65HVD230 (+ adaptador SOIC se usar chip) | **CAN** | 1 |

Nets **IAT**, **CLT**, **GINJ3**, **GINJ4**, **GRL1–3**, **CAN_TX/RX** já saem do U1 — hoje só passam trilha até CN1/socket, **sem** condicionamento ou driver.

## Fora da placa (chicote / motor — não entram na lista PCB)

| Item | Nota |
|------|------|
| Sensores IAT, CLT, MAP, TPS | vão no CN1 |
| 4× bico Bosch 0280156086 + conector EV1 | só 2 canais INJ na placa hoje |
| 3× relé SRD + chicote | bobina externa |
| Sonda LSU 4.2 + bung M18 | CN2 |
| Fusível **3–5 A** aquecedor λ | no fio +12 V do chicote (CN2-1); **não** tem na placa |
| Fiação, terminal, conectores dos sensores | — |

Comprar isso só quando colocar os footprints faltantes ou montar o chicote.
