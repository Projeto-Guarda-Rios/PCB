from pathlib import Path
import sexpdata as sx,xml.etree.ElementTree as E,json,hashlib,collections
root=Path(__file__).resolve().parents[2];out=Path(__file__).resolve().parent
r=E.parse(out/'netlist.xml');nets={n.get('name').lstrip('/'):set((a.get('ref'),a.get('pin')) for a in n) for n in r.findall('.//nets/net')};pins={p:name for name,ps in nets.items() for p in ps};c={x.get('ref'):x for x in r.findall('.//components/comp')};checks=[]
def check(msg,v):assert v,msg;checks.append(msg)
def expected(name,ps):check(name+' exact connections',nets[name]==set(ps))
expected('BAT_SWITCH_MID',[('Q4','2'),('Q9','2'),('R53','1')])
expected('BAT_GATE',[('Q4','1'),('Q9','1'),('Q7','3'),('R53','2')])
expected('CELL_FUSED',[('F1','2'),('Q4','3'),('SW4','1')])
expected('SW_FEED',[('SW4','2'),('R54','1')])
expected('CP2102_TX',[('U4','26'),('JP1','1')])
expected('EXT_UART_TX',[('J14','4'),('JP1','3')])
expected('TXD0',[('U5','34'),('JP1','2')])
check('SW4 has no terminal in battery negative path',pins['SW4','1']!='BMS_NEG' and pins['SW4','2']!='BMS_NEG')
# Verify no unrelated pin changes from the user's formatted schematic.
old=E.parse(root/'build/final-schematic-review/netlist.xml');op={(a.get('ref'),a.get('pin')):n.get('name').lstrip('/') for n in old.findall('.//nets/net') for a in n}
intent={('BT1','2'):'BMS_NEG',('Q4','2'):'BAT_SWITCH_MID',('R53','1'):'BAT_SWITCH_MID',('SW4','1'):'CELL_FUSED',('SW4','2'):'SW_FEED',('R54','1'):'SW_FEED',('U4','26'):'CP2102_TX',('J14','4'):'EXT_UART_TX'}
for p,name in op.items():check('Preserved/intentional pin '+str(p),pins[p]==intent.get(p,name))
# OFF: the P-channel body diodes both point from drains into the common source.
off_edges=[(pins['Q4','3'],pins['Q4','2']),(pins['Q9','3'],pins['Q9','2'])]
def reachable(start,end,edges):
 seen={start};q=[start]
 while q:
  n=q.pop()
  for a,b in edges:
   if a==n and b not in seen:seen.add(b);q.append(b)
 return end in seen
check('OFF body diodes block cell-to-charger conduction',not reachable('CELL_FUSED','BAT_PROTECTED',off_edges))
check('OFF body diodes block charger-to-cell conduction',not reachable('BAT_PROTECTED','CELL_FUSED',off_edges))
on_edges=off_edges+[(b,a) for a,b in off_edges]
check('ON channels allow charge and discharge',reachable('CELL_FUSED','BAT_PROTECTED',on_edges) and reachable('BAT_PROTECTED','CELL_FUSED',on_edges))
# A single 2-pin shunt joins exactly one transmitter to the ESP receive input.
check('USB selector 1-2 leaves external TX isolated',pins['JP1','1']!=pins['JP1','3'] and pins['JP1','2']=='TXD0')
check('External selector 2-3 leaves CP2102 TX isolated',pins['JP1','3']!=pins['JP1','1'])
calc={'switch_max_control_current_A':(4.25-.5)/(100000*.99),'Q7_min_base_current_A':(3.0-1.0)/(100000*1.01)-1.0/(100000*.99),'Q7_gate_pullup_sink_A':4.4/(100000*.99),'pair_max_Ron_ohm_at_2_5V_25C':2*.045,'pair_loss_W_at_1_84A_25C':1.84**2*(2*.045),'pair_voltage_drop_V_at_1_84A_25C':1.84*(2*.045)}
check('Switch control current within 100mA rating',calc['switch_max_control_current_A']<.1)
check('Q7 base drive has forced beta below 10',calc['Q7_gate_pullup_sink_A']/calc['Q7_min_base_current_A']<10)
# Footprint existence plus active pin/pad compatibility.
sub=lambda n,k:[a for a in n if isinstance(a,list) and a and str(a[0])==k]
ft=sx.loads((root/'fp-lib-table').read_text());paths={}
for n in sub(ft,'lib'):
 d={str(a[0]):a[1] for a in n[1:] if isinstance(a,list)};paths[d['name']]=Path(d['uri'].replace('${KIPRJMOD}',str(root)))
