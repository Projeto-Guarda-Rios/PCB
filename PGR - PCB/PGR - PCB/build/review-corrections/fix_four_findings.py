from pathlib import Path
import sys,uuid,copy,re,json,hashlib,shutil
import sexpdata as sx
sys.path.insert(0,str(Path('build/reliability-fixes/ipc').resolve()));import client
client.SOCKET='/tmp/pgr-visible-restore.sock'
from client import API,types,project,Empty
api=API();d=api.open(types.DOCTYPE_SCHEMATIC);api.request(project.CloseDocument(document=d),Empty)
P=Path('PGR.kicad_sch');original=P.read_text();root=sx.loads(original);S=sx.Symbol
sub=lambda n,k:[a for a in n if isinstance(a,list) and a and str(a[0])==k]
ch=lambda n,k:sub(n,k)[0]
props=lambda n:{a[1]:a for a in sub(n,'property')}
ss={props(n)['Reference'][2]:n for n in sub(root,'symbol')}
for f in ['PGR.kicad_sch','PGR.kicad_pro','PGR.kicad_pcb','symbols/PGR_Validated.kicad_sym']:
 shutil.copy2(f,Path('build/review-corrections/backups')/Path(f).name)
Path('build/review-corrections/before-hashes.json').write_text(json.dumps({f:hashlib.sha256(Path(f).read_bytes()).hexdigest() for f in ['PGR.kicad_sch','PGR.kicad_pro','PGR.kicad_pcb']},indent=2))
new=[];removed=set();changed={};changed_definitions=[]
def uid():return str(uuid.uuid4())
def translate(n,dx,dy):
 at=ch(n,'at');at[1]=round(at[1]+dx,5);at[2]=round(at[2]+dy,5)
 for f in sub(n,'property'):
  at=ch(f,'at');at[1]=round(at[1]+dx,5);at[2]=round(at[2]+dy,5)
 return n

def edit(ref):
 n=copy.deepcopy(ss[ref]);changed[ch(n,'uuid')[1]]=n;return n

def field(n,name,value):
 ps=props(n)
 if name in ps:ps[name][2]=value;return
 x,y=ch(n,'at')[1:3];n.append([S('property'),name,value,[S('at'),x,y,0],[S('hide'),S('yes')],[S('effects'),[S('font'),[S('size'),1.27,1.27]]]])

def clone(ref,newref,x,y,angle=None):
 n=copy.deepcopy(ss[ref]);ox,oy=ch(n,'at')[1:3];translate(n,x-ox,y-oy);ch(n,'uuid')[1]=uid();props(n)['Reference'][2]=newref
 if angle is not None:ch(n,'at')[3]=angle
 for pin in sub(n,'pin'):ch(pin,'uuid')[1]=uid()
 def walk(t):
  if isinstance(t,list):
   if t and str(t[0])=='reference':t[1]=newref
   for v in t:walk(v)
 walk(n);new.append(n);return n

def label(name,x,y,angle=0):
 template=copy.deepcopy(sub(root,'global_label')[0]);template[1]=name;ch(template,'at')[1:]=[x,y,angle];ch(template,'uuid')[1]=uid()
 eff=ch(template,'effects');j=sub(eff,'justify')
 if j:j[0][1:]=[S('right' if angle==180 else 'left')]
 else:eff.append([S('justify'),S('right' if angle==180 else 'left')])
 for f in sub(template,'property'):ch(f,'at')[1:]=[x,y,0]
 new.append(template);return template

def wire(a,b):new.append([S('wire'),[S('pts'),[S('xy'),*a],[S('xy'),*b]],[S('stroke'),[S('width'),0],[S('type'),S('default')]],[S('uuid'),uid()]])
def text(msg,x,y):new.append([S('text'),msg,[S('at'),x,y,0],[S('effects'),[S('font'),[S('size'),1,1]],[S('justify'),S('left'),S('top')]],[S('uuid'),uid()]])
def labels_at(x,y,name=None):
 return [n for n in sub(root,'global_label') if abs(ch(n,'at')[1]-x)<.001 and abs(ch(n,'at')[2]-y)<.001 and (name is None or n[1]==name)]
