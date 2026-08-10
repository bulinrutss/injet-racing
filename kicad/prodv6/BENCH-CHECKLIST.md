# ProdV6 — Checklist de bancada (sem motor)

> **Objetivo:** validar alimentação, nets críticas e saídas GPIO **antes** de chicote no carro.  
> **Tempo:** ~30–45 min (primeira vez) · ~15 min (repetição).  
> **Ref:** `modulo/esquema-eletrico.md` §9 · `firmware/include/pins.h`

---

## USB Black Board — regra do projeto

| Ação | 12 V ECU (CN1) | Cabo USB |
|------|----------------|----------|
| **Gravar firmware** (upload IDE) | **OFF** | Normal (com +5 V do PC) |
| **Monitor serial** (115200) | **ON** | **Power blocker** (só dados + GND) |
| **Tunar mapa** (futuro `SET`/`SAVE`) | **ON** | **Power blocker** |
| **No carro** | ON | **Desconectado** |

- Placa com **12 V ON** alimenta pelo **buck → pin 5V** da Black Board; USB **não** leva +5 V (blocker).
- Conferir **~5 V** em CN1-6 ou pin 5V antes de tune/monitor com ECU ligada.
- Serial: **115200 baud** (igual `Serial.begin(115200)` no firmware).

---

## 0. Ferramentas e segurança

| Item | Uso |
|------|-----|
| Fonte 12 V CC | limite **2 A** · fusível **5 A** em série (bancada) |
| Multímetro | tensão · continuidade · isolamento |
| USB (Black Board) | firmware / serial — ver regra abaixo |
| Carga simulada | lâmpada 12 V 5 W ou resistor **47 Ω 5 W** (inj/relé) |
| Osciloscópio (opc.) | RPM, INJ, CAN |
| **USB power blocker** | tune + monitor com **12 V ON** (corta VBUS, mantém dados) |

**Antes de energizar**

- [ ] Placa sobre superfície isolante (nada metálico embaixo)
- [ ] **Black Board encaixada** (J2/J3) — sem ela não há +3V3 lógico
- [ ] Nenhum chicote no motor; simular cargas nos conectores
- [ ] Polaridade 12 V: CN1 **1/2 = +12V_BAT** · **3/4/5 = GND**
- [ ] Primeira energização: **sem** bicos/relés reais conectados (usar lâmpada/resistor)

**Parar imediatamente se:** cheiro, aquecimento em Q1/U2/Q10+, tensão fora da tabela abaixo, fusível abrir.

---

## 1. Pré-voo — multímetro **desligado** (Ω)

Medir entre nets (referência GND = CN1 **3** ou **4**):

| Teste | Pontos | Esperado |
|-------|--------|----------|
| Bat ↔ GND | CN1-1 ou 2 → CN1-3 | **∞** (sem 12 V aplicado) |
| +5V ↔ GND | CN1-6 → GND | **∞** |
| +3V3 ↔ GND | CN1-7 → GND | **∞** |
| +12V_PROT ↔ GND | dreno flyback D10 **K** → GND | **∞** |
| INJ ↔ +12V | CN1-13 → CN1-1 | **∞** (MOSFET off) |

- [ ] Nenhum curto óbvio nas rails

---

## 2. Alimentação — só 12 V (MCU pode ficar off ou on)

Aplicar **12,0 V** em CN1 **2 (+12V_BAT)** · GND em CN1 **3**.

| Ponto | Net | Esperado | ✓ |
|-------|-----|----------|---|
| Após F1 / Q1 | +12V_PROT | 11,5–12,0 V | [ ] |
| CN1-6 | +5V | **4,9–5,2 V** | [ ] |
| CN1-7 | +3V3 | **3,25–3,40 V** | [ ] |
| J2 pin 3V3 (Black Board) | +3V3 | ≈ CN1-7 | [ ] |
| J2 pin 5V | +5V | ≈ CN1-6 | [ ] |
| U2 IN+ (pad 1 MP1584) | +12V_PROT | ≈ entrada | [ ] |
| Corrente total (vazio) | — | **< 150 mA** | [ ] |

**Se +5V ou +3V3 ausente:** highlight net no KiCad · conferir MOD4 / barra J2.

---

## 3. Sensores simulados (CN1, sem motor)

Simular entradas com trimpot ou resistores:

| Pino | Net | Simulação | MCU (`pins.h`) | Esperado ADC |
|------|-----|-----------|----------------|--------------|
| 8 | IAT | NTC 2,2 kΩ → GND | PC11 | valor estável |
| 9 | CLT | idem | PC9 | idem |
| 10 | MAP | 0–5 V (pot 10 k) | PC7 | segue pot |
| 11 | TPS | 0–3,3 V (pot 10 k) | PC6 | segue pot |

