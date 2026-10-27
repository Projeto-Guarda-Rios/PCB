from helper import api,d,project,Empty,types
from pathlib import Path
import sexpdata as sx
api.request(project.CloseDocument(document=d),Empty)
p=Path('PGR.kicad_sch');r=sx.loads(p.read_text())
def sub(n,k):return [a for a in n if isinstance(a,list) and a and str(a[0])==k]
def ch(n,k):return sub(n,k)[0]
xs=[]
for n in sub(r,'symbol'):
 ps={a[1]:a for a in sub(n,'property')}
 if ps['Reference'][2].startswith('TP'):
  at=ch(n,'at');xs.append(at[1]);at[2]-=6.35
  for f in sub(n,'property'):ch(f,'at')[2]-=6.35
for n in sub(r,'wire'):
 pts=ch(n,'pts')[1:]
 if all(abs(pt[1]-xs[0])<0.01 for pt in pts):pass
 if pts[0][1] in xs and pts[0][2] in [229.87,232.41] and pts[1][1]==pts[0][1]:
  for pt in pts:pt[2]=round(pt[2]-6.35,2)
 # J14 mirrored symbol: draw stubs outwards to the right.
 if pts[0][1]==256.54 and pts[0][2] in [191.77,194.31,196.85,189.23]:pts[1][1]=260.35
for n in sub(r,'label'):
 at=ch(n,'at')
 if at[1] in xs and at[2]==232.41:at[2]=226.06
 if at[1]==252.73 and at[2] in [191.77,194.31,196.85,189.23]:at[1]=260.35;at[3]=0
p.write_text(sx.dumps(r));d=api.open(types.DOCTYPE_SCHEMATIC);api.save(d)