def rename_at(x,y,name):
 ls=labels_at(x,y);assert len(ls)==1,(x,y,ls)
 n=copy.deepcopy(ls[0]);n[1]=name;changed[ch(n,'uuid')[1]]=n
# 1. Battery switch now controls Q7 base drive; two P-channel FETs interrupt both directions.
# Raw cell negative no longer passes through the small switch.
for n in sub(root,'global_label'):
 if n[1]=='CELL_N':
  z=copy.deepcopy(n);z[1]='BMS_NEG';changed[ch(z,'uuid')[1]]=z
# SW4 pin stubs keep their current positions and exact drawing geometry.
# Existing switch pin1 is left, pin2 right.
sw=ss['SW4'];sx0,sy0=ch(sw,'at')[1:3]
for n in sub(root,'global_label'):
 at=ch(n,'at')
 if abs(at[2]-sy0)<.001 and abs(at[1]-sx0)<12 and n[1] in ['BMS_NEG','CELL_N']:
  z=copy.deepcopy(n);z[1]='CELL_FUSED' if at[1]<sx0 else 'SW_FEED';changed[ch(z,'uuid')[1]]=z
n=edit('SW4');field(n,'Value','BATTERY ENABLE');field(n,'MPN','CHS-01A');field(n,'Manufacturer','Nidec Components');field(n,'Footprint','Button_Switch_SMD:SW_DIP_SPSTx01_Slide_Copal_CHS-01A_W5.08mm_P1.27mm_JPin');field(n,'Datasheet','https://www.nidec-components.com/e/catalog/switch/chs.pdf');field(n,'Rating','100mA at 6VDC; actual control current <40uA; not in battery current path')
# Q4 gate/source pullup follows common source; Q9 is opposite-facing, common-source/common-gate.
n=edit('Q4');field(n,'Value','DMP2035U');field(n,'MPN','DMP2035U-7');field(n,'Manufacturer','Diodes Incorporated');field(n,'Datasheet','https://www.diodes.com/datasheet/download/DMP2035U.pdf');field(n,'Description','20V P-channel MOSFET; G1 S2 D3; max45mOhm at VGS=-2.5V')
# Q4 source used to have a downward stub with BAT_PROTECTED label.
for n in sub(root,'wire'):
 pts=ch(n,'pts')[1:];xy=[tuple(t[1:]) for t in pts]
 if (340.36,358.14) in xy and (340.36,360.68) in xy:removed.add(ch(n,'uuid')[1])
for n in labels_at(340.36,360.68,'BAT_PROTECTED'):removed.add(ch(n,'uuid')[1])
wire((340.36,358.14),(340.36,363.22));wire((340.36,360.68),(346.71,360.68));label('BAT_SWITCH_MID',346.71,360.68)
new.append([S('junction'),[S('at'),340.36,360.68],[S('diameter'),0],[S('color'),0,0,0,0],[S('uuid'),uid()]])
# R53 source pull-up top label and R54 switch feed top label.
rename_at(365.76,344.17,'BAT_SWITCH_MID');rename_at(365.76,369.57,'SW_FEED')
n=clone('Q4','Q9',342.9,368.3,180);field(n,'Value','DMP2035U');field(n,'MPN','DMP2035U-7');field(n,'Manufacturer','Diodes Incorporated');field(n,'Datasheet','https://www.diodes.com/datasheet/download/DMP2035U.pdf');field(n,'Description','20V P-channel MOSFET; G1 S2 D3; common-source with Q4')
for f,y in [('Reference',369.57),('Value',372.11)]:ch(props(n)[f],'at')[1:]=[353.06,y,0]
# Q9 source2=340.36,363.22; drain3=340.36,373.38; gate1=347.98,368.30.
wire((340.36,373.38),(340.36,377.19));label('BAT_PROTECTED',340.36,377.19)
wire((347.98,368.3),(347.98,364.49));label('BAT_GATE',347.98,364.49)
# Move only Q5 and its attached stubs/power labels to clear the added Q9.
q5=ss['Q5'];ox,oy=ch(q5,'at')[1:3];dx=-22.86;n=edit('Q5');translate(n,dx,0)
for x in sub(root,'wire'):
 pts=ch(x,'pts')[1:]
 if all(327<=pt[1]<=341 and 373<=pt[2]<=389 for pt in pts):
  z=copy.deepcopy(x)
  for pt in ch(z,'pts')[1:]:pt[1]=round(pt[1]+dx,2)
  changed[ch(z,'uuid')[1]]=z
