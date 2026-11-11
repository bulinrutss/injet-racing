# BOM com códigos — PCB INJET RACING (1-layer)

> Placa **240×160 mm**. Códigos = silk / mapa de furos.

- Cruzamentos cobre (sinais/potência): **0**
- Fios topo: **43**
- **GND = pour** (cobre de fundo). Pads GND soldam no pour; CNC isola só trilhas de sinal/potência.

| Código | Valor / P/N | Função |
|---|---|---|
| **J1** | `ATX-24 header` | Conector principal chicote |
| **J2** | `PCIe-6 header` | Lambda LSU 4.2 |
| **Q1** | `IRLZ44N` | Driver INJ1 |
| **R10** | `100R` | Gate INJ1 |
| **R20** | `10k` | PD INJ1 |
| **D10** | `1N4007` | Flyback INJ1 |
| **Q2** | `IRLZ44N` | Driver INJ2 |
| **R11** | `100R` | Gate INJ2 |
| **R21** | `10k` | PD INJ2 |
| **D11** | `1N4007` | Flyback INJ2 |
| **Q3** | `IRLZ44N` | Driver INJ3 |
| **R12** | `100R` | Gate INJ3 |
| **R22** | `10k` | PD INJ3 |
| **D12** | `1N4007` | Flyback INJ3 |
| **Q4** | `IRLZ44N` | Driver INJ4 |
| **R13** | `100R` | Gate INJ4 |
| **R23** | `10k` | PD INJ4 |
| **D13** | `1N4007` | Flyback INJ4 |
| **Q5** | `IRLZ44N` | Aquecedor lambda |
| **R15** | `100R` | Gate Q5 |
| **R25** | `10k` | PD Q5 |
| **D14** | `1N4007` | Flyback Q5 |
| **Q6** | `IRF9540` | Proteção reversa |
| **C1** | `220u/50V` | Bulk |
| **C2** | `100n/100V` | Entrada |
| **D1** | `P6KE33A` | TVS |
| **R1** | `100k` | Gate Q6 |
| **D2** | `Zener 12V` | Gate Q6 |
| **U6** | `MP1584` | Buck 5V |
| **U7** | `AMS1117-3.3` | LDO 3V3 |
| **C3** | `10u` | LDO in |
| **C4** | `10u+100n` | LDO out |
| **Q7** | `2N7000` | Relé RL1 |
| **R30** | `1k` | Gate RL1 |
| **D20** | `1N4007` | Flyback RL1 |
| **Q8** | `2N7000` | Relé RL2 |
| **R31** | `1k` | Gate RL2 |
| **D21** | `1N4007` | Flyback RL2 |
| **Q9** | `2N7000` | Relé RL3 |
| **R32** | `1k` | Gate RL3 |
| **D22** | `1N4007` | Flyback RL3 |
| **U1** | `STM32F407 Black Board` | MCU |
| **J3** | `1x4 SWD` | Debug |
| **R40** | `2K26` | IAT |
| **C10** | `100n` | Filtro IAT |
| **R50** | `1k` | Série IAT |
| **R41** | `2K26` | CLT |
| **C11** | `100n` | Filtro CLT |
| **R51** | `1k` | Série CLT |
| **R42** | `10k 1%` | MAP |
| **R43** | `18k 1%` | MAP div |
| **C12** | `100n` | Filtro MAP |
| **R52** | `1k` | Série MAP |
| **C13** | `100n` | Filtro TPS |
| **R53** | `1k` | Série TPS |
| **U4** | `PC817` | Opto RPM |
| **R60** | `10k 2W` | RPM s1 |
| **R61** | `10k 2W` | RPM s2 |
| **D30** | `1N4148` | Opto prot |
| **R62** | `4k7` | Pull-up RPM |
| **C20** | `1nF` | Filtro RPM |
| **U5** | `SN65HVD230` | CAN |
| **U2** | `MCP6002` | Opamp WB |
| **U3** | `OPA388IDR SOIC` | Zero-drift Ip SMD |
| **R70** | `61R9 1%` | Shunt Ip |
| **R71** | `6k8 1%` | R_ESR |
| **C30** | `220n` | Filtro Ip |
| **C31** | `220n` | Filtro Un |
| **C32** | `100n+10u` | Decoupling |
| **R76** | `10k` | Bias Vm |
| **R77** | `10k` | Bias Vm |
| **R78** | `1k` | Serie OPA388IDR |
| **R74** | `100k 1%` | VBat hi |
| **R75** | `10k 1%` | VBat lo |
| **C33** | `100n` | Filtro VBat |
| **U8** | `REF3033` | Ref ADC 3V3 |

## Conectores

### J1 ATX-24
1:+12 IGN · 2:+12 BAT · 3/4:GND_P · 5:GND_S · 6:+5 · 7:+3V3 · 8:IAT · 9:CLT · 10:MAP · 11:TPS · 12:RPM
13–16:INJ1–4 · 17:RL bomba · 18:RL main · 19:RL IAC · 20:CANH · 21:CANL · 22:tacho · 23:start · 24:shield

**Pinagem MCU:** PA4=DAC Vm · PA5=Ip · PA6=Un · PC1=VBat

### J2 PCIe-6
1:H+ · 2:H− · 3:IP · 4:VM · 5:UN · 6:NC

### J3 SWD
1:+3V3 · 2:SWDIO · 3:SWCLK · 4:GND

## Arquivos

| Arquivo | Uso |
|---|---|
| `assets/ecu-pcb-1layer-pads-map.png` | Montagem: só furos THT + pads SMD + códigos |
| `assets/ecu-pcb-1layer-assembly.png` | Visão com trilhas (sem tarja) |
| `assets/ecu-pcb-1layer-traces-cnc.svg` | Máscara CNC |
