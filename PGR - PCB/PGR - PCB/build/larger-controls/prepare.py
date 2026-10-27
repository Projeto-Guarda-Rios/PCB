from pathlib import Path
import sexpdata as sx,copy,uuid,shutil
r=Path.cwd();o=r/'build/larger-controls';S=sx.Symbol
sub=lambda n,k:[x for x in n if isinstance(x,list) and x and str(x[0])==k]
b=sx.loads((r/'PGR.kicad_pcb').read_text());sch=sx.loads((r/'PGR.kicad_sch').read_text())
fs={next(p[2] for p in sub(f,'property') if p[1]=='Reference'):f for f in sub(b,'footprint')}
fixture=[copy.deepcopy(z) for z in b if not(isinstance(z,list) and z and str(z[0]) in ['footprint','segment','via','zone','group','gr_text','gr_rect','gr_line','gr_arc','gr_circle','gr_poly','gr_text_box','dimension','image'])]
choices={'SW1':('Button_Switch_SMD:SW_SPST_Omron_B3FS-100xP','/usr/share/kicad/footprints/Button_Switch_SMD.pretty/SW_SPST_Omron_B3FS-100xP.kicad_mod'),'SW2':('Button_Switch_SMD:SW_SPST_Omron_B3FS-100xP','/usr/share/kicad/footprints/Button_Switch_SMD.pretty/SW_SPST_Omron_B3FS-100xP.kicad_mod'),'SW4':('PGR-FootPrints:SW_Slide_CK_1101M2S3CBE2',str(r/'PGR-FootPrints.pretty/SW_Slide_CK_1101M2S3CBE2.kicad_mod'))}
for i,(ref,(fp,path)) in enumerate(choices.items()):
 f=sx.loads(Path(path).read_text());f[1]=fp;f.insert(2,[S('at'),20+i*25,20]);f.append([S('uuid'),str(uuid.uuid4())]);nets={p[1]:sub(p,'net')[0] for p in sub(fs[ref],'pad') if sub(p,'net')}
 for p in sub(f,'property'):
  if p[1]=='Reference':p[2]=ref
 for p in sub(f,'pad'):
  if p[1] in nets:p.append(copy.deepcopy(nets[p[1]]))
 fixture.append(f)
for p,q in [((5,5),(85,5)),((85,5),(85,35)),((85,35),(5,35)),((5,35),(5,5))]:fixture.append([S('gr_line'),[S('start'),*p],[S('end'),*q],[S('stroke'),[S('width'),.05],[S('type'),S('solid')]],[S('layer'),'Edge.Cuts'],[S('uuid'),str(uuid.uuid4())]])
(o/'fixture.kicad_pcb').write_text(sx.dumps(fixture)+'\n');shutil.copy2(r/'PGR.kicad_pro',o/'fixture.kicad_pro')
stock=sx.loads(Path('/usr/share/kicad/symbols/Switch.kicad_sym').read_text());z=copy.deepcopy(next(z for z in sub(stock,'symbol') if z[1]=='SW_SPDT'));z[1]='Switch:SW_SPDT'
old=copy.deepcopy(next(z for z in sub(sch,'symbol') if any(p[1:3]==['Reference','SW4'] for p in sub(z,'property'))));sub(old,'lib_id')[0][1]='Switch:SW_SPDT';sub(old,'at')[0][3]=180
old=[z for z in old if not(isinstance(z,list) and z and str(z[0]) in ['pin','instances'])]
for n in ['1','2','3']:old.append([S('pin'),n,[S('uuid'),str(uuid.uuid4())]])
id=str(uuid.uuid4());old.append([S('instances'),[S('project'),'fixture',[S('path'),'/'+id,[S('reference'),'SW4'],[S('unit'),1]]]])
(o/'fixture.kicad_sch').write_text(sx.dumps([S('kicad_sch'),[S('version'),20250114],[S('generator'),S('eeschema')],[S('uuid'),id],[S('paper'),'A1'],[S('lib_symbols'),z],old]))
for w in sub(sch,'wire'):
 pts=sub(w,'pts')[0][1:]
 if any(abs(p[1]-539.75)<.01 and abs(p[2]-163.83)<.01 for p in pts):print('SW4 left wire',w)
for p in sub(z,'symbol'):
 for pin in sub(p,'pin'):print('SPDT pin',sub(pin,'number'),sub(pin,'at'))
print('Footprint templates ready')
