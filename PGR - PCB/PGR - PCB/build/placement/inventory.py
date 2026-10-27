from pathlib import Path
import sys,json
sys.path.insert(0,str(Path('build/reliability-fixes/ipc').resolve()))
import client;client.SOCKET='/tmp/pgr-placement.sock'
from client import *
a=API();d=a.open(types.DOCTYPE_PCB);fs=a.items(d,[enums.KOT_PCB_FOOTPRINT])
Path('build/placement/source-items.json').write_text(json.dumps([json_format.MessageToDict(f,preserving_proto_field_name=True) for f in fs],indent=2))
for ref in ['U5','J9','J1','J7','J8','J11','U1','U3','IC1','U7','U11','U9','U10','U13','U14','U15','U4','Q4','Q9','L1','L2','C5','C13']:
 f=next(f for f in fs if f.reference_field.text.text.text==ref);print(ref,'ORIENT',f.orientation.value_degrees,'POS',xy(f.position))
 for child in f.definition.items:
  if child.Is(board.Pad.DESCRIPTOR):
   p=unpack(child)
   if p.type!=board.PT_SMD or ref not in ['U5','U4']:print(' ',p.number,p.net.name,tuple(round(q-o,3) for q,o in zip(xy(p.position),xy(f.position))))
