from pathlib import Path
import sys,json,uuid
r=Path.cwd();o=r/'build/larger-controls';sys.path.insert(0,str(r/'build/reliability-fixes/ipc'))
import client;client.SOCKET='/tmp/pgr-larger-controls.sock'
from client import *
a=API();bd=a.open(types.DOCTYPE_PCB);sd=a.open(types.DOCTYPE_SCHEMATIC)
fs=a.items(bd,[enums.KOT_PCB_FOOTPRINT]);ss=a.items(sd,[enums.KOT_SCH_SYMBOL]);lines=a.items(sd,[enums.KOT_SCH_LINE]);fmap={f.reference_field.text.text.text:f for f in fs};smap={s.reference_field.text.text:s for s in ss}
(o/'before-board-items.json').write_text(json.dumps([json_format.MessageToDict(f,preserving_proto_field_name=True) for f in fs],indent=2))
client.SOCKET='/tmp/pgr-larger-fixture.sock';fa=API();fbd=fa.request(editor.GetOpenDocuments(type=types.DOCTYPE_PCB),editor.GetOpenDocumentsResponse).documents[0];ft={f.reference_field.text.text.text:f for f in fa.items(fbd,[enums.KOT_PCB_FOOTPRINT])};docs=fa.request(editor.GetOpenDocuments(type=types.DOCTYPE_SCHEMATIC),editor.GetOpenDocumentsResponse);fsd=docs.documents[0] if docs.documents else fa.request(project.OpenDocument(type=types.DOCTYPE_SCHEMATIC,path=str(o/'fixture.kicad_sch')),project.OpenDocumentResponse).document;st=fa.items(fsd,[enums.KOT_SCH_SYMBOL])[0]
parts={ref:{'fp':'Button_Switch_SMD:SW_SPST_Omron_B3FS-100xP','mpn':'B3FS-1002P','mfr':'Omron','lcsc':'C87038','ds':'https://components.omron.com/sg-en/products/switches/B3FS','desc':'6x6mm SMT normally-open tactile pushbutton, 3.1mm high, 1.47N','pos':pos} for ref,pos in [('SW1',(126,173)),('SW2',(142,173))]}
parts['SW4']={'fp':'PGR-FootPrints:SW_Slide_CK_1101M2S3CBE2','mpn':'1101M2S3CBE2','mfr':'C&K / Littelfuse','lcsc':'C2798505','ds':'https://www.littelfuse.com/assetdocs/littelfuse-ck-slide-1000-series-datasheet?assetguid=68a2b41e-19a4-4cf4-821b-aca78a430f00','desc':'Top-actuated SPDT slide switch used as battery enable; gold dry-circuit contacts; 12.7x6.6mm body; 5.08mm protruding actuator','pos':(30,58)}
def sfield(z,name,val):
 f=next((f for f in z.user_fields if f.name==name),None)
 if f is None:f=z.user_fields.add();f.CopyFrom(z.datasheet_field);f.name=name
 f.text.text=val;f.visible=False;f.text.attributes.visible=False
snew=[]
for ref,p in parts.items():
 z=clone(smap[ref]);z.footprint_field.text.text=p['fp'];z.datasheet_field.text.text=p['ds'];z.description_field.text.text=p['desc']
 if ref=='SW4':z.definition.CopyFrom(st.definition);z.lib_name=st.lib_name;z.transform.CopyFrom(st.transform)
 for name,val in [('MPN',p['mpn']),('Manufacturer',p['mfr']),('LCSC',p['lcsc'])]:sfield(z,name,val)
 if ref=='SW4':
  sfield(z,'Rating','Gold low-level/dry-circuit contacts, 0.4VA max at 20V; control current <40uA')
  sfield(z,'Assembly','JLCPCB preorder C2798505; through-hole; pins 1-2 used, pin 3 intentionally NC')
 snew.append(z)
