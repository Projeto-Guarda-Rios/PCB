#!/usr/bin/env python3
"""Reproduce the read-only KiCad schematic evidence for this review."""
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
CLI = '/home/dauwt/.backplane-bend/kicad/10.0.6/bin/kicad-cli'
ENV = os.environ | {
    'KICAD10_SYMBOL_DIR': '/usr/share/kicad/symbols',
    'KICAD10_FOOTPRINT_DIR': '/usr/share/kicad/footprints',
}
COMMANDS = [
    ('version', ['--version']),
    ('netlist', ['sch', 'export', 'netlist', '--format', 'kicadxml', '--output', str(OUT / 'netlist.xml'), str(ROOT / 'PGR.kicad_sch')]),
    ('erc', ['sch', 'erc', '--format', 'json', '--severity-all', '--output', str(OUT / 'erc-resolved.json'), str(ROOT / 'PGR.kicad_sch')]),
    ('svg', ['sch', 'export', 'svg', '--output', str(OUT / 'svg'), str(ROOT / 'PGR.kicad_sch')]),
]
for name, args in COMMANDS:
    result = subprocess.run([CLI, *args], cwd=ROOT, env=ENV, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (OUT / (name + '.log')).write_text(result.stdout)
    print(name, result.returncode)
    if result.returncode:
        raise SystemExit(result.returncode)
print('ERC results must be interpreted from erc-resolved.json; export success is not electrical approval.')
