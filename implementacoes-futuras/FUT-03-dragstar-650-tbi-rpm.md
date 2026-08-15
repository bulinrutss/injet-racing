# FUT-03 — Drag Star 650 (XVS650) · TBI comum + RPM (bobina vs pick-up)

**Status:** ideia salva · **não** na prodv6 Fase 1  
**Contexto:** adaptar ECU INJET (speed-density / batch-fire / TBI única) à Yamaha **Drag Star / V-Star 650**.  
**ProdV6 hoje:** MOD7 = PC817 em **CN1-22** (negativo da bobina primária).

---

## Motor (manual / specs)

| Item | Valor |
|------|--------|
| Cilindros | V-twin **649 cm³**, 81×63 mm, **V 70°**, virabrequim **monopino** |
| Combustível OEM | **2×** Mikuni **BDS28** (28 mm CV) — admissão **separada** |
| Ignição | **TCI digital** Mitsubishi **J4T088** (ignitor) |
| Bobinas | **2×** F6T541 — primário **3,6–4,8 Ω** (2 fios: +12 V fixo · GND pulsado pelo TCI) |
| Potência | ~40 cv @ **6500 rpm** · torque ~51 N·m @ 3000 rpm |
| Corte | ~**7000 rpm** (limitador eletrônico) |
| TPS | **Sim** (no corpo do acelerador — reutilizável na ECU) |
| Bomba | **Elétrica** (já na moto) |

