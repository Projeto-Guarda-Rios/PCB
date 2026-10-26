from client import *
api=API();d=api.open(types.DOCTYPE_PCB);items=api.items(d,[enums.KOT_PCB_FOOTPRINT,enums.KOT_PCB_TRACE,enums.KOT_PCB_VIA]);updates=[]
# Keep new through vias clear of existing status traces on the back layer.
for x in items:
 if isinstance(x,board.Via) and x.id.value=='fe823bb7-a212-4bda-a4b7-e3d973214da2':x.position.CopyFrom(v(210.6,142.3));updates.append(x)
 if isinstance(x,board.Via) and x.id.value=='bdc46130-ba97-41fd-a4df-45fbaeb8b7d7':x.position.CopyFrom(v(212.7,142.55));updates.append(x)
 if isinstance(x,board.Track):
  if xy(x.start)==(211.451429,142.3) and xy(x.end)==(211.451429,142.95):x.end.CopyFrom(v(210.6,142.3));updates.append(x)
  if x.net.name=='Net-(U3-FB)' and x.layer==board.BL_F_Cu and xy(x.end)==(212.7,142.9):x.end.CopyFrom(v(212.7,142.55));updates.append(x)
  if x.net.name=='Net-(U3-FB)' and x.layer==board.BL_In2_Cu and xy(x.start)==(212.7,142.9):x.start.CopyFrom(v(212.7,142.55));x.end.CopyFrom(v(213.15,143.0));updates.append(x)
  if x.net.name=='Net-(U3-FB)' and x.layer==board.BL_In2_Cu and xy(x.start)==(212.8,143.0):x.start.CopyFrom(v(213.15,143.0));updates.append(x)
 if isinstance(x,board.FootprintInstance) and x.reference_field.text.text.text=='R23':
  for a in x.definition.items:
   if a.Is(board.Pad.DESCRIPTOR):
    p=unpack(a)
    if p.number=='2':p.pad_stack.zone_settings.zone_connection=board.ZCS_FULL;a.Pack(p)
  updates.append(x)
new=[]
for a,b in zip([(223.3,143.65),(223.3,142.3),(223.,142.)],[(223.3,142.3),(223.,142.)]):
 new.append(board.Track(id=types.KIID(value=str(uuid.uuid4())),start=v(*a),end=v(*b),width=types.Distance(value_nm=300000),layer=board.BL_F_Cu,net=board.Net(name='GND'),locked=types.LS_UNLOCKED))
c=api.begin(d)
try:api.update(d,updates);api.create(d,new);api.end(d,c,'Finish feedback routing and local ground returns')
except:api.end(d,c,'Rollback routing cleanup',drop=True);raise
api.request(bc.RefillZones(board=d),Empty);api.save(d);print('Saved route cleanup')
