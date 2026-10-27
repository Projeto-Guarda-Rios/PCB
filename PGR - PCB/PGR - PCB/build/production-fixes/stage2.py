from helper import *
# Remove superseded boost and linear-regulator drawings. Reused component UUIDs are retained.
boxes=[(355,160,470,215),(150,163,270,210)]
def in_box(p):return any(a<=p[0]<=c and b<=p[1]<=e for a,b,c,e in boxes)
for x in items:
 if isinstance(x,sch.SchematicSymbolInstance) and in_box(xy(x.position)):deletes.add(x.id.value)
 elif isinstance(x,sch.SchematicLine) and in_box(xy(x.start)) and in_box(xy(x.end)):deletes.add(x.id.value)
 elif isinstance(x,(sch.GlobalLabel,sch.LocalLabel,sch.Junction,sch.NoConnectMarker)) and in_box(xy(x.position)):deletes.add(x.id.value)
 elif isinstance(x,sch.SchematicText) and in_box(xy(x.text.position)):deletes.add(x.id.value)
 elif isinstance(x,sch.SchematicGraphicShape) and x.shape.HasField('rectangle') and in_box(xy(x.shape.rectangle.top_left)) and in_box(xy(x.shape.rectangle.bottom_right)):deletes.add(x.id.value)
# Disconnect connector supplies from their old direct global-power symbols.
for ref,n,name in [('J8','2','MODEM_5V'),('J11','3','NODE_5V')]:
 p=pin(ss[ref],n);remove_at(p)
 for x in items:
  if isinstance(x,sch.SchematicSymbolInstance) and x.reference_field.text.text.startswith('#PWR') and pin(x,'1')==p:deletes.add(x.id.value)
 label(name,p)
# Modem UART now passes through an independently disabled pair of buffers.
for n,name in [('3','MODEM_RX'),('4','MODEM_TX')]:remove_at(pin(ss['J8'],n));label(name,pin(ss['J8'],n))
# Power-input names stay explicit across the protection stages.
for x in items:
 if isinstance(x,(sch.LocalLabel,sch.GlobalLabel)) and x.text.text=='VBUS' and xy(x.position)==(322.58,176.53):
  q=clone(x);q.text.text='SOLAR_RAW';upd['solar_label']=q
# Battery raw positive is isolated from the existing protected charger/BMS rail.
remove_at(pin(ss['BT1'],'1'));label('CELL_P',pin(ss['BT1'],'1'));label('BAT_PROTECTED',(519.43,128.27));label('CELL_N',pin(ss['BT1'],'2'))
# External temperature window drives CE; the BQ TS pin gets its documented 10k termination.
remove_at(pin(ss['U1'],'1'))
for x in items:
 if isinstance(x,(sch.GlobalLabel,sch.LocalLabel)) and x.text.text=='BAT_NTC' and xy(x.position)==(518.16,90.17):deletes.add(x.id.value)
label('TS_FIXED',pin(ss['U1'],'1'));passive('R31',(553.72,88.9),'10kR','TS_FIXED','GND')
remove_at(pin(ss['U1'],'4'))
for x in items:
 if isinstance(x,sch.SchematicSymbolInstance) and x.reference_field.text.text=='#PWR012':deletes.add(x.id.value)
