# INJET 3 Step — tempo de trabalho e fabricação

Estimativas para **1 unidade piloto**, maker com ferramentas básicas (ferro, CNC router, FDM). Horas = tempo efetivo, não calendar.

---

## 1. Resumo rápido

| Fase | Tempo | Quem |
|------|-------|------|
| Esquemático + PCB layout | 8–16 h | Projeto (1ª vez) |
| CAM + CNC isolamento | 1–3 h | Fabricação |
| Soldagem SMD/PTH | 2–4 h | Montagem |
| Case 3D (modelar + imprimir) | 4–8 h | Fabricação |
| Chicote | 2–4 h | Montagem |
| Firmware v1 (RPM + 3 limiares + UI) | 20–40 h | Software |
| Teste bancada + carro | 4–8 h | Validação |
| **Total 1º protótipo** | **~40–80 h** | |
| **2ª unidade em diante** | **~8–15 h** | (sem redesenho) |

---

## 2. Projeto (KiCad / documentação)

| Tarefa | Tempo | Notas |
|--------|-------|-------|
| Esquemático (MCU, display, relé, RPM, alimentação) | 4–8 h | Reaproveitar lógica MOD9 relé + MOD7 opto |
| Footprints + layout 7×10 cm | 4–8 h | Display + botões na borda; relé potência no chicote |
| Revisão DRC + gerber/G-code CNC | 1–2 h | 1ª placa sempre mais lenta |
| **Subtotal projeto** | **8–16 h** | Só na 1ª versão |

---

## 3. PCB — CNC

| Tarefa | Tempo | Notas |
|--------|-------|-------|
| Export isolamento (FlatCAM / KiCad CAM) | 0,5–1 h | |
| Fixar FR4 10×15, nivelar | 0,25 h | |
| Fresar isolamento (DF 1,6 mm) | 0,5–1,5 h | Depende spindle/passada |
| Furar furos componentes (opcional) | 0,25–0,5 h | Ou furadeira manual |
| Limpeza + tinning opcional | 0,25 h | |
| **Subtotal CNC / placa** | **1,5–3,5 h** | |

**Material:** ~1 placa 10×15 por unidade; pack 5 Ali → 5 protótipos.

---

## 4. Soldagem

| Tarefa | Tempo | Notas |
|--------|-------|-------|
| PTH (relé SRD, conectores, caps) | 1–1,5 h | ~80–120 pontos |
| MCU / display / ULN (se SMD: +1 h) | 0,5–2 h | Blue Pill = módulo pronto (− tempo) |
| Inspeção + continuidade | 0,5 h | Multímetro |
| **Subtotal solda** | **2–4 h** | Com prática: ~2 h |

**Estanho:** 8–12 g/placa (ver `02-custos.md`).

---

## 5. Case impressão 3D

| Tarefa | Tempo | Notas |
|--------|-------|-------|
| Modelar caixa (janela display, 2 botões, 4 LED) | 3–6 h | 1ª versão; export STL |
| Slicer + impressão FDM | 2–4 h | ~40–80 g PLA; 0,2 mm; ~60–90 mm largura |
| Pós-processo (raspar furos, parafusos) | 0,5–1 h | |
| **Subtotal case** | **5,5–11 h** | 2ª unidade: ~3 h (só print) |

**Parâmetros típicos:** PLA/PETG, infill 20–25%, parede 3 perimeters, bico 0,4 mm.

---

## 6. Chicote

| Tarefa | Tempo | Notas |
|--------|-------|-------|
| Cortar fios, crimp terminal, identificar cores ODG | 1,5–2,5 h | 10 vias + 2 potência |
| Ramificação DI 2ch (Modo B) | +0,5–1 h | Se aplicável |
| Teste continuidade / polaridade | 0,5 h | |
| **Subtotal chicote** | **2–4 h** | |

---

## 7. Firmware

| Módulo | Tempo | Entregável |
|--------|-------|------------|
| Entrada RPM ( EXTI / timer ) | 4–8 h | Pulsos estáveis Modo A |
| Contagem + filtro + nº cilindros | 4–6 h | RPM display |
| 3 limiares + lógica burn/pre/corte | 6–10 h | Relé COM/NC |
| Display 7 seg. multiplex | 4–8 h | 2 dígitos |
| Shift light 4 LED + saída | 2–4 h | % antes do limiar |
| Menu SET (programação) | 4–8 h | SL, PC, BO, corte, CL |
| EEPROM / defaults | 2–4 h | Retém config |
| **Subtotal firmware v1** | **20–40 h** | |

**Extra Modo B/C:** +8–20 h (condensador externo ou DI 2ch no firmware).

---

## 8. Validação

| Etapa | Tempo | Onde |
|-------|-------|------|
| Bancada: alimentação, display, relé, RPM simulado | 2–4 h | Fonte + gerador pulsos |
| Motor parado / starter | 1–2 h | RPM real − bobina |
| Pista / dinamômetro | 2–4 h | Cut sob carga |
| **Subtotal testes** | **4–8 h** | |

---

## 9. Cronograma sugerido (piloto)

| Semana | Foco | Horas |
|--------|------|-------|
| 1 | Esquemático + layout + pedido peças Ali | 10–15 |
| 2 | CNC + solda + firmware RPM + relé | 10–15 |
| 3 | Case 3D + chicote + UI display/menu | 10–15 |
| 4 | Teste carro Modo A + ajustes | 8–12 |
| **Total** | **1º protótipo funcional Modo A** | **~40–55 h** |

Modo B/C (condensador): +1–2 semanas se necessário.

---

## 10. Paralelo com INJET ECU (FUT-01)

Se integrar cut na prodv6 depois:

| Item | Economia |
|------|----------|
| MCU / display / case 3-step | Produto separado mantém standalone |
| Canal relé bobina na ECU | −1 relé SRD + driver na prodv6 (~6–8 peç.) |
| RPM | Já existe PE8 — **− opto duplicado** se só ECU |
| Firmware limiter | Pode ser módulo no firmware ECU (+20–30 h) |

Piloto caixa independente valida **chicote + cut + UX** antes de puxar FUT-01 para prodv6.
