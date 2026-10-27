from pathlib import Path
import sys
sys.path.insert(0,str(Path('build/reliability-fixes/ipc').resolve()));import client
client.SOCKET='/tmp/pgr-visible-restore.sock'
from client import *
a=API();d=a.open(types.DOCTYPE_SCHEMATIC);a.request(project.CloseDocument(document=d),Empty)
p=Path('PGR.kicad_sch');s=p.read_text();assert s.count('Harwin M7582-05, quantity 1')==1;s=s.replace('Harwin M7582-05, quantity 1','Harwin M7567-05, quantity 1');p.write_text(s);d=a.open(types.DOCTYPE_SCHEMATIC);a.save(d)
q=Path('build/review-corrections/verify_corrections.py');q.write_text(q.read_text().replace('https://www.harwin.com/products/M7582-05','https://www.harwin.com/products/M7567-05'))
