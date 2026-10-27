from pathlib import Path
import sys,shutil,copy
import sexpdata as sx
sys.path.insert(0,str(Path('build/reliability-fixes/ipc').resolve()))
import client
client.SOCKET='/tmp/pgr-label-style.sock'
from client import API,types,project,Empty
api=API();d=api.open(types.DOCTYPE_SCHEMATIC);api.request(project.CloseDocument(document=d),Empty)
p=Path('PGR.kicad_sch');shutil.copy2(p,'build/production-fixes/backups/before-label-tags.kicad_sch');shutil.copy2('build/production-fixes/netlist-final.xml','build/production-fixes/before-label-tags.xml')
s=p.read_text();S=sx.Symbol
# Native editing preserves complete symbol graphics while changing label objects only.
r=sx.loads(s);n=0
for a in r:
 if not isinstance(a,list) or not a or str(a[0])!='label':continue
 a[0]=S('global_label');at=next(b for b in a if isinstance(b,list) and str(b[0])=='at');angle=at[3]
 # Match the original input-shaped tag convention, keeping each electrical anchor.
 a.insert(2,[S('shape'),S('input')]);a.insert(4,[S('fields_autoplaced'),S('yes')])
 effects=next(b for b in a if isinstance(b,list) and str(b[0])=='effects')
 effects[:]=[S('effects'),[S('font'),[S('size'),1.27,1.27]],[S('justify'),S('right' if angle in [180,270] else 'left')]]
 a.append([S('property'),'Intersheetrefs','${INTERSHEET_REFS}',copy.deepcopy(at),[S('hide'),S('yes')],[S('effects'),[S('font'),[S('size'),1.27,1.27]]]])
 n+=1
p.write_text(sx.dumps(r));d=api.open(types.DOCTYPE_SCHEMATIC);api.save(d);print('Restored tag shape on',n,'labels')
