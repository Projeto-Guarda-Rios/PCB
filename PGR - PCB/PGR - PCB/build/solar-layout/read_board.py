from pathlib import Path
import sys,json
sys.path.insert(0,str(Path('build/reliability-fixes/ipc').resolve()))
import client;client.SOCKET='/tmp/pgr-solar-layout-20261026.sock'
from client import *
a=API();d=a.open(types.DOCTYPE_PCB)
its=a.items(d,[enums.KOT_PCB_FOOTPRINT,enums.KOT_PCB_TRACE,enums.KOT_PCB_VIA,enums.KOT_PCB_ZONE,enums.KOT_PCB_SHAPE])
Path('build/solar-layout/items-before.json').write_text(json.dumps([json_format.MessageToDict(x,preserving_proto_field_name=True)|{'_type':x.DESCRIPTOR.name} for x in its],indent=2))
for f in its:
 if not isinstance(f,board.FootprintInstance):continue
 ref=f.reference_field.text.text.text
 print(ref,xy(f.position),f.orientation.value_degrees,f.value_field.text.text.text)
 if ref in ['U1','R1','R2','TH1','BT1','J10']:
  print('lib',f.definition.id,'path',f.symbol_path)
  for c in f.definition.items:
   if c.Is(board.Pad.DESCRIPTOR):
    p=unpack(c);print('PAD',p.number,xy(p.position),p.net.name)
