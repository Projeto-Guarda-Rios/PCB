from pathlib import Path
import sys,sexpdata as sx
sys.path.insert(0,str(Path('build/reliability-fixes/ipc').resolve()));import client
client.SOCKET='/tmp/pgr-label-style.sock'
from client import *
a=API();d=a.open(types.DOCTYPE_SCHEMATIC);a.request(project.CloseDocument(document=d),Empty)
p=Path('PGR.kicad_sch');r=sx.loads(p.read_text());sub=lambda n,k:[x for x in n if isinstance(x,list) and x and str(x[0])==k];ch=lambda n,k:sub(n,k)[0]
for n in sub(r,'symbol'):
 ps={f[1]:f for f in sub(n,'property')};ref=ps['Reference'][2]
 if ref in ['U13','U14']:
  x=62.23 if ref=='U13' else 118.11
  ch(ps['Reference'],'at')[1:3]=[x,341.63];ch(ps['Value'],'at')[1:3]=[x,344.17]
for n in sub(r,'rectangle'):
 st=ch(n,'start');en=ch(n,'end')
 if abs(st[1]-20.32)<.001 and abs(st[2]-330.2)<.001:en[2]=403.86
p.write_text(sx.dumps(r));d=a.open(types.DOCTYPE_SCHEMATIC);a.save(d)
