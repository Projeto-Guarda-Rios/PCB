from pathlib import Path
import sys,sexpdata as sx
sys.path.insert(0,str(Path('build/reliability-fixes/ipc').resolve()));import client
client.SOCKET='/tmp/pgr-label-style.sock'
from client import *
a=API();d=a.open(types.DOCTYPE_SCHEMATIC);a.request(project.CloseDocument(document=d),Empty)
p=Path('PGR.kicad_sch');r=sx.loads(p.read_text());S=sx.Symbol
sub=lambda n,k:[x for x in n if isinstance(x,list) and x and str(x[0])==k]
ch=lambda n,k:sub(n,k)[0]
lines=[ch(n,'pts')[1:] for n in sub(r,'wire')];symbols=sub(r,'symbol');count=0
for n in sub(r,'global_label'):
 at=ch(n,'at');x,y=at[1:3];angle=None
 for ends in lines:
  for i in [0,1]:
   u,v=ends[i],ends[1-i]
   if abs(u[1]-x)<.001 and abs(u[2]-y)<.001 and abs(v[2]-y)<.001 and abs(v[1]-x)>.001:angle=180 if v[1]>x else 0;break
  if angle is not None:break
 if angle is None:
  # Labels directly on left/right IC pins: use nearby component center to face outward.
  nearby=[]
  for z in symbols:
   pos=ch(z,'at');ps={f[1]:f for f in sub(z,'property')};ref=ps['Reference'][2]
   if ref.startswith(('U','IC','Q','J')):
    dx=pos[1]-x;dy=pos[2]-y
    if abs(dx)<=20.32 and abs(dy)<=35.56 and abs(dx)>3.5:nearby.append((dx*dx+dy*dy,dx))
  if nearby and min(nearby)[0]<270:angle=180 if min(nearby)[1]>0 else 0
 # Vertical passive stubs face left for label positions left of the corresponding body.
 if n[1]=='PWR_OUT' and abs(x-62.23)<.01 and abs(y-266.7)<.01:angle=180
 if angle is None:angle=at[3]
 if angle!=at[3]:count+=1
 at[3]=angle;eff=ch(n,'effects');just=sub(eff,'justify')
 if just:just[0][1:]=[S('right' if angle==180 else 'left')]
for n in symbols:
 ps={x[1]:x for x in sub(n,'property')}
 if ps['Reference'][2]=='U3':
  ch(ps['Reference'],'at')[1:3]=[90.17,271.78];ch(ps['Value'],'at')[1:3]=[90.17,274.32]
p.write_text(sx.dumps(r));d=a.open(types.DOCTYPE_SCHEMATIC);a.save(d);print('Oriented',count,'label tags outwards')
