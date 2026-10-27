from helper import *
# Complete the temperature interlock with a ratiometric NTC window.
block('Cell temperature interlock / charger enable',20.32,330.2,132.08,68.58)
for ref,p,plus,minus in [('U13',(48.26,353.06),'BAT_NTC','NTC_HOT'),('U14',(104.14,353.06),'NTC_COLD','BAT_NTC')]:
 u=component('stock:U13',ref,p,'MCP6566',footprint='Package_TO_SOT_SMD:SOT-23-5',mpn='MCP6566T-E/OT',manufacturer='Microchip',datasheet='https://ww1.microchip.com/downloads/aemDocuments/documents/MSLD/ProductDocuments/DataSheets/MCP6566-6R-6U-7-9-1.8V-Low-Power-Open-Drain-Output-Comparator-DS20002143G.pdf')
 for n,name in [('5','+3.3V'),('3',plus),('4',minus),('1','TEMP_OK')]:net(u,n,name)
 gnd(u,'2')
for ref,p,val,a,b in [('R45',(27.94,375.92),'10kR','+3.3V','BAT_NTC'),('R46',(53.34,375.92),'178kR','+3.3V','NTC_HOT'),('R47',(53.34,391.16),'100kR','NTC_HOT','GND'),('R48',(81.28,375.92),'43.2kR','+3.3V','NTC_COLD'),('R49',(81.28,391.16),'100kR','NTC_COLD','GND'),('R50',(109.22,375.92),'100kR','+3.3V','TEMP_OK'),('R51',(137.16,375.92),'100kR','PWR_OUT','CHG_CE')]:
 z=passive(ref,p,val,a,b);field(z,'Tolerance','0.1%')
q=component('stock:Q8','Q8',(130.81,353.06),'2N7002',mpn='2N7002-7-F',manufacturer='Diodes Incorporated')
for n,name in [('1','TEMP_OK'),('3','CHG_CE')]:net(q,n,name)
gnd(q,'2')
for ref,p,rail in [('C25',(25.4,353.06),'BAT_NTC'),('C26',(66.04,353.06),'+3.3V'),('C27',(119.38,391.16),'+3.3V')]:passive(ref,p,'100nF',rail,'GND','C')
# Exact off-board cell probe; its drawing and connector are preserved.
z=sym('TH1');z.value_field.text.text='103AT-2 10kR';field(z,'MPN','103AT-2');field(z,'Manufacturer','Semitec');field(z,'Specification','R25 10k +/-1%; B25/85 3435K +/-1%; insulated and thermally bonded to cell')
for x in items:
 if isinstance(x,sch.SchematicText) and x.text.text.startswith('REMOTE BATTERY TEMPERATURE'):
  q=clone(x);q.text.text='REMOTE CELL PROBE: Semitec 103AT-2, 10k +/-1%.\nInsulate and bond to the cell. External U13/U14 window\ndisables CE outside approximately 5 to 40 C.\nOpen or short probe inhibits charging; TS uses fixed 10k.';upd['ntc_note']=q
text('Window is ratiometric to 3.3 V; fault outputs are wired AND.\nNIMO limit is 0 to 45 C; verify actual probe trip temperatures.',(22.86,393.7),1.0)
# Modem UART buffers: disabled before power is removed, to prevent phantom supply.
block('Modem UART isolation / buzzer driver',160.02,330.2,132.08,68.58)
u1=component('stock:U15','U15',(190.5,351.79),'74LVC2G126',footprint='Package_SO:VSSOP-8_2.3x2mm_P0.5mm',mpn='SN74LVC2G126DCUR',manufacturer='Texas Instruments',datasheet='https://www.ti.com/lit/ds/symlink/sn74lvc2g126.pdf',unit=1)
for n,name in [('2','IO17'),('6','MODEM_RX'),('1','IO27')]:net(u1,n,name)
u2=component('stock:U15','U15',(246.38,351.79),'74LVC2G126',footprint='Package_SO:VSSOP-8_2.3x2mm_P0.5mm',mpn='SN74LVC2G126DCUR',manufacturer='Texas Instruments',unit=2)
for n,name in [('5','MODEM_TX'),('3','IO16'),('7','IO27')]:net(u2,n,name)
u3=component('stock:U15','U15',(283.21,351.79),'74LVC2G126',footprint='Package_SO:VSSOP-8_2.3x2mm_P0.5mm',mpn='SN74LVC2G126DCUR',manufacturer='Texas Instruments',unit=3);net(u3,'8','+3.3V');gnd(u3,'4')
for ref,p,a,b in [('R60',(170.18,378.46),'IO27','GND'),('R61',(190.5,378.46),'MODEM_TX','GND'),('R62',(210.82,378.46),'+3.3V','IO16'),('R63',(231.14,378.46),'+3.3V','IO17')]:passive(ref,p,'100kR',a,b)
passive('C28',(283.21,378.46),'100nF','+3.3V','GND','C')
# Replace the direct GPIO buzzer connection with a transistor and flyback diode.
for n in ['1','2']:remove_at(pin(ss['BZ1'],n))
for x in items:
 if isinstance(x,sch.SchematicSymbolInstance) and x.reference_field.text.text.startswith('#PWR') and pin(x,'1') in [(316.23,152.4),pin(ss['BZ1'],'2')]:deletes.add(x.id.value)
