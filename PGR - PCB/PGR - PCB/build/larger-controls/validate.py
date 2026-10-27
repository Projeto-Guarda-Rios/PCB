from pathlib import Path
import json,xml.etree.ElementTree as E,sexpdata as sx,hashlib
r=Path.cwd();o=r/'build/larger-controls';changed={'SW1','SW2','SW4'}
def nets(f):return {n.get('name'):sorted((a.get('ref'),a.get('pin')) for a in n.findall('node')) for n in E.parse(f).findall('.//nets/net')}
a=nets(o/'netlist-before.xml');b=nets(o/'netlist-after.xml');nc=b.pop('unconnected-(SW4-C-Pad3)');assert nc==[('SW4','3')];assert a==b
sub=lambda n,k:[x for x in n if isinstance(x,list) and x and str(x[0])==k]
def footprints(f):
 z=sx.loads(f.read_text());return {next(p[2] for p in sub(x,'property') if p[1]=='Reference'):x for x in sub(z,'footprint')}
old=footprints(o/'backups/PGR.kicad_pcb');new=footprints(r/'PGR.kicad_pcb');assert old.keys()==new.keys()
def normalized(z):
 if not isinstance(z,list):return z
 out=[normalized(x) for x in z]
 if out and str(out[0])=='font' and not sub(out,'thickness'):out.append([sx.Symbol('thickness'),.15])
 return out
for ref in old.keys()-changed:assert normalized(old[ref])==normalized(new[ref]),ref
for ref in changed:
 p={x[1]:x[2] for x in sub(new[ref],'property')};assert p['LCSC'];assert p['MPN']
e=json.loads((o/'erc.json').read_text());ev=[v for s in e['sheets'] for v in s['violations']];assert not ev,ev
d0=json.loads((o/'drc-before.json').read_text());d1=json.loads((o/'drc-after.json').read_text())
key=lambda v:(v['type'],tuple(sorted(x['description'] for x in v.get('items',[]))))
assert sorted(map(key,d0['violations']))==sorted(map(key,d1['violations']))
result={'replaced':sorted(changed),'other_footprints_unchanged':len(old)-3,'original_electrical_connections_unchanged':True,'new_unused_SW4_terminal':3,'ERC_violations':0,'DRC_violations_before':len(d0['violations']),'DRC_violations_after':len(d1['violations']),'new_DRC_violations':0,'unconnected_items_before':len(d0['unconnected_items']),'unconnected_items_after':len(d1['unconnected_items']),'unconnected_increase':'Four additional pads from four-terminal tactile switches; PCB still unrouted','sha256':{f:hashlib.sha256((r/f).read_bytes()).hexdigest() for f in ['PGR.kicad_sch','PGR.kicad_pcb']}}
(o/'validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
