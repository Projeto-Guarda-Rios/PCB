from pathlib import Path
import sys,uuid
sys.path.insert(0,str(Path('build/reliability-fixes/ipc').resolve()))
import client
client.SOCKET='/tmp/pgr-production-fixes.sock'
from client import *
api=API();d=api.open(types.DOCTYPE_SCHEMATIC);items=api.items(d,[enums.KOT_SCH_SYMBOL,enums.KOT_SCH_LINE,enums.KOT_SCH_JUNCTION,enums.KOT_SCH_GLOBAL_LABEL,enums.KOT_SCH_LABEL,enums.KOT_SCH_NO_CONNECT,enums.KOT_SCH_TEXT]);ss={x.reference_field.text.text:x for x in items if isinstance(x,sch.SchematicSymbolInstance)}
new=[];upd={};delete=set()
def uid():return types.KIID(value=str(uuid.uuid4()))
def wire(a,b):new.append(sch.SchematicLine(id=uid(),start=v(*a),end=v(*b),type=sch.SLT_WIRE))
def label(name,p):
 x=sch.LocalLabel(id=uid(),position=v(*p),spin_style=sch.SLSS_RIGHT);x.text.text=name;x.text.position.CopyFrom(v(*p));x.text.attributes.size.CopyFrom(v(1.27,1.27));x.text.attributes.visible=True;new.append(x)
def replacewire(a,b):
 found=[x for x in items if isinstance(x,sch.SchematicLine) and {xy(x.start),xy(x.end)}=={a,b}];assert len(found)==1,(a,b,len(found));delete.add(found[0].id.value)
def sym(ref):
 if ref not in upd:upd[ref]=clone(ss[ref])
 return upd[ref]
def move(ref,dx,dy):
 s=sym(ref);p=xy(s.position);s.position.CopyFrom(v(p[0]+dx,p[1]+dy))
 for f in [s.reference_field,s.value_field,s.footprint_field,s.datasheet_field,s.description_field,*s.user_fields]:
  p=xy(f.text.position);f.text.position.CopyFrom(v(p[0]+dx,p[1]+dy))
 for a in s.definition.items:
  if a.item.Is(sch.SchematicPin.DESCRIPTOR):
   pin=unpack(a.item);p=xy(pin.position);pin.position.CopyFrom(v(p[0]+dx,p[1]+dy));a.item.Pack(pin)
 return s
for ref,val in {'R13':'2.2kR','R14':'10kR','C2':'1uF','R18':'560R','R28':'560R','R21':'4.7kR','R24':'4.7kR','U4':'CP2102N-A02-GQFN28'}.items():sym(ref).value_field.text.text=val
keep=[clone(a) for a in sym('IC1').definition.items if not a.item.Is(sch.SchematicField.DESCRIPTOR)]
del sym('IC1').definition.items[:];sym('IC1').definition.items.extend(keep)
sym('IC1').footprint_field.text.text='Package_TO_SOT_SMD:SOT-223-3_TabPin2'
for ref in ['D8','R14']:sym(ref).attributes.do_not_populate=True
# Correct Q2 wiring without changing the transistor's physical pin numbering.
replacewire((237.49,-11.43),(237.49,-10.16));replacewire((219.71,-21.59),(237.49,-21.59))
# IO0 label remains at its previous endpoint, connect it to the collector.
wire((237.49,-21.59),(242.57,-21.59));label('IO0_BTN',(242.57,-21.59))
wire((237.49,-11.43),(242.57,-11.43));label('USB_DTR',(242.57,-11.43))
# Remove the now isolated old IO0 label and tiny leftover wire, if present.
for x in items:
 if isinstance(x,(sch.GlobalLabel,sch.LocalLabel)) and xy(x.position)==(237.49,-10.16):delete.add(x.id.value)
# Active-low status indicators, each fed from 3V3 through a sensible resistor.
for ref,led,ground,x1,x2,y,delta,net in [
 ('R21','D9','#PWR068',237.49,254.0,77.47,(15.24,20.32),'IO21'),
 ('R24','D10','#PWR015',240.03,252.73,74.93,(27.94,20.32),'IO15')]:
 oldx=xy(ss[ref].position)[0]
 replacewire((x1,y),(oldx,y));replacewire((oldx,y),(x2,y));wire((x1,y),(x2,y))
 for x in items:
  if isinstance(x,sch.Junction) and xy(x.position)==(oldx,y):delete.add(x.id.value)
 delete.add(ss[ground].id.value);move(ref,*delta);move(led,*delta)
 p=(oldx+delta[0],y+delta[1]);label('+3.3V',p)
 ledpins=[unpack(a.item) for a in upd[led].definition.items if a.item.Is(sch.SchematicPin.DESCRIPTOR)]
 label(net,xy(next(z for z in ledpins if z.number=='1').position))
# Separate receiver disable from driver enable to permit real MAX3485 shutdown.
# The shared old IO22 connection is retained on DE; RE gets its own GPIO23.
for x in items:
 if isinstance(x,sch.SchematicLine) and (96.52,45.72) in [xy(x.start),xy(x.end)]:delete.add(x.id.value)
wire((96.52,45.72),(93.98,45.72));label('IO23',(93.98,45.72))
# Tamper input moves to RTC GPIO33 for deep-sleep wake.
for x in items:
 if isinstance(x,(sch.GlobalLabel,sch.LocalLabel)) and x.text.text=='IO23' and 100<xy(x.position)[1]<120:
  delete.add(x.id.value);x=clone(x);x.id.CopyFrom(uid());x.text.text='IO33';new.append(x)
# Add explicit unused markers for the genuinely unused input pins and switch contact.
for p in [(201.93,-162.56),(201.93,-160.02),(229.87,138.43)]:
 for x in items:
  if isinstance(x,(sch.GlobalLabel,sch.LocalLabel)) and xy(x.position)==p:delete.add(x.id.value)
 new.append(sch.NoConnectMarker(id=uid(),position=v(*p)))
# Notes record changed firmware contracts and optional production indicators.
for msg,p in [('D8/R14 DNP: omit the permanent power LED for solar operation.',(120.65,-7.62)),('GPIO23 = RS485 /RE; GPIO22 = DE. Sleep: /RE=1, DE=0.\nJ7 signal = GPIO33 / RTC wake; reserve GPIO33 on J1.',(25.4,82.55))]:
 t=sch.SchematicText(id=uid());t.text.text=msg;t.text.position.CopyFrom(v(*p));t.text.attributes.size.CopyFrom(v(1.27,1.27));t.text.attributes.visible=True;t.text.attributes.multiline=True;new.append(t)
c=api.begin(d)
try:
 api.delete(d,list(delete))
 for ref,s in upd.items():
  keep=[clone(a) for a in s.definition.items if not a.item.Is(sch.SchematicField.DESCRIPTOR)]
  del s.definition.items[:];s.definition.items.extend(keep)
  print('Updating',ref,flush=True);api.update(d,[s])
 api.create(d,new);api.end(d,c,'Correct auto-boot, RS485 control and bias, status LEDs, and RTC tamper wake')
except:
 api.end(d,c,'Rollback first production schematic fixes',drop=True);raise
api.save(d);print('Saved first schematic milestone',len(upd),len(new),len(delete))
