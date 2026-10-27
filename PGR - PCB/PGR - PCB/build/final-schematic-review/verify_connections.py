"""Validate intended schematic connectivity and conservative design calculations.
This checks design intent against KiCad's independently exported netlist, not API state.
"""
from pathlib import Path
import xml.etree.ElementTree as E,json,math,itertools,hashlib
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
r=E.parse(OUT/'netlist.xml');pins={(a.get('ref'),a.get('pin')):n.get('name').lstrip('/') for n in r.findall('.//nets/net') for a in n}
comps={a.get('ref'):a for a in r.findall('.//components/comp')};checks=[]
def check(name,ok):
 assert ok,name
 checks.append(name)
def expect(ref,mapping):
 for pin,net in mapping.items():check(f'{ref}.{pin} = {net}',pins[(ref,str(pin))]==net)
expect('U1',{13:'VBUS',2:'BAT_PROTECTED',3:'BAT_PROTECTED',10:'PWR_OUT',11:'PWR_OUT',6:'PWR_OUT',5:'GND',4:'CHG_CE',1:'TS_FIXED',15:'ITERM_SET',7:'IO34',9:'IO21',8:'GND',17:'GND'})
expect('U3',{10:'PWR_OUT',1:'BOOST_SW',2:'BOOST_SW',3:'BOOST_5V',4:'BOOST_5V',7:'BOOST_FB',9:'BOOST_EN',8:'BOOST_HYS',6:'BOOST_SS',11:'GND'})
expect('IC1',{4:'+5V',1:'+5V',3:'BUCK_SW',5:'BUCK_FB',2:'GND'})
expect('U7',{3:'BOOST_5V',5:'BOOST_5V',6:'USB_LIMIT',4:'BOOST_PR',2:'+5V',7:'+5V',8:'BOOST_ACTIVE',1:'GND'})
for ref,en,out,ilim,slew in [('U9','IO25','MODEM_5V','U9_ILIM','U9_SLEW'),('U10','IO26','NODE_5V','U10_ILIM','U10_SLEW'),('U11','+5V_PROGRAM','USB_LIMIT','USB_ILIM','USB_SLEW')]:
 expect(ref,{1:'+5V_PROGRAM' if ref=='U11' else '+5V',3:en,6:out,4:ilim,5:slew,2:'GND'})
for cap,slew,rail in [('C21','USB_SLEW','+5V_PROGRAM'),('C23','U9_SLEW','+5V'),('C24','U10_SLEW','+5V')]:expect(cap,{1:slew,2:rail})
expect('U12',{1:'EN',3:'+3.3V',5:'+3.3V',6:'+3.3V',2:'GND'})
expect('U13',{3:'BAT_NTC',4:'NTC_HOT',1:'TEMP_OK',5:'+3.3V',2:'GND'})
expect('U14',{3:'NTC_COLD',4:'BAT_NTC',1:'TEMP_OK',5:'+3.3V',2:'GND'})
expect('U15',{2:'IO17',6:'MODEM_RX',5:'MODEM_TX',3:'IO16',1:'IO27',7:'IO27',8:'+3.3V',4:'GND'})
expect('Q4',{3:'CELL_FUSED',2:'BAT_PROTECTED',1:'BAT_GATE'})
expect('Q5',{3:'SOLAR_RAW',2:'VBUS',1:'GND'})
expect('Q7',{1:'BAT_DETECT',2:'BMS_NEG',3:'BAT_GATE'})
expect('D13',{1:'BAT_DETECT',2:'BMS_NEG'})
expect('Q8',{1:'TEMP_OK',2:'GND',3:'CHG_CE'})
expect('SW4',{1:'BMS_NEG',2:'CELL_N'})
expect('BT1',{1:'CELL_P',2:'CELL_N'})
expect('F1',{1:'CELL_P',2:'CELL_FUSED'})
expect('Q1',{2:'USB_RTS',3:'EN'});expect('Q2',{2:'USB_DTR',3:'IO0_BTN'})
expect('Q6',{1:'BUZZ_B',2:'GND',3:'BUZZ_SW'});expect('D14',{1:'+5V',2:'BUZZ_SW'});expect('BZ1',{1:'+5V',2:'BUZZ_SW'})
expect('J8',{1:'GND',2:'MODEM_5V',3:'MODEM_RX',4:'MODEM_TX'})
expect('J11',{1:'RS-485-A',2:'RS-485-B',3:'NODE_5V',4:'GND'})
expect('J7',{1:'+3.3V',2:'GND',3:'TAMPER_EXT'})
expect('J13',{1:'+3.3V',2:'GND',3:'IO13',4:'IO14',5:'IO12',6:'IO15'})
expect('J14',{1:'GND',2:'+3.3V',3:'RXD0',4:'TXD0'})
expect('U5',{4:'BATT_ADC',5:'NTC_ADC',6:'IO34',7:'BOOST_ACTIVE',9:'IO33',10:'IO25',11:'IO26',12:'IO27',27:'IO16',28:'IO17',36:'IO22',37:'IO23',35:'RXD0',34:'TXD0'})
expect('U4',{6:'+3.3V',7:'+3.3V',28:'USB_DTR',24:'USB_RTS',25:'RXD0',26:'TXD0'})
expect('U8',{2:'IO23',3:'IO22',1:'IO4',4:'IO5',8:'+3.3V',5:'GND'})
# No passive or protection-control path bypasses the switched battery negative.
cell_n={(ref,pin) for (ref,pin),net in pins.items() if net=='CELL_N'}
check('Raw cell negative only reaches battery disconnect',cell_n=={('BT1','2'),('SW4','2')})
check('CHG and hardware JTAG TDO are separate',pins[('U1','9')]!=pins[('J13','6')])
check('Modem supply and UART are isolated from main rails/GPIO',pins[('J8','2')]!=pins[('U7','2')] and pins[('J8','3')]!=pins[('U5','28')] and pins[('J8','4')]!=pins[('U5','27')])
# Verify all board-assigned footprint files exist, including project custom libraries.
import sexpdata as sx
ft=sx.loads((ROOT/'fp-lib-table').read_text())
libpaths={}
for n in ft[1:]:
 if isinstance(n,list) and n and str(n[0])=='lib':
  d={str(a[0]):a[1] for a in n[1:] if isinstance(a,list)};libpaths[d['name']]=Path(d['uri'].replace('${KIPRJMOD}',str(ROOT)).replace('${KICAD10_FOOTPRINT_DIR}','/usr/share/kicad/footprints'))
