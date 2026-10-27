from pathlib import Path
import sys,re,shutil
sys.path.insert(0,str(Path('build/reliability-fixes/ipc').resolve()))
import client
client.SOCKET='/tmp/pgr-production-fixes.sock'
from client import *
api=API();d=api.open(types.DOCTYPE_SCHEMATIC);api.request(project.CloseDocument(document=d),Empty)
p=Path('PGR.kicad_sch');shutil.copy2(p,'build/production-fixes/backups/before-sheet-layout.kicad_sch');s=p.read_text()
# Document/page geometry is edited natively because this IPC revision has no page-settings command.
def end_form(a):
 depth=0;quote=False;esc=False
 for i in range(a,len(s)):
  c=s[i]
  if quote:
   if esc:esc=False
   elif c=='\\':esc=True
   elif c=='"':quote=False
  elif c=='"':quote=True
  elif c=='(':depth+=1
  elif c==')':
   depth-=1
   if depth==0:return i+1
 raise ValueError(a)
pat=r'\((at|xy|start|end) (-?\d+(?:\.\d+)?) (-?\d+(?:\.\d+)?)'
changes=[]
for m in re.finditer(r'^\t\((symbol|wire|junction|no_connect|label|global_label|text|rectangle|polyline)\b',s,re.M):
 a=m.start();b=end_form(s.index('(',a));t=s[a:b];coords=list(re.finditer(pat,t))
 if not coords:continue
 y=float(coords[0].group(3));dx,dy=(0,255.27) if y<0 else (279.4,20.32)
 def f(z):return '('+z[1]+' '+format(float(z[2])+dx,'.6f').rstrip('0').rstrip('.')+' '+format(float(z[3])+dy,'.6f').rstrip('0').rstrip('.')
 changes.append((a,b,re.sub(pat,f,t)))
for a,b,t in reversed(changes):s=s[:a]+t+s[b:]
s=s.replace('(paper "A4")','(paper "A2")');p.write_text(s)
d=api.open(types.DOCTYPE_SCHEMATIC);print('Arranged',len(changes),'items on an A2 sheet')
