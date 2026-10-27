from helper import api,d,project,Empty,types
from pathlib import Path
import sexpdata as sx
api.request(project.CloseDocument(document=d),Empty)
p=Path('PGR.kicad_sch');s=p.read_text().replace('CHG32; JTAG','CHG21; JTAG')
assert 'CHG32; JTAG' not in s
r=sx.loads(s);S=sx.Symbol
assert not any(isinstance(n,list) and n and str(n[0])=='title_block' for n in r)
r.insert(5,[S('title_block'),[S('title'),'PGR parent water monitoring station'],[S('date'),'2026-10-26'],[S('rev'),'Schematic review 1'],[S('company'),'Projeto Guarda Rios']])
p.write_text(sx.dumps(r));d=api.open(types.DOCTYPE_SCHEMATIC);api.save(d)
