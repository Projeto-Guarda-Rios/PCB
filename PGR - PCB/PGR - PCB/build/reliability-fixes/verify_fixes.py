from pathlib import Path
import json,re,collections,xml.etree.ElementTree as ET,math
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'build/reliability-fixes'
def sexpr(path):
 tokens=re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',Path(path).read_text());stack=[];root=[];cur=root
 for t in tokens:
  if t=='(':stack.append(cur);new=[];cur.append(new);cur=new
  elif t==')':cur=stack.pop()
  else:cur.append(json.loads(t) if t.startswith('"') else t)
 return root[0]
def xs(o,k):return [a for a in o if isinstance(a,list) and a and a[0]==k]
def x(o,k):return next(iter(xs(o,k)),[])
def id(o):return x(o,'uuid')[1]
def net(o):return x(o,'net')[-1] if x(o,'net') else ''
def ref(f):return next(a[2] for a in xs(f,'property') if a[1]=='Reference')
def pins(r):return {x.attrib['ref']+'.'+x.attrib['pin']:n.attrib['name'] for n in r.findall('.//nets/net') for x in n.findall('node')}
oldpins=pins(ET.parse(ROOT/'build/board-review/netlist.xml'));newpins=pins(ET.parse(OUT/'netlist-final.xml'))
expected={'R22.2':('GND','Net-(U3-FB)'),'R23.1':('GND','Net-(U3-FB)'),'U3.10':('GND','Net-(U3-FB)'),'U3.11':('unconnected-(U3-PAD-Pad11)','GND'),'U4.7':('+5V_PROGRAM','+3.3V')}
changes={k:(oldpins.get(k),newpins.get(k)) for k in oldpins.keys()|newpins.keys() if oldpins.get(k)!=newpins.get(k)}
assert changes==expected,changes
assert newpins['C15.2']=='GND' and newpins['U3.9']=='GND' and newpins['U3.4']=='GND'
old=sexpr(OUT/'backups/before/PGR.kicad_pcb');new=sexpr(ROOT/'PGR.kicad_pcb')
oldfps={id(f):f for f in xs(old,'footprint')};newfps={id(f):f for f in xs(new,'footprint')}
assert oldfps.keys()==newfps.keys()
geometry_changes=[];net_changes=[]
for fid,of in oldfps.items():
 nf=newfps[fid];assert x(of,'at')==x(nf,'at'),ref(of)
 op={id(p):p for p in xs(of,'pad')};np={id(p):p for p in xs(nf,'pad')};assert op.keys()==np.keys(),ref(of)
 for pid,p in op.items():
  q=np[pid]
  for prop in ['at','size','drill','layers','roundrect_rratio']:
   assert x(p,prop)==x(q,prop),(ref(of),p[1],prop,x(p,prop),x(q,prop))
  if net(p)!=net(q):
   pin=ref(of)+'.'+p[1];want=expected.get(pin)
   assert want and net(q)==want[1],(pin,net(p),net(q))
   net_changes.append([pin,net(p),net(q)])
all_pads={}
for f in newfps.values():
 for p in xs(f,'pad'):all_pads.setdefault(ref(f)+'.'+p[1],[]).append(net(p))
for pin,(_,wanted) in expected.items():assert all(n==wanted for n in all_pads[pin]),(pin,all_pads[pin])
# U3 power-pad solid connections are required on all its pad shapes and thermal vias.
u3=next(f for f in newfps.values() if ref(f)=='U3')
for p in xs(u3,'pad'):
 if p[1]=='11':assert net(p)=='GND' and x(p,'zone_connect')==['zone_connect','2']
# Preserve previously routed copper unless explicitly removed; existing segment widths are not relaxed.
oldsegs={id(t):t for t in xs(old,'segment')};newsegs={id(t):t for t in xs(new,'segment')}
assert all(oldsegs[k]==newsegs[k] for k in oldsegs.keys()&newsegs.keys())
def errors(d):return { (v['type'],tuple(sorted(i['uuid'] for i in v['items']))) for k in ['violations','unconnected_items','schematic_parity'] for v in d[k] if v['severity']=='error'}
drc=json.load(open(OUT/'drc-final.json'));baseline=json.load(open(ROOT/'build/board-review/drc-library-resolved.json'))
assert not drc['unconnected_items']
assert errors(drc)<=errors(baseline),errors(drc)-errors(baseline)
assert not any(v['type'] in ['shorting_items','clearance','starved_thermal'] for v in drc['violations'])
parity=[v for v in drc['schematic_parity'] if any(i['description'] in ['Footprint U3','Footprint U4','Footprint R22','Footprint R23'] for i in v['items']) and v['type'] in ['net_conflict','footprint_symbol_mismatch']]
assert not parity,parity
assert (OUT/'ground-connectivity.txt').read_text().startswith('GROUND CONNECTED COMPONENTS 1\n')
erc=json.load(open(OUT/'erc-final.json'));erc0=json.load(open(ROOT/'build/board-review/erc-library-resolved.json'))
def erc_errors(d):return {(v['type'],tuple(i['uuid'] for i in v['items'])) for s in d['sheets'] for v in s['violations'] if v['severity']=='error'}
assert erc_errors(erc)<=erc_errors(erc0)
report={'result':'PASS','schematic_pin_net_changes':changes,'all_other_schematic_pin_nets_unchanged':True,'all_81_footprint_positions_and_all_pad_geometries_unchanged':True,'board_pad_net_changes':net_changes,'nominal_boost_output_before_D1_volts':.5*(1+820000/91000),'unconnected_items':len(drc['unconnected_items']),'new_DRC_errors':0,'remaining_preexisting_DRC_errors':len(errors(drc)),'new_ERC_errors':0,'remaining_preexisting_ERC_errors':len(erc_errors(erc)),'ground_copper_connected_components':1}
(OUT/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
