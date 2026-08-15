# FUT-05 — Condicionador VR (pick-up moto / distribuidor eletrônico 2 fios)

**Status:** ideia salva · **não** na prodv6 Fase 1  
**Contexto:** MOD7 atual = negativo da bobina (PC817, CN1-22). Este item = entrada **paralela** para sensor **indutivo (VR)** — mesmo tipo elétrico do pick-up da moto e dos 2 fios do distribuidor eletrônico (antes da caixinha).  
**Relacionado:** [FUT-03](./FUT-03-dragstar-650-tbi-rpm.md) · [FUT-04](./FUT-04-roda-fonica-rpm.md)

> **Não implementar na PCB atual** até puxar este FUT. Continua válido: RPM Fase 1 = bobina −.

---

## 1. O que este circuito lê

| Fonte | Fios | Sinal | Onde |
|-------|------|-------|------|
| Pick-up / sensor de pulso (moto) | 2 | AC, mV–V | estator |
| Distribuidor eletrônico (Opala etc.) | 2 | AC, mV–V | antes da caixinha |
| Hall 3 fios | 3 | digital 0/5 V | **outro** circuito (não este) |
| Negativo da bobina | 1 (+GND) | DC + pico | **MOD7** (já existe) |

Pick-up moto e 2 fios do distribuidor = **mesma família**. Um condicionador serve os dois.

---

## 2. Regras de ligação (obrigatório)

1. **Não cortar** o fio entre sensor e caixinha/TCI — só **derivação** (solda no condutor + termorretrátil).
2. **Não** ligar no CN1-22 / PC817 — carga errada → caixinha falha a centelha.
3. Entrada nova na ECU (ex. `RPM_VR` / pino GPIO dedicado).
4. Firmware: **uma** fonte ativa (`RPM_SOURCE = COIL | VR`). Cabear os dois ok; contar os dois juntos **não**.
5. Chicote: par **trançado**, ≤ ~1 m, longe de cabo de vela; se blindado, malha só no GND da ECU.

```
pick-up / distr. ═══ (continua) ═══► caixinha ──► bobina ──► faísca
         │
         └── derivação ──► [FUT-05] ──► GPIO 3,3 V (EXTI)
```

---

## 3. Função do circuito

```
AC (mV na lenta → vários V no corte)
        │
        ▼
  limitador (diodos)     ← não estoura o comparador
        │
        ▼
  comparador / LM1815    ← “acha” a passagem por zero / borda
        │
        ▼
  pulso 0 … 3,3 V        ← MCU (borda de descida ou subida)
```

Sem isso: MCU não lê AC direito e/ou a caixinha perde o sensor.

---

## 4. Opção A — Comparador discreto (recomendado p/ protótipo)

Alta impedância na entrada → pouco carga no pick-up → caixinha OEM continua ok.

### 4.1 Esquema

```
 VR+ (derivação) ──[R1 47k]──┬──[D1 BAT54S A→nó · K→+3V3]── +3V3
                             │
                             ├──[D2 BAT54S K→nó · A→GND]── GND
                             │
                             └──[C1 10nF]── GND          (filtro RF; opcional 4n7–22nF)
                             │
                             └──► (−) LM393 pin2

 VR− (ou GND sensor) ──────────► (+) LM393 pin3
                                  │
                             [R2 100k] entre pin2↔pin1 (histerese; ajustar 47k–220k)
                                  │
 +3V3 ──[R3 4k7]──┬── LM393 pin1 (open collector out)
                  │
                  └──► GPIO RPM_VR  (+ [C2 1nF] p/ GND)
 LM393 pin4 = GND · pin8 = +3V3 · pin5/6/7 NC ou 2º canal
```

Se o sensor for flutuante (2 fios sem terra comum): ligar **VR−** no pin3 e **não** amarrar VR− no chassi sem testar polaridade. Em muitos carros um lado do pick-up já é referenciado à caixinha — medir com osciloscópio antes.

### 4.2 Tabela Net | De | Para

| Net | De (comp.polo) | Para (comp.polo) |
|-----|----------------|------------------|
| VR_RAW+ | derivação fio sensor | R1.A |
| VR_LIM | R1.B | D1.A · D2.K · C1.A · U_cmp.in− |
| +3V3 | barra ECU | D1.K · U_cmp.VCC · R3.A |
| GND | barra ECU | D2.A · C1.B · U_cmp.GND · C2.B |
| VR_REF | VR− / retorno sensor | U_cmp.in+ |
| HYST | U_cmp.out | R2 → U_cmp.in− |
| RPM_VR | U_cmp.out · R3.B · C2.A | GPIO (EXTI) |

