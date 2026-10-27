from helper import api,d,project,Empty,types
from pathlib import Path
import sexpdata as sx,re
api.request(project.CloseDocument(document=d),Empty)
p=Path('PGR.kicad_sch');s=p.read_text()
def end(t,a):
 dep=0;q=False;esc=False
 for i in range(a,len(t)):
  c=t[i]
  if q:
   if esc:esc=False
   elif c=='\\':esc=True
   elif c=='"':q=False
  elif c=='"':q=True
  elif c=='(':dep+=1
  elif c==')':
   dep-=1
   if dep==0:return i+1
changes=[]
def sub(n,k):return[a for a in n if isinstance(a,list) and a and str(a[0])==k]
def ch(n,k):return sub(n,k)[0]
fields={'L1':[(66.04,262.89,90),(66.04,265.43,90)],'L2':[(220.98,273.05,90),(220.98,275.59,90)],'U3':[(76.2,271.78,0),(76.2,274.32,0)],'Q4':[(346.71,350.52,0),(346.71,353.06,0)],'Q5':[(346.71,378.46,0),(346.71,381,0)],'Q6':[(273.05,381,0),(273.05,383.54,0)],'Q7':[(405.13,350.52,0),(405.13,353.06,0)],'Q8':[(139.7,350.52,0),(139.7,353.06,0)],'D14':[(264.16,358.14,0),(264.16,360.68,0)],'J14':[(251.46,181.61,0),(251.46,184.15,0)]}
notes={'5.02 V nominal':(302.26,182.88),'3.3 V / 1 A.':(441.96,179.07),'Window is ratiometric':(302.26,191.77),'GPIO36 ADC':(441.96,187.96),'GPIO25 powers modem':(302.26,201.93),'INPUT: J10':(441.96,199.39),'J13 JTAG':(172.72,163.83),'GPIO23 = RS485':(304.8,107.95),'U11/U9/U10:':(300.99,212.09)}
for m in re.finditer(r'^\t\((symbol|text|rectangle)\b',s,re.M):
 a=m.start();b=end(s,s.index('(',a));n=sx.loads(s[a:b]);kind=str(n[0]);changed=False
 if kind=='symbol':
  ps={x[1]:x for x in sub(n,'property')};ref=ps['Reference'][2]
  if ref in fields:
   for f,pos in zip(['Reference','Value'],fields[ref]):ch(ps[f],'at')[1:]=pos
   changed=True
 elif kind=='text':
  if n[1]=='Step-Up Convertor':changes.append((a,b,''));continue
  for prefix,pos in notes.items():
   if n[1].startswith(prefix):ch(n,'at')[1:3]=pos;changed=True
  if n[1].startswith('INPUT: J10'):n[1]=n[1].replace('C5: 10 uF','C5: 22 uF');changed=True
  if n[1].startswith('Reserved GPIOs'):n[1]=n[1].replace('33 tamper wake, 35 USB status','33 tamper wake, 34 solar status, 35 USB status');changed=True
 elif kind=='rectangle':
  st=ch(n,'start');en=ch(n,'end')
  if st[1]>430 and st[2]>320:en[2]=389.89;changed=True
 if changed:changes.append((a,b,sx.dumps(n)))
for a,b,t in sorted(changes,reverse=True):s=s[:a]+t+s[b:]
p.write_text(s);d=api.open(types.DOCTYPE_SCHEMATIC);api.save(d);print('Tidied drawing elements',len(changes))
