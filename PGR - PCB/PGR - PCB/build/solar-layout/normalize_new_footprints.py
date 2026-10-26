"""Normalize the two new footprints to the installed library revision.
The older board templates use four line primitives per rectangle. KiCad 10's
library comparison treats that as a mismatch. Prove drawn segments and pad
geometry are identical before replacing only those graphics and the description.
"""
from pathlib import Path
import re,uuid,shutil
from native_utils import footprint_spans,end_form,subforms

def parse(s):
 st=[]
 for t in re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',s):
  if t=='(':st.append([])
  elif t==')':
   x=st.pop()
   if st:st[-1].append(x)
   else:return x
  else:st[-1].append(t)
def drawn_segments(s):
 ans=[]
 for x in parse(s):
  if not isinstance(x,list) or x[0] not in ['fp_line','fp_rect']:continue
  d={y[0]:y[1:] for y in x[1:] if isinstance(y,list)}
  a,b=tuple(map(float,d['start'])),tuple(map(float,d['end']))
  st=str(d['stroke']);layer=d['layer'][0]
  pts=[a,b] if x[0]=='fp_line' else [a,(a[0],b[1]),b,(b[0],a[1]),a]
  ans.extend((tuple(sorted((p,q))),st,layer) for p,q in zip(pts,pts[1:]))
 return sorted(ans)

p=Path('PGR.kicad_pcb');s=p.read_text();changes=[]
libs={'R30':'Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod','J12':'Connector_JST.pretty/JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical.kicad_mod'}
for ref,uid,a,b,c in footprint_spans(s):
 if ref not in libs:continue
 lib=(Path('/usr/share/kicad/footprints')/libs[ref]).read_text()
 assert drawn_segments(c)==drawn_segments(lib),ref
 new=c;spans=[]
 for m in re.finditer(r'^\t\t\(fp_(?:line|rect)\b',new,re.M):spans.append((m.start(),end_form(new,new.index('(',m.start()))))
 for aa,bb in sorted(spans,reverse=True):new=new[:aa]+new[bb:]
 graphics=[]
 for head in ['fp_line','fp_rect']:
  for form in subforms(lib,head):
   form=form[:-1]+'\n\t(uuid "'+str(uuid.uuid4())+'")\n)'
   graphics.append('\n\t\t'+'\n\t\t'.join(form.splitlines()))
 new=new[:-1]+''.join(graphics)+'\n\t)'
 olddesc=subforms(new,'descr');newdesc=subforms(lib,'descr');assert len(olddesc)==len(newdesc)==1
 new=new.replace(olddesc[0],newdesc[0],1)
 assert drawn_segments(new)==drawn_segments(c)
 assert subforms(new,'pad')==subforms(c,'pad')
 assert subforms(new,'model')==subforms(c,'model')
 changes.append((a,b,new))
assert len(changes)==2
shutil.copy2(p,'build/solar-layout/backups/before-library-normalization.kicad_pcb')
for a,b,c in sorted(changes,reverse=True):s=s[:a]+c+s[b:]
p.write_text(s);print('Normalized the two new footprints; copper and drawn outlines are identical')
