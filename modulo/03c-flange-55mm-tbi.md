# Tópico 3C — Flange SIMPLES (chapa quadrada) p/ TBI 55 mm

> Projeto INJET RACING — Fase 1 (TBI / monoponto)
> Versão "grotesca"/simples: **chapa quadrada** feita no **torno + furadeira**.
> TBI definida = **55 mm** (a da foto, furação **80 × 70 mm**).
> 🖼️ Imagens:
> - **Técnica/cotada:** `../assets/flange-55mm-cotas-v5.png`
> - **Realista (4 ângulos):** `../assets/flange-55mm-3d-v5.png`
> - **Passos de fabricação:** `../assets/flange-55mm-passos-v5.png`
> - Fotos da TBI: `../assets/tbi-55mm-vista.png`, `../assets/tbi-55mm-furacao.png`

---

## 1. Conceito

Uma **chapa quadrada de alumínio** simples:
- **120 × 120 mm**, espessura **30 mm** (6061-T6).
- **Furo central Ø55** (torno) para a TBI.
- **Fixação do coletor:** furos com **Allen rebaixado** (cabeça **abaixo da superfície**) → a TBI
  assenta plana por cima sem bater nos parafusos.
- **Fixação da TBI:** **furos roscados** no topo, padrão **80 × 70 mm** (da sua TBI).
- **Bicos:** 4 furos **inclinados a 30°** (2 por lado), apontando **para dentro e para baixo**,
  direcionados **para a abertura do coletor**.
- **MAP:** furo lateral (1/8" NPT), abaixo da borboleta.
- **IAT:** furo **na parede da própria TBI**, **acima da borboleta**, sensor **rosqueado na horizontal**.
- Sem dutos internos de combustível → **flautas externas**.

---

## 2. Dados do 3E (pesquisados) e por que o bico vai a 30°

**Carburador 3E ("30/34"):**
- Borboletas: **30 mm (1º estágio)** e **34 mm (2º estágio)**.
- Venturi/difusor: **25 / 29 mm**.
- É **2 bocas lado a lado** → a **abertura do coletor é alongada (~70 × 40 mm)**, não redonda.

**Furação da base 3E:** ⚠️ **NÃO tem padrão universal** — a distância dos furos **muda conforme o
coletor** (as flanges são vendidas **sem furo** de propósito). **➡️ Medir no SEU coletor.**
- O 3E usa tipicamente **3 furos** (triangular). Alguns coletores têm **4 furos** — confirmar no seu.

**Ângulo do bico (30°):**
- Como a abertura do coletor é **menor que o Ø55** num dos eixos, existe uma "prateleira" ao redor.
- Se o bico fosse horizontal, o jato bateria **na parede/prateleira**.
- Por isso o furo do bico vai **inclinado ~30° para baixo e para dentro**, para o spray **cair dentro
  da abertura** (garganta) do coletor. Geometria: bico entrando a ~30 mm do centro e caindo ~20 mm
  → `atan(20/30) ≈ 34°` → **~30°** é o alvo.

---

## 3. Cotas (v5)

| Cota | Valor |
|---|---|
| Chapa (L × W × E) | **120 × 120 × 30 mm** |
| Furo central (TBI) | **Ø55 mm** |
| Furos roscados TBI | **4× M6 em retângulo 80 × 70 mm** |
| Furos fixação coletor (3E) | **medir** (3 furos típico) + **rebaixo p/ Allen** |
| Bicos | **4× inclinados 30°**, 2 por lado, apontando p/ a abertura |
| Abertura do coletor 3E | ~**70 × 40 mm** (bocas 30 e 34) |
| MAP | **1/8" NPT** lateral, abaixo da borboleta |
| IAT | furo **na parede da TBI**, acima da borboleta, **horizontal** |
| Flautas | 2 externas (torneadas) + o-rings + 1/8" NPT |

---

## 4. Passos de fabricação (imagem `flange-55mm-passos-v5.png`)

1. **Chapa quadrada 120×120×30** (6061-T6).
2. **TORNO — furo central Ø55** (placa de 4 castanhas; facear e mandrilar).
3. **FURADEIRA — 4 furos roscados da TBI** (retângulo 80×70, rosca M6).
4. **FURADEIRA — furos de fixação do 3E + rebaixo do Allen** (cabeça abaixo da superfície).
5. **FURADEIRA ANGULADA — furos dos bicos a 30°** (chapa inclinada em morsa angular).
6. **Furos laterais — MAP e IAT** (rosca 1/8" NPT / rosca do sensor).

> Passo 5 exige **morsa/gabarito angular** na furadeira (simples de improvisar). É o único furo
> "inclinado"; o resto é reto.

---

## 5. Sensores (simples — só furar/rosquear)

| Sensor | Onde | Como |
|---|---|---|
| **TPS** | eixo da borboleta da TBI | já vem/parafusa na TBI |
| **MAP** | lateral da chapa, abaixo da borboleta | **furar + roscar 1/8" NPT** → mangueira |
| **IAT** | **parede da TBI, acima da borboleta** | **furar + roscar** o sensor, **horizontal** (ar fresco) |

---

## 6. Fixação (detalhe importante)

- **Coletor → chapa:** parafusos **Allen (cabeça cilíndrica) em furo rebaixado (counterbore)**, de
  modo que a **cabeça fique abaixo da superfície superior** → a TBI assenta plana por cima e esconde
  os parafusos.
- **TBI → chapa:** **4 furos roscados** (M6) no topo, no padrão **80 × 70 mm**; parafusa a TBI de cima.
- Vedação: junta entre chapa e coletor, junta/anel entre TBI e chapa, o-rings nos bicos.

---

## 7. Checklist
- [x] TBI definida → **55 mm**, furação **80 × 70 mm**
- [x] Chapa → **120 × 120 × 30 mm**, furo central **Ø55**
- [x] Ângulo do bico → **30°** (para cair na abertura do coletor)
- [x] Dados do 3E → bocas 30/34, abertura ~70×40
- [ ] **Medir furação do 3E no seu coletor** (sem padrão!) e conferir 3 ou 4 furos
- [ ] Confirmar profundidade do rebaixo do Allen
- [ ] Confirmar altura total (chapa + TBI + flautas) x capô
- [ ] Fazer gabarito de furação (bicos 30° + parafusos)
- [ ] Tornear as 2 flautas
