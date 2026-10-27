from helper import *
for x in items:
 if isinstance(x,sch.LocalLabel) and xy(x.position)==(519.43,161.29) and x.text.text=='CELL_N':deletes.add(x.id.value)
label('BMS_NEG',pin(ss['U6'],'6'))
for i,name in enumerate(['GND','+3.3V','+5V','PWR_OUT','BAT_PROTECTED','MODEM_5V','NODE_5V','EN'],1):
 old=ss[f'TP{i}'];p=pin(old,'1');remove_at(p)
 for x in items:
  if isinstance(x,sch.LocalLabel) and xy(x.position)==(p[0],p[1]+2.54):deletes.add(x.id.value)
 z=sym(f'TP{i}');x=round(p[0]/1.27)*1.27;translate(z,(x,229.87));net(z,1,name,2.54)
commit('Restore switched battery ground domain and align test points to the connection grid')
