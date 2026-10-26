from pathlib import Path
import re,shutil
p=Path('PGR.kicad_sch');s=p.read_text();original=Path('build/solar-schematic/backups/PGR.kicad_sch').read_text()
def form(text,name):
 m=re.search(r'^\t\t\(symbol "'+re.escape(name)+r'"\n',text,re.M);assert m,name
 start=m.start();depth=0;quote=False;escape=False
 for i in range(text.index('(',start),len(text)):
  c=text[i]
  if quote:
   if escape:escape=False
   elif c=='\\':escape=True
   elif c=='"':quote=False
  elif c=='"':quote=True
  elif c=='(':depth+=1
  elif c==')':
   depth-=1
   if depth==0:return start,i+1,text[start:i+1]
 raise ValueError('unbalanced')
a,b,cur=form(s,'Device:Thermistor_NTC');_,_,old=form(original,'Device:Thermistor_NTC')
# The symbol's pin definitions must be identical. Only graphics fidelity is restored.
def pins(s):return re.findall(r'\(pin passive line\s*\(at ([^)]+)\).*?\(number "([^"]+)"',s,re.S)
assert pins(cur)==pins(old),(pins(cur),pins(old))
shutil.copy2(p,'build/solar-schematic/backups/before-probe-graphics-restore.kicad_sch')
p.write_text(s[:a]+old+s[b:]);print('Restored original probe library graphics; pins and wiring unchanged')
