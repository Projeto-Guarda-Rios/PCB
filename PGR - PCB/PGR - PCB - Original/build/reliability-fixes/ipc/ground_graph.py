from pathlib import Path
import re,json,math,collections
from shapely.geometry import Polygon,Point,LineString,box
from shapely.affinity import rotate,translate
from shapely.strtree import STRtree
s=Path('PGR.kicad_pcb').read_text();tokens=re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',s);stack=[];root=[];cur=root
for t in tokens:
 if t=='(':stack.append(cur);new=[];cur.append(new);cur=new
 elif t==')':cur=stack.pop()
 else:cur.append(json.loads(t) if t.startswith('"') else t)
b=root[0]
def xs(o,k):return [a for a in o if isinstance(a,list) and a and a[0]==k]
def x(o,k):return next(iter(xs(o,k)),[])
def net(o):return x(o,'net')[-1] if x(o,'net') else ''
layers=['F.Cu','In1.Cu','In2.Cu','B.Cu'];geoms=[];meta=[];physical=collections.defaultdict(list)
def add(g,layer,key):
 if not g.is_valid:g=g.buffer(0)
 if not g.is_empty:physical[key].append(len(geoms));geoms.append(g);meta.append((layer,key,g.bounds))
for i,z in enumerate(xs(b,'zone')):
 if x(z,'net_name') and x(z,'net_name')[1]!='GND':continue
 if not x(z,'net_name') and net(z)!='GND':continue
 for j,f in enumerate(xs(z,'filled_polygon')):
  layer=x(f,'layer')[1];coords=[tuple(map(float,a[1:])) for a in xs(x(f,'pts'),'xy')]
  add(Polygon(coords),layer,('zone',i,j))
for vi in xs(b,'via'):
 if net(vi)!='GND':continue
 a=x(vi,'at');px,py=map(float,a[1:3]);g=Point(px,py).buffer(float(x(vi,'size')[1])/2,resolution=16)
 for l in layers:add(g,l,('via',x(vi,'uuid')[1],px,py))
for t in xs(b,'segment'):
 if net(t)!='GND':continue
 a=x(t,'start');bb=x(t,'end');g=LineString([tuple(map(float,a[1:3])),tuple(map(float,bb[1:3]))]).buffer(float(x(t,'width')[1])/2,resolution=16)
 add(g,x(t,'layer')[1],('track',x(t,'uuid')[1]))
for fp in xs(b,'footprint'):
 at=x(fp,'at');fx,fy=map(float,at[1:3]);fa=math.radians(float(at[3]) if len(at)>3 else 0)
 ref=next(a[2] for a in xs(fp,'property') if a[1]=='Reference')
 for p in xs(fp,'pad'):
  if net(p)!='GND':continue
  a=x(p,'at');px,py=map(float,a[1:3]);xx=fx+px*math.cos(fa)+py*math.sin(fa);yy=fy-px*math.sin(fa)+py*math.cos(fa);ang=float(a[3]) if len(a)>3 else 0
  w,h=map(float,x(p,'size')[1:3]);r=min(w,h)/2
  if p[3]=='circle':g=Point(0,0).buffer(r,resolution=16)
  elif p[3]=='oval':g=box(-w/2+r,-h/2+r,w/2-r,h/2-r).buffer(r,resolution=16) if w!=h else Point(0,0).buffer(r,resolution=16)
  elif p[3]=='roundrect':
   r=min(w,h)*float(x(p,'roundrect_rratio')[1]);g=box(-w/2+r,-h/2+r,w/2-r,h/2-r).buffer(r,resolution=16)
  else:g=box(-w/2,-h/2,w/2,h/2)
  g=translate(rotate(g,-ang,origin=(0,0)),xx,yy);ls=x(p,'layers')[1:]
  if '*.Cu' in ls:ls=layers
  for l in ls:
   if l in layers:add(g,l,('pad',ref,p[1],x(p,'uuid')[1],xx,yy))
parent=list(range(len(geoms)))
def find(a):
 while parent[a]!=a:parent[a]=parent[parent[a]];a=parent[a]
 return a
def union(a,b):parent[find(a)]=find(b)
for ids in physical.values():
 for k in ids[1:]:union(ids[0],k)
for layer in layers:
 ids=[i for i,m in enumerate(meta) if m[0]==layer];gs=[geoms[i] for i in ids];tree=STRtree(gs)
 pairs=tree.query(gs,predicate='intersects')
 for a,b in zip(*pairs):union(ids[a],ids[b])
groups=collections.defaultdict(list)
for i in range(len(geoms)):groups[find(i)].append(i)
print('GROUND CONNECTED COMPONENTS',len(groups))
for g in sorted(groups.values(),key=len):
 print('COMPONENT size',len(g),'area',sum(geoms[i].area for i in g))
 for i in g[:30]:print(meta[i])