for ref,c in comps.items():
 fp=c.findtext('footprint')
 if fp:
  lib,entry=fp.split(':',1);path=libpaths.get(lib,Path('/usr/share/kicad/footprints')/(lib+'.pretty'))/(entry+'.kicad_mod');check(f'{ref} footprint exists',path.is_file())
# Worst case component tolerance calculations. These are static estimates, not bench results.
calc={}
calc['boost_output_nominal_V']=1*(1+402/100)
calc['boost_output_max_PFM_V']=1.015*1.007*(1+402*1.001/(100*.999))
calc['boost_shutdown_min_V']=1.11*(1+200*.999/(110*1.001))
calc['boost_shutdown_nominal_V']=1.14*(1+200/110)
calc['boost_restart_nominal_V']=1.19*(1+200/100)
calc['usb_limit_max_A']=299/(620*.99)
calc['modem_limit_min_A']=168/(330*1.01)
calc['node_limit_min_A']=144/(1000*1.01)
calc['mux_priority_threshold_max_V']=1.08*(1+312*1.001/(100*.999))
calc['charge_current_nominal_A']=890/2000
calc['charge_current_max_A']=975/(2000*.99)
calc['termination_current_nominal_A']=.03*1600/2000
calc['battery_adc_max_V']=4.23*270*1.01/(1000*.99+270*1.01)
load=1/(1/57+1/6000)
calc['rs485_idle_min_differential_V']=4.75*load/(2*470*1.01+load)
check('Normal cutoff remains above NIMO 3.0 V minimum',calc['boost_shutdown_min_V']>3.0)
check('Boost maximum stays below 5.25 V',calc['boost_output_max_PFM_V']<5.25)
check('USB limited below 500 mA',calc['usb_limit_max_A']<.5)
check('Modem branch supports at least 500 mA',calc['modem_limit_min_A']>.5)
check('Battery ADC stays below 1 V',calc['battery_adc_max_V']<1)
check('RS485 biased idle exceeds 200 mV with two terminations',calc['rs485_idle_min_differential_V']>.2)
# NTC beta model, comparator offset plus half typical hysteresis conservatively 12 mV.
# Probe curve, self heating and thermal attachment still require prototype verification.
for label,top in [('hot',178000),('cold',43200)]:
 ts=[]
 for rb,rt,rbot,r25,beta,offset in itertools.product([.999,1.001],[.999,1.001],[.999,1.001],[.99,1.01],[3435*.99,3435*1.01],[-.012,.012]):
  f=100000*rbot/(top*rt+100000*rbot)+offset/3.135
  resistance=10000*rb*f/(1-f)
  temp=1/(1/298.15+math.log(resistance/(10000*r25))/beta)-273.15
  ts.append(temp)
 calc[f'ntc_{label}_estimated_trip_range_C']=[min(ts),max(ts)]
check('NTC model cold trip above 0 C',calc['ntc_cold_estimated_trip_range_C'][0]>0)
check('NTC model hot trip below 45 C',calc['ntc_hot_estimated_trip_range_C'][1]<45)
erc=json.loads((OUT/'erc.json').read_text());violations=[v for s in erc['sheets'] for v in s['violations']]
check('KiCad ERC has zero violations',len(violations)==0)
check('Firmware charge status pin is GPIO21', 'CHG21;' in next(a.get('value') for a in comps['U5'].findall('property') if a.get('name')=='Firmware_pin_contract'))
result={'schematic_sha256':hashlib.sha256((ROOT/'PGR.kicad_sch').read_bytes()).hexdigest(),'result':'AUTOMATED_CHECKS_PASS_MANUAL_FINDINGS_OPEN','checks':checks,'check_count':len(checks),'components':len(comps),'nets':len(r.findall('.//nets/net')),'calculations':calc,'limitations':['Manual review findings must be resolved before layout signoff; see findings.json.','Schematic checks only; PCB requires synchronization and layout validation.','No hardware measurements or simulations were performed.','NTC temperature numbers use a beta model and require probe calibration/temperature testing.','Solar autonomy and cable voltage drop await exact panel, cable and load measurements.','USB fallback is limited to under 500 mA; full modem operation needs solar/battery power.'],'sources':['https://www.ti.com/lit/ds/symlink/tps61230.pdf','https://www.ti.com/lit/ds/symlink/tps2116.pdf','https://www.ti.com/lit/ds/symlink/bq24074.pdf','https://www.microchip.com/content/dam/mchp/documents/APID/ProductDocuments/DataSheets/MIC20XX-Fixed-and-Adjustable-Current-Limiting-Power-Distribution-Switches-DS20006486B.pdf','https://docs.m5stack.com/en/unit/Unit%20NB-IoT2%28SIM7028%29','https://www.mercantilelectrico.com/archivos/bat534-ficha-tecnica.pdf','https://www.ic-fortune.com/upload/Download/FS8205A-DS-18_EN.pdf']}
(OUT/'validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['result','check_count','components','nets','calculations']},indent=2))
