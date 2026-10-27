from pathlib import Path
import sys,sexpdata as sx
sys.path.insert(0,str(Path('build/reliability-fixes/ipc').resolve()));import client
client.SOCKET='/tmp/pgr-visible-restore.sock'
from client import *
a=API();d=a.open(types.DOCTYPE_SCHEMATIC);a.request(project.CloseDocument(document=d),Empty)
p=Path('PGR.kicad_sch');r=sx.loads(p.read_text());sub=lambda n,k:[z for z in n if isinstance(z,list) and z and str(z[0])==k];ch=lambda n,k:sub(n,k)[0]
for n in list(sub(r,'wire')):
 pts=ch(n,'pts')[1:];xy=[tuple(z[1:]) for z in pts]
 if set(xy)=={(340.36,358.14),(340.36,361.95)}:r.remove(n)
 if set(xy)=={(340.36,373.38),(340.36,369.57)}:
  for z in pts:z[1]=317.5
for n in list(sub(r,'global_label')):
 at=ch(n,'at')
 if n[1]=='BAT_PROTECTED' and at[1:3]==[340.36,361.95]:r.remove(n)
 if n[1]=='SOLAR_RAW' and at[1:3]==[340.36,369.57]:at[1]=317.5
p.write_text(sx.dumps(r));d=a.open(types.DOCTYPE_SCHEMATIC);a.save(d)