z=sym('BZ1');z.value_field.text.text='AI-1223-TWT-5V-2-R';z.footprint_field.text.text='Buzzer_Beeper:Buzzer_12x9.5RM7.6';z.datasheet_field.text.text='https://puiaudio.com/product/indicators/ai-1223-twt-5v-2-r';field(z,'MPN','AI-1223-TWT-5V-2-R');field(z,'Manufacturer','PUI Audio');field(z,'Rating','5V active magnetic indicator, 30mA max; lead pitch 7.6mm')
label('+5V',pin(ss['BZ1'],'1'));label('BUZZ_SW',pin(ss['BZ1'],'2'))
q=component('Q1','Q6',(264.16,383.54),'SS8050-G',mpn='SS8050-G',manufacturer='Comchip')
net(q,'3','BUZZ_SW');gnd(q,'2');net(q,'1','BUZZ_B')
passive('R64',(248.92,383.54),'1kR','IO19','BUZZ_B');passive('R65',(248.92,363.22),'100kR','BUZZ_B','GND')
z=component('D2','D14',(264.16,365.76),'SS14',mpn='SS14',manufacturer='Vishay');net(z,'1','+5V');net(z,'2','BUZZ_SW')
text('GPIO25 powers modem; wait for rail, then GPIO27 enables UART.\nDisable GPIO27 before GPIO25=0. Preserve modem PSM if needed.',(162.56,393.7),1.0)
# Battery polarity protection works with both battery and charger present.
block('Battery / solar polarity protection',299.72,330.2,132.08,68.58)
f=component('stock:F1','F1',(309.88,353.06),'3A fast',footprint='Fuse:Fuse_1206_3216Metric',mpn='0467003.NR',manufacturer='Littelfuse')
net(f,'1','CELL_P');net(f,'2','CELL_FUSED')
q=component('stock:Q4','Q4',(337.82,353.06),'AO3401A',mpn='AO3401A',manufacturer='Alpha & Omega Semiconductor',datasheet='https://www.aosmd.com/sites/default/files/res/datasheets/AO3401A.pdf')
for n,name in [('3','CELL_FUSED'),('2','BAT_PROTECTED'),('1','BAT_GATE')]:net(q,n,name)
q=component('Q1','Q7',(393.7,353.06),'SS8050-G',mpn='SS8050-G',manufacturer='Comchip')
for n,name in [('1','BAT_DETECT'),('2','CELL_N'),('3','BAT_GATE')]:net(q,n,name)
passive('R53',(365.76,350.52),'100kR','BAT_PROTECTED','BAT_GATE');passive('R54',(365.76,375.92),'100kR','CELL_FUSED','BAT_DETECT')
z=component('stock:D13','D13',(393.7,375.92),'1N4148W',footprint='Diode_SMD:D_SOD-123',mpn='1N4148W-7-F',manufacturer='Diodes Incorporated');net(z,'1','BAT_DETECT');net(z,'2','CELL_N')
q=component('stock:Q4','Q5',(337.82,381),'AO3401A',mpn='AO3401A',manufacturer='Alpha & Omega Semiconductor')
for n,name in [('3','SOLAR_RAW'),('2','VBUS'),('1','GND')]:net(q,n,name)
text('Q4 gate turns on only with correct cell polarity.\nQ7/D13 protect against reversal even while solar is connected.\nJ10: regulated 5 V panel; respect 10.2 V maximum open circuit.',(302.26,393.7),1.0)
# Battery voltage / NTC telemetry, wake filtering, and reserved-pin notes.
block('Battery telemetry / commissioning contracts',439.42,330.2,132.08,68.58)
for n,name in [('4','BATT_ADC'),('5','NTC_ADC')]:remove_at(pin(ss['U5'],n));label(name,pin(ss['U5'],n))
passive('R66',(454.66,351.79),'1MR','BAT_PROTECTED','BATT_ADC');passive('R67',(454.66,375.92),'270kR','BATT_ADC','GND')
for ref in ['R66','R67']:field(created[ref],'Tolerance','0.1%')
passive('C29',(474.98,375.92),'100nF','BATT_ADC','GND','C')
passive('R68',(497.84,351.79),'100kR','BAT_NTC','NTC_ADC');passive('C30',(497.84,375.92),'100nF','NTC_ADC','GND','C')
# Remove the pin's global IO33 label, keep the short cable on the connector side of R70.
p=pin(ss['J7'],'3');remove_at(p);label('TAMPER_EXT',p)
passive('R69',(523.24,351.79),'100kR','+3.3V','TAMPER_EXT');passive('R70',(548.64,351.79),'1kR','TAMPER_EXT','IO33');passive('C31',(548.64,375.92),'100nF','IO33','GND','C')
# GPIO12 must be low at reset for the selected 3.3-V flash module.
passive('R71',(525.78,375.92),'100kR','IO12','GND')
# Expose selected source to firmware, so USB programming need not start the modem.
label('USB_ACTIVE',pin(ss['U5'],'7')) # GPIO35, input-only, also present on J1.
text('GPIO36 ADC: Vcell x270/1270; calibrate ADC, settle >=200 ms.\nGPIO39: filtered cell NTC. GPIO35: USB selected when high.\nGPIO33: lid switch / RTC wake. GPIO12 must stay low at boot.',(441.96,393.7),1.0)
# Additional local energy storage at cable connectors, with rated parts.
for ref,p,rail in [('C32',(363.22,146.05),'MODEM_5V'),('C33',(386.08,146.05),'MODEM_5V'),('C34',(429.26,146.05),'NODE_5V')]:
 z=passive(ref,p,'22uF',rail,'GND','C','Capacitor_SMD:C_1210_3225Metric','C3225X7R1C226M250AC');field(z,'Manufacturer','TDK');field(z,'Rating','16V X7R +/-20%')
