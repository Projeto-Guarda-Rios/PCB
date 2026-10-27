from helper import *
def reconnect(ref,n,name):
 s=ss[ref];p=pin(s,n)
 for x in items:
  if isinstance(x,sch.SchematicLine) and p in [xy(x.start),xy(x.end)]:
   deletes.add(x.id.value)
   for pt in [xy(x.start),xy(x.end)]:
    for y in items:
     if isinstance(y,sch.LocalLabel) and xy(y.position)==pt:deletes.add(y.id.value)
 net(s,n,name)
# Preserve the higher-current solar/battery source when USB is plugged in.
# USB is a fallback for programming; it must not repeatedly current-limit modem bursts.
reconnect('U7','3','BOOST_5V');reconnect('U7','6','USB_LIMIT');reconnect('U7','5','BOOST_5V');reconnect('R38','1','BOOST_5V')
for x in items:
 if isinstance(x,sch.LocalLabel) and x.text.text in ['USB_ACTIVE','USB_PR']:
  q=clone(x);q.text.text={'USB_ACTIVE':'BOOST_ACTIVE','USB_PR':'BOOST_PR'}[q.text.text];upd[x.id.value]=q
for x in items:
 if isinstance(x,sch.SchematicText):
  q=clone(x);t=q.text.text
  if t.startswith('USB priority trip'):q.text.text='Solar/battery boost has priority above ~4.12 V.\nUSB fallback <=0.49 A; modem bursts require battery/solar power.';upd[x.id.value]=q
  elif t.startswith('GPIO36 ADC'):q.text.text=t.replace('USB selected when high','boost selected when high');upd[x.id.value]=q
  elif t.startswith('Reserved GPIOs'):q.text.text=t.replace('USB status','boost status');upd[x.id.value]=q
field(sym('U5'),'Firmware_pin_contract','RS485 RX4 TX5 DE22 /RE23; modem TX17 RX16 EN25 UART_OE27; AquaNode EN26 default ON; tamper RTC33; battery ADC36; NTC ADC39; boost selected35; solar /PGOOD34; CHG32; JTAG12/13/14/15. USB-only budget <=0.49A: keep modem off.')
commit('Prioritize solar/battery power so USB current limiting cannot interrupt modem bursts')
