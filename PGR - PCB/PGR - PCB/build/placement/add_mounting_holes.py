from pathlib import Path
import sexpdata as sx,uuid,copy
S=sx.Symbol
p=Path('PGR.kicad_pcb');root=sx.loads(p.read_text());sub=lambda n,k:[x for x in n if isinstance(x,list) and x and str(x[0])==k]
assert not any(any(pr[1]=='Reference' and pr[2] in ['H1','H2','H3','H4'] for pr in sub(f,'property')) for f in sub(root,'footprint'))
original=sx.loads(Path('/usr/share/kicad/footprints/MountingHole.pretty/MountingHole_3.2mm_M3.kicad_mod').read_text());out=[]
for num,(x,y) in enumerate([(55,55),(155,55),(55,130),(155,130)],1):
 f=copy.deepcopy(original);f[1]='MountingHole:MountingHole_3.2mm_M3';f[:]=[z for z in f if not(isinstance(z,list) and z and str(z[0]) in ['version','generator','embedded_fonts'])]
 f.insert(2,[S('at'),x,y]);f.insert(3,[S('uuid'),str(uuid.uuid4())])
 for prop in sub(f,'property'):
  if prop[1]=='Reference':prop[2]=f'H{num}';at=sub(prop,'at')[0];at[2]=6.3 if num<3 else -6.3
  elif prop[1]=='Value':prop.append([S('hide'),S('yes')])
 attr=sub(f,'attr')[0];attr.append(S('board_only'))
 out.append(sx.dumps(f))
s=p.read_text();i=s.rfind(')');p.write_text(s[:i]+'\n\t'+'\n\t'.join(out)+'\n'+s[i:])
print('Added four official 3.2mm NPTH M3 footprints')
