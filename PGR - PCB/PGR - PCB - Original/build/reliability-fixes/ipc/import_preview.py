from client import *
api=API();d=api.open(types.DOCTYPE_PCB)
r=api.request(bc.ImportNetlist(board=d,netlist_path=str(ROOT/'build/reliability-fixes/netlist-stage1.net'),dry_run=True,match_mode=bc.NMM_UUID,delete_extra_footprints=False,update_footprints=False),bc.ImportNetlistResponse)
print(r)
