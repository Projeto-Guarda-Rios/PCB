from pathlib import Path
import sys,copy,uuid,sexpdata as sx
sys.path.insert(0,str(Path('build/reliability-fixes/ipc').resolve()));import client
client.SOCKET='/tmp/pgr-label-style.sock'
from client import *
a=API();d=a.open(types.DOCTYPE_SCHEMATIC);a.request(project.CloseDocument(document=d),Empty)
p=Path('PGR.kicad_sch');r=sx.loads(p.read_text());S=sx.Symbol
sub=lambda n,k:[x for x in n if isinstance(x,list) and x and str(x[0])==k]
ch=lambda n,k:sub(n,k)[0]
def move_symbol(n,dx,dy):
 at=ch(n,'at');at[1]+=dx;at[2]+=dy
 for f in sub(n,'property'):
  at=ch(f,'at');at[1]+=dx;at[2]+=dy
for ref,ox,nx in [('C25',25.4,99.06),('C26',66.04,139.7)]:
 dx=nx-ox;dy=38.1
 for n in sub(r,'symbol'):
  ps={f[1]:f[2] for f in sub(n,'property')};at=ch(n,'at')
  if ps['Reference']==ref or ps['Reference'].startswith('#PWR') and abs(at[1]-ox)<.001 and abs(at[2]-359.41)<.001:move_symbol(n,dx,dy)
 for n in sub(r,'wire'):
  pts=ch(n,'pts')[1:]
  if all(abs(pt[1]-ox)<.001 for pt in pts) and all(346.7<=pt[2]<=359.42 for pt in pts):
   for pt in pts:pt[1]=round(pt[1]+dx,2);pt[2]=round(pt[2]+dy,2)
 for n in sub(r,'global_label'):
  at=ch(n,'at')
  if abs(at[1]-ox)<.001 and abs(at[2]-346.71)<.001:
   at[1]=nx;at[2]=384.81
for n in sub(r,'global_label'):
 at=ch(n,'at')
 if abs(at[1]-30.48)<.001 and 260<at[2]<320:
  at[3]=180;ch(ch(n,'effects'),'justify')[1]=S('right')
for n in sub(r,'rectangle'):
 st=ch(n,'start');en=ch(n,'end')
 if abs(st[1]-20.32)<.001 and abs(st[2]-254)<.001:st[1]=12.7;en[1]=158.75
# U14 and Q8 share TEMP_OK. Replace facing overlapping tags with one visible stub.
remove=[];template=None
for n in sub(r,'global_label'):
 at=ch(n,'at')
 if n[1]=='TEMP_OK' and abs(at[2]-353.06)<.001 and any(abs(at[1]-x)<.001 for x in [115.57,121.92]):remove.append(n);template=copy.deepcopy(n)
for n in remove:r.remove(n)
def wire(x1,y1,x2,y2):return [S('wire'),[S('pts'),[S('xy'),x1,y1],[S('xy'),x2,y2]],[S('stroke'),[S('width'),0],[S('type'),S('default')]],[S('uuid'),str(uuid.uuid4())]]
r.extend([wire(115.57,353.06,121.92,353.06),wire(118.11,353.06,118.11,347.98),[S('junction'),[S('at'),118.11,353.06],[S('diameter'),0],[S('color'),0,0,0,0],[S('uuid'),str(uuid.uuid4())]]])
at=ch(template,'at');at[1:]=[118.11,347.98,0];ch(ch(template,'effects'),'justify')[1]=S('left');ch(template,'uuid')[1]=str(uuid.uuid4());r.append(template)
p.write_text(sx.dumps(r));d=a.open(types.DOCTYPE_SCHEMATIC);a.save(d)