for x in sub(root,'global_label'):
 at=ch(x,'at')
 if x[1] in ['SOLAR_RAW','VBUS','GND'] and 327<=at[1]<=341 and 373<=at[2]<=389:
  z=copy.deepcopy(x);ch(z,'at')[1]=round(at[1]+dx,2);changed[ch(z,'uuid')[1]]=z
# R73 guarantees Q7 off when the small switch opens.
n=clone('R53','R73',403.86,391.16);field(n,'Value','100kR');field(n,'MPN','RC0603FR-07100KL');field(n,'Manufacturer','Yageo');field(n,'Tolerance','1%')
for f,y in [('Reference',389.89),('Value',392.43)]:ch(props(n)[f],'at')[1:]=[406.4,y,0]
wire((403.86,387.35),(403.86,384.81));label('BAT_DETECT',403.86,384.81)
wire((403.86,394.97),(403.86,397.51));label('BMS_NEG',403.86,397.51)
for n in sub(root,'text'):
 if n[1].startswith('Q4 gate turns on'):
  z=copy.deepcopy(n);z[1]='Q4/Q9: back-to-back battery switch and reverse-polarity protection.\nSW4 carries <40uA control current; OFF blocks charge and discharge.\nJ10: regulated 5 V panel; respect 10.2 V maximum open circuit.';changed[ch(z,'uuid')[1]]=z
# 2. UART RX source selector: 1=CP2102 TX, 2=ESP RX, 3=external adapter TX.
# Label nearest U4 TXD pin26; pin anchor/line positions were preserved by user formatting.
for n in sub(root,'global_label'):
 if n[1]=='TXD0':
  x,y=ch(n,'at')[1:3]
  if 140<x<180 and 70<y<120:
   z=copy.deepcopy(n);z[1]='CP2102_TX';changed[ch(z,'uuid')[1]]=z
  elif 200<x<230 and 185<y<205:
   z=copy.deepcopy(n);z[1]='EXT_UART_TX';changed[ch(z,'uuid')[1]]=z
# Complete stock jumper symbol, unchanged pin table.
stock=sx.loads(Path('/usr/share/kicad/symbols/Jumper.kicad_sym').read_text());definition=copy.deepcopy(next(n for n in sub(stock,'symbol') if n[1]=='Jumper_3_Bridged12'));definition[1]='PGR_Validated:Jumper_3_Bridged12';ch(root,'lib_symbols').append(definition);changed_definitions.append(definition)
rootuuid=ch(root,'uuid')[1];n=[S('symbol'),[S('lib_id'),'PGR_Validated:Jumper_3_Bridged12'],[S('at'),238.76,201.93,0],[S('unit'),1],[S('in_bom'),S('yes')],[S('on_board'),S('yes')],[S('dnp'),S('no')],[S('uuid'),uid()],[S('instances'),[S('project'),'PGR',[S('path'),'/'+rootuuid,[S('reference'),'JP1'],[S('unit'),1]]]]]
for name,val,y in [('Reference','JP1',194.31),('Value','RX SELECT',196.85),('Footprint','Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical',201.93),('Datasheet','',201.93)]:
 prop=[S('property'),name,val,[S('at'),238.76,y,0],[S('effects'),[S('font'),[S('size'),1.27,1.27]]]]
 if name in ['Footprint','Datasheet']:prop.append([S('hide'),S('yes')])
 n.append(prop)
