# Tópico 0 — Hardware (placa/MCU por fase e adaptação 5 V ↔ 3,3 V)

> Projeto INJET RACING — Fase 1 (TBI / monoponto / batch-fire / speed-density)
> Escolha do "cérebro" (microcontrolador) e como migrar o circuito dos sensores
> entre placas de 5 V (Arduino) e 3,3 V (STM32).
> Ver sensores no `05-sensores.md`.

---

## 0. DECISÃO CONFIRMADA (caminho de hardware por fase)

| Fase | Placa / MCU | Lógica | ADC | Para quê |
|---|---|---|---|---|
| **Aprender / testar sensores** | **Arduino Uno R3** (ATmega328) | **5 V** | 10 bits (0–1023) | montar divisores, rodar código da seção 7, levantar curvas R×T, calibrar MAP/TPS |
| **Protótipo da ECU** | **Arduino Mega 2560** (ATmega2560) | **5 V** | 10 bits (0–1023) | injeção batch-fire, RPM, mais pinos/memória (o código já é escrito pra ele) |
| **Produto final** ✅ | **STM32F407VET6** (Cortex-M4 168 MHz + FPU) | **3,3 V** | 12 bits (0–4095) | ECU completa: bicos, ignição, CAN, mapas, logging |

> **Atenção:** Arduino = **5 V**, STM32 = **3,3 V**. O circuito de entrada dos sensores
> **muda** na migração (ver seção 3). Não ligar sinal de 0–5 V direto no STM32 → **queima o pino**.

---

## 1. Por que cada placa

### 1.1 Arduino Uno (fase de aprendizado)
- Tem **6 entradas analógicas (A0–A5)** → suficiente pros 4 sensores (IAT, CLT, MAP, TPS).
- ADC 10 bits (0–1023) — exatamente o que o código da seção 7 do `05-sensores.md` assume.
- Junto com protoboard/resistores do kit, é **perfeito pra montar e testar** os divisores dos NTC.
- **Limite:** só 2 KB RAM / 32 KB flash e poucos pinos → **não serve** pra ECU completa.

### 1.2 Arduino Mega 2560 (protótipo da ECU)
- **16 entradas analógicas, 54 I/O, mais timers, 8 KB RAM.**
- O firmware da seção 7 já cita **"Arduino/ATmega2560"** → migração quase sem mudança.
- Folga pra saídas de bicos, relés, bomba, leitura de RPM por interrupção.

### 1.3 STM32F407VET6 (produto final)
- **Cortex-M4 168 MHz com FPU + DSP** → contas de `float` (equação Beta dos NTC) nativas e rápidas.
- **512 KB flash / 192+4 KB RAM** → sobra pra tabela VE, mapas de ignição, logging.
- **3x ADC de 12 bits, até 24 canais, 2,4 MSPS** → lê os 4 sensores com folga enorme.
- **2x CAN** → painel digital / telemetria (o STM32F401 NÃO tinha CAN).
- **Até 17 timers** → controle preciso de bicos (batch-fire), ignição e leitura de RPM.
- **86 GPIO** → pinos de sobra.
- É a mesma classe de chip usada por ECUs open-source sérias (rusEFI).

### 1.4 Placas descartadas / por que
| Placa | Flash / RAM | CAN | Veredito |
|---|---|---|---|
| STM32F103C6T6 | 32 KB / 10 KB | 1x | **fraca demais** ❌ (memória some com a tabela VE) |
| STM32F103C8T6 ("Blue Pill") | 64 KB / 20 KB | 1x | ok só p/ brincar |
| STM32F401RE (Nucleo) | 512 KB / 96 KB | **não tem** ❌ | boa, mas sem CAN → limita automotivo |
| **STM32F407VET6** | **512 KB / 192 KB** | **2x** ✅ | **escolhida** ✅ |

---

## 2. Diferença elétrica: 5 V (Arduino) × 3,3 V (STM32)

- **Arduino:** alimenta sensores em **+5 V**, referência do ADC = **5 V**, lê **0–5 V → 0–1023**.
- **STM32:** lógica **3,3 V**, referência do ADC = **3,3 V**, lê **0–3,3 V → 0–4095**.
- **Regra de ouro:** **nunca** colocar mais que ~3,3 V num pino do STM32.
  Sinal de 0–5 V ligado direto **danifica a entrada**.

Por isso, ao migrar do Arduino pro STM32, todo **sinal que pode passar de 3,3 V**
precisa ser **reduzido** antes do pino ADC.

---

## 3. Como reduzir a tensão do sinal (divisor de tensão)

> O ajuste é **no fio de SINAL** de cada sensor, **não** na alimentação.

### 3.1 Princípio
Mesmo conceito dos NTC (seção 2 do `05-sensores.md`): dois resistores em série,
lê-se no ponto do meio.

