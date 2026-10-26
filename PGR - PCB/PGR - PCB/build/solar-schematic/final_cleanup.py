from pathlib import Path
import sys
sys.path.insert(0,str(Path('build/reliability-fixes/ipc').resolve()))
import client
client.SOCKET='/tmp/pgr-solar-finish-20261026.sock'
from client import *
a=API();d=a.open(types.DOCTYPE_SCHEMATIC);its=a.items(d,[enums.KOT_SCH_SYMBOL,enums.KOT_SCH_LINE])
s=clone(next(x for x in its if isinstance(x,sch.SchematicSymbolInstance) and x.reference_field.text.text=='#PWR084'))
old=xy(s.position);new=(210.82,100.33);delta=(new[0]-old[0],new[1]-old[1]);s.position.CopyFrom(v(*new))
for f in [s.reference_field,s.value_field,s.footprint_field,s.datasheet_field,s.description_field,*s.user_fields]:
 p=xy(f.text.position);f.text.position.CopyFrom(v(p[0]+delta[0],p[1]+delta[1]))
for child in s.definition.items:
 if child.item.Is(sch.SchematicPin.DESCRIPTOR):
  p=unpack(child.item);p.position.CopyFrom(v(*new));child.item.Pack(p)
w=next(x for x in its if isinstance(x,sch.SchematicLine) and {xy(x.start),xy(x.end)}=={(210.82,100.33),(210.82,102.87)})
c=a.begin(d)
try:a.update(d,[s]);a.delete(d,[w.id.value]);a.end(d,c,'Keep remote-probe ground annotation clear of the battery-positive rail')
except:a.end(d,c,'Rollback final annotation cleanup',drop=True);raise
a.save(d);a.request(project.CloseDocument(document=d),Empty)
d=a.open(types.DOCTYPE_SCHEMATIC);ss={x.reference_field.text.text:x for x in a.items(d,[enums.KOT_SCH_SYMBOL])}
assert ss['R1'].value_field.text.text=='2kR' and ss['R30'].value_field.text.text=='68kR'
assert xy(ss['TH1'].position)==(190.5,93.98) and xy(ss['J12'].position)==(176.53,88.9)
assert not ss['TH1'].footprint_field.text.text
print('Saved/reopened schematic: charge settings and remote-probe connector persist')
a.request(project.CloseDocument(document=d),Empty)
