# Guarda-Rios PCB Repository

This repository contains all PCB design files for the **Guarda-Rios Project** — an open-source, low-cost, low-power water quality monitoring system. Multiple stations are deployed along a river so that parameter spikes between adjacent stations reveal precisely where pollution enters the waterway.

The system has two PCBs:

| Board | Role | Placement |
|---|---|---|
| **AquaNode PCB** | Submerged sensor node — reads water parameters and transmits them over RS-485 | Below waterline |
| **Main PCB (PGR)** | Station hub — receives RS-485 data, manages power (solar + 18650 Li-ion), and sends data to the cloud via NB-IoT | Above waterline |

> GitHub organisation: [github.com/Projeto-Guarda-Rios](https://github.com/Projeto-Guarda-Rios)
> Project site: [guarda-rios.pt](https://guarda-rios.pt) · Data portal: [data.guarda-rios.pt](https://data.guarda-rios.pt)

---

## Directory Structure

```
PCB/
├── AquaNode - PCB/          # AquaNode submerged sensor node
├── PGR - PCB/               # Main Station PCB
├── Datasheets/              # Component datasheets
├── Resources/               # Logos, SVGs, and images (silkscreen assets)
└── LICENSE
```

---

## AquaNode - PCB

The AquaNode is the submerged node of each station. It is built around an **STM32L053R8** microcontroller (ultra-low-power) and integrates a DS18B20 water temperature sensor (1-Wire) and a DFRobot SEN0554 turbidity sensor. Readings are encoded into the custom Guarda-Rios protocol and transmitted to the Main PCB over RS-485.

```
AquaNode - PCB/
├── Renders/                              # PNG renders of the current board
│   ├── AquaNode - PCB.png               #   Top-side render
│   └── AquaNode - PCB - 2.png           #   Bottom-side / alternate angle render
│
├── AquaNode - PCB.step                  # STEP model of the assembled board
├── AquaNode - PCB - Render.step         # STEP model used for rendering
├── AquaNode - PCB.stl                   # STL mesh of the board
│
└── AquaNode - PCB/                      # KiCAD project (current version)
    ├── AquaNode - PCB.kicad_pro         #   KiCAD project file  ← open this in KiCAD
    ├── AquaNode - PCB.kicad_pcb         #   PCB layout
    ├── AquaNode - PCB.kicad_sch         #   Schematic
    ├── footprints/                      #   Custom footprint library
    ├── symbols/                         #   Custom symbol library
    └── production/                      # Production files (PCBA) — current version
        ├── -v2.0.zip                    #   Gerbers + drill files (upload to JLCPCB)
        ├── -v2.0_bom.csv               #   Bill of Materials
        ├── -v2.0_positions.csv         #   Component placement (pick & place)
        ├── -v2.0_designators.csv       #   Designator mapping
        ├── netlist.ipc                  #   IPC netlist
        └── backups/                     #   Auto-generated production backups
```

**Key files:**
- Edit the PCB: `AquaNode - PCB/AquaNode - PCB/AquaNode - PCB.kicad_pro`
- Order the board: `AquaNode - PCB/AquaNode - PCB/production/-v2.0.zip`
- BOM for assembly: `AquaNode - PCB/AquaNode - PCB/production/-v2.0_bom.csv`
- Positions for assembly: `AquaNode - PCB/AquaNode - PCB/production/-v2.0_positions.csv`

---

## PGR - PCB

The Main PCB (PGR) is the above-water hub of each station. It is built around an **ESP32-WROOM-32D** and includes an RS-485 receiver, NB-IoT modem, BMS (battery management system), 18650 Li-ion charger, and solar charger — making each station fully self-sufficient in the field.

```
PGR - PCB/
├── Renders/                              # PNG renders of the current board
│   ├── PGR.png                          #   Top-side render
│   └── PGR - 2.png                      #   Bottom-side / alternate angle render
│
├── PGR.step                             # STEP model of the assembled board
├── PGR-Solder.step                      # STEP model showing solder joints
├── PGR.3mf                             # 3MF model (for 3D printing / Fusion 360)
│
├── PGR - PCB - v1.0-v4.0.zip           # Archived KiCAD projects (versions 1.0 – 4.0)
├── PGR - PCB - v5.0.zip                # Archived KiCAD project (version 5.0)
│
├── gerbers/                             # Gerber archives for previous board versions
│   ├── PGR-gerbers-v1.0.zip
│   ├── PGR-gerbers-v2.0.zip
│   ├── PGR-gerbers-v3.0.zip
│   ├── PGR-gerbers-v3.1.zip
│   ├── PGR-gerbers-v4.0.zip
│   ├── PGR-gerbers.zip                  #   (legacy export)
│   ├── PGR-F_Paste.zip                  #   Front paste layer export
│   └── PGR-PTH.zip                      #   PTH drill file export
│
└── PGR - PCB/                           # KiCAD project (current version)
    ├── PGR.kicad_pro                    #   KiCAD project file  ← open this in KiCAD
    ├── PGR.kicad_pcb                    #   PCB layout
    ├── PGR.kicad_sch                    #   Schematic
    ├── PGR-Library.kicad_sym           #   Custom symbol library
    ├── PGR-FootPrints.pretty/          #   Custom footprint library
    ├── footprints/                      #   Additional footprints
    ├── symbols/                         #   Additional symbols
    └── production/                      # Production files (PCBA) — current versions
        ├── PGR_PCB_v5.1.zip            #   Gerbers + drill files — latest (upload to JLCPCB)
        ├── PGR_PCB_v5.1_bom.csv        #   Bill of Materials — latest
        ├── PGR_PCB_v5.1_positions.csv  #   Component placement — latest
        ├── PGR_PCB_v5.1_designators.csv
        ├── PGR_PCB_v5.0.zip            #   Gerbers + drill files — v5.0
        ├── PGR_PCB_v5.0_bom.csv        #   Bill of Materials — v5.0
        ├── PGR_PCB_v5.0_positions.csv
        ├── PGR_PCB_v5.0_designators.csv
        ├── bom-JLCPCB Assembly Order.xls  # JLCPCB-formatted BOM for online ordering
        ├── bom.csv
        ├── designators.csv
        ├── positions.csv
        ├── netlist.ipc
        └── backups/                    # Auto-generated production backups
```

**Key files:**
- Edit the PCB: `PGR - PCB/PGR - PCB/PGR.kicad_pro`
- Order the board (latest): `PGR - PCB/PGR - PCB/production/PGR_PCB_v5.1.zip`
- BOM for assembly (latest): `PGR - PCB/PGR - PCB/production/PGR_PCB_v5.1_bom.csv`
- Positions for assembly (latest): `PGR - PCB/PGR - PCB/production/PGR_PCB_v5.1_positions.csv`
- Previous version gerbers: `PGR - PCB/gerbers/`

> Note: There are no current production files inside `PGR - PCB/gerbers/` — that directory holds archives of older board revisions only. Current production files are inside `PGR - PCB/PGR - PCB/production/`.

---

## Datasheets

Reference datasheets for ICs and components used across both PCBs.

```
Datasheets/
├── STM32L053C6.PDF                       # AquaNode MCU — STM32L053 datasheet
├── an4467-getting-started-with-stm32l0xx-hardware-development-stmicroelectronics.pdf
│                                         # STM32L0 hardware development guide (ST AppNote AN4467)
└── st485eb.pdf                           # ST485EB RS-485 transceiver (used on AquaNode)
```

---

## Resources

Images, SVGs, and logos used in PCB silkscreen layers or project documentation.

```
Resources/
├── guarda_rios_logo.svg / .png          # Official Guarda-Rios project logo
├── dwtLogo.svg                          # Designer logo
├── MIT_license_logo.svg / .png         # MIT license badge
├── open_source_logo.svg                 # Open-source hardware logo
├── open-source-hardware6230.logowik.com.webp
├── logo-colegio-ribadouro.png           # School/institution logo
│
├── AquaNodeBack.svg                     # AquaNode back silkscreen artwork
├── AquaNodeBack - Sem Logo.svg          # AquaNode back silkscreen (no logo variant)
├── BackSilkScreen.svg                   # Generic back silkscreen asset
│
├── AquaNode_v2_image_top.png            # AquaNode v2 board image — top
├── AquaNode_v2_image_bottom.png         # AquaNode v2 board image — bottom
├── PGR_v5.1_image_top.png              # PGR v5.1 board image — top
├── PGR_v5.1_image_bottom.png           # PGR v5.1 board image — bottom
│
└── Gemini_Generated_Image_iya1lhiya1lhiya1.png   # AI-generated concept image
```

---

## Hardware Summary

| Parameter | AquaNode PCB | Main PCB (PGR) |
|---|---|---|
| MCU | STM32L053R8 | ESP32-WROOM-32D |
| Sensors | DS18B20 (temp), DFRobot SEN0554 (turbidity) | — |
| Communication | RS-485 out (custom protocol) | RS-485 in · NB-IoT out |
| Power | From Main PCB via RS-485 cable | Solar + 18650 Li-ion (BMS + charger on-board) |
| Placement | Submerged | Above waterline |
| CAD tool | KiCAD | KiCAD |

---

## License

This project is fully open-source. See [`LICENSE`](LICENSE) for details.
