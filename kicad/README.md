# KiCad — INJET RACING ECU (Fase 1)

Projeto esquemático hierárquico gerado a partir de `modulo/esquema-eletrico.md`.

## Abrir

1. Instale [KiCad 8](https://www.kicad.org/download/) (ou 7 — formato compatível)
2. Abra **`injet-racing-ecu.kicad_pro`** no KiCad
3. No **Eeschema**, navegue pelas folhas na barra lateral ou duplo-clique nos blocos

## Folhas

| Página | Arquivo | Conteúdo |
|--------|---------|----------|
| 1 | `injet-racing-ecu.kicad_sch` | Índice hierárquico (blocos) |
| 2 | `sheets/power.kicad_sch` | 12V → fusível → IRF9540 → TVS → **MP1584** → +5V |
| 3 | `sheets/mcu.kicad_sch` | **Black Board** U1 + REF3033 + barra +3V3 |
| 4 | `sheets/sensors.kicad_sch` | IAT/CLT/MAP/TPS/VBat + CN1 ATX-24 |
| 5 | `sheets/rpm.kicad_sch` | PC817 opto (negativo bobina) |
| 6 | `sheets/injectors.kicad_sch` | 4× IRLZ44N low-side |
| 7 | `sheets/relays.kicad_sch` | 3× relé (principal/bomba/IAC) |
| 8 | `sheets/lambda.kicad_sch` | MCP6004 + AD8628 + heater + CN2 PCIe-6 |
| 9 | `sheets/can.kicad_sch` | SN65HVD230 transceiver |

## Regenerar

```powershell
cd kicad
pip install sexpdata
python _gen_kicad_ecu.py
```

## Notas

- **Símbolos embutidos** na biblioteca `Injet:*` — não precisa instalar libs externas para abrir
- **PCB vazio** — próximo passo: importar netlist e rotear (fenolite 1-layer ou PCB futuro)
- Após abrir, rode **Ferramentas → Associar footprints** e **Inspectar → Regras elétricas (ERC)**
- Se o KiCad pedir migrar formato, aceite — salve de volta na mesma pasta
- Pinagem GPIO = `firmware/include/pins.h` e `esquema-eletrico.md` §2.0

## Alimentação (resumo)

```
+12V_BAT → proteção → +12V_PROT
                    → MP1584 → +5V → Black Board pin 5V
                                      ↓ LDO interno
                                    +3V3 → barra ECU → sensores/CAN/opto
```

Não há AMS1117 extra na placa ECU — ver `esquema-eletrico.md` §1.4.
