from pathlib import Path
import sys,sexpdata as sx
sys.path.insert(0,str(Path('build/reliability-fixes/ipc').resolve()));import client
client.SOCKET='/tmp/pgr-visible-restore.sock'
from client import *
a=API();d=a.open(types.DOCTYPE_SCHEMATIC);a.request(project.CloseDocument(document=d),Empty)
p=Path('PGR.kicad_sch');r=sx.loads(p.read_text());S=sx.Symbol;sub=lambda n,k:[z for z in n if isinstance(z,list) and z and str(z[0])==k];ch=lambda n,k:sub(n,k)[0]
for n in sub(r,'symbol'):
 ps={f[1]:f for f in sub(n,'property')};ref=ps['Reference'][2]
 if ref in ['Q4','Q5']:
  for f in ['Reference','Value']:ch(ps[f],'at')[1]=354.33 if ref=='Q4' else 330.2
 if ref=='#FLG03':
  at=ch(n,'at');dx=421.64-at[1];dy=386.08-at[2];at[1:3]=[421.64,386.08]
  for f in sub(n,'property'):
   at=ch(f,'at');at[1]=round(at[1]+dx,3);at[2]=round(at[2]+dy,3)
 if ref=='JP1':
  n.append([S('property'),'Accessory_MPN','Harwin M7582-05, quantity 1',[S('at'),238.76,201.93,0],[S('hide'),S('yes')],[S('effects'),[S('font'),[S('size'),1.27,1.27]]]])
  ps['Datasheet'][2]='https://www.harwin.com/products/M20-9990345'
for n in sub(r,'global_label'):
 at=ch(n,'at')
 if n[1]=='VBUS' and at[1:3]==[406.4,391.16]:at[1:3]=[421.64,386.08]
 if n[1]=='GND' and at[1:3]==[306.07,378.46]:at[1]=307.34
for n in sub(r,'wire'):
 for pt in ch(n,'pts')[1:]:
  if pt[1:]==[306.07,378.46]:pt[1]=307.34
for n in list(sub(r,'text')):
 if n[1].startswith('JP1:'):r.remove(n)
 elif n[1].startswith('J13 JTAG:'):
  n[1]=n[1].replace('\r\n','\n')+'\nJP1: 1-2 USB default; 2-3 EXT. Fit one shunt only.'
p.write_text(sx.dumps(r));d=a.open(types.DOCTYPE_SCHEMATIC);a.save(d)
f=Path('PGR-FootPrints.pretty/USB_C_GCT_USB4105_PGR.kicad_mod');s=f.read_text().replace('(property "Value" "USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal"','(property "Value" "USB_C_GCT_USB4105_PGR"');f.write_text(s)