```
Sinal do sensor (0–5V) ---[ R1 ]---+--- pino ADC do STM32 (0–3,3V)
                                   |
                                 [ R2 ]
                                   |
                                  GND
+ capacitor 100 nF do pino ADC p/ GND (mantém o filtro)
```

**Fórmula:**
```
V_saida = V_entrada × R2 / (R1 + R2)
```

Para **5 V → ~3,3 V**, quer-se `R2 / (R1 + R2) ≈ 0,66`:

| R1 (cima) | R2 (baixo) | Razão | 5 V vira | Observação |
|---|---|---|---|---|
| 10 kΩ | 20 kΩ | 0,667 | 3,33 V | no limite (arriscado) |
| **10 kΩ** | **18 kΩ** | **0,643** | **~3,21 V** | **recomendado (com margem)** ✅ |
| 10 kΩ | 15 kΩ | 0,600 | 3,00 V | mais margem, perde um pouco de escala |

> Manter os resistores na casa de **kΩ** (ex.: 10 k / 18 k): baixo o bastante pra não
> sofrer com a impedância do ADC, alto o bastante pra não sobrecarregar o sensor.

### 3.2 Onde precisa de divisor — e onde NÃO precisa
| Sensor | Alimentação | Precisa divisor no sinal? | Como fazer no STM32 |
|---|---|---|---|
| **MAP** (Bosch, ratiométrico) | **+5 V** (precisa de 5 V p/ funcionar certo) | **SIM** ⚠️ | divisor 10 k / 18 k na saída |
| **TPS** (potenciômetro) | **+3,3 V** | **NÃO** ✅ | alimentar o pote com 3,3 V → cursor já sai 0–3,3 V |
| **IAT** (NTC) | pull-up p/ **+3,3 V** | **NÃO** ✅ | pull-up no +3,3 V (não +5 V) e recalcular curva |
| **CLT** (NTC) | pull-up p/ **+3,3 V** | **NÃO** ✅ | pull-up no +3,3 V (não +5 V) e recalcular curva |

**Resumo:** só o **MAP** obriga divisor (porque ele precisa de 5 V de alimentação).
TPS e NTC dá pra resolver **alimentando com 3,3 V** e recalibrando.

### 3.3 Proteção extra (recomendado no produto final)
- **Diodo de clamp** em cada entrada ADC (ex.: **BAT54S** p/ +3,3 V e GND) → segura picos.
- Manter os **100 nF** de filtro em cada pino ADC.
- Resistor série pequeno (100 Ω–1 k) ajuda a limitar corrente em transientes.

---

## 4. O que muda no firmware (seção 7 do `05-sensores.md`)

Ao migrar Arduino → STM32, ajustar as constantes de hardware:

```cpp
const float VREF    = 3.3f;      // era 5.0  (referencia do ADC no STM32)
const float ADC_MAX = 4095.0f;   // era 1023 (ADC de 12 bits)
```

E:
- **NTC (IAT/CLT):** `R_PULLUP` agora referenciado a **3,3 V**. A curva R×T em si não muda
  (é resistência), mas os valores de ADC/tensão da tabela mudam → **recalcular** a tabela
  ou confiar no cálculo por `R_ntc` (a fórmula `R_ntc = R_pullup × ADC / (ADC_MAX − ADC)` continua válida).
- **MAP:** recalibrar `MAP_A` e `MAP_B` considerando o **divisor** (o ADC vê a tensão dividida).
- **TPS:** recalibrar `TPS_ADC_FECHADO` / `TPS_ADC_ABERTO` (novos valores em 12 bits).

> A leitura por **resistência** dos NTC é imune à tensão de referência; o que muda é a
> escala de ADC. Já MAP e TPS são lidos por **tensão**, então **precisam recalibrar** ao mudar
> de 5 V p/ 3,3 V (e o MAP ainda por causa do divisor).

---

## 5. Checklist de migração p/ STM32
- [ ] Definir MCU final → **STM32F407VET6** ✅
- [ ] Alimentar **TPS** com **3,3 V** (dispensa divisor) e recalibrar
- [ ] Pull-up dos **NTC** (IAT/CLT) no **+3,3 V** e recalcular tabela/ADC
- [ ] **MAP** em **+5 V** + **divisor 10 k / 18 k** no sinal → recalibrar `a`, `b`
- [ ] Trocar no firmware: `VREF = 3.3`, `ADC_MAX = 4095`
- [ ] (Recomendado) diodo de clamp (BAT54S) + 100 nF em cada entrada ADC
- [ ] Conferir que **nenhum** sinal chega acima de ~3,3 V no pino (medir com multímetro)
- [ ] Planejar uso de **CAN** (2x disponíveis) p/ painel/telemetria