- [ ] Pull-ups: CN1-8/9 sobem com NTC aberto (~3,3 V no nó)
- [ ] MAP: CN1-6 = **+5 V** presente enquanto mede CN1-10

**Firmware (serial):** gravar `firmware/` · ler valores IAT/CLT/MAP/TPS no `main.cpp`.

- [ ] Valores mudam ao girar pot · sem travamento em 0 ou 4095 fixo

---

## 4. RPM (MOD7) — pulso simulado

| Item | Detalhe |
|------|---------|
| Entrada | CN1-12 **RPM_IN** |
| Circuito | opto U7 · pull-up R22 **+3V3** |
| MCU | **PE8** · EXTI falling |

**Teste sem bobina:** gerador ~50 Hz em CN1-12 (via **1 kΩ** em série) ou toque curto GND↔sinal.

- [ ] Firmware reporta RPM > 0 com pulso
- [ ] Sem pulso → RPM ≈ 0

---

## 5. Injetores (MOD8) — uma saída por vez

| Canal | CN1 | GPIO | Q | Flyback |
|-------|-----|------|---|---------|
| INJ1 | 13 | PE9 | Q10 | D10 K→+12V_PROT |
| INJ2 | 14 | PE11 | Q11 | D11 |
| INJ3 | 15 | PE13 | Q12 | D12 |
| INJ4 | 16 | PE15 | Q13 | D13 |

**Carga:** lâmpada 12 V ou 47 Ω entre **CN1-13** e **+12V** (CN1-1/2).

Por canal:

- [ ] Repouso: dreno ≈ **+12 V** (MOSFET off)
- [ ] GPIO HIGH 10 ms: dreno → **≈ 0 V** · corrente limitada
- [ ] Flyback: sem pico > 20 V no dreno (osciloscópio, se tiver)

Teste rápido firmware: toggle PE9–PE15.

---

## 6. Relés (MOD9 + CN3)

| CN3 | Net | GPIO | RL |
|-----|-----|------|-----|
| 1 | RL_IAC | PD9 | RL3 |
| 2 | RL_PUMP | PD8 | RL2 |
| 3 | RL_MAIN | PD10 | RL1 |
| 4 | GND | — | — |

- [ ] Repouso: NO aberto (∞ Ω para COM)
- [ ] GPIO HIGH: relé **clica** · NO fecha (~0 Ω)
- [ ] Bobina: flyback D20–D22 **K → +12V_PROT**

CN1 **17–19 = NC** (relés só por CN3).

---

## 7. CAN (MOD10)

| Ponto | Net |
|-------|-----|
| CN1-20 | CANH |
| CN1-21 | CANL |
| U6 | SN65HVD230 · VCC = +3V3 |

- [ ] CANH/CANL: **2,5 V** típico em repouso (terminação off-board)
- [ ] USB-CAN ou segundo nó: frames com firmware CAN ativo

---

## 8. Lambda + aquecedor (CN2) — opcional na 1ª bancada

| CN2 | Função |
|-----|--------|
| 1 | +12V_PROT (aquecedor) |
| 2 | H− (dreno Q30) |
| 3–5 | IP / VM / UN |
| 6 | NC |

- [ ] CN2-1 = +12V_PROT
- [ ] PWM PD12: CN2-2 alterna 0 ↔ 12 V (aquecedor simulado)
- [ ] VM (PA4 DAC) ≈ **2,5 V** · UN/IP dentro de faixa com sonda ou simulador

---

## 9. Registro rápido

| Data | Operador | FW commit | Resultado |
|------|----------|-----------|-----------|
| | | | |

**Falhas anotadas:**

```
(mod / net / medido / esperado / ação)
```

---

## 10. Ordem mínima (15 min)

1. [ ] §1 curto-circuitos  
2. [ ] §2 rails  
3. [ ] §5 um injetor  
4. [ ] §6 um relé  
5. [ ] §3 um sensor (MAP ou TPS)  

Motor, chicote e CAN no carro = **depois** desta lista.

---

## Scripts PCB (opcional, sem energia)

```powershell
cd "e:\injet racing\kicad\prodv6"
python _check_mod6_now.py
python _check_mod8_now.py
python _check_mod9_routes.py
python _review_routes.py
```

DRC salvo: `DRC.rpt` (unconnected PTH = aceitável se highlight net OK).
