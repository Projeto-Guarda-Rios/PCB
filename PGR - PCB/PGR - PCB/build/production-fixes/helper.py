from pathlib import Path
import sys,uuid,math
sys.path.insert(0,str(Path('build/reliability-fixes/ipc').resolve()))
import client
client.SOCKET='/tmp/pgr-production-final.sock'
from client import *
api=API();d=api.open(types.DOCTYPE_SCHEMATIC)
items=api.items(d,[enums.KOT_SCH_SYMBOL,enums.KOT_SCH_LINE,enums.KOT_SCH_JUNCTION,enums.KOT_SCH_GLOBAL_LABEL,enums.KOT_SCH_LABEL,enums.KOT_SCH_NO_CONNECT,enums.KOT_SCH_TEXT,enums.KOT_SCH_SHAPE])
ss={x.reference_field.text.text:x for x in items if isinstance(x,sch.SchematicSymbolInstance)}
new=[];upd={};deletes=set();created={}
def uid():return types.KIID(value=str(uuid.uuid4()))
def pins(s):return [unpack(a.item) for a in s.definition.items if a.item.Is(sch.SchematicPin.DESCRIPTOR)]
def pin(s,n):return xy(next(p.position for p in pins(s) if p.number==str(n)))
def field(s,name,value,visible=False):
 f=next((x for x in s.user_fields if x.name==name),None)
 if f is None:f=s.user_fields.add(name=name)
 f.text.text=value;f.visible=visible;f.text.position.CopyFrom(s.position)
 return f
def clean(s):
 keep=[clone(a) for a in s.definition.items if not a.item.Is(sch.SchematicField.DESCRIPTOR)];del s.definition.items[:];s.definition.items.extend(keep)
 return s
def translate(s,p):
 old=xy(s.position);dx,dy=p[0]-old[0],p[1]-old[1];s.position.CopyFrom(v(*p))
 for f in [s.reference_field,s.value_field,s.footprint_field,s.datasheet_field,s.description_field,*s.user_fields]:
  a=xy(f.text.position);f.text.position.CopyFrom(v(a[0]+dx,a[1]+dy))
 for a in s.definition.items:
  if a.item.Is(sch.SchematicPin.DESCRIPTOR):
   z=unpack(a.item);p0=xy(z.position);z.position.CopyFrom(v(p0[0]+dx,p0[1]+dy));z.id.CopyFrom(uid());a.item.Pack(z)
 return s
def component(template,ref,p,value=None,footprint=None,mpn=None,manufacturer=None,datasheet=None,existing=False,unit=1):
 if not template.startswith('stock:') and template in ss:s=clone(ss[template])
 else:s=sch.SchematicSymbolInstance.FromString(Path(f'build/production-fixes/templates/{template.replace("stock:","")}_{unit}.pb').read_bytes())
 clean(s);translate(s,p);s.id.CopyFrom(ss[ref].id if existing else uid());s.path.CopyFrom(ss['U1'].path);s.lib_name='';s.reference_field.text.text=ref;s.attributes.do_not_populate=False
 if value is not None:s.value_field.text.text=value
 if footprint is not None:s.footprint_field.text.text=footprint
 if datasheet is not None:s.datasheet_field.text.text=datasheet
 if mpn:field(s,'MPN',mpn)
 if manufacturer:field(s,'Manufacturer',manufacturer)
 s.fields_autoplaced=False
 # Compact horizontal reference/value fields independent of the old template orientation.
 for f,y in [(s.reference_field,p[1]-10.16),(s.value_field,p[1]-7.62)]:
  f.visible=True;f.allow_auto_place=False;f.text.position.CopyFrom(v(p[0],y));f.text.attributes.angle.value_degrees=0;f.text.attributes.horizontal_alignment=enums.HA_CENTER;f.text.attributes.size.CopyFrom(v(1.27,1.27))
 if existing:upd[ref]=s
 else:new.append(s)
 created[ref]=s
 return s
def sym(ref):
 if ref not in upd:upd[ref]=clean(clone(ss[ref]))
 return upd[ref]
def wire(a,b):
 if a==b:return
 new.append(sch.SchematicLine(id=uid(),start=v(*a),end=v(*b),type=sch.SLT_WIRE))
