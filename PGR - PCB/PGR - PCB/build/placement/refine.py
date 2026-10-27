from pathlib import Path
import sys,json
sys.path.insert(0,str(Path('build/reliability-fixes/ipc').resolve()))
import client;client.SOCKET='/tmp/pgr-placement.sock'
from client import *
a=API();d=a.open(types.DOCTYPE_PCB)
fs={f.reference_field.text.text.text:f for f in a.items(d,[enums.KOT_PCB_FOOTPRINT])}
changes={'F1':(64,64),'Q4':(71,64),'Q9':(76,64),'R53':(73,60.9),'SW4':(55.5,68),'R54':(62,68.5),'Q7':(66,69),'D13':(71.5,69),'R73':(79.7,66.5),'C11':(75,75),'C5':(83.5,69.5),'R2':(85.5,74),'R1':(77.8,70),'R72':(80.5,70),'R19':(86.5,78.5),'R20':(86.5,81),'L1':(73,83.5),'C13':(82.3,83.5),'C8':(97.1,77),'R36':(100.5,75.5),'R5':(58.5,82.5),'R4':(62,82.5),'D3':(58.8,97.5),'C1':(58,102),'D4':(59,89.5),'D5':(59,92.5),'R6':(69.5,91),'R7':(68,94.5),'C3':(68,85),'C17':(142.5,117),'R3':(145.5,114.8),'R51':(147,73.5),'C26':(145.5,60.5)}
coord_names={'position','start','mid','end','center','top_left','bottom_right','point','control1','control2','control_1','control_2','radius_point'}
def shift(m,dx,dy):
 for fd,val in m.ListFields():
  if fd.message_type is None:continue
  for z in (val if fd.label==fd.LABEL_REPEATED else [val]):
   if fd.message_type.full_name==types.Vector2.DESCRIPTOR.full_name and fd.name in coord_names:z.x_nm+=dx;z.y_nm+=dy
   else:shift(z,dx,dy)
updates=[]
for ref,(x,y) in changes.items():
 f=clone(fs[ref]);ox,oy=xy(f.position);dx=round((x-ox)*1e6);dy=round((y-oy)*1e6)
 for fld in [f.reference_field,f.value_field,f.datasheet_field,f.description_field]:shift(fld,dx,dy)
 for item in f.definition.items:
  z=unpack(item);shift(z,dx,dy);item.Pack(z)
 f.position.CopyFrom(v(x,y));updates.append(f)
for z in a.items(d,[enums.KOT_PCB_ZONE]):
 if z.type==board.ZT_RULE_AREA and z.name.startswith('M3'):
  z.rule_area_settings.keepout_pads=False;z.rule_area_settings.keepout_footprints=False;updates.append(z)
for t in a.items(d,[enums.KOT_PCB_TEXT]):
 if t.text.text in ['TAMPER','MODEM','AQUANODE']:
  target={'TAMPER':(158.3,74),'MODEM':(158.3,88),'AQUANODE':(158.3,110)}
  # Distinguish MODEM connector label from MODEM testpoint label.
  if xy(t.text.position)[0]>145:t.text.position.CopyFrom(v(*target[t.text.text]));t.text.attributes.angle.value_degrees=90
 if t.layer==board.BL_F_SilkS:t.text.attributes.size.CopyFrom(v(1,1));updates.append(t)
a.update(d,updates);a.save(d)
print('Saved clearance refinement',len(changes),'parts')
