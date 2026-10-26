from client import *
api=API();d=api.open(types.DOCTYPE_PCB);items=api.items(d,[enums.KOT_PCB_VIA])
x=clone(next(i for i in items if isinstance(i,board.Via) and i.net.name=='GND'));x.id.value=str(uuid.uuid4());x.position.CopyFrom(v(202.5,125.025))
t=board.Track(id=types.KIID(value=str(uuid.uuid4())),start=v(201.3625,125.025),end=v(202.5,125.025),width=types.Distance(value_nm=400000),layer=board.BL_F_Cu,net=board.Net(name='GND'),locked=types.LS_UNLOCKED)
c=api.begin(d)
try:api.create(d,[x,t]);api.end(d,c,'Connect RS-485 surge protection ground island to ground planes')
except:api.end(d,c,'Rollback TVS ground repair',drop=True);raise
api.request(bc.RefillZones(board=d),Empty);api.save(d);print('Saved D6 ground repair')
