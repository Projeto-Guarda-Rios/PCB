from pathlib import Path
import sys,json
sys.path.insert(0,str(Path('build/reliability-fixes/ipc').resolve()))
import client
client.SOCKET='/tmp/pgr-layout-groups.sock'
from client import *
a=API();d=a.open(types.DOCTYPE_PCB)
r=a.request(bc.ImportNetlist(board=d,netlist_path=str(Path('build/layout-groups/netlist.net').resolve()),dry_run=True,match_mode=bc.NMM_UUID,delete_extra_footprints=True,update_footprints=True,override_locks=True),bc.ImportNetlistResponse)
Path('build/layout-groups/import-preview.txt').write_text(str(r));print(r)
fs=a.items(d,[enums.KOT_PCB_FOOTPRINT]);print(fs[0])
print(a.request(bc.GetBoardDesignRules(board=d),bc.BoardDesignRulesResponse))
