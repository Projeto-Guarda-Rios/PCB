from pathlib import Path
import shutil
from native_utils import footprint_spans
p=Path('PGR.kicad_pcb');s=p.read_text();changes=[]
for ref,uid,a,b,c in footprint_spans(s):
 if ref in ['J12','R30']:
  assert c.count('${KICAD9_3DMODEL_DIR}')==1
  changes.append((a,b,c.replace('${KICAD9_3DMODEL_DIR}','${KICAD10_3DMODEL_DIR}')))
assert len(changes)==2
shutil.copy2(p,'build/solar-layout/backups/before-model-metadata.kicad_pcb')
for a,b,c in sorted(changes,reverse=True):s=s[:a]+c+s[b:]
p.write_text(s);print('Assigned current KiCad model paths to the two new footprints')
