from pathlib import Path
import sexpdata as sx
r=Path.cwd();o=r/'build/larger-controls'
sub=lambda n,k:[x for x in n if isinstance(x,list) and x and str(x[0])==k]
def block(s,key):
 a=s.index('('+key);depth=0;q=False;esc=False
 for i in range(a,len(s)):
  c=s[i]
  if q:
   if esc:esc=False
   elif c=='\\':esc=True
   elif c=='"':q=False
  elif c=='"':q=True
  elif c=='(':depth+=1
  elif c==')':
   depth-=1
   if depth==0:return a,i+1
now=(r/'PGR.kicad_sch').read_text();old=(o/'backups/PGR.kicad_sch').read_text();a,b=block(now,'lib_symbols');x,y=block(old,'lib_symbols');stock=sx.loads((o/'fixture.kicad_sch').read_text());z=sub(sub(stock,'lib_symbols')[0],'symbol')[0]
# IPC symbol field edits can rewrite cached polyline artwork. Restore unchanged
# library definitions verbatim, and use the stock definition for the added SPDT.
newcache=old[x:y-1]+'\n'+sx.dumps(z)+'\n)';(r/'PGR.kicad_sch').write_text(now[:a]+newcache+now[b:])
print('Restored original cached artwork plus stock SPDT symbol')
