from pathlib import Path
import json,hashlib,collections,xml.etree.ElementTree as E
import sexpdata as sx
sub=lambda n,k:[x for x in n if isinstance(x,list) and x and str(x[0])==k]
r=sx.loads(Path('PGR.kicad_pcb').read_text());fs={next(p[2] for p in sub(f,'property') if p[1]=='Reference'):f for f in sub(r,'footprint')}
x=E.parse('build/layout-groups/netlist.xml');cs={c.get('ref'):c for c in x.findall('.//components/comp') if c.findtext('footprint')}
assert set(cs)==set(fs),(set(cs)-set(fs),set(fs)-set(cs))
actual={(ref,p[1]):sub(p,'net')[0][-1] for ref,f in fs.items() for p in sub(f,'pad') if sub(p,'net')}
errors=[];missing_nc=[];checked=0
for net in x.findall('.//nets/net'):
 for node in net.findall('node'):
  key=(node.get('ref'),node.get('pin'))
  if key[0] not in fs:continue
  if 'no_connect' in node.get('pintype',''):
   if key not in actual:missing_nc.append(key)
   continue
  checked+=1
  if actual.get(key)!=net.get('name'):errors.append([key,net.get('name'),actual.get(key)])
assert not errors,errors
assert len(missing_nc)==8 and all(k[0]=='J9' for k in missing_nc)
assert not sub(r,'segment') and not sub(r,'via')
assert hashlib.sha256(Path('PGR.kicad_sch').read_bytes()).digest()==hashlib.sha256(Path('build/layout-groups/backups/PGR.kicad_sch').read_bytes()).digest()
drc=json.loads(Path('build/layout-groups/drc.json').read_text());counts=collections.Counter(i['type'] for i in drc['violations'])
assert not counts['courtyards_overlap'] and not counts['items_not_allowed']
report={'footprints':len(fs),'groups':len(json.loads(Path('build/layout-groups/groups.json').read_text())),'active_pad_net_assignments_verified':checked,'schematic_unchanged':True,'remaining_footprint_drc':dict(counts),'expected_absent_usb3_no_connect_pins':missing_nc,'unrouted_items':len(drc['unconnected_items']),'board_sha256':hashlib.sha256(Path('PGR.kicad_pcb').read_bytes()).hexdigest()}
Path('build/layout-groups/verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
