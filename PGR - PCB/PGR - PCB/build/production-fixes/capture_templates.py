from pathlib import Path
import sys,json
sys.path.insert(0,str(Path('build/reliability-fixes/ipc').resolve()))
import client
client.SOCKET='/tmp/pgr-production-templates.sock'
from client import *
api=API();d=api.request(editor.GetOpenDocuments(type=types.DOCTYPE_SCHEMATIC),editor.GetOpenDocumentsResponse).documents[0]
items=api.items(d,[enums.KOT_SCH_SYMBOL]);p=Path('build/production-fixes/templates');p.mkdir(exist_ok=True)
for s in items:
 key=s.reference_field.text.text+'_'+str(s.unit.unit);(p/(key+'.pb')).write_bytes(s.SerializeToString())
 pins=[unpack(a.item) for a in s.definition.items if a.item.Is(sch.SchematicPin.DESCRIPTOR)]
 print(key,s.value_field.text.text,s.footprint_field.text.text,[(a.number,a.name,xy(a.position),a.orientation) for a in pins])
