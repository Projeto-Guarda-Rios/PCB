from pathlib import Path
import re,json,math
from shapely.geometry import Polygon,Point
s=Path('PGR.kicad_pcb').read_text();tokens=re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',s);stack=[];root=[];cur=root
for t in tokens:
 if t=='(':stack.append(cur);new=[];cur.append(new);cur=new
 elif t==')':cur=stack.pop()
 else:cur.append(json.loads(t) if t.startswith('"') else t)
b=root[0]
def xs(o,k):return [a for a in o if isinstance(a,list) and a and a[0]==k]
def x(o,k):return next(iter(xs(o,k)),[])
def net(o):return x(o,'net')[-1] if x(o,'net') else ''
conductors=[]
for via in xs(b,'via'):
 if net(via)=='GND':conductors.append(('via',float(x(via,'at')[1]),float(x(via,'at')[2]),['F.Cu','In1.Cu','In2.Cu','B.Cu']))
for fp in xs(b,'footprint'):
 at=x(fp,'at');fx,fy=map(float,at[1:3]);fa=math.radians(float(at[3]) if len(at)>3 else 0)
 ref=next(a[2] for a in xs(fp,'property') if a[1]=='Reference')
 for pad in xs(fp,'pad'):
  if net(pad)!='GND':continue
  a=x(pad,'at');px,py=map(float,a[1:3]);xx=fx+px*math.cos(fa)+py*math.sin(fa);yy=fy-px*math.sin(fa)+py*math.cos(fa)
  layers=x(pad,'layers')[1:]
  if '*.Cu' in layers:layers=['F.Cu','In1.Cu','In2.Cu','B.Cu']
  conductors.append((ref+'.'+pad[1],xx,yy,layers))
for zone in xs(b,'zone'):
 if x(zone,'net_name') and x(zone,'net_name')[1]!='GND':continue
 if not x(zone,'net_name') and net(zone)!='GND':continue
 print('ZONE',x(zone,'uuid'))
 for f in xs(zone,'filled_polygon'):
  layer=x(f,'layer')[1];coords=[tuple(map(float,a[1:])) for a in xs(x(f,'pts'),'xy')]
  try:p=Polygon(coords)
  except:continue
  if p.area<.001:continue
  matches=[c[0] for c in conductors if layer in c[3] and p.buffer(.001).covers(Point(c[1],c[2]))]
  if not matches:
   nearest=sorted((Point(c[1],c[2]).distance(p),c[0],c[1],c[2]) for c in conductors if layer in c[3])[:5]
   print('NO ANCHOR',layer,'area',round(p.area,3),'bounds',p.bounds,'centroid',p.centroid.x,p.centroid.y,'nearest',nearest)
