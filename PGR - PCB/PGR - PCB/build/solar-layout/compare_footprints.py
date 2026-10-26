from pathlib import Path
import re,difflib,json
from native_utils import footprint_spans

def parse(s):
 toks=re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',s);stack=[]
 for t in toks:
  if t=='(':stack.append([])
  elif t==')':
   x=stack.pop()
   if stack:stack[-1].append(x)
   else:return x
  else:stack[-1].append(t)

def clean(x):
 if not isinstance(x,list):return x
 if x and x[0] in ['uuid','net','pintype','pinfunction','tstamp','property','path','sheetname','sheetfile']:return None
 return [z for y in x if (z:=clean(y)) is not None]
s=Path('PGR.kicad_pcb').read_text()
for ref,_,_,_,ch in footprint_spans(s):
 if ref not in ['J12','R30']:continue
 lib=Path('/usr/share/kicad/footprints')/({'J12':'Connector_JST.pretty/JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical.kicad_mod','R30':'Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod'}[ref])
 a=parse(ch);b=parse(lib.read_text())
 for kind in ['pad','fp_line','fp_text','fp_rect','fp_arc','model','attr','descr','tags']:
  aa=[clean(x) for x in a if isinstance(x,list) and x[0]==kind];bb=[clean(x) for x in b if isinstance(x,list) and x[0]==kind]
  if sorted(map(str,aa))!=sorted(map(str,bb)):
   print(ref,kind)
   for z in difflib.unified_diff(sorted(map(str,bb)),sorted(map(str,aa)),fromfile='library',tofile='board'):print(z)
