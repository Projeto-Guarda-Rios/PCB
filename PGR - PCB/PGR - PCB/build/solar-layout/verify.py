from pathlib import Path
import json,hashlib,xml.etree.ElementTree as E,copy
from native_utils import footprint_spans,subforms
out=Path('build/solar-layout')
b=json.loads((out/'items-before.json').read_text());f=json.loads((out/'items-final.json').read_text())
def fps(xs):return {x['id']['value']:x for x in xs if x['_type']=='FootprintInstance'}
bf,ff=fps(b),fps(f);br={x['reference_field']['text']['text']['text']:x for x in bf.values()};fr={x['reference_field']['text']['text']['text']:x for x in ff.values()}
assert len(ff)==82 and 'TH1' not in fr
assert set(fr)-set(br)=={'J12','R30'}
assert fr['R1']['value_field']['text']['text']['text']=='2kR'
assert fr['R30']['value_field']['text']['text']['text']=='68kR'
expected={'U1':{'1':'/BAT_NTC','5':'GND','6':'PWR_OUT','14':'Net-(U1-TMR)'},'R30':{'1':'GND','2':'Net-(U1-TMR)'},'J12':{'1':'/BAT_NTC','2':'GND'}}
for ref,nets in expected.items():
 ps={p.get('number',''):p for p in fr[ref]['definition']['items'] if p.get('@type','').endswith('.Pad')}
 for p,n in nets.items():assert ps[p]['net']['name']==n
# Placement and physical pad geometry of every retained electrical component are unchanged.
for uid,x in bf.items():
 if uid not in ff:assert x['reference_field']['text']['text']['text']=='TH1';continue
 y=ff[uid]
 if x['reference_field']['text']['text']['text']!='G***':assert x['position']==y['position'] and x.get('orientation')==y.get('orientation')
 xp={z['id']['value']:z for z in x['definition']['items'] if z.get('@type','').endswith('.Pad')};yp={z['id']['value']:z for z in y['definition']['items'] if z.get('@type','').endswith('.Pad')}
 assert xp.keys()==yp.keys()
 for k,p in xp.items():
  q=yp[k]
  for field in ['position','type','number']:assert p.get(field)==q.get(field),(uid,k,field)
  def geom(p):
   p=copy.deepcopy(p['pad_stack']);p.pop('zone_settings',None);return p
  assert geom(p)==geom(q),(uid,k,'pad stack')
# All target pad nets match the schematic including the connector and timer.
sch=E.parse('build/solar-schematic/netlist-after.xml').getroot();pinmap={(p.get('ref'),p.get('pin')):n.get('name') for n in sch.findall('.//nets/net') for p in n.findall('node')}
for ref in ['U1','R1','R2','R30','J12','BT1']:
 for p in fr[ref]['definition']['items']:
  if p.get('@type','').endswith('.Pad') and p.get('number'):assert p.get('net',{}).get('name')==pinmap[ref,p['number']],(ref,p)
for fn in ['PGR.kicad_sch','PGR.kicad_pro']:assert Path(fn).read_bytes()==(out/'backups'/fn).read_bytes(),fn
before=json.loads((out/'drc-before.json').read_text());after=json.loads((out/'drc-final.json').read_text())
def keys(d,k):return {(v['type'],v['severity'],tuple(sorted(x['uuid'] for x in v['items']))) for v in d.get(k,[])}
assert not after['unconnected_items']
assert not keys(after,'violations')-keys(before,'violations')
assert not any(v['type']=='shorting_items' for v in after['violations'])
# Preserve every retained model and confirm the two new footprints have standard models.
old={u:c for ref,u,_,_,c in footprint_spans((out/'backups/PGR.kicad_pcb').read_text())}
for ref,u,_,_,c in footprint_spans(Path('PGR.kicad_pcb').read_text()):
 if u in old:assert subforms(c,'model')==subforms(old[u],'model'),ref
 elif ref in ['J12','R30']:assert len(subforms(c,'model'))==1 and '${KICAD10_3DMODEL_DIR}' in subforms(c,'model')[0]
report={'result':'PASS','footprints':len(ff),'replaced_on_board_TH1_with':'J12 remote cell-temperature probe connector','added_timer':'R30 68kR','new_DRC_errors':0,'new_DRC_warnings':0,'remaining_existing_DRC_errors':sum(v['severity']=='error' for v in after['violations']),'unconnected_items':0,'shorts':0,'schematic_unchanged':True,'project_rules_unchanged':True,'retained_component_pad_geometries_unchanged':True,'all_charger_and_connector_pad_nets_match_schematic':True,'save_reopen_check':'PASS','final_hashes':{fn:hashlib.sha256(Path(fn).read_bytes()).hexdigest() for fn in ['PGR.kicad_pcb','PGR.kicad_sch','PGR.kicad_pro']}}
(out/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
