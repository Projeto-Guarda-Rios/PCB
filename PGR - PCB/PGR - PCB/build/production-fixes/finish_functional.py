from helper import *
for r in ['#PWR124','#PWR127']:deletes.add(ss[r].id.value)
# Free all four hardware JTAG pins: /PGOOD belongs on input-only GPIO34.
for x in items:
 if isinstance(x,sch.LocalLabel) and x.text.text=='IO15' and xy(x.position)[0]>400:
  q=clone(x);q.text.text='IO34';upd[x.id.value]=q
# Replace the three-terminal symbol with the actual two-terminal disconnect.
old=ss['SW4']
for n in ['1','2','3']:remove_at(pin(old,n))
z=component('stock:SW4','SW4',(544.83,163.83),'BATTERY DISCONNECT',footprint=old.footprint_field.text.text,existing=True)
net(z,'1','BMS_NEG');net(z,'2','CELL_N')
# The wire at the old common terminal remains the switched cell negative connection.
label('CELL_N',(519.43,161.29))
# Programming and JTAG access; header 3.3V pins are voltage reference.
z=component('stock:J13','J13',(190.5,194.31),'JTAG',footprint='Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical')
for n,name in enumerate(['+3.3V','GND','IO13','IO14','IO12','IO15'],1):net(z,n,name)
z=component('J11','J14',(251.46,194.31),'UART0 DEBUG',footprint='Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical')
for n,name in enumerate(['GND','+3.3V','RXD0','TXD0'],1):net(z,n,name)
for i,(x,name) in enumerate(zip([315,350,385,420,455,490,525,560],['GND','+3.3V','+5V','PWR_OUT','BAT_PROTECTED','MODEM_5V','NODE_5V','EN']),1):
 z=component('stock:TP1',f'TP{i}',(x,230),'TP',footprint='TestPoint:TestPoint_Pad_D1.0mm');z.value_field.visible=False;z.reference_field.text.position.CopyFrom(v(x,225));z.attributes.exclude_from_bill_of_materials=True;net(z,1,name,2.54)
field(sym('U5'),'Firmware_pin_contract','RS485 RX4 TX5 DE22 /RE23; modem TX17 RX16 EN25 UART_OE27; AquaNode EN26 default ON; tamper RTC33; battery ADC36; NTC ADC39; USB status35; solar /PGOOD34; CHG32; JTAG12/13/14/15')
text('J13 JTAG: 1 VTREF, 2 GND, 3 TCK, 4 TMS, 5 TDI, 6 TDO.\nJ14 UART0: 1 GND, 2 VTREF, 3 ESP TX, 4 ESP RX.\nVTREF is an output reference. Do not feed external power into these pins.',(172.72,210.82),1.0)
commit('Finish battery disconnect and add independent UART/JTAG debug access')
