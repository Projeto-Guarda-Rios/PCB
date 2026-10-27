from pathlib import Path
import sexpdata as sx
p=Path('PGR.kicad_sch');s=p.read_text()
# Repair IPC-generated per-instance cache alias and rotated field positions.
def spans(t):
 q=False;esc=False;depth=0;a=None
 for i,c in enumerate(t):
  if q:
   if esc:esc=False
   elif c=='\\':esc=True
   elif c=='"':q=False
  elif c=='"':q=True
  elif c=='(':
   if depth==1:a=i
   depth+=1
  elif c==')':
   depth-=1
   if depth==1:yield a,i+1
sub=lambda n,k:[x for x in n if isinstance(x,list) and x and str(x[0])==k]
for a,b in reversed(list(spans(s))):
 t=s[a:b]
 if not t.startswith('(symbol\n'):continue
 z=sx.loads(t);props={x[1]:x for x in sub(z,'property')};ref=props.get('Reference',[None,None,None])[2]
 if ref=='SW1':z=[x for x in z if not(isinstance(x,list) and str(x[0])=='lib_name')]
 elif ref=='SW4':
  for name,y in [('Reference',153.67),('Value',156.21)]:sub(props[name],'at')[0][1:]=[544.83,y,0]
 else:continue
 s=s[:a]+sx.dumps(z)+s[b:]
p.write_text(s)
