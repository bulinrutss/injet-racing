# FUT-04 — Roda fônica / trigger · tipos · dentes · vs sinal da bobina

**Status:** referência · **Fase 2** (fora prodv6 Fase 1)  
**Relacionado:** [FUT-03 Drag Star 650](./FUT-03-dragstar-650-tbi-rpm.md) · MOD7 bobina · `implementacoes-futuras/README.md`

---

## O que é

**Roda fônica** (trigger wheel, reluctor wheel): disco ou coroa no **virabrequim** (ou comando) com **dentes** de metal.  
Um **sensor** fixo lê a passagem dos dentes → tren de pulsos proporcional ao **ângulo** do motor, não à faísca.

```
[ Dente ][ Dente ][ Dente ][  gap  ][ Dente ]...  ← volante
                    ↑
              sensor (VR ou Hall) fixo no motor
                    │
                    ▼
              pulsos digitais → ECU
```

---

## Tipos de sensor (o que existe)

| Sensor | Física | Sinal | Condicionamento ECU |
|--------|--------|-------|---------------------|
| **VR** (indutivo) | Bobina + ímã; dente de ferro perturba campo | **AC** (senoide) | LM1815 / comparador / CI VR→TTL |
| **Hall** | Chip Hall + ímã no sensor | **Digital** (0/5 V ou open collector) | GPIO + pull-up (3,3 V com divisor se 5 V) |
| **Óptico** | LED + fototransistor, fenda no disco | Digital | GPIO + pull-up |
| **Pick-up estator** (ex. Drag Star) | VR com **1** protuberância no volante | AC, **1×/volta** | Igual VR — é o caso **mínimo** de “roda fônica” |

**Hall vs VR:** mesma **função** (pulso por posição); **forma elétrica diferente**. Hall não precisa conditioner AC.

---

## Padrões comuns (quantidade de dentes)

| Padrão | Dentes / volta | Sync (dente faltando) | Onde aparece |
|--------|----------------|------------------------|--------------|
| **1×/volta** | 1 | Não | TCI Yamaha/Honda antigo, Drag Star pick-up |
| **12-1** | 12, falta 1 | Sim (720° grosso) | Adaptações simples |
| **36-1** | 36, falta 1 | Sim | **Muito usado** aftermarket (rusEFI, MS, Speeduino) |
| **60-2** | 60, faltam 2 | Sim | Megasquirt clássico |
| **24x** | 24 (GM LS) | Padrão OEM específico | Motores GM modernos |
| **58x** | 58 | OEM | Ford / variantes |

### Por que a **quantidade de dentes** importa

1. **Resolução angular** — mais dentes → ECU sabe a posição do virabrequim com mais precisão (ex.: 360°/36 = **10°** por dente no 36-1).
2. **RPM em baixa rotação** — mais pulsos/volta → período entre pulsos menor → RPM **atualiza mais rápido** (menos “lag” na lenta).
3. **Agendamento** — injeção/ignição em **graus** (ex.: “injetar 120° BTDC”) exige saber onde o virabrequim está **entre** duas faíscas.
4. **Dente(s) faltando** — só contar dentes dá RPM, mas **não** distingue 0° de 360° num 4-tempos (ciclo = **720°**). O **gap** gera pulso longo → ECU acha **PMH / fase** (sync).
5. **Limite superior** — dentes demais → frequência de pulso alta no corte de giro → pode estourar **EXTI/capture** do MCU (ex.: 60 dentes @ 7000 rpm = 7000 Hz × 60 = **420 kHz** edge rate — precisa avaliar hardware).

**Regra prática:**  
- **Só RPM + batch grosso:** 1×/volta ou poucos dentes basta (Fase 1 / TBI).  
- **Sequencial / ponto fino:** 24–60 dentes + sync (+ **cam** ou dente faltante + lógica 720°).

---

## Qual a mais usada?

