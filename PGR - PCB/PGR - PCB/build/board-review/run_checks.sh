#!/usr/bin/env bash
set -u
KICAD="/home/dauwt/.backplane-bend/kicad/10.0.6/bin/kicad-cli"
"$KICAD" pcb drc --format json --units mm --severity-all --refill-zones --schematic-parity --output build/board-review/drc.json PGR.kicad_pcb
"$KICAD" sch erc --format json --units mm --severity-all --output build/board-review/erc.json PGR.kicad_sch
"$KICAD" sch export netlist --format kicadxml --output build/board-review/netlist.xml PGR.kicad_sch
"$KICAD" sch export svg --output build/board-review/schematic PGR.kicad_sch
"$KICAD" pcb export svg --layers F.Cu,B.Cu,F.Silkscreen,B.Silkscreen,F.Fab,Edge.Cuts --common-layers Edge.Cuts --mode-multi --fit-page-to-board --exclude-drawing-sheet --output build/board-review/layers PGR.kicad_pcb
