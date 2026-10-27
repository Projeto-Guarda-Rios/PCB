from pathlib import Path
import sys,json,math,uuid,collections
import sexpdata as sx
sys.path.insert(0,str(Path('build/reliability-fixes/ipc').resolve()))
import client;client.SOCKET='/tmp/pgr-layout-groups.sock'
from client import *
a=API();d=a.open(types.DOCTYPE_PCB)
sub=lambda n,k:[x for x in n if isinstance(x,list) and x and str(x[0])==k]
raw=sx.loads(Path('PGR.kicad_pcb').read_text()); bounds={}
for f in sub(raw,'footprint'):
 props={p[1]:p[2] for p in sub(f,'property')};at=sub(f,'at')[0];ang=math.radians(-float(at[3] if len(at)>3 else 0));pts=[]
 def add(x,y):pts.append((float(x)*math.cos(ang)-float(y)*math.sin(ang),float(x)*math.sin(ang)+float(y)*math.cos(ang)))
 for pad in sub(f,'pad'):
  p=sub(pad,'at')[0];sz=sub(pad,'size')[0];rot=math.radians(float(p[3] if len(p)>3 else 0));w=abs(float(sz[1])*math.cos(rot))+abs(float(sz[2])*math.sin(rot));h=abs(float(sz[1])*math.sin(rot))+abs(float(sz[2])*math.cos(rot))
  for dx in [-w/2,w/2]:
   for dy in [-h/2,h/2]:add(float(p[1])+dx,float(p[2])+dy)
 for g in f:
  if isinstance(g,list) and g and str(g[0]).startswith('fp_') and str(g[0]) not in ['fp_text','fp_text_box']:
   for key in ['start','end','mid','center']:
    for p in sub(g,key):add(p[1],p[2])
 for z in sub(f,'zone'):
  for poly in sub(z,'polygon'):
   for chain in sub(poly,'pts'):
    for point in sub(chain,'xy'):pts.append((float(point[1])-float(at[1]),float(point[2])-float(at[2])))
 if pts:bounds[props['Reference']]=(min(p[0] for p in pts),min(p[1] for p in pts),max(p[0] for p in pts),max(p[1] for p in pts))
groups=[
('Battery protection / disconnect','BT1 F1 U6 Q3 Q4 Q9 Q7 SW4 R11 R17 R53 R54 R73 C12 D13'),
('Solar input / charger','J10 Q5 U1 C5 C11 R1 R2 R19 R20 R30 R31 R72 D9 D10 R21 R24'),
('Cell temperature interlock','J12 U13 U14 Q8 R45 R46 R47 R48 R49 R50 R51 C25 C26 C27'),
('Battery / status measurements','R66 R67 R68 R69 R70 R71 C29 C30 C31'),
('5 V boost / undervoltage','U3 L1 C13 C14 C15 C18 C19 R22 R23 R32 R33 R34'),
('USB current limit / source mux','U11 U7 C10 C21 C22 C35 R37 R38 R39 R40'),
('3.3 V supply / reset supervisor','IC1 L2 U12 C8 C9 C20 R35 R36'),
('Modem power / connection','J8 U9 C23 C32 C33 C36 R41 R43'),
('USB-C / USB-UART','J9 U4 C1 C3 C4 D3 D4 D5 R4 R5 R6 R7 R8'),
('ESP32 / boot / debug','U5 J1 J13 J14 JP1 SW1 SW2 C2 C6 C7 R9 R10 R12 R25 Q1 Q2 R15 R16'),
('RS485 / AquaNode power','J11 U8 U10 D6 C17 C24 C34 C37 R3 R18 R28 R29 R42 R44'),
('Modem UART isolation','U15 C28 R60 R61 R62 R63'),
('Buzzer driver','BZ1 Q6 D14 R64 R65'),
('Indicators / tamper input','J7 D7 D8 R13 R14'),
('Commissioning test points','TP1 TP2 TP3 TP4 TP5 TP6 TP7 TP8')]
fs={f.reference_field.text.text.text:f for f in a.items(d,[enums.KOT_PCB_FOOTPRINT])}
refs=[ref for _,rs in groups for ref in rs.split()]
assert len(refs)==len(set(refs)) and set(refs)==set(fs),(set(fs)-set(refs),set(refs)-set(fs))
# Translate all serialized world-coordinate geometry along with each footprint.
def shift(m,dx,dy):
 for fd,val in m.ListFields():
  if fd.message_type is None:continue
  for z in (val if fd.label==fd.LABEL_REPEATED else [val]):
   if fd.message_type.full_name==types.Vector2.DESCRIPTOR.full_name:
    if fd.name in ['position','start','mid','end','center','top_left','bottom_right','point','control1','control2','control_1','control_2','radius_point']:z.x_nm+=dx;z.y_nm+=dy
   else:shift(z,dx,dy)
def uid():return types.KIID(value=str(uuid.uuid4()))
def text_at(t,x,y,size=1.2):
 z=board.BoardText(id=uid(),layer=board.BL_Dwgs_User);z.text.text=t;z.text.position.CopyFrom(v(x,y));z.text.attributes.size.CopyFrom(v(size,size));z.text.attributes.stroke_width.value_nm=150000;z.text.attributes.horizontal_alignment=enums.HA_LEFT;z.text.attributes.vertical_alignment=enums.VA_CENTER;return z
