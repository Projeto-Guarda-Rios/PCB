"""Freeze reviewed embedded symbols into a project-local KiCad library.
No circuit or pin positions change. Multi-unit UART buffer uses its complete stock definition.
"""
from helper import *
import re,shutil,json
api.request(project.CloseDocument(document=d),Empty)
p=Path('PGR.kicad_sch');s=p.read_text();shutil.copy2(p,'build/production-fixes/backups/before-library-freeze.kicad_sch')
def end_form(text,a):
 depth=0;quote=False;esc=False
 for i in range(a,len(text)):
  c=text[i]
  if quote:
   if esc:esc=False
   elif c=='\\':esc=True
   elif c=='"':quote=False
  elif c=='"':quote=True
  elif c=='(':depth+=1
  elif c==')':
   depth-=1
   if not depth:return i+1
 raise ValueError(a)
def rename_definition(t,full_name):
 entry=full_name.split(':')[-1];t=re.sub(r'^\s*\(symbol "[^"]+"',lambda m:'\t\t(symbol "'+full_name+'"',t,count=1)
 t=re.sub(r'(\(symbol ")[^"]+(_\d+_\d+)(")',lambda m:m[1]+entry+m[2]+m[3],t)
 return t
cache={}
for m in re.finditer(r'^\t\t\(symbol "([^"]+)"',s,re.M):cache[m[1]]=s[m.start():end_form(s,s.index('(',m.start()))]
fixture=Path('build/production-fixes/templates.kicad_sch').read_text()
import sexpdata as sx
rr=sx.loads(fixture);lib=next(a for a in rr if isinstance(a,list) and a and str(a[0])=='lib_symbols');stock_logic=sx.dumps(next(a for a in lib[1:] if a[1]=='74xGxx:74LVC2G126'))
changes=[];defs={};mapping={}
for m in re.finditer(r'^\t\(symbol\b',s,re.M):
 a=m.start();b=end_form(s,s.index('(',a));t=s[a:b];lid=re.search(r'\(lib_id "([^"]+)"\)',t)[1];alias=re.search(r'\(lib_name "([^"]+)"\)',t);key=alias[1] if alias else lid
 assert key in cache,key
 logic='74LVC2G126' in lid
 entry='Logic_74LVC2G126' if logic else key.split(':',1)[1] if key.startswith('PGR_Validated:') else re.sub(r'[^A-Za-z0-9_+-]','_',key)
 full='PGR_Validated:'+entry
 source=stock_logic if logic else cache[key]
 defs.setdefault(entry,rename_definition(source,entry).replace('\t\t(symbol','\t(symbol',1))
 mapping[key]=full
 t=re.sub(r'\n\s*\(lib_name "[^"]+"\)','',t,count=1)
 t=re.sub(r'\(lib_id "[^"]+"\)','(lib_id "'+full+'")',t,count=1)
 changes.append((a,b,t))
# Replace the embedded cache with exactly the definitions available in the local library.
start=s.index('\t(lib_symbols');end=end_form(s,s.index('(',start))
newcache='\t(lib_symbols\n'+'\n'.join(rename_definition(t,'PGR_Validated:'+entry) for entry,t in defs.items())+'\n\t)'
changes.append((start,end,newcache))
for a,b,t in sorted(changes,reverse=True):s=s[:a]+t+s[b:]
p.write_text(s)
out=Path('symbols/PGR_Validated.kicad_sym');out.write_text('(kicad_symbol_lib (version 20241209) (generator kicad_symbol_editor)\n'+'\n'.join(defs.values())+'\n)\n')
lt=Path('sym-lib-table');table=lt.read_text();shutil.copy2(lt,'build/production-fixes/backups/sym-lib-table')
if '(name "PGR_Validated")' not in table:
 i=table.rfind(')');table=table[:i]+'  (lib (name "PGR_Validated")(type "KiCad")(uri "${KIPRJMOD}/symbols/PGR_Validated.kicad_sym")(options "")(descr "Reviewed project-local symbol definitions"))\n'+table[i:];lt.write_text(table)
Path('build/production-fixes/library-map.json').write_text(json.dumps(mapping,indent=2)+'\n')
d=api.open(types.DOCTYPE_SCHEMATIC);print('Frozen',len(defs),'reviewed definitions; rebound',len(changes)-1,'instances')
