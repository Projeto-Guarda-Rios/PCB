#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
KICAD="/home/dauwt/.backplane-bend/kicad/10.0.6/bin/kicad-cli"
export KICAD10_SYMBOL_DIR=/usr/share/kicad/symbols
export KICAD10_FOOTPRINT_DIR=/usr/share/kicad/footprints
"$KICAD" pcb drc --format json --units mm --severity-all --refill-zones --schematic-parity --output build/reliability-fixes/drc-final.json PGR.kicad_pcb > build/reliability-fixes/drc-final.log 2>&1
"$KICAD" sch erc --format json --units mm --severity-all --output build/reliability-fixes/erc-final.json PGR.kicad_sch > build/reliability-fixes/erc-final.log 2>&1
"$KICAD" sch export netlist --format kicadxml --output build/reliability-fixes/netlist-final.xml PGR.kicad_sch > build/reliability-fixes/netlist-final.log 2>&1
build/reliability-fixes/ipc/venv/bin/python build/reliability-fixes/ipc/ground_graph.py > build/reliability-fixes/ground-connectivity.txt
python build/reliability-fixes/verify_fixes.py > build/reliability-fixes/verification.log
