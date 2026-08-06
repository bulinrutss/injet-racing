# DRC — INJET RACING ECU prodv4 (2 camadas FR4)

- Placa: **240.0×160.0 mm**
- **B.Cu:** 61 trilhas (roteamento principal prodv2)
- **F.Cu:** 26 trilhas (ex-jumpers prodv2 → cobre topo)
- **Fios/jumpers:** **0**
- **Vias F↔B:** **11**
- Cruzamentos B.Cu: **0**
- Cruzamentos F.Cu: **0**
- Sobreposição B.Cu: **0**
- Sobreposição F.Cu: **0**

## Stackup

| Camada | Função |
|---|---|
| F.Cu | Componentes THT + trilhas de ligação (face componentes) |
| FR4 | Core 1.6 mm |
| B.Cu | Trilhas principais + GND pour |

## vs prodv3

| | prodv3 | prodv4 |
|---|---|---|
| Pad nets KiCad | parcial | **completo (MCU+passivos)** |
| Stubs pad↔trilha | não | **sim** |