field(n,'MPN','M20-9990345');field(n,'Manufacturer','Harwin');field(n,'Assembly','Fit one 2.54mm shunt 1-2 for USB, move to 2-3 for external UART. Never bridge all three pins.');new.append(n)
wire((233.68,201.93),(229.87,201.93));label('CP2102_TX',229.87,201.93,180)
wire((243.84,201.93),(247.65,201.93));label('EXT_UART_TX',247.65,201.93)
wire((238.76,205.74),(238.76,207.01));label('TXD0',238.76,207.01)
text('JP1: 1-2 USB default; 2-3 external UART. Fit ONE shunt only.',172.72,170.18)
# 3. Remote probe belongs in the harness BOM, not on the board.
n=edit('TH1');ch(n,'on_board')[1]=S('no');field(n,'Assembly','Offboard insulated cell probe connected through J12. Not placed on PCB.')
# 4. Pin-compatible local USB footprint freezes shield pad name S1.
n=edit('J9');field(n,'Footprint','PGR-FootPrints:USB_C_GCT_USB4105_PGR')
fp=Path('/usr/share/kicad/footprints/Connector_USB.pretty/USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal.kicad_mod').read_text();fp=fp.replace('(footprint "USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal"','(footprint "USB_C_GCT_USB4105_PGR"',1).replace('(pad "SH"','(pad "S1"');Path('PGR-FootPrints.pretty/USB_C_GCT_USB4105_PGR.kicad_mod').write_text(fp)
# Preserve all original forms unless specifically edited. Append only new definitions/items.
def end(s,a):
 depth=0;quote=False;esc=False
 for i in range(a,len(s)):
  c=s[i]
  if quote:
   if esc:esc=False
   elif c=='\\':esc=True
   elif c=='"':quote=False
  elif c=='"':quote=True
  elif c=='(':depth+=1
  elif c==')':
   depth-=1
   if depth==0:return i+1
replacements=[]
for m in re.finditer(r'^\t\((symbol|global_label|wire|text|junction)\b',original,re.M):
 a=m.start();b=end(original,original.index('(',a));item=sx.loads(original[a:b]);ids=sub(item,'uuid')
 if not ids:continue
 key=ids[0][1]
 if key in removed:replacements.append((a,b,''))
 elif key in changed:replacements.append((a,b,sx.dumps(changed[key])))
# Add new complete jumper definition to the embedded cache and the same local library.
start=original.index('\t(lib_symbols');stop=end(original,original.index('(',start));cache=sx.loads(original[start:stop]);cache.extend(changed_definitions);replacements.append((start,stop,sx.dumps(cache)))
for a,b,t in sorted(replacements,reverse=True):original=original[:a]+t+original[b:]
idx=original.rfind(')');original=original[:idx]+'\n'+'\n'.join(sx.dumps(n) for n in new)+'\n'+original[idx:];P.write_text(original)
libp=Path('symbols/PGR_Validated.kicad_sym');lib=sx.loads(libp.read_text())
for n in changed_definitions:
 z=copy.deepcopy(n);z[1]=z[1].split(':',1)[1];lib[:]=[v for v in lib if not isinstance(v,list) or not v or str(v[0])!='symbol' or v[1]!=z[1]];lib.append(z)
libp.write_text(sx.dumps(lib)+'\n');d=api.open(types.DOCTYPE_SCHEMATIC);api.save(d)
print('Corrected four findings, added Q9/R73/JP1; preserved existing board and project files.')