# Correct USB selection divider for guaranteed preference at a valid USB supply.
# 1V reference +/-8%; nominal trip 4.12V, worst upper trip <=4.47V.
z=sym('R38');z.value_field.text.text='312kR';field(z,'Tolerance','0.1%');field(sym('R39'),'Tolerance','0.1%')
# Replace the discontinued initial capacitor candidate with the current TDK version.
for ref in ['C8','C9','C13','C14','C18','C19','C22']:
 z=sym(ref);field(z,'MPN','C3225X7R1C226M250AC');field(z,'Manufacturer','TDK');field(z,'Rating','22uF 16V X7R +/-20%; 1210; DC bias evaluated')
for x in items:
 if isinstance(x,sch.SchematicText) and x.text.text.startswith('USB priority above'):
  q=clone(x);q.text.text='USB priority trip ~4.12 V; worst high trip <4.47 V.\nUSB limit <=0.49 A. USB powers the station, not the charger.';upd['usb_note']=q
# Update connector labels with explicit product and harness information.
field(sym('J8'),'Connected_device','M5Stack Unit NB-IoT2 U111-B / SIM7028')
field(sym('J8'),'Cable','PGR J8.1 GND -> M5 J1.4 black; .2 MODEM_5V -> J1.3 red; .3 RX_module -> J1.2 yellow; .4 TX_module -> J1.1 white')
field(sym('J11'),'Connected_device','AquaNode J3: 1=A, 2=B, 3=5V, 4=GND; verify connector family and cable gauge')
text('Reserved GPIOs on J1: 25 modem power, 26 node power, 27 UART OE,\n33 tamper wake, 35 USB status. Do not drive these from expansion hardware.',(154.94,175.26),1.27)
commit('Add cell temperature cutoff, polarity protection, modem isolation, buzzer driver, and telemetry')
