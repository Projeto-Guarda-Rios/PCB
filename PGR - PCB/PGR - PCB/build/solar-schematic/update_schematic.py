from pathlib import Path
import sys,math
sys.path.insert(0,str(Path('build/reliability-fixes/ipc').resolve()))
import client
client.SOCKET='/tmp/pgr-solar-20261026.sock'
from client import *
api=API();d=api.open(types.DOCTYPE_SCHEMATIC)
items=api.items(d,[enums.KOT_SCH_SYMBOL,enums.KOT_SCH_LINE,enums.KOT_SCH_JUNCTION,enums.KOT_SCH_NO_CONNECT,enums.KOT_SCH_GLOBAL_LABEL,enums.KOT_SCH_LABEL,enums.KOT_SCH_TEXT])
syms={x.reference_field.text.text:x for x in items if isinstance(x,sch.SchematicSymbolInstance)}
new=[];updates=[];deletes=[]
def uid():return str(uuid.uuid4())
def wire(a,b):new.append(sch.SchematicLine(id=types.KIID(value=uid()),start=v(*a),end=v(*b),type=sch.SLT_WIRE))
def remove_wire(a,b):
 found=[x for x in items if isinstance(x,sch.SchematicLine) and {xy(x.start),xy(x.end)}=={a,b}]
 assert len(found)==1,(a,b,found)
 deletes.append(found[0].id.value)
def moved(s,pos,newref=None,orientation=None,pins=None):
 s=clone(s);old=xy(s.position);delta=(pos[0]-old[0],pos[1]-old[1]);s.position.CopyFrom(v(*pos))
 for f in [s.reference_field,s.value_field,s.footprint_field,s.datasheet_field,s.description_field,*s.user_fields]:
  p=xy(f.text.position);f.text.position.CopyFrom(v(p[0]+delta[0],p[1]+delta[1]))
 for c in s.definition.items:
  if c.item.Is(sch.SchematicPin.DESCRIPTOR):
   p=unpack(c.item);a=xy(p.position)
   p.position.CopyFrom(v(*(pins[p.number] if pins else (a[0]+delta[0],a[1]+delta[1]))))
   if newref:p.id.value=uid()
   c.item.Pack(p)
 if newref:
  s.id.value=uid();s.reference_field.text.text=newref
 if orientation is not None:s.transform.orientation=orientation
 s.fields_autoplaced=False
 return s
def field_at(s,field,pos,size=1.27,align=enums.HA_LEFT):
 f=getattr(s,field);p=xy(s.position);deg={sch.SSO_0:0,sch.SSO_90:90,sch.SSO_180:180,sch.SSO_270:270}[s.transform.orientation]
 th=math.radians(deg);dx,dy=pos[0]-p[0],pos[1]-p[1]
 f.text.position.CopyFrom(v(p[0]+math.cos(th)*dx-math.sin(th)*dy,p[1]+math.sin(th)*dx+math.cos(th)*dy))
 f.text.attributes.angle.value_degrees=deg
 f.text.attributes.horizontal_alignment=align;f.text.attributes.vertical_alignment=enums.VA_CENTER
 f.text.attributes.size.CopyFrom(v(size,size));f.visible=True;f.allow_auto_place=False
nums=[int(k[4:]) for k in syms if k.startswith('#PWR') and k[4:].isdigit()];nextp=max(nums)
groundtemplate=next(x for x in syms.values() if x.definition.id.entry_name=='GND' and x.transform.orientation==sch.SSO_0)
def ground(p):
 global nextp
 nextp+=1;s=moved(groundtemplate,p,f'#PWR{nextp:03d}');new.append(s)
def text(content,p,size=1.0):
 t=sch.SchematicText(id=types.KIID(value=uid()));t.text.text=content;t.text.position.CopyFrom(v(*p));a=t.text.attributes
 a.horizontal_alignment=enums.HA_LEFT;a.vertical_alignment=enums.VA_TOP;a.size.CopyFrom(v(size,size));a.line_spacing=1.2;a.multiline=True;a.visible=True
 new.append(t)
def label(name,p):
 t=sch.LocalLabel(id=types.KIID(value=uid()),position=v(*p),spin_style=sch.SLSS_RIGHT);t.text.text=name;t.text.position.CopyFrom(v(*p));t.text.attributes.horizontal_alignment=enums.HA_LEFT;t.text.attributes.vertical_alignment=enums.VA_BOTTOM;t.text.attributes.size.CopyFrom(v(1.27,1.27));t.text.attributes.visible=True
 new.append(t)
# Disconnect the old EN1 grounding and EN2 battery tie. CE grounding remains.
for a,b in [((207.01,67.31),(210.82,67.31)),((210.82,72.39),(210.82,69.85)),((223.52,72.39),(210.82,72.39)),((223.52,64.77),(223.52,72.39)),((207.01,64.77),(210.82,64.77))]:remove_wire(a,b)
for ref in ['#PWR051','#PWR052']:
 if ref in syms and xy(syms[ref].position) in [(207.01,67.31),(207.01,64.77)]:deletes.append(syms[ref].id.value)
