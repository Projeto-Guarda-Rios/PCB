from pathlib import Path
import sexpdata as sx,copy,shutil,uuid
r=Path.cwd();out=r/'build/battery-holder';sub=lambda n,k:[x for x in n if isinstance(x,list) and x and str(x[0])==k];S=sx.Symbol
b=sx.loads((r/'PGR.kicad_pcb').read_text());bt=next(f for f in sub(b,'footprint') if any(p[1:3]==['Reference','BT1'] for p in sub(f,'property')))
f=sx.loads(Path('/usr/share/kicad/footprints/Battery.pretty/BatteryHolder_Keystone_1042_1x18650.kicad_mod').read_text());f[1]='Battery:BatteryHolder_Keystone_1042_1x18650';f.insert(2,[S('at'),50,25]);f.insert(3,[S('uuid'),str(uuid.uuid4())])
for prop in sub(f,'property'):
 if prop[1]=='Reference':prop[2]='BT1'
 if prop[1]=='Value':prop[2]='1042'
nets={p[1]:sub(p,'net')[0] for p in sub(bt,'pad') if sub(p,'net')}
print('Existing battery nets',nets)
for p in sub(f,'pad'):
 if p[1]:p.append(copy.deepcopy(nets[p[1]]))
fixture=[copy.deepcopy(z) for z in b if not(isinstance(z,list) and z and str(z[0]) in ['footprint','segment','via','zone','group','gr_text','gr_rect','gr_line','gr_arc','gr_circle','gr_poly','gr_text_box','dimension','image'])]
fixture.append(f)
for p,q in [((0,0),(100,0)),((100,0),(100,50)),((100,50),(0,50)),((0,50),(0,0))]:fixture.append([S('gr_line'),[S('start'),*p],[S('end'),*q],[S('stroke'),[S('width'),.05],[S('type'),S('solid')]],[S('layer'),'Edge.Cuts'],[S('uuid'),str(uuid.uuid4())]])
(out/'fixture.kicad_pcb').write_text(sx.dumps(fixture)+'\n');shutil.copy2(r/'PGR.kicad_pro',out/'fixture.kicad_pro')
