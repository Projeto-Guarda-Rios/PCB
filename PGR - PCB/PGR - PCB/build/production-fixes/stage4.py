from helper import *
# Correct the diode stubs for a 180-degree symbol rotation. Pin numbers stay unchanged.
for x in items:
 if isinstance(x,sch.SchematicLine) and xy(x.start) in [pin(ss['D14'],'1'),pin(ss['D14'],'2')]:deletes.add(x.id.value)
 elif isinstance(x,sch.LocalLabel) and xy(x.position)==(264.16,365.76):deletes.add(x.id.value)
wire(pin(ss['D14'],'1'),(271.78,365.76));label('+5V',(271.78,365.76))
wire(pin(ss['D14'],'2'),(256.54,365.76));label('BUZZ_SW',(256.54,365.76))
# The reverse-polarity gate detector uses the switched cell-negative domain.
# This avoids a control-current path around the battery disconnect switch.
for p in [(396.24,361.95),(401.32,375.92)]:
 for x in items:
  if isinstance(x,sch.LocalLabel) and xy(x.position)==p and x.text.text=='CELL_N':
   q=clone(x);q.text.text='BMS_NEG';upd['rename'+x.id.value]=q
label('BMS_NEG',pin(ss['SW4'],'1'))
# Explicit charge termination at about 24mA, compatible with the NIMO standard charge.
p=pin(ss['U1'],'15');remove_at(p);label('ITERM_SET',p)
z=passive('R72',(566.42,104.14),'1.6kR','ITERM_SET','GND');field(z,'Tolerance','1%')
# Resolve leftover labels/wires from the earlier direct connector drawings.
erc=__import__('json').load(open('build/production-fixes/erc-stage3.json'))
for sheet in erc['sheets']:
 for violation in sheet['violations']:
  if violation['type'] in ['label_dangling','unconnected_wire_endpoint']:
   for entry in violation['items']:deletes.add(entry['uuid'])
# A power-good signal is reserved as an explicit no-connect, rather than an isolated label.
p=pin(ss['U3'],'5');remove_at(p)
for x in items:
 if isinstance(x,sch.LocalLabel) and x.text.text=='BOOST_PG':deletes.add(x.id.value)
new.append(sch.NoConnectMarker(id=uid(),position=v(*p)))
# Single sheet: use one label scope consistently and remove the GPIO35 alias ambiguity.
for x in items:
 if isinstance(x,sch.GlobalLabel) and x.id.value not in deletes:
  deletes.add(x.id.value)
  label('USB_ACTIVE' if x.text.text=='IO35' else x.text.text,xy(x.position),left=x.spin_style==sch.SLSS_LEFT)
# Power flags declare the actual sources and passive protected-ground domains.
def flag(ref,p,name):
 f=component('stock:#FLG01',ref,p)
 f.reference_field.visible=False;f.value_field.text.position.CopyFrom(v(p[0],p[1]-3.81));f.value_field.text.attributes.size.CopyFrom(v(1.0,1.0));label(name,p)
flag('#FLG01',(251.46,264.16),'+3.3V')
flag('#FLG02',(314.96,264.16),'+5V_PROGRAM')
flag('#FLG03',(426.72,391.16),'VBUS')
flag('#FLG04',(294.64,179.07),'GND')
flag('#FLG05',(492.76,173.99),'BMS_NEG')
flag('#FLG06',(469.9,151.13),'BMS_VCC');label('BMS_VCC',pin(ss['U6'],'5'))
# Guarantee adequate effective BQ battery/input capacitance, not just nominal 4.7uF.
for ref in ['C5','C11']:
 z=sym(ref);z.value_field.text.text='22uF';z.footprint_field.text.text='Capacitor_SMD:C_1210_3225Metric';field(z,'MPN','C3225X7R1C226M250AC');field(z,'Manufacturer','TDK');field(z,'Rating','16V X7R +/-20%; verify effective C >=4.7uF')
# Correct references after configurable UART pin allocation.
field(sym('U5'),'Firmware_pin_contract','RS485 RX4 TX5 DE22 /RE23; modem TX17 RX16 EN25 UART_OE27; AquaNode EN26; tamper GPIO33; battery ADC36; NTC ADC39; USB status35')
commit('Verify protected domains, termination current, diode polarity, and ERC supply declarations')