**Intervalo de faísca** (monopino + V 70° — [Starbike crank angle](https://www.starbikeforums.com/threads/crank-angle.90529/)):

- Traseiro dispara **290°** depois da frente  
- Frente dispara **430°** depois da traseira  
- **1 faísca / 360°** de virabrequim (espaçamento **irregular**)

---

## Pick-up, pulser, “sensor de pulso” — é a **mesma peça**

No manual Yamaha e em fóruns/oficina aparecem nomes diferentes para **um único componente**:

| Nome comum | O que é |
|------------|---------|
| **Pick-up coil** | Bobina indutiva (VR) presa ao estator |
| **Pulser coil / pulsar** | Mesmo sensor (ex.: RMStator: “Pick up pulsar coil included”) |
| **Sensor de pulso** | Tradução / linguagem de scanner — **não** é outro sensor à parte |
| **Pulse coil** | Mesmo (teste de 182–222 Ω no conector) |

**Não confundir com:**

| Sinal | Origem | Função |
|-------|--------|--------|
| **Pick-up (estator)** | Imã + enrolamento · dente/ferro no volante | **Posição + RPM** para o **ignitor** |
| **Negativo da bobina** | Saída do TCI já processada | **Evento de faísca** (quando o TCI puxa GND) |

São **dois pontos diferentes** na cadeia de ignição.

---

## Como funciona o pick-up do estator (XVS650)

```
Volante (flywheel)
    └── trecho ferroso / protuberância passa perto do pick-up
              │
              ▼
    Pick-up coil (VR) no estator — cinza + preto, ~200 Ω
              │  tensão AC alternada (senoide), típ. unidades mV–V AC
              ▼
    Ignitor / TCI (J4T088) — lê RPM + posição do virabrequim
              │  avanço/recuo por RPM + TPS (não ajustável no 650)
              ├──► bobina dianteira (GND pulsado)
              └──► bobina traseira (GND pulsado)
                        │
                        ▼
                   faísca nas velas (290° / 430°)
```

### Dados elétricos (manual 2007)

| Teste | Spec |
|-------|------|
| Resistência pick-up | **182–222 Ω** @ 20 °C |
| Cores típicas | **Gray + Black** (conector traseiro do chicote, perto do tanque) |
| Sinal vivo | **AC pulsante** ao girar motor (multímetro analógico ou osciloscópio) |
| Destino | Entrada do **ignitor** — **não** vai direto às bobinas de faísca |

### Estator completo (outra parte do mesmo conjunto)

O **magneto AC** (fios brancos / estator de carga) gera **alternador** para bateria — **independente** do pick-up.  
Pick-up = **1 par** de fios, função **sincronismo**; estator de potência = **carga elétrica**.

### Pulses por volta

Padrão TCI Yamaha desta classe: **1 impulso por volta** do virabrequim (1 reluctor no volante).  
O TCI usa esse pulso como referência de **ângulo fixo** (posição do pick-up ~ dezenas de graus antes do PMH — valor exato no manual de serviço / marca no volante).  
A partir daí calcula **quando** disparar cada bobina (290° / 430°) e o **avanço** por RPM.

---

## Negativo da bobina (MOD7 prodv6) — o que a ECU lê hoje

```
CN1-22 → R20/R21 (10k) → PC817 → PE8 (R17O)
```

| Aspecto | Pick-up → TCI | Bobina − → PC817 |
|---------|---------------|------------------|
| Tipo de sinal | **AC** (VR) | **DC** — TCI chaveia GND |
| Momento | Referência de **virabrequim** (antes do PMH) | **Faísca** (fim compressão + avanço) |
| Pulsos/volta | **1** (regular) | **1** (mas nos instantes 290° / 430°) |
| Avanço ignição | Não aparece no pick-up bruto; TCI aplica | Avanço **embutido** — pulso “anda” com RPM |
| Entrada prodv6 Fase 1 | **Não** (precisa conditioner VR) | **Sim** (MOD7) |

Para **contar RPM**, os dois servem (com condicionamento correto no pick-up).  
Para **fase de injeção TBI**, pick-up é **melhor** (ângulo de virabrequim estável); bobina − amarra na **faísca**.

---

## Adaptação TBI única + ECU INJET

### Mecânica

- OEM: **2 carburadores** → TBI exige **coletor-Y / plenum comum** (fabricação).
- **1 bico** → usar **1 canal INJ** (ex. INJ1); demais NC.

### RPM — opções

| Opção | Hardware | Firmware |
|-------|----------|----------|
| **A — OR 2 bobinas** (recomendado Fase 1) | Diodo 1N4148 em cada − → CN1-22 | `ENGINE_CYLINDERS = 2` |
| **B — 1 bobina só** | CN1-22 num − só | `pulsesPerRev = 0.5` (×2 RPM); pior gatilho de injeção |
| **C — Pick-up estator** (Fase 2) | Conditioner VR → GPIO/EXTI | 1 pulso/volta; offset ° pick-up no mapa |

### Injeção batch-fire + plenum comum

- Quantidade (MAP + RPM): **adequado** — recalibrar `DISPLACEMENT_CC` (**649**, não 4400).
- Timing: TBI no coletor **tolera** fase imperfecta; intervalo **290/430** na faísca é **assimétrico** (pior que V-twin 360° “limpa”).
- Scheduler de injeção: ainda **TODO** em `firmware/src/main.cpp`.

### Sensores reutilizáveis da moto

| Sensor | Uso ECU |
|--------|---------|
| TPS OEM | Entrada analógica (escala 3,3 V) |
| MAP (novo) | Vácuo no plenum comum |
| Pick-up | Só com placa/firmware VR (fora Fase 1) |

---

## Veredito piloto

| Item | Drag Star 650 |
|------|----------------|
| RPM via bobina (MOD7) | **OK** — preferir OR das 2 bobinas |
| RPM via pick-up | **Melhor fase** · exige **hardware novo** (não CN1-22 direto) |
| TBI + batch-fire | **Viável** cruiser 3k–5,5k rpm |
| Plug-and-play | **Não** — coletor, calibração, scheduler |

---

## Pick-up na ECU (trabalho futuro)

Circuito completo (BOM, netlist, regras de tap): **[FUT-05](./FUT-05-condicionador-vr-pickup.md)**.

Esboço mínimo (fora prodv6):

1. **Conditioner:** pick-up VR → limitador + shaper → pulso 0–3,3 V (LM393 ou LM1815) — ver FUT-05.
2. **1 pulso/volta** → RPM = `60e6 / period_us` (sem `/2` de cilindros).
3. **Injeção:** disparar em **offset fixo** após borda do pick-up (ex. +120° BTDC admissão — calibrar).
4. **Não cortar** o pick-up entre moto e ignitor OEM se ignição original permanecer — **derivação** ou relé; ou substituir ignitor por controle ECU (escopo maior).

---

## Duas entradas cabeadas — **não** usar as duas no firmware ao mesmo tempo

Placa **pode** ter MOD7 (bobina) **e** MOD7b (pick-up VR) ligados na Drag Star. Ignição OEM continua; ECU só escuta.

| Pergunta | Resposta |
|----------|----------|
| Cabear os dois? | **Sim** — circuitos independentes |
| Contar RPM com os dois juntos? | **Não** — pulsos em **instantes diferentes** (virabrequim vs faísca 290°/430° + avanço) |
| Firmware | `#define RPM_SOURCE COIL \| VR` — **uma** fonte ativa |
| Outra fonte | Debug/osciloscópio **ou** fallback se uma falhar |
| Drag Star só pick-up? | **Sim** — se MOD7b existir, CN1-22 pode ficar desligado |

**Pick-up Drag Star ≠ Hall ≠ roda fônica completa** — ver tabela em [FUT-04](./FUT-04-roda-fonica-rpm.md).

---

## Referências

- Manual serviço XVS650 (TCI, pick-up 182–222 Ω, bobinas F6T541)
- [Starbike — crank angle 290° / 430°](https://www.starbikeforums.com/threads/crank-angle.90529/)
- [FUT-04 — roda fônica, dentes, vs bobina](./FUT-04-roda-fonica-rpm.md)
- ProdV6 MOD7: `kicad/prodv6/CHECKLIST.md` · `firmware/src/rpm.cpp`
- ODG 3-step (OR bobinas Modo B): `projetos piloto/injet 3 step/01-projeto-detalhado.md`
