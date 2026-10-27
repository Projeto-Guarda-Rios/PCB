from pathlib import Path
import sys,math,json
import sexpdata as sx
from shapely.geometry import Polygon,LineString,Point,box
from shapely.ops import polygonize,unary_union
from shapely.prepared import prep
sys.path.insert(0,str(Path('build/reliability-fixes/ipc').resolve()))
import client;client.SOCKET='/tmp/pgr-placement.sock'
from client import *
a=API();d=a.open(types.DOCTYPE_PCB)
sub=lambda n,k:[x for x in n if isinstance(x,list) and x and str(x[0])==k]
r=sx.loads(Path('PGR.kicad_pcb').read_text());boxes={};regions={}
for f in sub(r,'footprint'):
 props={p[1]:p[2] for p in sub(f,'property')};ref=props['Reference'];at=sub(f,'at')[0];fx,fy=map(float,at[1:3]);ang=math.radians(float(at[3] if len(at)>3 else 0));pts=[];segments=[];polys=[]
 def world(x,y):return (round(fx+float(x)*math.cos(ang)+float(y)*math.sin(ang),6),round(fy-float(x)*math.sin(ang)+float(y)*math.cos(ang),6))
 def point(x,y):pts.append((fx+float(x)*math.cos(ang)+float(y)*math.sin(ang),fy-float(x)*math.sin(ang)+float(y)*math.cos(ang)))
 for shape in f:
  if not isinstance(shape,list) or not shape or str(shape[0]) not in ['fp_line','fp_rect','fp_circle','fp_arc','fp_poly']:continue
  layers=sub(shape,'layer')
  if not layers or layers[0][1]!='F.CrtYd':continue
  kind=str(shape[0])
  if kind=='fp_rect':
   st=sub(shape,'start')[0];en=sub(shape,'end')[0];polys.append(Polygon([world(st[1],st[2]),world(en[1],st[2]),world(en[1],en[2]),world(st[1],en[2])]))
  if kind=='fp_line':
   st=sub(shape,'start')[0];en=sub(shape,'end')[0];segments.append(LineString([world(st[1],st[2]),world(en[1],en[2])]))
  if str(shape[0])=='fp_circle':
   c=sub(shape,'center')[0];e=sub(shape,'end')[0];rad=math.hypot(float(e[1])-float(c[1]),float(e[2])-float(c[2]));polys.append(Point(*world(c[1],c[2])).buffer(rad));point(float(c[1])-rad,float(c[2])-rad);point(float(c[1])+rad,float(c[2])+rad)
  else:
   for key in ['start','end','mid']:
    for p in sub(shape,key):point(p[1],p[2])
   for chain in sub(shape,'pts'):
    for p in sub(chain,'xy'):point(p[1],p[2])
 polys+=list(polygonize(segments))
 if polys:regions[ref]=unary_union(polys)
 if pts:boxes[ref]=(min(p[0] for p in pts),min(p[1] for p in pts),max(p[0] for p in pts),max(p[1] for p in pts))
assert len(boxes)==165 and len(regions)==165,(len(boxes),len(regions))
# Candidate positions for U5 follow its body; the polygon still enforces its complete courtyard.
boxes['U5']=(99.75,50,118.25,70)
def intersects(a,b,gap=0):return a[0]<b[2]+gap and a[2]>b[0]-gap and a[1]<b[3]+gap and a[3]>b[1]-gap
def tb(text,x,y,size=1,angle=0):
 w=len(text)*size*.8+.4;h=size+.4
 if int(angle)%180:w,h=h,w
 return (x-w/2,y-h/2,x+w/2,y+h/2)
occupied=[]
for t in a.items(d,[enums.KOT_PCB_TEXT]):
 if t.layer==board.BL_F_SilkS:
  x,y=xy(t.text.position);occupied.append(tb(t.text.text,x,y,t.text.attributes.size.x_nm/1e6,t.text.attributes.angle.value_degrees))
fs={f.reference_field.text.text.text:f for f in a.items(d,[enums.KOT_PCB_FOOTPRINT])}
for ref in ['H1','H2','H3','H4']:
 f=fs[ref];x,y=xy(f.position);boxes[ref]=(x-4.5,y-4.5,x+4.5,y+4.5);regions[ref]=Point(x,y).buffer(4.5);occupied.append(tb(ref,*xy(f.reference_field.text.text.position)))
# Dense areas get their nearest free labeling space first.
def density(ref):
 x,y=xy(fs[ref].position);return sum(math.hypot(x-xy(g.position)[0],y-xy(g.position)[1])<9 for g in fs.values())
region_union=prep(unary_union(list(regions.values())).buffer(.1))
updated=[];failed=[];manifest={}
options={}
for ref in (k for k in fs if not k.startswith('H')):
 f=fs[ref];x0,y0,x1,y1=boxes[ref];cx=(x0+x1)/2;cy=(y0+y1)/2;w=len(ref)*.8+.4;h=1.4;ox,oy=xy(f.position);candidates=[]
 for extra in [0,.5,1,1.5,2,3,4,5,6,7,8]:
  for offset in [0,-.5,.5,-1,1,-2,2,-3,3]:
   for x,y in [(cx+offset,y0-h/2-.25-extra),(cx+offset,y1+h/2+.25+extra),(x0-w/2-.25-extra,cy+offset),(x1+w/2+.25+extra,cy+offset)]:
    b=tb(ref,x,y)
    if b[0]<50.4 or b[2]>159.6 or b[1]<50.4 or b[3]>134.6:continue
    if region_union.intersects(box(*b)) or any(intersects(b,bb,.15) for bb in occupied):continue
    candidates.append((math.hypot(x-ox,y-oy)+abs(offset)*.15,x,y,b))
 options[ref]=sorted(candidates)
# Place the most constrained labels first, recomputing choices after each placement.
while options:
 ref=min(options,key=lambda k:len(options[k]));f=fs[ref];candidates=options.pop(ref)
 if not candidates:failed.append(ref);continue
 _,x,y,b=candidates[0];f.reference_field.text.text.position.CopyFrom(v(x,y));f.reference_field.text.text.attributes.angle.value_degrees=0;f.reference_field.text.text.attributes.size.CopyFrom(v(1,1));f.reference_field.text.text.attributes.stroke_width.value_nm=150000;f.reference_field.visible=True;f.reference_field.text.text.attributes.visible=True;updated.append(f);occupied.append(b);manifest[ref]=[x,y]
 for k in options:options[k]=[c for c in options[k] if not intersects(c[3],b,.15)]
assert not failed,failed
a.update(d,updated);a.save(d)
Path('build/placement/reference-positions.json').write_text(json.dumps(manifest,indent=2));Path('build/placement/courtyards.json').write_text(json.dumps(boxes,indent=2));print('Placed',len(updated),'references outside component courtyards')
