from helper import api,d,project,Empty
from pathlib import Path
import sexpdata as sx,re,copy,json
api.request(project.CloseDocument(document=d),Empty)
S=sx.Symbol
p=Path('PGR.kicad_sch');txt=p.read_text();root=sx.loads(txt)
def sub(n,k):return [a for a in n if isinstance(a,list) and a and str(a[0])==k]
def ch(n,k):return next(a for a in sub(n,k))
def props(n):return {a[1]:a[2] for a in sub(n,'property')}
def suffix(u):return tuple(u[1].split('_')[-2:])
def sig(n):return sorted((suffix(u),sx.dumps(a)) for u in sub(n,'symbol') for a in sub(u,'pin'))
def key(n):return props(n).get('Value'),str(sig(n))
sources=[]
for src in ['build/production-fixes/backups/PGR.kicad_sch','build/production-fixes/templates.kicad_sch']:
 sources+=ch(sx.loads(Path(src).read_text()),'lib_symbols')[1:]
by={key(n):n for n in sources};restored=[];unmatched=[]
lib=ch(root,'lib_symbols')
for n in lib[1:]:
 source=by.get(key(n))
 if source is None:unmatched.append(n[1]);continue
 us={suffix(u):u for u in sub(source,'symbol')}
 for u in sub(n,'symbol'):
  original=us.get(suffix(u))
  if original is not None:
   graphics=[copy.deepcopy(a) for a in original[2:] if str(a[0])!='pin']
   u[:]=u[:2]+graphics+sub(u,'pin')
 restored.append(n[1])
# Keep the native file's structure; replace just its embedded cache.
def end(s,a):
 dep=0;q=False;e=False
 for i in range(a,len(s)):
  c=s[i]
  if q:
   if e:e=False
   elif c=='\\':e=True
   elif c=='"':q=False
  elif c=='"':q=True
  elif c=='(':dep+=1
  elif c==')':
   dep-=1
   if dep==0:return i+1
start=txt.index('\t(lib_symbols');stop=end(txt,txt.index('(',start));p.write_text(txt[:start]+sx.dumps(lib)+txt[stop:])
ld=[]
for n in lib[1:]:
 z=copy.deepcopy(n);z[1]=z[1].split(':',1)[1];ld.append(z)
Path('symbols/PGR_Validated.kicad_sym').write_text(sx.dumps([S('kicad_symbol_lib'),[S('version'),20241209],[S('generator'),S('kicad_symbol_editor')],*ld])+'\n')
Path('build/production-fixes/graphics-restoration.json').write_text(json.dumps({'restored':restored,'unmatched':unmatched},indent=2))
print('Restored graphics',len(restored),'unmatched',unmatched)
# Native load/save pretty-prints without replacing definitions through protobuf.
d=api.open(__import__('client').types.DOCTYPE_SCHEMATIC);api.save(d)
