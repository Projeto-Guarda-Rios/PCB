from pathlib import Path
import sys,json,xml.etree.ElementTree as ET
sys.path.insert(0,str(Path('build/reliability-fixes/ipc').resolve()))
import client;client.SOCKET='/tmp/pgr-solar-layout-20261026.sock'
from client import *
a=API();d=a.open(types.DOCTYPE_PCB)
items=a.items(d,[enums.KOT_PCB_FOOTPRINT,enums.KOT_PCB_TRACE,enums.KOT_PCB_VIA,enums.KOT_PCB_TEXT])
fps={x.reference_field.text.text.text:x for x in items if isinstance(x,board.FootprintInstance)}
byid={x.id.value:x for x in items};new=[];updates={};removed=[];ids={}
def uid():return str(uuid.uuid4())
def put(x):updates[x.id.value]=x
# Geometry in a footprint's children is serialized in world coordinates.
def shift_geom(m,dx,dy):
 for fd,value in m.ListFields():
  if fd.message_type is None:continue
  vals=value if fd.label == fd.LABEL_REPEATED else [value]
  for z in vals:
   if fd.message_type.full_name==types.Vector2.DESCRIPTOR.full_name:
    if fd.name in ['position','start','mid','end','center','top_left','bottom_right','point','control1','control2','control_1','control_2']:
     z.x_nm+=round(dx*1e6);z.y_nm+=round(dy*1e6)
   else:shift_geom(z,dx,dy)
def movefp(f,pos,ref=None,value=None,sym=None):
 f=clone(f);old=xy(f.position);dx,dy=pos[0]-old[0],pos[1]-old[1];f.position.CopyFrom(v(*pos))
 if ref:f.id.value=uid()
 for fld in [f.reference_field,f.value_field,f.datasheet_field,f.description_field]:
  shift_geom(fld,dx,dy)
  if ref:fld.text.id.value=uid();fld.text.parent.value=f.id.value
 for child in f.definition.items:
  x=unpack(child);shift_geom(x,dx,dy)
  if ref:
   if hasattr(x,'id'):x.id.value=uid()
   if hasattr(x,'parent'):x.parent.value=f.id.value
  child.Pack(x)
 if ref:f.reference_field.text.text.text=ref
 if value:f.value_field.text.text.text=value
 if sym:
  del f.symbol_path.path[:];f.symbol_path.path.add(value=sym);f.symbol_sheet_name='';f.symbol_sheet_filename='PGR.kicad_sch'
 f.locked=types.LS_UNLOCKED
 return f
def setpads(f,nets):
 for child in f.definition.items:
  if child.Is(board.Pad.DESCRIPTOR):
   p=unpack(child)
   if p.number in nets:p.net.name=nets[p.number];p.symbol_pin.no_connect=False
   child.Pack(p)
def field(f,p,size=.8):
 f.reference_field.text.text.position.CopyFrom(v(*p));f.reference_field.text.text.attributes.angle.value_degrees=0;f.reference_field.text.text.attributes.size.CopyFrom(v(size,size));f.reference_field.text.text.attributes.stroke_width.value_nm=120000;f.reference_field.visible=True
 f.value_field.visible=False
root=ET.parse('build/solar-schematic/netlist-after.xml').getroot();cs={c.get('ref'):c for c in root.findall('.//components/comp')}
assert 'J12' not in fps and 'R30' not in fps
j12=movefp(fps['BT1'],(196.8,133.6),'J12','BATTERY_NTC',cs['J12'].findtext('tstamps'));setpads(j12,{'1':'/BAT_NTC','2':'GND'});field(j12,(198.05,129.8),.8)
for child in j12.definition.items:
 if child.Is(board.Pad.DESCRIPTOR):
  p=unpack(child);p.symbol_pin.name='Pin_'+p.number;child.Pack(p)
