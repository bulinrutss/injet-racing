# Tópico 3B — Flange ALTERNATIVA (Torno + Furadeira, a partir de um cubo)

> Projeto INJET RACING — Fase 1 (TBI / monoponto)
> Alternativa de fabricação SIMPLES ao `03-flange.md`. Objetivo: fazer **sem CNC**, só com
> **TORNO + FURADEIRA DE BANCADA**.
> 🖼️ Imagens:
> - **Passos de usinagem:** `../assets/flange-torno-passos-v4.png`
> - **Projeto realista (bicos verticais):** `../assets/flange-torno-3d-v4.png`

---

## 1. Ideia geral

Partir de um **cubo/bloco quadrado de alumínio** e:
1. **Tornear o centro** para criar o furo Ø60 e o **assento da TBI**.
2. Manter o corpo **quadrado** (ocupa mais espaço, mas simplifica) e **furar os 4 parafusos** que
   fixam no coletor (padrão **retangular** do 3E/DFV).
3. **Cortar as sobras** de dois lados (depois dos furos de fixação) → vira um retângulo.
4. **Furar os bicos** na **furadeira de bancada**.

Material: **alumínio 6061-T6**. Sem dutos internos de combustível → **flautas externas**.

---

## 2. Bicos: VERTICAL (recomendado) — confirmação de espaço

**Decisão: bicos na VERTICAL.** É a opção **preferida** e a **mais fácil na furadeira de bancada**
(furo vertical é a posição natural: prende o bloco e fura para baixo).

**Confirmação de espaço (cálculo):**
- Bico Bosch 0280156086 ≈ **16 mm** de corpo (região dos o-rings).
- Furo central Ø60 → raio **30 mm**.
- Centro de cada bico fica a ~**42 mm** do centro (30 + 8 + parede ~4).
- Logo o **cubo precisa de ~110 mm de lado** para caber **2 bicos por lado** colados na TBI.
  → é o "ocupar mais espaço" esperado. **Cabe.**

**Como o bico trabalha na vertical:**
- O furo do bico desce ao lado do furo central e **encontra a garganta/parte baixa do Ø60**,
  borrifando **para baixo, junto com o ar**, para dentro do coletor.
- Fica parecido com **TBI de fábrica** (bico apontando para baixo no fluxo) → **boa atomização**.

> Alternativa horizontal (bicos na lateral) continua válida (ver `03-flange.md` v3), mas exige mais
> altura na base e furo lateral. **Para torno+furadeira, a vertical é melhor.**

---

## 3. Dimensões de referência (v4)

| Cota | Valor |
|---|---|
| Cubo inicial | ~**110 × 110 × 40 mm** |
| Após cortar 2 lados | ~**110 × 90 × 35 mm** |
| Furo central (TBI) | **Ø60 mm** |
| Assento/rebaixo da TBI | Ø ~65 mm × prof. 3–5 mm (conforme flange da TBI) |
| Bicos | **4 × vertical**, 2 por lado, ~42 mm do centro |
| Furo do bico | vertical, encontra a garganta do Ø60 |
| Furos de fixação (coletor) | retangular (3E/DFV **46 × 93 mm**) — confirmar no coletor |
| Flautas | 2 externas (tarugo torneado + o-rings + 1/8" NPT) |
| MAP | 1/8" NPT na lateral, abaixo da borboleta |

---

## 4. Passos de usinagem (imagem `flange-torno-passos-v4.png`)

1. **Cubo de alumínio** (matéria-prima 6061).
2. **TORNO — furar o centro Ø60** (bloco na placa de 4 castanhas; facear e mandrilar).
3. **TORNO — assento da TBI** (rebaixo circular no topo do furo p/ a TBI assentar).
4. **FURADEIRA — 4 furos de fixação** no padrão **retangular** (bloco ainda quadrado, centralizado
   sobre o retângulo do coletor).
5. **Cortar as sobras dos 2 lados** (serra) → vira retângulo, mantendo os furos de fixação.
6. **FURADEIRA — furos dos bicos (vertical)** ao redor do furo central, encontrando a garganta.
   (+ furar/rosquear o **MAP** e as roscas das **flautas**.)

---

## 5. Sensores (simples — só furar ou parafusar)

| Sensor | Onde | Como (simples) |
|---|---|---|
| **TPS** | no eixo da borboleta da **TBI** | já vem/parafusa na TBI (nada na flange) |
| **MAP** | lateral da base, **abaixo da borboleta** | **furar + roscar 1/8" NPT** → mangueira ao sensor |
| **IAT** (temp. do ar) | **entrada de ar** (topo, ar fresco) | **furar + roscar** p/ o sensor (rosca comum) |

- Sem dutos: o MAP é só um furo até a região de vácuo; o IAT é um furo roscado no ar de admissão.
- Se preferir, os sensores MAP/IAT podem ir em um **suporte parafusado** ao lado (ainda mais simples
  de fazer/dar manutenção), ligados por mangueira curta.

---

## 6. Combustível (flautas externas)

- **2 flautas** (uma por lado) torneadas de tarugo redondo de alumínio:
  - 2 cavidades com o-ring para receber o topo dos bicos;
  - **entrada 1/8" NPT** numa ponta; a outra ponta segue para o regulador (retorno).
- Pressão **3 bar** com regulador com retorno.

---

## 7. Prós e contras desta versão

**Prós:**
- Faz **sem CNC** (torno + furadeira).
- Bicos verticais = fácil de furar + boa atomização.
- Sensores só furar/parafusar; manutenção simples.

**Contras:**
- **Maior/mais pesada** (corpo de ~110 mm).
- Conferir **altura total** e **folga do capô** (base + TBI + flautas + bicos em pé).
- Furos de fixação e do bico precisam de **boa marcação** (gabarito ajuda a acertar).

---

## 8. Checklist
- [x] Definir método → **torno + furadeira**, a partir de cubo
- [x] Definir posição do bico → **vertical** (espaço confirmado p/ cubo ~110 mm)
- [ ] Medir furação do coletor (retângulo do 3E) e confirmar 46 × 93 (DFV)
- [ ] Confirmar Ø e profundidade do **assento da TBI** Bosch 60 mm
- [ ] Confirmar **altura total** x capô
- [ ] Fazer **gabarito de furação** dos bicos e dos parafusos
- [ ] Tornear as 2 flautas + o-rings