# Locate the TMR ground by position rather than assuming its reference.
for s in syms.values():
 if s.definition.id.entry_name=='GND' and xy(s.position)==(207.01,64.77) and s.id.value not in deletes:deletes.append(s.id.value)
# EN1 from the system rail permits battery-free start-up. EN2 low enables VIN-DPM.
wire((203.2,67.31),(210.82,67.31));label('PWR_OUT',(203.2,67.31))
wire((210.82,69.85),(198.12,69.85));wire((198.12,69.85),(198.12,71.12));ground((198.12,71.12))
# Charge setpoint is below the 500-mA input ceiling; DPPM reduces it for system demand.
r1=clone(syms['R1']);r1.value_field.text.text='2kR';updates.append(r1)
# A 68-kohm timer resistor restores a nominal 9.07-h fast-charge / 54.4-min precharge timer.
assert 'R30' not in syms
r30=moved(syms['R2'],(187.96,64.77),'R30');r30.value_field.text.text='68kR'
field_at(r30,'reference_field',(187.96,60.96),align=enums.HA_CENTER);field_at(r30,'value_field',(187.96,62.865),align=enums.HA_CENTER)
new.append(r30);wire((191.77,64.77),(210.82,64.77));wire((184.15,64.77),(180.34,64.77));wire((180.34,64.77),(180.34,66.04));ground((180.34,66.04))
# Replace the on-board TS sensor with a dedicated connector and remote probe.
remove_wire((236.22,69.85),(238.76,69.85));remove_wire((250.19,69.85),(246.38,69.85));deletes.append(syms['#PWR031'].id.value)
wire((236.22,69.85),(238.76,69.85));label('BAT_NTC',(238.76,69.85))
assert 'J12' not in syms
j12=moved(syms['J10'],(156.21,93.98),'J12');j12.value_field.text.text='BATTERY_NTC'
field_at(j12,'reference_field',(154.94,85.09),align=enums.HA_CENTER);field_at(j12,'value_field',(154.94,87.63),align=enums.HA_CENTER)
new.append(j12)
th=moved(syms['TH1'],(170.18,99.06),orientation=sch.SSO_0,pins={'1':(170.18,95.25),'2':(170.18,102.87)})
th.value_field.text.text='10k NTC';th.footprint_field.text.text='';th.attributes.exclude_from_board=True;th.attributes.exclude_from_position_files=True
field_at(th,'reference_field',(173.99,97.79));field_at(th,'value_field',(173.99,100.33));updates.append(th)
wire((161.29,93.98),(170.18,93.98));wire((170.18,93.98),(170.18,95.25));label('BAT_NTC',(161.29,93.98))
wire((161.29,91.44),(190.5,91.44));wire((190.5,91.44),(190.5,105.41));wire((190.5,105.41),(170.18,105.41));wire((170.18,105.41),(170.18,102.87));wire((190.5,105.41),(190.5,107.95));ground((190.5,107.95))
new.append(sch.Junction(id=types.KIID(value=uid()),position=v(190.5,105.41)))
bat=clone(syms['BT1']);bat.value_field.text.text='1S Li-ion 4.2V';updates.append(bat)
# On-sheet specifications travel with the schematic and assembly documentation.
text('SOLAR CONTROL\nEN1=OUT, EN2=GND: VIN-DPM enabled\n500 mA input limit; ~4.5 V input regulation\n445 mA charge target; system load has priority\nR30: ~9.1 h fast charge / ~54 min precharge',(151.13,46.99))
text('REMOTE BATTERY TEMPERATURE\nTH1 is off-board. Insulate and bond it to the cell.\nUse 10k at 25 C, 103AT-2-compatible NTC curve.\nMatch trip temperatures to the selected cell.\nAn open/missing probe inhibits charging.',(144.78,112.395))
text('INPUT: J10 pin 2 = +IN; pin 1 = GND\nUse regulated 5 V DC or a compatible nominal 6 V panel.\nCold panel open-circuit voltage must be below 10.2 V.\nC5: 10 uF, X7R, >=16 V; verify effective capacitance.\n500 mA input ceiling. Fixed VIN-DPM, no MPPT.\nPanel and battery sizing require the load energy budget.',(22.86,171.45))
text('BATTERY / SOLAR POWER PATH\nJ10 -> U1 OUT -> U3 -> D1 -> +5V -> IC1 -> +3.3V\nU1 supplies the load first and charges with spare input.\nBattery supplements weak input and supplies the night load.',(25.4,109.22))
c=api.begin(d)
try:
 api.delete(d,list(dict.fromkeys(deletes)));api.update(d,updates);api.create(d,new)
 api.end(d,c,'Enable solar input regulation, restore charge timers, and add remote cell-temperature sensing')
except Exception:
 api.end(d,c,'Rollback solar charger updates',drop=True);raise
api.save(d)
print('Saved canonical schematic:',len(updates),'updated,',len(new),'added,',len(set(deletes)),'removed')
