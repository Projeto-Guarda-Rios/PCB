from pathlib import Path
import xml.etree.ElementTree as E,json,hashlib,collections,math
# Reuse the exact courtyard polygon reader without running its reference-placement code.
s=Path('build/placement/tidy_references.py').read_text();exec(s[:s.index('region_union=')])
root=sx.loads(Path('PGR.kicad_pcb').read_text());fps={next(p[2] for p in sub(f,'property') if p[1]=='Reference'):f for f in sub(root,'footprint')}
netlist=E.parse('build/placement/netlist.xml');expected={c.get('ref') for c in netlist.findall('.//components/comp') if c.findtext('footprint')}
assert set(fps)==expected|{'H1','H2','H3','H4'}
assert hashlib.sha256(Path('PGR.kicad_sch').read_bytes()).digest()==hashlib.sha256(Path('build/placement/backups/PGR.kicad_sch').read_bytes()).digest()
actual={(ref,p[1]):sub(p,'net')[0][-1] for ref,f in fps.items() for p in sub(f,'pad') if sub(p,'net')};checked=0
for net in netlist.findall('.//nets/net'):
 for node in net.findall('node'):
  ref,pin=node.get('ref'),node.get('pin')
  if ref not in expected or 'no_connect' in node.get('pintype',''):continue
  assert actual.get((ref,pin))==net.get('name'),(ref,pin,net.get('name'),actual.get((ref,pin)))
  checked+=1
hardware=[]
for ref in ['H1','H2','H3','H4']:
 f=fps[ref];at=sub(f,'at')[0];x,y=map(float,at[1:3]);pad=sub(f,'pad')[0];assert float(sub(pad,'drill')[0][1])==3.2
 area=Point(x,y).buffer(4.5)
 collisions=[k for k,p in regions.items() if k!=ref and area.intersects(p)]
 assert not collisions,(ref,collisions)
 hardware.append({'reference':ref,'center_from_board_origin_mm':[x-50,y-50],'drill_mm':3.2,'hardware_clear_diameter_mm':9})
probe_clearances={}
for ref in [f'TP{i}' for i in range(1,9)]:
 x,y=xy(fs[ref].position);p=Point(x,y);nearest=min((p.distance(poly),k) for k,poly in regions.items() if k!=ref)
 assert nearest[0]>=3,(ref,nearest)
 probe_clearances[ref]={'nearest_other_courtyard_distance_mm':round(nearest[0],3),'nearest_component':nearest[1]}
drc=json.loads(Path('build/placement/drc-final.json').read_text());counts=collections.Counter(v['type'] for v in drc['violations'])
for key in ['courtyards_overlap','items_not_allowed','shorting_items','clearance','silk_overlap','silk_over_copper','silk_edge_clearance','invalid_outline','copper_edge_clearance']:assert counts[key]==0,(key,counts[key])
assert not sub(root,'segment') and not sub(root,'via')
assert len(sub(root,'gr_line'))==8
# Physical bypass-pad distances verify the tightest supply placement decisions.
def padpos(ref,num):
 f=fs[ref]
 return xy(next(unpack(p).position for p in f.definition.items if p.Is(board.Pad.DESCRIPTOR) and unpack(p).number==str(num)))
def distance(p,q):return round(math.dist(p,q),3)
power={'charger_OUT_to_C13_PWR_mm':distance(padpos('U1',10),padpos('C13',1)),'boost_VIN_to_C13_PWR_mm':distance(padpos('U3',10),padpos('C13',1)),'boost_SW_to_inductor_mm':distance(padpos('U3',1),padpos('L1',2)),'buck_SW_to_inductor_mm':distance(padpos('IC1',3),padpos('L2',1))}
assert power['charger_OUT_to_C13_PWR_mm']<4 and power['boost_VIN_to_C13_PWR_mm']<3
assert all(f.layer==board.BL_F_Cu for f in fs.values())
report={'board_size_mm':[110,85],'hole_pattern_mm':[100,75],'component_count':len(expected),'mounting_holes':hardware,'all_components_front':True,'schematic_unchanged':True,'active_pad_nets_verified':checked,'tracks':0,'vias':0,'probe_access':probe_clearances,'critical_power_pad_distances':power,'remaining_drc':dict(counts),'unconnected_items':len(drc['unconnected_items']),'board_sha256':hashlib.sha256(Path('PGR.kicad_pcb').read_bytes()).hexdigest()}
Path('build/placement/verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
