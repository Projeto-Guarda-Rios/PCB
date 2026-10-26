"""Restore standard GND cache bindings after an IPC polygon-serialization limitation.
Functional changes are made through IPC. Its PolySet serializer drops the repeated
vertex used to close KiCad's standard ground icon, producing a broken icon and
three library-mismatch warnings. Bind only the three new instances to the original,
unchanged embedded power:GND definition. No pin positions or wiring are changed.
"""
from pathlib import Path
import re,shutil
p=Path('PGR.kicad_sch');s=p.read_text();backup=Path('build/solar-schematic/backups/before-ground-library-restore.kicad_sch');shutil.copy2(p,backup)
def end_form(s,start):
 depth=0;quote=False;escape=False
 for i in range(start,len(s)):
  c=s[i]
  if quote:
   if escape:escape=False
   elif c=='\\':escape=True
   elif c=='"':quote=False
  elif c=='"':quote=True
  elif c=='(':depth+=1
  elif c==')':
   depth-=1
   if not depth:return i+1
 raise ValueError('unbalanced')
original=Path('build/solar-schematic/backups/PGR.kicad_sch').read_text()
assert not re.search(r'\(symbol "GND_[123]"',original)
changes=[]
aliases=re.findall(r'^\t\t\(symbol "(GND_\d+)"\n',s,re.M)
assert 1 <= len(aliases) <= 6
for alias in aliases:
 m=re.search(r'^\t\t\(symbol "'+alias+r'"\n',s,re.M);assert m,alias
 start=m.start();end=end_form(s,s.index('(',start));changes.append((start,end,''))
 assert s.count('(lib_name "'+alias+'")') in [0,1]
for a,b,replacement in sorted(changes,reverse=True):s=s[:a]+replacement+s[b:]
for alias in aliases:s=s.replace('\t\t(lib_name "'+alias+'")\n','')
p.write_text(s)
print('Restored three standard GND library bindings; no circuit changes')
