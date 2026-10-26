from client import *
api=API();d=api.open(types.DOCTYPE_PCB)
items=api.items(d,[enums.KOT_PCB_FOOTPRINT,enums.KOT_PCB_TRACE,enums.KOT_PCB_VIA])
fps={x.reference_field.text.text.text:x for x in items if isinstance(x,board.FootprintInstance)}
updates=[]
def setpads(ref,nets):
 f=fps[ref]
 for a in f.definition.items:
  if a.Is(board.Pad.DESCRIPTOR):
   p=unpack(a)
   if p.number in nets:
    p.net.name=nets[p.number];p.symbol_pin.no_connect=False
    if ref=='U3' and p.number=='11':p.pad_stack.zone_settings.zone_connection=board.ZCS_FULL
    a.Pack(p)
 updates.append(f)
setpads('U3',{'10':'Net-(U3-FB)','11':'GND'})
setpads('U4',{'7':'+3.3V'})
setpads('R22',{'2':'Net-(U3-FB)'});fps['R22'].value_field.text.text.text='820K'
setpads('R23',{'1':'Net-(U3-FB)'});fps['R23'].value_field.text.text.text='91K'
# Remove obsolete ground straps to the former FB net and its redundant ground via.
remove=['05f1db66-ac2f-4eee-8a5b-25a65ab820ad','6dec657d-7c94-4577-a543-48109ad09455','7acbdb75-4827-41a1-81f0-6b0ec45628b6',
'49330d0e-8421-4967-8b9a-7fa269d01d79','6dfce309-cd2a-431d-819b-2275c3cd3c2f','a72da921-fc51-4589-97a2-96be01959178','b5f023a6-6ada-47c0-9f14-23fff0b4ac46',
'd670e439-1f46-4dab-a1dc-d70efba147c0','b33e765d-bf83-4f3a-9602-671c8a984ccf','9cd81a33-dab7-460f-a18e-4bc788a9829b','950a6d8a-fa8d-4d89-a71f-e206078bf03d','88bda19d-dc82-4570-ae15-e92a8b38891d','41dbd92c-8d5c-4d10-a7b8-c1c59f3477d8',
'1e3bb3e4-cac5-40c4-bfd6-9b2f1497e591','df0c4fb2-f6bb-4f2e-a559-f7bc565e15ba']
assert all(any(x.id.value==i for x in items) for i in remove)
new=[]
def track(net,pts,width=.254,layer=board.BL_F_Cu):
 for a,b in zip(pts,pts[1:]):
  if a==b:continue
  new.append(board.Track(id=types.KIID(value=str(uuid.uuid4())),start=v(*a),end=v(*b),width=types.Distance(value_nm=round(width*1e6)),layer=layer,net=board.Net(name=net),locked=types.LS_UNLOCKED))
via_template=next(x for x in items if isinstance(x,board.Via) and x.net.name=='GND')
def via(net,p):
 x=clone(via_template);x.id.value=str(uuid.uuid4());x.position.CopyFrom(v(*p));x.net.name=net;new.append(x)
# RS-485 ground via sits outside the solder pad and connects to the solid inner ground plane.
track('GND',[(206.5,123.12),(206.5,122.3)],.3);via('GND',(206.5,122.3))
# Bypass the USB bridge's internal regulator; retain VBUS sensing through R6/R7.
track('+3.3V',[(223.89,128.095),(224.39,128.095)],.2)
# Restore short local control and power ground connections to the grounded exposed pad.
track('GND',[(213.2,141.9),(214.46,141.9)],.254)
track('GND',[(216.435,140.9),(215.46,140.9)],.3)
track('GND',[(211.451429,142.3),(211.451429,142.95)],.4);via('GND',(211.451429,142.95))
track('GND',[(222.35,142.0),(223.0,142.0)],.4);via('GND',(223.0,142.0))
# Quiet FB route on In2, shielded from the top switching node by the solid In1 ground plane.
track('Net-(U3-FB)',[(213.2,142.4),(212.7,142.9)],.2);via('Net-(U3-FB)',(212.7,142.9))
track('Net-(U3-FB)',[(212.7,142.9),(212.8,143.0),(218.9,143.0),(219.2,142.7),(219.2,141.6),(221.25,141.6)],.2,board.BL_In2_Cu)
via('Net-(U3-FB)',(221.25,141.6))
track('Net-(U3-FB)',[(220.5,141.625),(221.225,141.625),(221.25,141.6)],.2)
track('Net-(U3-FB)',[(221.25,141.6),(221.25,143.25),(221.65,143.65)],.2)
c=api.begin(d)
try:
 result=api.delete(d,remove);assert all(x.status==editor.IDS_OK for x in result.deleted_items),result
 api.update(d,updates)
 api.create(d,new)
 api.end(d,c,'Correct boost feedback, exposed-pad ground, RS-485 ground and USB bridge power')
except:
 api.end(d,c,'Rollback board correction',drop=True);raise
api.request(bc.RefillZones(board=d),Empty);api.save(d)
print('Saved canonical board. Updated',len(updates),'footprints, removed',len(remove),'obsolete copper items, added',len(new),'tracks/vias.')
for f in api.items(d,[enums.KOT_PCB_FOOTPRINT]):
 ref=f.reference_field.text.text.text
 if ref in ['U3','U4','R22','R23']:
  print(ref,[(unpack(a).number,unpack(a).net.name) for a in f.definition.items if a.Is(board.Pad.DESCRIPTOR) and unpack(a).number in ({'10','11'} if ref=='U3' else {'7'} if ref=='U4' else {'1','2'})])
