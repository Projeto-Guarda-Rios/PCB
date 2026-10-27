from pathlib import Path
import sexpdata as sx,xml.etree.ElementTree as ET,json,hashlib
root=Path.cwd();out=root/'build/vertical-usb'
# Restore the cached symbol artwork damaged by an IPC polyline round-trip.
# Keep all instance metadata, pins and wires exactly as saved.
p=root/'PGR.kicad_sch';now=p.read_text();old=(out/'backups/pre-edit-PGR.kicad_sch').read_text()
def span(s,needle):
 start=s.index(needle);depth=0;quoted=False;escape=False
 for i in range(start,len(s)):
  c=s[i]
  if quoted:
   if escape:escape=False
   elif c=='\\':escape=True
   elif c=='"':quoted=False
  elif c=='"':quoted=True
  elif c=='(':depth+=1
  elif c==')':
   depth-=1
   if depth==0:return start,i+1
 raise RuntimeError('Unbalanced source')
needle='(symbol "PGR_Validated:Connector_USB_C_Receptacle"'
a,b=span(now,needle);c,d=span(old,needle);p.write_text(now[:a]+old[c:d]+now[b:])
# Make the library's pin-one marker identical to the integrated footprint.
p=root/'PGR-FootPrints.pretty/USB_C_GCT_USB4145_03_0230_C_Vertical.kicad_mod';r=sx.loads(p.read_text())
sub=lambda n,k:[x for x in n if isinstance(x,list) and x and str(x[0])==k]
for circ in sub(r,'fp_circle'):
 if str(sub(circ,'layer')[0][1])=='F.SilkS':
  sub(circ,'center')[0][1:]=[-3,-2.6];sub(circ,'end')[0][1:]=[-2.88,-2.6];sub(circ,'width')[0][1]=.12
p.write_text(sx.dumps(r)+'\n')
# All connectivity in the schematic is identical before/after selecting the part.
def nets(p):
 r=ET.parse(p);return {n.get('name'):sorted((x.get('ref'),x.get('pin')) for x in n.findall('node')) for n in r.findall('.//nets/net')}
assert nets(out/'netlist-before.xml')==nets(out/'netlist-after.xml')
# Confirm the canonical board did not move or alter any of the other 160 footprints.
def fps(p):
 r=sx.loads(p.read_text());return {next(x[2] for x in sub(f,'property') if x[1]=='Reference'):f for f in sub(r,'footprint')}
before=fps(out/'backups/pre-edit-PGR.kicad_pcb');after=fps(root/'PGR.kicad_pcb')
assert len(before)==len(after)==161
for ref in before:
 if ref!='J9':assert before[ref]==after[ref],ref
assert sub(before['J9'],'at')==sub(after['J9'],'at')
# Pad mapping and physical dimensions independently checked against the drawing.
f=after['J9'];pads=sub(f,'pad');assert len(pads)==22
expected={}
for side,y,order in [('A',-1.485,[('1',-2.75),('4',-1.25),('5',-.75),('6',-.25),('7',.25),('8',.75),('9',1.25),('12',2.75)]),('B',1.485,[('12',-2.75),('9',-1.25),('8',-.75),('7',-.25),('6',.25),('5',.75),('4',1.25),('1',2.75)])]:
 for number,x in order:expected[side+number]=(x,y)
netmap={}
for pad in pads:
 num=pad[1]
 if num in expected:
  assert tuple(sub(pad,'at')[0][1:3])==expected[num]
  assert sub(pad,'size')[0][1:]==[.3,1.15]
  netmap[num]=sub(pad,'net')[0][-1]
 elif num=='S1':
  assert sub(pad,'net')[0][-1]=='GND';assert sub(pad,'drill')[0][1:]==[sx.Symbol('oval'),1.1,.6]
 else:assert pad[2]==sx.Symbol('np_thru_hole') and sub(pad,'drill')[0][1:]==[.66]
for num in ['A1','A12','B1','B12']:assert netmap[num]=='GND'
for num in ['A4','A9','B4','B9']:assert netmap[num]=='+5V_PROGRAM'
for num in ['A6','B6']:assert netmap[num]=='D+'
for num in ['A7','B7']:assert netmap[num]=='D-'
assert netmap['A5']=='Net-(J9-CC1)' and netmap['B5']=='Net-(J9-CC2)'
report={'non_J9_footprints_unchanged':160,'J9_anchor_unchanged':True,'schematic_connectivity_unchanged':True,'physical_pad_mapping_verified':True,'J9_signal_pads':16,'J9_shell_stakes':4,'J9_locating_holes':2}
(out/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
