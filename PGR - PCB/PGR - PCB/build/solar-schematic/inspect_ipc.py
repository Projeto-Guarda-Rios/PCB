import sys,json
from pathlib import Path
sys.path.insert(0,str(Path('build/reliability-fixes/ipc').resolve()))
import client
client.SOCKET='/tmp/pgr-solar-20261026.sock'
from client import *
a=API();d=a.open(types.DOCTYPE_SCHEMATIC)
its=a.items(d,[enums.KOT_SCH_SYMBOL,enums.KOT_SCH_LINE,enums.KOT_SCH_JUNCTION,enums.KOT_SCH_NO_CONNECT,enums.KOT_SCH_GLOBAL_LABEL,enums.KOT_SCH_LABEL,enums.KOT_SCH_TEXT])
Path('build/solar-schematic/items-before.json').write_text(json.dumps([json_format.MessageToDict(x,preserving_proto_field_name=True)|{'_type':x.DESCRIPTOR.name} for x in its],indent=2))
for x in its:
 if isinstance(x,sch.SchematicSymbolInstance) and x.reference_field.text.text in ['U1','TH1','R1','R2','J10','IC1']:print(x)
 if isinstance(x,sch.SchematicLine) and 194<=xy(x.start)[0]<=265 and 52<=xy(x.start)[1]<=90:print('LINE',x.id.value,xy(x.start),xy(x.end))
