from pathlib import Path
import sexpdata as sx,copy,uuid,re,json,shutil
S=sx.Symbol
sub=lambda n,k:[a for a in n if isinstance(a,list) and a and str(a[0])==k]
root=Path.cwd();out=root/'build/vertical-usb';backup=out/'backups'
for name in ['PGR.kicad_pcb','PGR.kicad_sch','PGR.kicad_pro','PGR.kicad_pcb.backplane.json','PGR.kicad_sch.backplane.json']:
 if (root/name).exists():shutil.copy2(root/name,backup/name)
libname='USB_C_GCT_USB4145_03_0230_C_Vertical';fp=sx.loads((out/'C5291559.pretty/USB-C-SMD_USB4145-03-0230-C.kicad_mod').read_text());fp[0]=S('footprint');fp[1]=libname
# Repair the supplied CAD against GCT's official drawing, Rev A1 page 2.
fp[:]=[n for n in fp if not(isinstance(n,list) and n and (str(n[0]) in ['tedit','property'] or (str(n[0]).startswith('fp_') and sub(n,'layer') and sub(n,'layer')[0][1] in ['F.CrtYd','Cmts.User'])))]
sub(fp,'attr')[0][1:]=[S('smd')]
fp.append([S('descr'),'GCT USB4145-03-0230-C vertical USB2.0, H7.46mm, 2.3mm shell stakes; GCT drawing Rev A1 page 2'])
fp.append([S('tags'),'USB C vertical 16pin USB2.0 C5291559'])
fp[:]=[n for n in fp if not(isinstance(n,list) and n and str(n[0])=='pad' and n[1]=='')]
for pad in sub(fp,'pad'):
 pad[1]=str(pad[1])
 at=sub(pad,'at')[0];sz=sub(pad,'size')[0]
 if pad[1]=='0':
  pad[1]='S1';sz[1:]=[1.6,1.1];sub(pad,'drill')[0][1:]=[S('oval'),1.1,.6]
 else:
  sz[1:]=[.3,1.15];at[2]=1.485 if pad[1].startswith('B') else -1.485
for x in [-4,4]:fp.append([S('pad'),' ',S('np_thru_hole'),S('circle'),[S('at'),x,0],[S('size'),.66,.66],[S('drill'),.66],[S('layers'),'*.Cu','*.Mask']]);fp[-1][1]=''
def rect(layer,x0,y0,x1,y1,width):return [S('fp_rect'),[S('start'),x0,y0],[S('end'),x1,y1],[S('stroke'),[S('width'),width],[S('type'),S('solid')]],[S('fill'),S('none')],[S('layer'),layer]]
fp.append(rect('F.CrtYd',-5.05,-2.35,5.05,2.35,.05));fp.append(rect('F.Fab',-4.47,-1.845,4.47,1.845,.1))
# Body model is shared by the family. Extend only the four shell stakes to this variant's 2.3mm length.
models=root/'3dmodels';models.mkdir(exist_ok=True)
src=(out/'C5291559.3dshapes/USB-C-SMD_USB4145-03-0230-C.wrl').read_text();count=0
pattern=r'point\s*\[([^\]]*)\]'
def adjust(m):
 global count
 coords=[]
 for raw in m.group(1).split(','):
  nums=raw.split()
  if len(nums)!=3:continue
  x,y,z=map(float,nums)
  if z<0 and abs(x*2.54)>3.6 and abs(y*2.54)>.8:z*=2.3/.7;count+=1
  coords.append(f'{x:.6f} {y:.6f} {z:.6f}')
 return 'point [\n'+', '.join(coords)+'\n]'
src=re.sub(pattern,adjust,src);modelpath=models/(libname+'.wrl');modelpath.write_text(src)
assert count>0
mod=sub(fp,'model')[0];mod[1]='${KIPRJMOD}/3dmodels/'+libname+'.wrl'
for t in sub(fp,'fp_text'):
 if str(t[1])=='reference':sub(t,'at')[0][1:]=[0,-3.4]
 elif str(t[1])=='value':t[2]='USB4145-03-0230-C'
(root/'PGR-FootPrints.pretty'/f'{libname}.kicad_mod').write_text(sx.dumps(fp)+'\n')
# A disposable fixture lets the IPC parser instantiate the imported footprint and supports visual QA.
br=sx.loads((root/'PGR.kicad_pcb').read_text());old=next(f for f in sub(br,'footprint') if any(p[1]=='Reference' and p[2]=='J9' for p in sub(f,'property')))
nets={p[1]:copy.deepcopy(sub(p,'net')[0]) for p in sub(old,'pad') if sub(p,'net')}
f=copy.deepcopy(fp);f[1]='PGR-FootPrints:'+libname
f[:]=[n for n in f if not(isinstance(n,list) and n and str(n[0])=='fp_text' and str(n[1]) in ['reference','value'])]
f.insert(2,[S('at'),10,8]);f.insert(3,[S('uuid'),str(uuid.uuid4())])
for p in sub(old,'property'):
 if not sub(p,'at'):continue
 q=copy.deepcopy(p);at=sub(q,'at')[0];at[1:]=[0,-3.4,0] if p[1]=='Reference' else [0,3.4,0]
 if q[1]=='Value':q[2]='USB4145-03-0230-C'
 if q[1]=='Datasheet':q[2]='https://gct.co/files/drawings/usb4145.pdf'
 f.append(q)
for pad in sub(f,'pad'):
 if pad[1]:pad.append(copy.deepcopy(nets[pad[1]]))
fixture=[copy.deepcopy(z) for z in br if not(isinstance(z,list) and z and str(z[0]) in ['footprint','segment','via','zone','group','gr_text','gr_rect','gr_line','gr_arc','gr_circle','gr_poly','gr_text_box','dimension','image'])]
fixture.append(f)
for p,q in [((0,0),(20,0)),((20,0),(20,16)),((20,16),(0,16)),((0,16),(0,0))]:fixture.append([S('gr_line'),[S('start'),*p],[S('end'),*q],[S('stroke'),[S('width'),.05],[S('type'),S('solid')]],[S('layer'),'Edge.Cuts'],[S('uuid'),str(uuid.uuid4())]])
(out/'footprint-fixture.kicad_pcb').write_text(sx.dumps(fixture)+'\n')
(out/'selected-part.json').write_text(json.dumps({'MPN':'USB4145-03-0230-C','Manufacturer':'GCT','LCSC':'C5291559','Footprint':'PGR-FootPrints:'+libname,'pcb_thickness_mm':1.6,'shell_stakes_mm':2.3,'height_mm':7.46,'live_stock':1608,'live_orderable':1535,'live_price_usd_1pc':1.3962,'drawing':'https://gct.co/files/drawings/usb4145.pdf','cad_corrections':['Signal pads 0.30 x 1.15mm, rows +/-1.485mm','Shell plated slots 1.10 x 0.60mm, pads 1.60 x 1.10mm at x+/-4 y+/-1.43','Two NPTH locating holes, diameter0.66mm at x+/-4 y0','Courtyard includes all pads; S1 shell matches schematic','3D family shell stakes extended from0.7mm to2.3mm']},indent=2))
shutil.copy2(root/'PGR.kicad_pro',out/'footprint-fixture.kicad_pro')
print('Prepared corrected footprint; 16 signal pads, 4 shell slots, 2 locating holes; model stake vertices adjusted',count)
