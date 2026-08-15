# FUT-02 — Driver relé reforçado (bobina >150 mA)

**Status:** ideia salva · **não** na prodv6 Fase 1  
**Contexto:** MOD9 usa **2N7000** (Q20–Q22) p/ chavear bobina 12 V low-side. SRD-12V externo (~30–70 mA) OK.  
Relé automotivo “grande” (bobina **>150–200 mA**) **queima** o 2N7000.

> **Fase 1 vigente:** 3× **SRD-12V** no chicote · bobina pin1→+12V · pin2→RLx (dreno Q) · NO→CN3.  
> Ver `modulo/esquema-eletrico.md` §6 · §1.7.5.

---

## Problema

| Item | Limite atual | Relé pesado no carro |
|------|--------------|----------------------|
| Q20–Q22 | 2N7000 Id ~**200 mA** | Bobina **150–300 mA** comum |
| Papel do Q | Chaveia **corrente da bobina** (não é só sinal lógico) | Mesma função — precisa driver mais forte |
| CN3 | Só contato **NO** (carga) | Inalterado |

Relé **externo** no chicote **não remove** o driver onboard — a bobina ainda passa pelo Q.

---

## Opção B1 — Trocar MOSFET (mesmo esquema §6)

Substituir **Q20, Q21, Q22**: 2N7000 → **IRLZ44N** (igual MOD8 bicos).

| Ref | De | Para |
|-----|-----|------|
| Q20–Q22 | 2N7000 TO-92 | **IRLZ44N** TO-220 |
| R50–R52 (R_gate) | 1 kΩ | **100 Ω** |
| R55–R57 (R_gs) | 10 kΩ | 10 kΩ (manter) |
| D20–D22 | 1N4007 flyback | manter (K→+12V_PROT) |

**Ligações (inalteradas):**

| Net | De (comp.polo) | Para (comp.polo) |
|-----|----------------|------------------|
| +12V_PROT | barra 12 V | bobina externa pin1 (COIL+) |
| RL1 / RL2 / RL3 | bobina pin2 (COIL−) | Q20/Q21/Q22.D |
| GRL1 / GRL2 / GRL3 | U1 pad (PD10/8/9) | R_gate.A |
| — | R_gate.B | Q.G |
| — | Q.S | GND |
| RL_MAIN / RL_PUMP / RL_IAC | relé pin4 NO | CN3 pads 3 / 2 / 1 |

**Footprint PCB:** trocar `MOD9` TO-92 → TO-220 (courtyard ≥1 mm vs vizinhos).  
**Firmware:** nenhuma mudança (mesmos GPIO PD8/9/10).

**Bancada:** medir corrente da bobina @ 12 V antes de montar; IRLZ44N aguenta **>4 A** — folga para qualquer relé 12 V automotivo.

---

## Opção B2 — Módulo relé com opto / IN lógico

Para **não** passar corrente de bobina pela ECU:

| Net | De | Para |
|-----|-----|------|
| GPIO | PD8/9/10 | **IN** do módulo (3,3 V ou open-drain) |
| +12V / GND | chicote | alimentação **do módulo** (bobina interna ao módulo) |
| NO / COM | módulo | carga (bomba / main / IAC) — pode substituir CN3 parcialmente |

**Delta prodv6:** remover ou não montar Q20–Q22; rotear GPIO → conector dedicado; **refazer** chicote e esquemático §6.  
Flyback onboard deixa de ser necessário na bobina (módulo já traz).

---

## Quando puxar da fila

- [ ] Chicote definido com relé **>150 mA** de bobina (ex. 20–30 A automotivo no NO)
- [ ] B1: revisar MOD9 footprint + DRC + `_check_mod9_now.py`
- [ ] B2: nova folha / conector / doc chicote — maior refactor

**Prioridade sugerida:** baixa se mantiver **SRD-12V** no carro (Fase 1).

---

## Fora deste item

- Corrente dos **contatos** NO (bomba) — dimensionar relé/fusível no chicote, não o 2N7000.
- FUT-01 (corte bobina limiter) — canal separado se unificar no futuro.