| Contexto | Escolha típica |
|----------|----------------|
| **Aftermarket open-source** (rusEFI, Speeduino, MS) | **36-1** no virabrequim |
| **Megasquirt histórico** | **60-2** |
| **OEM carro moderno** | Padrão do fabricante (24x, 58x, 60-2…) — **não** padronizado |
| **Moto OEM antiga (TCI)** | **1 pick-up** no estator — **sem** roda fônica multi-dente |
| **Projeto INJET Fase 2** | **36-1** se for fabricar roda; reutilizar pick-up 1×/volta só se aceitar batch/TBI |

**36-1** ganha por equilíbrio: resolução boa, sync claro, documentação abundante, cabe em MCU com input capture.

---

## Roda fônica vs sinal da bobina (MOD7)

| | **Roda fônica (+ VR/Hall)** | **Bobina − (PC817 / faísca)** |
|--|----------------------------|-------------------------------|
| **Mede** | **Posição** do virabrequim | **Evento de ignição** (TCI já decidiu) |
| **Avanço de ignição** | ECU **calcula** (mapa) | Já aplicado pelo TCI — pulso **“anda”** com RPM |
| **Pulsos/volta** | N dentes (ex. 35 efectivos no 36-1) | ~cilindros/2 no carro; 290/430 na Drag Star |
| **Regularidade** | Dentes **igualmente** espaçados (exceto gap) | Irregular se V 70° / multi-bobina |
| **Sync 720°** | Com dente faltante (+ cam se necessário) | **Não** — só instantes de faísca |
| **Injeção sequencial** | **Sim** (com firmware + dentes) | **Fraco** — amarrado na faísca |
| **Injeção batch / TBI** | **Sim** — melhor fase | **Funciona** — mais tolerante |
| **Hardware prodv6** | **Não** (Fase 2) | **Sim** (MOD7) |
| **Chicote** | Sensor no motor + roda | TCI → bobina, fácil em carros 1 bobina |

### Analogia

- **Roda fônica** = relógio com **mostrador** (sabe a hora exata).  
- **Bobina −** = campainha que toca quando alguém **decidiu** que é hora (ignição) — útil, mas não substitui o mostrador.

---

## Onde entra o pick-up da Drag Star

Pick-up XVS650 = **VR de 1 dente** no volante:

- Mesma **família** que roda fônica + sensor indutivo.  
- **Não** é Hall.  
- **Não** é roda fônica “completa” (sem multi-dente, sem sync 720° robusto).  
- Equivalente funcional a **1×/volta** — suficiente p/ RPM + TBI batch; **insuficiente** p/ injeção sequencial fina sem **sensor de comando** (cam).

---

## Duas fontes na moto (FUT-03)

Bobina **e** pick-up **cabeados juntos** ≠ usar os dois no **mesmo** contador de RPM.  
Firmware escolhe **uma** fonte. Ver [FUT-03 § duas entradas](./FUT-03-dragstar-650-tbi-rpm.md).

---

## Caminho INJET (Fase 2)

| Nível | Trigger | Injeção |
|-------|---------|---------|
| **Fase 1** (prodv6) | Bobina − (MOD7) | Batch-fire speed-density |
| **Fase 2a** | Pick-up OEM 1×/volta (MOD7b VR) | Batch com offset ° |
| **Fase 2b** | Roda **36-1** + Hall ou VR | Sequencial / ponto por mapa |
| **Fase 2c** | 36-1 + **cam** (Hall 1×/2 voltas) | Sequencial por cilindro |

---

## Referências

- rusEFI / Megasquirt docs — wheel decoders (36-1, 60-2)
- [FUT-03 — Drag Star 650](./FUT-03-dragstar-650-tbi-rpm.md)
- [FUT-05 — Condicionador VR (pick-up / distr. 2 fios)](./FUT-05-condicionador-vr-pickup.md)
- ProdV6 MOD7: bobina − · `firmware/src/rpm.cpp`
