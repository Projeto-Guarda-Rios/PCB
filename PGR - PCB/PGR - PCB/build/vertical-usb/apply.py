from pathlib import Path
import sys,json,copy,uuid,math,shutil,hashlib
import sexpdata as sx
sys.path.insert(0,str(Path('build/reliability-fixes/ipc').resolve()))
import client;client.SOCKET='/tmp/pgr-vertical-usb.sock'
from client import *
root=Path.cwd();out=root/'build/vertical-usb';part=json.loads((out/'selected-part.json').read_text());lib=root/'PGR-FootPrints.pretty'/('USB_C_GCT_USB4145_03_0230_C_Vertical.kicad_mod')
sub=lambda n,k:[x for x in n if isinstance(x,list) and x and str(x[0])==k]
# Move the supplied pin-1 marker clear of the grounded mounting pad.
l=sx.loads(lib.read_text())
for cir in sub(l,'fp_circle'):
 if sub(cir,'layer')[0][1]=='F.SilkS':
  sub(cir,'center')[0][1:]=[-3,-2.6];sub(cir,'end')[0][1:]=[-2.88,-2.6];sub(cir,'width')[0][1]=.12
lib.write_text(sx.dumps(l)+'\n')
a=API();bd=a.open(types.DOCTYPE_PCB);sd=a.open(types.DOCTYPE_SCHEMATIC)
for name in ['PGR.kicad_pcb','PGR.kicad_sch','PGR.kicad_pro','PGR.kicad_pcb.backplane.json','PGR.kicad_sch.backplane.json']:
 p=root/name
 if p.exists():shutil.copy2(p,out/'backups'/('pre-edit-'+name))
before_board=a.items(bd,[enums.KOT_PCB_FOOTPRINT]);before_sch=a.items(sd,[enums.KOT_SCH_SYMBOL])
(out/'board-items-before.json').write_text(json.dumps([json_format.MessageToDict(f,preserving_proto_field_name=True) for f in before_board],indent=2))
old=next(f for f in before_board if f.reference_field.text.text.text=='J9');symbol=next(f for f in before_sch if f.reference_field.text.text=='J9')
# Change the BOM details in the source schematic, preserving its pins, location and wiring.
symbol.value_field.text.text=part['MPN'];symbol.footprint_field.text.text=part['Footprint'];symbol.datasheet_field.text.text=part['drawing']
symbol.description_field.text.text='Vertical USB-C USB2.0 receptacle, H7.46mm, 2.3mm grounded shell stakes'
for name,val in [('MPN',part['MPN']),('Manufacturer','GCT'),('LCSC',part['LCSC'])]:
 fld=next((f for f in symbol.user_fields if f.name==name),None)
 if fld is None:
  fld=symbol.user_fields.add();fld.CopyFrom(symbol.datasheet_field);fld.name=name
 fld.text.text=val;fld.visible=False;fld.text.attributes.visible=False
c=a.begin(sd)
try:a.update(sd,[symbol]);a.end(sd,c,'Select vertical USB-C GCT USB4145-03-0230-C for J9')
except:a.end(sd,c,'Rollback J9 part metadata',drop=True);raise
a.save(sd)
# Replace only J9's geometry, keeping its UUID, symbol association, anchor and orientation.
template=board.FootprintInstance();json_format.Parse((out/'fixture-footprint.json').read_text(),template)
new=clone(old);new.definition.CopyFrom(template.definition);new.attributes.mounting_style=board.FMS_SMD
new.value_field.text.text.text=part['MPN'];new.datasheet_field.text.text.text=part['drawing'];new.description_field.text.text.text=symbol.description_field.text.text
ox,oy=xy(template.position);nx,ny=xy(old.position);angle=old.orientation.value_degrees-template.orientation.value_degrees
coord_names={'position','start','mid','end','center','top_left','bottom_right','point','control1','control2','control_1','control_2','radius_point'}
def transform(m):
 c=math.cos(math.radians(angle));s=math.sin(math.radians(angle))
 for fd,val in m.ListFields():
  if fd.message_type is None:continue
  for z in (val if fd.label==fd.LABEL_REPEATED else [val]):
   if fd.message_type.full_name==types.Vector2.DESCRIPTOR.full_name and fd.name in coord_names:
    x=z.x_nm/1e6-ox;y=z.y_nm/1e6-oy;z.CopyFrom(v(nx+x*c+y*s,ny-x*s+y*c))
   elif fd.message_type.full_name==types.Angle.DESCRIPTOR.full_name and fd.name=='angle':z.value_degrees=(z.value_degrees+angle)%360
   else:transform(z)
for child in new.definition.items:
 z=unpack(child)
 if isinstance(z,board.BoardGraphicShape) and z.layer==board.BL_F_SilkS and z.shape.WhichOneof('geometry')=='circle':
  z.shape.circle.center.CopyFrom(v(7,5.4));z.shape.circle.radius_point.CopyFrom(v(7.12,5.4));z.shape.attributes.stroke.width.value_nm=120000
 transform(z)
 if hasattr(z,'parent'):z.parent.value=new.id.value
 child.Pack(z)
for name,val in [('MPN',part['MPN']),('Manufacturer','GCT'),('LCSC',part['LCSC'])]:
 fld=clone(new.datasheet_field);fld.id.id=0;fld.name=name;fld.visible=False;fld.text.id.value=str(uuid.uuid4());fld.text.parent.value=new.id.value;fld.text.text.text=val;fld.text.text.attributes.visible=False;fld.text.text.position.CopyFrom(new.position);new.definition.items.add().Pack(fld)
c=a.begin(bd)
try:a.update(bd,[new]);a.end(bd,c,'Replace J9 with verified vertical USB-C footprint; retain all placement')
except:a.end(bd,c,'Rollback J9 footprint replacement',drop=True);raise
a.save(bd)
after=a.items(bd,[enums.KOT_PCB_FOOTPRINT]);aftermap={f.id.value:f for f in after}
assert len(after)==len(before_board)
for f in before_board:
 if f.id.value!=old.id.value:assert f.SerializeToString()==aftermap[f.id.value].SerializeToString(),f.reference_field.text.text.text
actual=aftermap[old.id.value];assert actual.position==old.position and actual.orientation==old.orientation
assert actual.symbol_path==old.symbol_path
for d in [bd,sd]:a.request(project.CloseDocument(document=d),Empty)
print('Saved J9 schematic and PCB; all other footprints unchanged; J9 anchor and rotation retained')