label('CHG_CE',pin(ss['U1'],'4'))
# ------------------- 5-V converter -------------------
block('5 V supply / controlled low-battery shutdown',20.32,254,132.08,68.58)
u=component('stock:U3','U3',(66.04,285.75),'TPS61230',mpn='TPS61230DRCR',manufacturer='Texas Instruments',datasheet='https://www.ti.com/lit/ds/symlink/tps61230.pdf',existing=True)
for n,name in [('10','PWR_OUT'),('9','BOOST_EN'),('8','BOOST_HYS'),('6','BOOST_SS'),('7','BOOST_FB'),('3','BOOST_5V'),('1','BOOST_SW'),('5','BOOST_PG')]:net(u,n,name)
gnd(u,'11')
# 1-uH inductor and ceramic capacitors follow the TPS61230 reference design.
l=passive('L1',(66.04,269.24),'1uH','PWR_OUT','BOOST_SW','L','Inductor_SMD:L_Coilcraft_XAL4020-XXX','XAL4020-102MEC');field(l,'Manufacturer','Coilcraft');field(l,'Current_rating','Isat 8.7A; Irms 6.7A at 20C rise; DCR max 14.6mR')
passive('R22',(101.6,284.48),'402kR','BOOST_5V','BOOST_FB',mpn='RT0603BRD07402KL');field(upd['R22'],'Tolerance','0.1%')
passive('R23',(101.6,304.8),'100kR','BOOST_FB','GND',mpn='RT0603BRD07100KL');field(upd['R23'],'Tolerance','0.1%')
passive('R32',(30.48,274.32),'200kR','PWR_OUT','BOOST_EN');field(created['R32'],'Tolerance','0.1%')
passive('R33',(30.48,293.37),'100kR','BOOST_EN','BOOST_HYS');field(created['R33'],'Tolerance','0.1%')
passive('R34',(30.48,311.15),'10kR','BOOST_HYS','GND');field(created['R34'],'Tolerance','0.1%')
passive('C15',(76.2,309.88),'10nF','BOOST_SS','GND','C')
passive('C13',(48.26,309.88),'22uF','PWR_OUT','GND','C','Capacitor_SMD:C_1210_3225Metric','GRM32ER71C226KE18L')
for ref,x in [('C14',116.84),('C18',129.54),('C19',142.24)]:
 s=passive(ref,(x,304.8),'22uF','BOOST_5V','GND','C','Capacitor_SMD:C_1210_3225Metric','GRM32ER71C226KE18L');field(s,'Rating','16V X7R; combined effective C >=20uF at 5V')