for ref,comp in c.items():
 fp=comp.findtext('footprint')
 if not fp:continue
 lib,entry=fp.split(':',1);p=paths.get(lib,Path('/usr/share/kicad/footprints')/(lib+'.pretty'))/(entry+'.kicad_mod');check(ref+' footprint exists',p.exists());f=sx.loads(p.read_text());padnums={str(a[1]) for a in sub(f,'pad')}
 used={pin for (rr,pin),name in pins.items() if rr==ref and not name.startswith('unconnected-')}
 check(ref+' used pins have matching footprint pads',not(used-padnums))
# Native metadata and unchanged user files.
native=sx.loads((root/'PGR.kicad_sch').read_text());ns={next(p[2] for p in sub(n,'property') if p[1]=='Reference'):n for n in sub(native,'symbol')}
check('TH1 remains in BOM',sub(ns['TH1'],'in_bom')[0][1]==sx.Symbol('yes'))
check('TH1 excluded from PCB',sub(ns['TH1'],'on_board')[0][1]==sx.Symbol('no'))
check('TH1 has no footprint',not c['TH1'].findtext('footprint'))
check('J9 uses project-local frozen footprint',c['J9'].findtext('footprint')=='PGR-FootPrints:USB_C_GCT_USB4105_PGR')
oldcomp={x.get('ref'):x for x in old.findall('.//components/comp')}
for ref,comp in oldcomp.items():
 if ref not in ['J9','SW4']:check(ref+' user footprint preserved',comp.findtext('footprint')==c[ref].findtext('footprint'))
before=json.loads((out/'before-hashes.json').read_text())
for name in ['PGR.kicad_pro','PGR.kicad_pcb']:check(name+' unchanged from start of corrections',hashlib.sha256((root/name).read_bytes()).hexdigest()==before[name])
violations=[v for s in json.loads((out/'erc.json').read_text())['sheets'] for v in s['violations']];check('Zero ERC violations',len(violations)==0)
result={'result':'PASS','decision':'SCHEMATIC_READY_FOR_PROTOTYPE_LAYOUT','check_count':len(checks),'checks':checks,'calculations':calc,'schematic_sha256':hashlib.sha256((root/'PGR.kicad_sch').read_bytes()).hexdigest(),'closed_findings':['SW4_CURRENT_RATING','UART_DEBUG_CONTENTION','OFFBOARD_PROBE_FLAG','USB_SHIELD_LIBRARY_RENUMBERING'],'layout_notes':['Route the common source connection between Q4/Q9 as a short high-current node. Allow copper area for thermal performance; resistor/logic switch traces carry microamps.','JP1 must have exactly one shunt fitted. Default 1-2 selects USB programming; 2-3 selects external UART.','Use the project-local USB footprint with S1 shield pads.','Do not import TH1 as a PCB component.'],'limitations':['These are schematic, connectivity and static design checks, not hardware measurements.','Prototype tests must still verify power transitions, modem bursts, temperature trips, programming and actual cable/panel performance.'],'sources':['https://www.diodes.com/datasheet/download/DMP2035U.pdf','https://www.nidec-components.com/e/catalog/switch/chs.pdf','https://www.harwin.com/products/M20-9990345','https://www.harwin.com/products/M7567-05']}
(out/'closure.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS',len(checks),'correction checks;',len(c),'components;',len(nets),'nets; zero ERC violations; board/project preserved.')
