from pathlib import Path
import hashlib,json,xml.etree.ElementTree as E,re
out=Path('build/solar-schematic')
def net(path):
 r=E.parse(path).getroot();ns={n.get('name'):frozenset((p.get('ref'),p.get('pin')) for p in n.findall('node')) for n in r.findall('.//nets/net')};return r,ns,{p:n for n,ps in ns.items() for p in ps}
b,bns,bp=net(out/'netlist-before.xml');a,ans,ap=net(out/'netlist-after.xml')
assert ap['U1','6']=='PWR_OUT'
assert ap['U1','5']=='GND'
assert ans[ap['U1','14']]==frozenset([('U1','14'),('R30','2')])
assert ap['R30','1']=='GND'
assert ans[ap['U1','1']]==frozenset([('U1','1'),('J12','1'),('TH1','1')])
assert ap['J12','2']=='GND'
assert ap['IC1','3']==ap['D1','1']==ap['D2','1']=='+5V'
assert ap['IC1','2']==ap['U5','2']=='+3.3V'
# Exact unchanged circuit-node relationships outside intended charger controls.
controls={('U1','5'),('U1','6'),('U1','14'),('J12','1'),('J12','2'),('R30','1'),('R30','2')}
def memberships(ns,p):return ns[p]-controls
for p in set(bp)-controls:
 assert memberships(bns,bp[p])==memberships(ans,ap[p]),p
comps={x.get('ref'):x for x in a.findall('.//components/comp')}
assert set(comps)-{x.get('ref') for x in b.findall('.//components/comp')}=={'J12','R30'}
assert comps['R1'].findtext('value')=='2kR'
assert comps['R30'].findtext('value')=='68kR'
s=Path('PGR.kicad_sch').read_text();m=re.search(r'\(symbol\s*\(lib_id "Device:Thermistor_NTC"\)(.*?)\(property "Reference" "TH1"',s,re.S);assert m
assert '(on_board no)' in m[1] and '(in_pos_files no)' in m[1]
for f in ['PGR.kicad_pcb','PGR.kicad_pro']:
 assert Path(f).read_bytes()==(out/'backups'/f).read_bytes(),f
before=json.loads((out/'erc-before.json').read_text());after=json.loads((out/'erc-after.json').read_text())
def issues(o):return {(v['severity'],v['type'],tuple(sorted(i['uuid'] for i in v['items']))) for sh in o['sheets'] for v in sh.get('violations',[])}
assert not (issues(after)-issues(before))
report={'result':'PASS','new_ERC_findings':0,'existing_ERC_errors':sum(x[0]=='error' for x in issues(after)),'PCB_byte_identical':True,'project_byte_identical':True,'all_unrelated_circuit_node_relationships_unchanged':True,'added_board_parts':['R30 68kR timer','J12 remote NTC connector'],'TH1_off_board':True,'input_limit_max_A':0.5,'input_DPM_typ_V':4.5,'charge_target_typ_A':890/2000,'fast_charge_timer_typ_hours':10*68*48/3600,'precharge_timer_typ_minutes':68*48/60,'final_hashes':{f:hashlib.sha256(Path(f).read_bytes()).hexdigest() for f in ['PGR.kicad_sch','PGR.kicad_pcb','PGR.kicad_pro']}}
(out/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