text('5.02 V nominal. EN/HYS: off ~3.21 V, restart ~3.57 V.\nAutomatic PFM; soft start ~10 ms. Design load: 1 A peak.',(48.26,316.23),1.0)
# ------------------- 3V3 buck and reset supervisor -------------------
block('3.3 V efficient supply / brownout reset',160.02,254,132.08,68.58)
u=component('stock:IC1','IC1',(187.96,281.94),'TLV62568',mpn='TLV62568DBVR',manufacturer='Texas Instruments',datasheet='https://www.ti.com/lit/ds/symlink/tlv62568.pdf',existing=True)
for n,name in [('4','+5V'),('1','+5V'),('3','BUCK_SW'),('5','BUCK_FB')]:net(u,n,name)
gnd(u,'2')
s=passive('L2',(220.98,279.4),'2.2uH','BUCK_SW','+3.3V','L','Inductor_SMD:L_Coilcraft_XAL4020-XXX','XAL4020-222MEC');field(s,'Manufacturer','Coilcraft')
passive('C8',(170.18,303.53),'22uF','+5V','GND','C','Capacitor_SMD:C_1210_3225Metric','GRM32ER71C226KE18L')
passive('C9',(251.46,279.4),'22uF','+3.3V','GND','C','Capacitor_SMD:C_1210_3225Metric','GRM32ER71C226KE18L')
passive('C10',(266.7,279.4),'100nF','+3.3V','GND','C')
passive('R35',(238.76,302.26),'450kR','+3.3V','BUCK_FB');field(created['R35'],'Tolerance','0.1%')
passive('R36',(269.24,302.26),'100kR','BUCK_FB','GND');field(created['R36'],'Tolerance','0.1%')
u=component('stock:U12','U12',(203.2,307.34),'TPS3808G33',mpn='TPS3808G33DBVR',manufacturer='Texas Instruments',datasheet='https://www.ti.com/lit/ds/symlink/tps3808.pdf')
for n,name in [('6','+3.3V'),('5','+3.3V'),('3','+3.3V'),('1','EN')]:net(u,n,name)
gnd(u,'2');new.append(sch.NoConnectMarker(id=uid(),position=v(*pin(u,'4'))))
passive('C20',(226.06,313.69),'100nF','+3.3V','GND','C')
text('3.3 V / 1 A. Reset threshold 3.07 V; 20-ms release delay.\nC2 remains 1uF on EN. Supervisor output is open drain.',(162.56,316.23),1.0)
# ------------------- USB source limiting and power mux -------------------
block('USB power limit / reverse-blocking source selection',299.72,254,132.08,68.58)
u=component('stock:U9','U11',(327.66,281.94),'MIC2007',mpn='MIC2007YM6-TR',manufacturer='Microchip',datasheet='https://www.microchip.com/en-us/product/MIC2007')
for n,name in [('1','+5V_PROGRAM'),('3','+5V_PROGRAM'),('6','USB_LIMIT'),('4','USB_ILIM'),('5','USB_SLEW')]:net(u,n,name)
gnd(u,'2')
passive('R37',(307.34,309.88),'620R','USB_ILIM','GND');passive('C21',(327.66,309.88),'1nF','USB_SLEW','GND','C')
u=component('stock:U7','U7',(388.62,283.21),'TPS2116',mpn='TPS2116DRLR',manufacturer='Texas Instruments',datasheet='https://www.ti.com/lit/ds/symlink/tps2116.pdf')
for n,name in [('3','USB_LIMIT'),('4','USB_PR'),('5','USB_LIMIT'),('6','BOOST_5V'),('2','+5V'),('8','USB_ACTIVE')]:net(u,n,name)
gnd(u,'1')
passive('R38',(358.14,274.32),'402kR','USB_LIMIT','USB_PR');passive('R39',(358.14,304.8),'100kR','USB_PR','GND')
passive('R40',(414.02,309.88),'100kR','+3.3V','USB_ACTIVE')
passive('C22',(414.02,279.4),'22uF','+5V','GND','C','Capacitor_SMD:C_1210_3225Metric','GRM32ER71C226KE18L')
text('USB priority above ~5.0 V threshold? See final verified divider.\nUSB limit <=0.49 A. USB powers the station, not the charger.',(302.26,316.23),1.0)
# ------------------- Independently protected peripheral supplies -------------------
block('Modem and AquaNode power / inrush and short protection',439.42,254,132.08,68.58)
for ref,p,out,en,r,c,rv in [('U9',(467.36,279.4),'MODEM_5V','IO25','R41','C23','330R'),('U10',(533.4,279.4),'NODE_5V','IO26','R42','C24','1kR')]:
 u=component('stock:U9',ref,p,'MIC2007',mpn='MIC2007YM6-TR',manufacturer='Microchip',datasheet='https://www.microchip.com/en-us/product/MIC2007')
 for n,name in [('1','+5V'),('3',en),('6',out),('4',ref+'_ILIM'),('5',ref+'_SLEW')]:net(u,n,name)
 gnd(u,'2');passive(r,(p[0]-17.78,304.8),rv,ref+'_ILIM','GND');passive(c,(p[0],304.8),'1nF',ref+'_SLEW','GND','C')
passive('R43',(490.22,304.8),'100kR','IO25','GND');passive('R44',(556.26,304.8),'100kR','+3.3V','IO26')
text('GPIO25: modem ON=1, default OFF. GPIO26: node ON=1, default ON.\nNode stays powered while ESP32 sleeps; power-cycle only for recovery.',(441.96,316.23),1.0)
# Preserve existing IDs for parts that were moved or replaced, not deleted.
for s in upd.values():
 if isinstance(s,sch.SchematicSymbolInstance):deletes.discard(s.id.value)
# Update stale power-chain annotation, preserving the rest of the original charger notes.
for x in items:
 if isinstance(x,sch.SchematicText) and x.text.text.startswith('BATTERY / SOLAR POWER PATH'):
  q=clone(x);q.text.text='SOLAR / BATTERY POWER PATH\nJ10 -> polarity protection -> BQ24074 -> boost -> mux -> 5 V.\nUSB -> current limiter -> mux. Buck provides 3.3 V.\nCharge current reduces first; battery supplements weak input.';upd['power_note']=q
commit('Upgrade power conversion, source isolation, peripheral power control, and brownout reset')