new.append(j12);ids['J12']=j12.id.value
r30=movefp(fps['R2'],(232.8,143.8),'R30','68kR',cs['R30'].findtext('tstamps'));setpads(r30,{'1':'GND','2':'Net-(U1-TMR)'});field(r30,(235.6,143.7),.7);new.append(r30);ids['R30']=r30.id.value
# The probe belongs on the cell. Replace its on-board footprint with J12.
removed.append(fps['TH1'].id.value)
logo=next(x for x in items if isinstance(x,board.FootprintInstance) and x.reference_field.text.text.text=='G***' and xy(x.position)[0]<220)
put(movefp(logo,(198.333003,105.5)))
u1=clone(fps['U1']);setpads(u1,{'1':'/BAT_NTC','5':'GND','6':'PWR_OUT','14':'Net-(U1-TMR)'});put(u1)
r1=clone(fps['R1']);r1.value_field.text.text.text='2kR';put(r1)
bat=clone(fps['BT1']);bat.value_field.text.text.text='1S Li-ion 4.2V';put(bat)
# Remove the old BAT->EN2 branch, EN1/EP ground straps, and TMR ground strap.
removed += ['c44bab49-dd7b-4343-b1f8-806f6c8cb979','510e28d5-3ecb-4a64-9c6f-f0ecce022fec','1e023aff-2379-47cb-952c-b2a9d5dde82b','424ec0fe-cc6f-4ece-9478-05421e446d9d','4df6c0d5-f904-4097-afcf-28b435b8c7be','5f6c43a1-3eb0-4e5d-b386-e0bfa6771c9d']
assert all(i in byid for i in removed)
for x in items:
 if isinstance(x,(board.Track,board.Via)) and x.net.name=='Net-(U1-TS)':x=clone(x);x.net.name='/BAT_NTC';put(x)
 if isinstance(x,board.Via) and x.id.value=='bc22d415-db4e-48a4-a781-67bf79a02b94':x=clone(x);x.position.CopyFrom(v(230.65,137.25));put(x)
 if isinstance(x,board.Via) and x.id.value=='a9d53c85-0b99-40b3-945c-9c9feef905e9':x=clone(x);x.position.CopyFrom(v(231.0,143.6));put(x)
 if isinstance(x,board.BoardText) and 'Thermistor' in x.text.text:
  x=clone(x);x.text.text='BAT NTC';x.text.position.CopyFrom(v(198.05,138.5));x.text.attributes.size.CopyFrom(v(.8,.8));x.text.attributes.angle.value_degrees=0;put(x)
def track(net,pts,width=.2,layer=board.BL_F_Cu,key=None):
 for i,(p,q) in enumerate(zip(pts,pts[1:])):
  x=board.Track(id=types.KIID(value=uid()),start=v(*p),end=v(*q),width=types.Distance(value_nm=round(width*1e6)),layer=layer,net=board.Net(name=net),locked=types.LS_UNLOCKED);new.append(x)
  if key:ids[f'{key}-{i}']=x.id.value
vt=next(x for x in items if isinstance(x,board.Via) and x.net.name=='GND')
def via(net,p,diam=.5,key=None):
 x=clone(vt);x.id.value=uid();x.position.CopyFrom(v(*p));x.net.name=net
 # Copper diameter is set in the via padstack; the original drill is 0.2 mm.
 for l in x.pad_stack.copper_layers:l.size.CopyFrom(v(diam,diam))
 new.append(x)
 if key:ids[key]=x.id.value
# EN2 low, with a direct connection to the ground plane.
track('GND',[(231.575,137.8),(231.2,137.8),(230.65,137.25)],.2,key='EN2')
# EN1 uses OUT; a small signal branch joins the existing OUT routing on the back.
track('PWR_OUT',[(231.575,138.3),(230.9,138.3),(230.65,138.05)],.2,key='EN1-front');via('PWR_OUT',(230.65,138.05),key='EN1-via')
track('PWR_OUT',[(230.65,138.05),(230.0,138.05),(230.0,140.7),(230.3,141.0),(230.527,141.0)],.2,board.BL_B_Cu,key='EN1-back')
# Keep the timer trace short at the charger, then take the quiet signal to R30 below it.
track('Net-(U1-TMR)',[(234.45,138.8),(234.85,138.8),(235.2,138.45),(235.2,138.4)],.2,key='TMR-front');via('Net-(U1-TMR)',(235.2,138.4),.4,key='TMR-chip-via')
track('Net-(U1-TMR)',[(235.2,138.4),(235.2,142.35),(234.1,143.45)],.2,board.BL_B_Cu,key='TMR-back');via('Net-(U1-TMR)',(234.1,143.45),key='TMR-R30-via')
track('Net-(U1-TMR)',[(234.1,143.45),(233.975,143.45),(233.625,143.8)],.2,key='TMR-R30')
track('GND',[(231.975,143.8),(231.2,143.8),(231.0,143.6)],.25,key='R30-ground')
# Use the inner layer for the probe extension to cross existing back-side status traces.
track('/BAT_NTC',[(196.8,133.6),(196.8,142.55),(196.75,142.6)],.254,board.BL_In2_Cu,key='NTC-extension');via('/BAT_NTC',(196.75,142.6),key='NTC-via')
# Assembly pin identification remains visible beside the connector body.
t=board.BoardText(id=types.KIID(value=uid()),layer=board.BL_F_SilkS);t.text.text='1 TS  2 GND';t.text.position.CopyFrom(v(198.05,139.6));t.text.attributes.size.CopyFrom(v(.65,.65));t.text.attributes.stroke_width.value_nm=110000;t.text.attributes.horizontal_alignment=enums.HA_CENTER;t.text.attributes.vertical_alignment=enums.VA_CENTER;new.append(t)
c=a.begin(d)
try:
 a.delete(d,removed);a.update(d,list(updates.values()));a.create(d,new);a.end(d,c,'Implement solar regulation controls, charge timer, and remote battery-temperature connector')
except:a.end(d,c,'Rollback solar layout update',drop=True);raise
a.request(bc.RefillZones(board=d),Empty);a.save(d)
Path('build/solar-layout/new-ids.json').write_text(json.dumps(ids,indent=2));print('Saved PCB milestone:',len(updates),'updates,',len(new),'new items,',len(removed),'removed')
