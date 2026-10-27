from pathlib import Path
import os,subprocess,hashlib,json,xml.etree.ElementTree as E
root=Path(__file__).resolve().parents[2];out=Path(__file__).resolve().parent
cli='/home/dauwt/.backplane-bend/kicad/10.0.6/bin/kicad-cli';env=os.environ|{'KICAD10_SYMBOL_DIR':'/usr/share/kicad/symbols','KICAD10_FOOTPRINT_DIR':'/usr/share/kicad/footprints'}
for name,args in [('erc',['sch','erc','--format','json','--severity-all','--output',str(out/'erc.json')]),('netlist',['sch','export','netlist','--format','kicadxml','--output',str(out/'netlist.xml')]),('svg',['sch','export','svg','--output',str(out/'svg')])]:
 p=subprocess.run([cli,*args,str(root/'PGR.kicad_sch')],cwd=root,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);(out/(name+'.log')).write_text(p.stdout);p.check_returncode()
r=E.parse(out/'netlist.xml');comps={c.get('ref'):c for c in r.findall('.//components/comp')}
pins={ref:{} for ref in comps}
for n in r.findall('.//nets/net'):
 for a in n:pins[a.get('ref')][a.get('pin')]=n.get('name')
rows=[]
for ref,c in sorted(comps.items(),key=lambda a:(a[0].rstrip('0123456789'),int(''.join(filter(str.isdigit,a[0])) or 0))):
 fs={a.get('name'):a.text for a in c.findall('./fields/field')};rows.append({'ref':ref,'value':c.findtext('value'),'footprint':c.findtext('footprint'),'fields':fs,'pins':pins[ref]})
(out/'components.json').write_text(json.dumps(rows,indent=2))
(out/'components.txt').write_text('\n'.join(f"{x['ref']} {x['value']} [{x['footprint']}] {x['fields'].get('MPN',x['fields'].get('MP',''))} {x['pins']}" for x in rows))
print('SHA256',hashlib.sha256((root/'PGR.kicad_sch').read_bytes()).hexdigest())
print('Components',len(comps),'Nets',len(r.findall('.//nets/net')))
for s in json.loads((out/'erc.json').read_text())['sheets']:
 for v in s['violations']:print(v['severity'],v['type'],v['description'],[i['description'] for i in v['items']])
