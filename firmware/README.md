# Firmware INJET RACING — Fase 1

ECU TBI speed-density / batch-fire para STM32F407 (Black Board).

## Módulos

| Arquivo | Função |
|---|---|
| `include/pins.h` | Pinagem fixada (sensores PD0/PA9/PC9/PC8/PA8 · PA4=DAC Vm · PA5=Ip · PA6=Un) |
| `src/wideband.cpp` | Wideband DIY (topologia rusEFI / mck1117/wideband) |
| `src/sensors.cpp` | IAT, CLT, MAP, TPS, VBat |
| `src/fuel.cpp` | Speed-density, VE, dead-time |
| `src/rpm.cpp` | RPM pelo negativo da bobina (PE8 / R17O) |
| `src/closed_loop.cpp` | Malha fechada PI (trim lambda) |
| `src/main.cpp` | Loop principal (referência / bancada) |

## Plataforma

- **Alvo:** STM32F407VET6 Black Board (Arduino core STM32 ou bare-metal Cube)
- **Protótipo sensores:** Arduino Mega 2560 (`05-sensores.md`)

## USB / serial (regra fixa)

| Ação | 12 V ECU | USB |
|------|----------|-----|
| **Gravar firmware** (upload) | **OFF** | Cabo normal |
| **Monitor / tune** | **ON** | **Power blocker** (só D+/D−/GND) |

- Monitor: **115200 baud** — log RPM, MAP, TPS, lambda, PW (`main.cpp`).
- **Tune** (mapa VE): futuro protocolo serial `SET`/`SAVE` — **não** é upload de sketch; mesmo cabo com blocker.
- No carro: USB **desconectado**; tune via CAN quando implementado.

Detalhes: `kicad/prodv6/BENCH-CHECKLIST.md` · `modulo/esquema-eletrico.md` §1.3

## Compilar (Arduino IDE / PlatformIO)

1. Instalar core **STM32duino** (STM32F4).
2. Placa: **Generic F407VET6** ou Black Board equivalente.
3. Abrir `src/main.cpp` como sketch ou usar PlatformIO com `platform = ststm32`.

## Referências

- Wideband: [mck1117/wideband](https://github.com/mck1117/wideband) (MIT)
- Hardware: `modulo/esquema-eletrico.md`, `modulo/06-sonda-lambda.md`
- PCB ProdV6: `kicad/prodv6/CHECKLIST.md` · bancada: `kicad/prodv6/BENCH-CHECKLIST.md`
