"""Preserve native fabrication metadata absent from the stable IPC Pad schema.
All electrical and routing edits were applied through the matching KiCad IPC API.
Run only with the edit server stopped, after saving and closing both documents.
"""
from pathlib import Path
import json,re,shutil
root=Path(__file__).resolve().parents[2];path=root/'PGR.kicad_pcb';s=path.read_text()
# Find the original CP2102N exposed-pad identifier, then its exact native pad span.
original=(root/'build/reliability-fixes/backups/before/PGR.kicad_pcb').read_text()
def padspans(text):
 stack=[]
 for m in re.finditer(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',text):
  t=m.group()
  if t=='(':stack.append([m.start(),None])
  elif t==')':
   start,tag=stack.pop()
   if tag=='pad':yield start,m.end()
  elif stack and stack[-1][1] is None:stack[-1][1]=t
old_pads=[original[a:b] for a,b in padspans(original) if '(property pad_prop_heatsink)' in original[a:b]]
missing=[]
for old in old_pads:
 uid=re.search(r'\(uuid "([^"]+)"\)',old).group(1)
 match=[(a,b) for a,b in padspans(s) if uid in s[a:b]]
 assert len(match)==1,(uid,match)
 a,b=match[0]
 if '(property pad_prop_heatsink)' not in s[a:b]:missing.append((a,b,uid))
assert len(missing)==1,missing
backup=root/'build/reliability-fixes/backups/before-metadata-restore';backup.mkdir(exist_ok=True)
shutil.copy2(path,backup/path.name)
for a,b,uid in sorted(missing,reverse=True):
 block=s[a:b];insertion=re.search(r'\n\s*\(net ',block)
 assert insertion,uid
 block=block[:insertion.start()]+'\n\t\t\t(property pad_prop_heatsink)'+block[insertion.start():]
 s=s[:a]+block+s[b:]
path.write_text(s);print('Restored original exposed-pad fabrication metadata without changing geometry or connectivity')