### 4.3 BOM (Opção A)

| Ref | Peça | Qtd | Notas |
|-----|------|-----|-------|
| U_cmp | **LM393** (ou LM2903) | 1 | 1 canal usado |
| R1 | **47 kΩ** | 1 | série — alta Z; ↑ se ainda carregar a caixinha |
| R2 | **100 kΩ** | 1 | histerese |
| R3 | **4k7** | 1 | pull-up 3,3 V |
| D1/D2 | **BAT54S** (ou 2× 1N4148) | 1/2 | clamp a +3V3 e GND |
| C1 | **10 nF** | 1 | filtro entrada |
| C2 | **1 nF** | 1 | filtro GPIO |

**Alimentação do comparador: +3V3** (mesma lógica do STM32). Não alimentar com 12 V se a saída for direto no GPIO.

### 4.4 Polaridade

Se RPM não contar ou contar no “lugar errado”: **inverter** VR+ / VR− na entrada. Na moto/distribuidor a caixinha OEM já está certa — só a ECU inverte a borda.

---

## 5. Opção B — LM1815 (CI dedicado VR)

Usado em ECUs aftermarket clássicas. Limiar adaptativo (melhor na lenta fraca + corte alto).

```
 VR+ ──[R 1k–10k]──► LM1815 pin3 (IN)
 VR− / GND ──────────► pin2 (GND CI) + GND ECU
 +5 V ou +3V3* ──────► pin8 (VCC)   *verificar datasheet / nível OUT
 OUT (pin1) ──[nível]──► GPIO 3,3 V
```

| Prós | Contras |
|------|---------|
| Menos ajuste, limiar adaptativo | Peça menos comum no varejo BR |
| Bom em amplitude variável | Pode precisar nível OUT → 3,3 V |

BOM mínimo: LM1815 + R série + caps datasheet + clamp se VCC=5 V e MCU=3,3 V (divisor ou buffer).

---

## 6. Onde entra na ECU (quando implementar)

| Item | Fase 1 (hoje) | Com FUT-05 |
|------|---------------|------------|
| Bobina − | CN1-22 → PC817 → PE8 | **mantém** |
| VR | — | conector novo ou pino livre CN1 → condicionador → **outro GPIO** |
| Firmware | só bobina | `#define RPM_SOURCE VR` **ou** `COIL` |

Sugestão de GPIO: pino EXTI livre (não reutilizar PE8 se bobina e VR forem coexistir no hardware).

Não colocar o condicionador VR **em série** no caminho sensor→caixinha.

---

## 7. Firmware (quando existir)

| Fonte | Pulsos / volta virabrequim (típico) | Conta RPM |
|-------|-------------------------------------|-----------|
| Pick-up moto 1 dente | **1** | `rpm = 60e6 / period_us` |
| Distribuidor 6 cil. (6 janelas) | **3** (= cilindros/2) | igual bobina 6 cil. |
| Distribuidor 4 cil. | **2** | igual bobina 4 cil. |
| Bobina − 6 cil. | **3** | já em `rpm.cpp` |

Mesa **móvel** no distribuidor: o VR **também avança** com RPM — ganho de fase limitado (ver conversa / FUT-04). Mesa **fixa** ou pick-up no virabrequim: melhor.

---

## 8. Teste bancada (antes do motor)

1. Gerador de função: seno ~0,2–5 Vpp, 50–500 Hz, no VR+/VR−.  
2. Osciloscópio: saída GPIO = onda quadrada 0/3,3 V.  
3. Com caixinha OEM ligada: motor de partida / marcha — faísca **normal**; se falhar, ↑ R1 (mais Z) ou revisar clamp.  
4. Serial: RPM bate com tacômetro (±5 %).

---

## 9. Veredito

| Pergunta | Resposta |
|----------|----------|
| Dá para ler pick-up e distr. eletrônico 2 fios? | **Sim** — este circuito |
| Substitui MOD7 bobina? | **Não** — opção paralela |
| Risco de matar faísca? | Sim se cortar fio ou usar PC817; **baixo** com R1≥47k + derivação |
| Na prodv6 agora? | **Não** — só documentação |

**Caminho prático:** protótipo Opção A (LM393) fora da placa → validar na moto/Opala → depois footprint MOD7b na próxima revisão de PCB.

---

## Referências

- FUT-03 § pick-up na ECU  
- FUT-04 — VR vs Hall vs bobina  
- Datasheet LM393 / LM1815  
- `firmware/src/rpm.cpp` · `modulo/esquema-eletrico.md` §4 (só bobina)
