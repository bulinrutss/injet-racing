# Firmware INJET RACING — Fase 1

ECU TBI speed-density / batch-fire para STM32F407 (Black Board).

## Módulos

| Arquivo | Função |
|---|---|
| `include/pins.h` | Pinagem fixada (sensores PC9/7/11/8/6 · PA4=DAC Vm · PA5=Ip · PA6=Un) |
| `src/wideband.cpp` | Wideband DIY (topologia rusEFI / mck1117/wideband) |
| `src/sensors.cpp` | IAT, CLT, MAP, TPS, VBat |
| `src/fuel.cpp` | Speed-density, VE, dead-time |
| `src/rpm.cpp` | RPM pelo negativo da bobina (PE8 / R17O) |
| `src/closed_loop.cpp` | Malha fechada PI (trim lambda) |
| `src/main.cpp` | Loop principal (referência / bancada) |

## Plataforma

- **Alvo:** STM32F407VET6 Black Board (Arduino core STM32 ou bare-metal Cube)
- **Protótipo sensores:** Arduino Mega 2560 (`05-sensores.md`)

## Compilar (Arduino IDE / PlatformIO)

1. Instalar core **STM32duino** (STM32F4).
2. Placa: **Generic F407VET6** ou Black Board equivalente.
3. Abrir `src/main.cpp` como sketch ou usar PlatformIO com `platform = ststm32`.

## Referências

- Wideband: [mck1117/wideband](https://github.com/mck1117/wideband) (MIT)
- Hardware: `modulo/esquema-eletrico.md`, `modulo/06-sonda-lambda.md`