def junction(p):new.append(sch.Junction(id=uid(),position=v(*p)))
def label(name,p,left=False):
 x=sch.LocalLabel(id=uid(),position=v(*p),spin_style=sch.SLSS_LEFT if left else sch.SLSS_RIGHT);x.text.text=name;x.text.position.CopyFrom(v(*p));x.text.attributes.size.CopyFrom(v(1.27,1.27));x.text.attributes.visible=True;new.append(x);return x
def net(s,n,name,offset=3.81):
 pp=next(z for z in pins(s) if z.number==str(n));a=xy(pp.position)
 # Pin orientation points into the body; extend the wire away from it.
 vec={sch.SPO_RIGHT:(-1,0),sch.SPO_LEFT:(1,0),sch.SPO_UP:(0,1),sch.SPO_DOWN:(0,-1)} if False else {1:(-1,0),2:(1,0),3:(0,1),4:(0,-1)}
 dx,dy=vec[pp.orientation];b=(a[0]+dx*offset,a[1]+dy*offset);wire(a,b);label(name,b,left=(dx<0));return b
pwr_counter=max([int(k[4:]) for k in ss if k.startswith('#PWR') and k[4:].isdigit()]+[99])
def ground(p):
 global pwr_counter
 pwr_counter+=1;n=pwr_counter
 s=component('#PWR055',f'#PWR{n}',p);s.value_field.visible=True;s.reference_field.visible=False
 # Power fields are anchored close to their one pin; no component-style 10mm offset.
 s.value_field.text.position.CopyFrom(v(p[0],p[1]+3.81));s.value_field.text.attributes.size.CopyFrom(v(1.0,1.0));s.value_field.text.attributes.horizontal_alignment=enums.HA_CENTER
 return s
def gnd(s,n):
 p=pin(s,n);b=(p[0],p[1]+2.54);wire(p,b);ground(b)
def passive(ref,p,value,a,b,kind='R',footprint=None,mpn=None):
 temp={'R':'R25','C':'C10','L':'L1','D':'D2'}[kind]
 s=component(temp,ref,p,value,footprint=footprint,mpn=mpn,existing=ref in ss)
 # R25 and C10 are vertical; retain their orientations, except for L1 horizontal.
 for f,y in [(s.reference_field,p[1]-1.27),(s.value_field,p[1]+1.27)]:
  f.text.position.CopyFrom(v(p[0]+2.54,y));f.text.attributes.horizontal_alignment=enums.HA_LEFT;f.text.attributes.size.CopyFrom(v(1.0,1.0))
 for n,name in [('1',a),('2',b)]:
  if name is None:continue
  if name=='GND':gnd(s,n)
  else:net(s,n,name,2.54)
 return s
def text(msg,p,size=1.27):
 t=sch.SchematicText(id=uid());t.text.text=msg;t.text.position.CopyFrom(v(*p));t.text.attributes.size.CopyFrom(v(size,size));t.text.attributes.visible=True;t.text.attributes.multiline=True;t.text.attributes.horizontal_alignment=enums.HA_LEFT;t.text.attributes.vertical_alignment=enums.VA_TOP;new.append(t)
def block(title,x,y,w=130,h=70):
 z=sch.SchematicGraphicShape(id=uid());z.shape.rectangle.top_left.CopyFrom(v(x,y));z.shape.rectangle.bottom_right.CopyFrom(v(x+w,y+h));z.shape.attributes.stroke.width.value_nm=254000;new.append(z);text(title,(x+2.54,y+2.54),1.8)
def remove_at(p):
 for x in items:
  if isinstance(x,sch.SchematicLine) and p in [xy(x.start),xy(x.end)]:deletes.add(x.id.value)
  elif isinstance(x,(sch.LocalLabel,sch.GlobalLabel,sch.NoConnectMarker,sch.Junction)) and xy(x.position)==p:deletes.add(x.id.value)
def commit(message):
 c=api.begin(d)
 try:
  if deletes:api.delete(d,list(deletes))
  if upd:api.update(d,list(upd.values()))
  if new:api.create(d,new)
  api.end(d,c,message)
 except:
  api.end(d,c,'Rollback '+message,drop=True);raise
 api.save(d);print('Saved:',message,'updated',len(upd),'created',len(new),'deleted',len(deletes))
