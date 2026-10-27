from pathlib import Path
import sys,json
sys.path.insert(0,str(Path('build/reliability-fixes/ipc').resolve()))
import client
client.SOCKET='/tmp/pgr-production-fixes.sock'
from client import *
api=API();d=api.open(types.DOCTYPE_SCHEMATIC)
ts=[v for k,v in enums.KiCadObjectType.items() if k.startswith('KOT_SCH_')]
items=api.items(d,ts)
Path('build/production-fixes/items-before.json').write_text(json.dumps([json_format.MessageToDict(x,preserving_proto_field_name=True)|{'_type':x.DESCRIPTOR.full_name} for x in items],indent=2))
print('types',sorted(set(type(x).__name__ for x in items)))
for x in items:
 if isinstance(x,sch.SchematicSymbolInstance) and x.reference_field.text.text in ['Q2','R18','U3','U5','D9','BZ1','IC1']:print(x)
print('commands',list(sc.DESCRIPTOR.message_types_by_name))