updates=[];new=[];manifest=[];row_y=35
for row in range(0,len(groups),4):
 rowheight=0
 for col,(name,rs) in enumerate(groups[row:row+4]):
  gx=30+col*61;gy=row_y;cursor_x=0;cursor_y=0;shelf_h=0;members=[];placements={}
  # Large components first make compact, readable blocks; exact electrical placement is deferred.
  ordered=sorted(rs.split(),key=lambda ref:-(bounds[ref][3]-bounds[ref][1]))
  for ref in ordered:
   x0,y0,x1,y1=bounds[ref];w=max(x1-x0,2)+2;h=max(y1-y0,1.5)+4
   if cursor_x+w>54 and cursor_x>0:cursor_x=0;cursor_y+=shelf_h;shelf_h=0
   f=clone(fs[ref]);nx=gx+2+cursor_x-x0;ny=gy+7+cursor_y-y0;ox,oy=xy(f.position);dx=round((nx-ox)*1e6);dy=round((ny-oy)*1e6)
   f.position.CopyFrom(v(nx,ny));f.locked=types.LS_UNLOCKED
   for field in [f.reference_field,f.value_field,f.datasheet_field,f.description_field]:shift(field,dx,dy)
   for child in f.definition.items:
    z=unpack(child);shift(z,dx,dy);child.Pack(z)
   rf=f.reference_field;rf.visible=True;rf.text.text.attributes.visible=True;rf.text.text.position.CopyFrom(v(gx+2+cursor_x+(x1-x0)/2,gy+7+cursor_y-1.1));rf.text.text.attributes.angle.value_degrees=0;rf.text.text.attributes.size.CopyFrom(v(1,1));rf.text.text.attributes.stroke_width.value_nm=150000
   f.value_field.visible=False;updates.append(f);members.append(f.id);placements[ref]=[nx,ny]
   cursor_x+=w;shelf_h=max(shelf_h,h)
  height=cursor_y+shelf_h+9;rowheight=max(rowheight,height)
  label=text_at(f'{row+col+1:02d}  {name}',gx+1,gy+2,1.0);new.append(label)
  box=board.BoardGraphicShape(id=uid(),layer=board.BL_Dwgs_User);box.shape.rectangle.top_left.CopyFrom(v(gx,gy));box.shape.rectangle.bottom_right.CopyFrom(v(gx+58,gy+height));box.shape.attributes.stroke.width.value_nm=150000;new.append(box)
  group=board.Group(id=uid(),name=name,items=members+[label.id,box.id]);new.append(group)
  manifest.append({'name':name,'references':rs.split(),'positions_mm':placements,'planning_box_mm':[gx,gy,gx+58,gy+height]})
 row_y+=rowheight+8
new.append(text_at('PGR - functional groups only. Board size, placement and routing are NOT finalized.',30,25,1.5))
new.append(text_at('4 layers | L2 continuous GND | JLCPCB conservative rules | no production outline yet',30,29,1.1))
old=a.items(d,[enums.KOT_PCB_TRACE,enums.KOT_PCB_VIA,enums.KOT_PCB_ZONE,enums.KOT_PCB_SHAPE,enums.KOT_PCB_TEXT,enums.KOT_PCB_TEXTBOX,enums.KOT_PCB_DIMENSION,enums.KOT_PCB_GROUP])
old=list(old)
c=a.begin(d)
try:
 
 if old:a.delete(d,[i.id.value for i in old])
 remaining={f.id.value for f in a.items(d,[enums.KOT_PCB_FOOTPRINT])}
 a.update(d,[f for f in updates if f.id.value in remaining]);a.create(d,[f for f in updates if f.id.value not in remaining]+new);a.end(d,c,'Restart PCB as labeled functional groups from current schematic')
except:a.end(d,c,'Rollback grouping',drop=True);raise
a.save(d)
# Apply design minima and routing presets through the supported project-rule API.
rules=a.request(bc.GetBoardDesignRules(board=d),bc.BoardDesignRulesResponse).rules
for key,mm in {'min_clearance':.127,'min_track_width':.15,'min_via_annular_width':.15,'min_via_size':.6,'min_through_drill':.2,'copper_edge_clearance':.5,'hole_clearance':.2,'hole_to_hole_min':.25,'silk_clearance':.15,'min_silk_text_height':1.,'min_silk_text_thickness':.15}.items():getattr(rules.constraints,key).value_nm=round(mm*1e6)
del rules.predefined_sizes.tracks[:]
for mm in [.15,.2,.25,.3,.5,.75,1,1.5,2]:rules.predefined_sizes.tracks.add().width.value_nm=round(mm*1e6)
del rules.predefined_sizes.vias[:]
for dia,drill in [(.6,.3),(.7,.3),(.8,.4)]:
 z=rules.predefined_sizes.vias.add();z.diameter.value_nm=round(dia*1e6);z.drill.value_nm=round(drill*1e6)
rules.solder_mask_paste.mask_min_width.value_nm=100000
rules.solder_mask_paste.mask_expansion.value_nm=0
rules.via_protection.tent_front=True;rules.via_protection.tent_back=True
result=a.request(bc.SetBoardDesignRules(board=d,rules=rules),bc.BoardDesignRulesResponse)
a.save(d)
Path('build/layout-groups/groups.json').write_text(json.dumps(manifest,indent=2))
Path('build/layout-groups/rules.json').write_text(json_format.MessageToJson(result))
print('Saved',len(updates),'footprints in',len(groups),'groups; removed',len(old),'old board items')
a.request(project.CloseDocument(document=d),Empty)