# SPDT rotated 180 degrees keeps common pin 2 at the old right-hand endpoint.
# Its pin 1 is 2.54 mm below the old left-hand endpoint.
w=clone(next(w for w in lines if w.id.value=='ae9250e5-d28f-4208-8085-eb167be6e428'));w.start.CopyFrom(v(537.21,163.83))
created=[]
for p,q in [((537.21,163.83),(537.21,166.37)),((537.21,166.37),(539.75,166.37))]:
 z=clone(w);z.id.value=str(uuid.uuid4());z.start.CopyFrom(v(*p));z.end.CopyFrom(v(*q));created.append(z)
nc=sch.NoConnectMarker(id=types.KIID(value=str(uuid.uuid4())),position=v(539.75,161.29));created.append(nc)
c=a.begin(sd);a.update(sd,snew+[w]);a.create(sd,created);a.end(sd,c,'Fit larger BOOT/RESET buttons and gold-contact battery slide switch');a.save(sd);a.request(project.CloseDocument(document=sd),Empty)
# Replace footprints through IPC, preserving references, paths, and all other items.
coord_names={'position','start','mid','end','center','top_left','bottom_right','point','control1','control2','control_1','control_2','radius_point'}
def translate(m,dx,dy):
 for field,val in m.ListFields():
  if field.message_type is None:continue
  for z in (val if field.label==field.LABEL_REPEATED else [val]):
   if field.message_type.full_name==types.Vector2.DESCRIPTOR.full_name and field.name in coord_names:
    x,y=xy(z);z.CopyFrom(v(x+dx,y+dy))
   else:translate(z,dx,dy)
updates=[]
for ref,p in parts.items():
 old=fmap[ref];t=ft[ref];new=clone(old);new.definition.CopyFrom(t.definition);new.orientation.value_degrees=0;new.position.CopyFrom(v(*p['pos']));new.attributes.mounting_style=board.FMS_THROUGH_HOLE if ref=='SW4' else board.FMS_SMD
 tx,ty=xy(t.position);nx,ny=p['pos']
 for child in new.definition.items:
  z=unpack(child);translate(z,nx-tx,ny-ty)
  if hasattr(z,'id') and hasattr(z.id,'value'):z.id.value=str(uuid.uuid4())
  if hasattr(z,'parent'):z.parent.value=new.id.value
  child.Pack(z)
 for attr,txt in [('value_field',old.value_field.text.text.text),('datasheet_field',p['ds']),('description_field',p['desc'])]:getattr(new,attr).text.text.text=txt
 for attr,delta in [('reference_field',-5.5),('value_field',5.5),('datasheet_field',0),('description_field',0)]:getattr(new,attr).text.text.position.CopyFrom(v(nx,ny+delta))
 for name,val in [('MPN',p['mpn']),('Manufacturer',p['mfr']),('LCSC',p['lcsc'])]:
  fld=clone(new.datasheet_field);fld.id.id=0;fld.name=name;fld.visible=False;fld.text.id.value=str(uuid.uuid4());fld.text.parent.value=new.id.value;fld.text.text.text=val;fld.text.text.attributes.visible=False;new.definition.items.add().Pack(fld)
 updates.append(new)
c=a.begin(bd);a.update(bd,updates);a.end(bd,c,'Install larger controls with finger clearance');a.save(bd)
after=a.items(bd,[enums.KOT_PCB_FOOTPRINT]);m={f.id.value:f for f in after}
for f in fs:
 if f.reference_field.text.text.text not in parts:assert f.SerializeToString()==m[f.id.value].SerializeToString(),f.reference_field.text.text.text
(o/'parts.json').write_text(json.dumps(parts,indent=2));print('Saved 3 replacements; other',len(fs)-3,'footprints unchanged')
a.request(project.CloseDocument(document=bd),Empty)
fa.request(project.CloseDocument(document=fsd),Empty);fa.request(project.CloseDocument(document=fbd),Empty)
