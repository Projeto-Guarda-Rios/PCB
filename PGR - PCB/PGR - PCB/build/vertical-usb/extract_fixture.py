from pathlib import Path
import sys,json
sys.path.insert(0,str(Path('build/reliability-fixes/ipc').resolve()))
import client;client.SOCKET='/tmp/pgr-usb-fixture.sock'
from client import *
a=API();docs=a.request(editor.GetOpenDocuments(type=types.DOCTYPE_PCB),editor.GetOpenDocumentsResponse);d=docs.documents[0]
fps=a.items(d,[enums.KOT_PCB_FOOTPRINT]);assert len(fps)==1
Path('build/vertical-usb/fixture-footprint.json').write_text(json_format.MessageToJson(fps[0]));a.save(d);a.request(project.CloseDocument(document=d),Empty)
# Render fixture model paths relative to the same stable project library.
p=Path('build/vertical-usb/3dmodels')
if not p.exists():p.symlink_to('../../3dmodels',target_is_directory=True)
print('Parsed corrected connector via KiCad; staged for integration')
