# INJET 3 Step — custos (referência Aug/2026)

Valores em **R$**, estimativa **1 unidade**. Câmbio Ali: **US$ 1 ≈ R$ 5,50**. Frete internacional **não** incluso.

Fontes consultadas: AliExpress (prioridade), Casa do Resistor, Fermarc, Autocore/AF Eletrônica, WJ Componentes, Mercado Livre / A2 Robotics (estanho).

---

## 1. Componentes eletrônicos (BOM)

### 1.1 AliExpress (prioridade — faixa por unidade)

| Item | Qtd | US$ ref. | R$ ref. |
|------|-----|----------|---------|
| STM32F103 Blue Pill | 1 | 2,0–3,5 | 11–19 |
| Display 0,56" 2 dígitos 7 seg. | 1 | ~0,2–0,5 (pack) | 1–3 |
| LED 5 mm | 6 | pack | ~0,6 |
| Botão tátil 8×8 | 3 | pack | ~0,5 |
| Relé SLA/SRD 12 V 30 A (potência) | 1 | 0,8–1,5 | 4–8 |
| Relé SRD-12V placa | 1 | 0,22–0,31 | 1–2 |
| PC817 + passivos RPM | 1 | pack | ~1 |
| 7805/AMS1117 + caps | 1 | pack | ~1 |
| ULN2003 / 2N7000 + R/C/D | lote | — | 3–8 |
| Passivos + conectores | — | — | 5–12 |
| **Subtotal eletrônica Ali** | | | **35–55** |

### 1.2 Nacional — referência anúncio atual

| Item | Loja | R$ |
|------|------|-----|
| STM32F103 Blue Pill | Fermarc | 41,55 |
| Display 7 seg. 1 dígito CC | Casa do Resistor | 3,20 (×2 ≈ 6,40) |
| LED 5 mm vermelho | Casa do Resistor | 0,19 |
| Botão tátil 8×8 | Casa do Resistor | 0,98 |
| Relé SRD-12V PCB | AF Eletrônica | 4,90 |
| Relé SLA 12 V 30 A | Autocore | 15,90 |
| Relé SLA 12 V 30 A | AF Eletrônica | 24,80 |
| PC817 | Casa do Resistor | 1,20 |
| 7805 / AMS1117-5V | Casa do Resistor | 1,60–1,90 |
| ULN2003 DIP | Casa do Resistor | 2,60 |
| **Subtotal eletrônica BR (sem MCU)** | | **~45–90** |
| **Subtotal eletrônica BR (com MCU Fermarc)** | | **~85–130** |

---

## 2. PCB CNC (cobreada virgem)

| Fonte | Produto | R$ | R$/placa útil |
|-------|---------|-----|---------------|
| AliExpress | FR4 DF 10×15 pack 5 | 7–50/pack | **3–12** |
| WJ Componentes | FR4 DF 10×15 1 un. | 30,99 (Pix 30,06) | **~31** |

Recomendação piloto: **pack Ali**; 1 placa 10×15 rende ~1 layout 7×10 cm.

---

## 3. Solda (estanho)

| Fonte | Produto | R$ | R$/g |
|-------|---------|-----|------|
| Casa do Resistor | Cobix 500 g 1 mm | 155 (sem estoque) | 0,31 |
| A2 Robotics | Soft 500 g 1 mm | 165 / Pix 156,75 | 0,31–0,33 |
| Mercado Livre | Soft 500 g 1,5 mm | 183,56 | 0,37 |
| Saravati | Best 100 g 1 mm | 65,90 | 0,66 |

**Consumo estimado por placa 3-step:** 80–120 juntas → **8–12 g** fio.  
**Custo solda / unidade:** **R$ 2,50–4,50** (usar **R$ 3,50** no total).

---

## 4. Fabricação (separado da BOM)

| Etapa | DIY | Terceirizado |
|-------|-----|--------------|
| PCB CNC (isolamento FR4) | 3–12 (chapa Ali) + broca ~2–8 | 60–150 |
| Montagem / solda (mão) | 0 | 80–150 |
| Case 3D PLA (~40–80 g) | 8–20 filamento | 35–80 |
| Chicote completo (10+2 vias) | 50–90 | 110–130 |
| Broca/fresa CNC (amortizado) | 2–8 | — |

**Chicote referência ODG avulso GIII:** ~R$ 109–116 (BlackLine / ODG loja).

---

## 5. Totais por unidade

### 5.1 Só peças + solda (sem case/chicote/frete)

| Cenário | R$ |
|---------|-----|
| Ali prioritário | **45–75** |
| Misto (MCU/relé BR + resto Ali) | **80–120** |
| Só BR | **120–165** |

### 5.2 Produto completo DIY (Ali + case + chicote próprio)

| Item | R$ |
|------|-----|
| Eletrônica + PCB + solda | 50–80 |
| Case 3D | 8–20 |
| Chicote DIY | 50–90 |
| **Total** | **~110–190** |

### 5.3 Produto completo (misto / terceirizado)

| Cenário | R$ |
|---------|-----|
| Misto | **250–450** |
| Tudo pago (PCB+case+chicote+montagem) | **500–800** |

### 5.4 Comparativo mercado

| Produto | R$ |
|---------|-----|
| ODG 3 Step G3 Rev8 | ~595–613 |
| ODG chicote avulso GIII | ~109–116 |
| ODG condensador DI/TR 6ch | ~105 |
| **Piloto INJET DIY completo** | **~110–200** |
| **Piloto + condensador ODG (COP)** | **+105** |

---

## 6. O que não entra no orçamento

- Frete (Ali / lojas)  
- Ferramentas: ferro, CNC, impressora 3D, multímetro  
- Estanho: carretel 500 g ~R$ 155–185 (rende dezenas de placas)  
- Desenvolvimento firmware (tempo — ver `03-tempo-fabricacao.md`)  
- Condensador DI/TR próprio (Fase 2; hoje comprar ODG)  
- Homologação / certificação  

---

## 7. Atualização de preços

Revisar antes de comprar:

- Ali: STM32, display, relé, FR4 — vendedor ≥95% + frete  
- Casa do Resistor: `casadoresistor.com.br`  
- Fermarc: Blue Pill  
- WJ Componentes: FR4 10×15  
- ML: `estanho solda 60x40 500g`
