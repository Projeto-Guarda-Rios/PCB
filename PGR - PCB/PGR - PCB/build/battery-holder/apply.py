from pathlib import Path
import sys,json,uuid
sys.path.insert(0,str(Path('build/reliability-fixes/ipc').resolve()))
import client;client.SOCKET='/tmp/pgr-holder.sock'
from client import *
r=Path.cwd();out=r/'build/battery-holder';a=API();bd=a.open(types.DOCTYPE_PCB);sd=a.open(types.DOCTYPE_SCHEMATIC)
fs=a.items(bd,[enums.KOT_PCB_FOOTPRINT]);symbols=a.items(sd,[enums.KOT_SCH_SYMBOL]);old=next(f for f in fs if f.reference_field.text.text.text=='BT1');symbol=next(s for s in symbols if s.reference_field.text.text=='BT1')
(out/'before-items.json').write_text(json.dumps([json_format.MessageToDict(f,preserving_proto_field_name=True) for f in fs],indent=2))
client.SOCKET='/tmp/pgr-holder-fixture.sock';fixture_api=API();fd=fixture_api.request(editor.GetOpenDocuments(type=types.DOCTYPE_PCB),editor.GetOpenDocumentsResponse).documents[0]
template=fixture_api.items(fd,[enums.KOT_PCB_FOOTPRINT])[0];fixture_api.request(project.CloseDocument(document=fd),Empty)
fp='Battery:BatteryHolder_Keystone_1042_1x18650';datasheet='https://www.keyelco.com/product.cfm/product_id/918';description='Keystone 1042 PCB-mounted single 18650 Li-ion cell holder, SMT; 4.2V full charge'
symbol.value_field.text.text='1042';symbol.footprint_field.text.text=fp;symbol.datasheet_field.text.text=datasheet;symbol.description_field.text.text=description
for name,val in [('MPN','1042'),('Manufacturer','Keystone'),('LCSC','C5249310')]:
 fld=next((f for f in symbol.user_fields if f.name==name),None)
 if fld is None:fld=symbol.user_fields.add();fld.CopyFrom(symbol.datasheet_field);fld.name=name
 fld.text.text=val;fld.visible=False;fld.text.attributes.visible=False
c=a.begin(sd);a.update(sd,[symbol]);a.end(sd,c,'Replace external battery connector with PCB 18650 holder');a.save(sd);a.request(project.CloseDocument(document=sd),Empty)
new=clone(old);new.definition.CopyFrom(template.definition);new.orientation.value_degrees=0;new.attributes.mounting_style=board.FMS_SMD
# Put the larger holder below all current component groups, without moving other items.
ny=round(max(xy(f.position)[1] for f in fs)+35,2);nx=80.;new.position.CopyFrom(v(nx,ny));ox,oy=xy(template.position)
coord_names={'position','start','mid','end','center','top_left','bottom_right','point','control1','control2','control_1','control_2','radius_point'}
def translate(m):
 for field,val in m.ListFields():
  if field.message_type is None:continue
  for z in (val if field.label==field.LABEL_REPEATED else [val]):
   if field.message_type.full_name==types.Vector2.DESCRIPTOR.full_name and field.name in coord_names:
    x,y=xy(z);z.CopyFrom(v(x-ox+nx,y-oy+ny))
   else:translate(z)
for child in new.definition.items:
 z=unpack(child);translate(z)
 if hasattr(z,'parent'):z.parent.value=new.id.value
 child.Pack(z)
for attr,txt in [('value_field','1042'),('datasheet_field',datasheet),('description_field',description)]:getattr(new,attr).text.text.text=txt
for attr,delta in [('reference_field',-12),('value_field',12),('datasheet_field',0),('description_field',0)]:
 fld=getattr(new,attr);fld.text.text.position.CopyFrom(v(nx,ny+delta))
for name,val in [('MPN','1042'),('Manufacturer','Keystone'),('LCSC','C5249310')]:
 fld=clone(new.datasheet_field);fld.id.id=0;fld.name=name;fld.visible=False;fld.text.id.value=str(uuid.uuid4());fld.text.parent.value=new.id.value;fld.text.text.text=val;fld.text.text.attributes.visible=False;new.definition.items.add().Pack(fld)
c=a.begin(bd);a.update(bd,[new]);a.end(bd,c,'Install BT1 single 18650 holder below component groups');a.save(bd)
after=a.items(bd,[enums.KOT_PCB_FOOTPRINT]);m={f.id.value:f for f in after};assert len(fs)==len(after)
for f in fs:
 if f.id.value!=old.id.value:assert f.SerializeToString()==m[f.id.value].SerializeToString(),f.reference_field.text.text.text
(out/'placement.json').write_text(json.dumps({'BT1_center_mm':[nx,ny],'other_footprints_unchanged':len(fs)-1,'positive_net':'CELL_P','negative_net':'BMS_NEG'},indent=2));a.request(project.CloseDocument(document=bd),Empty);print('Saved holder and metadata; other footprints unchanged. Center',nx,ny)
