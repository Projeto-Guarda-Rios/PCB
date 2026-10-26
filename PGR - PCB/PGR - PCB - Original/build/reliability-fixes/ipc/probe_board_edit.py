from client import *
api=API();d=api.open(types.DOCTYPE_PCB);fps=api.items(d,[enums.KOT_PCB_FOOTPRINT]);f=next(x for x in fps if x.reference_field.text.text.text=='U3');c=api.begin(d)
try:
 for a in f.definition.items:
  if a.Is(board.Pad.DESCRIPTOR):
   p=unpack(a)
   if p.number=='10':p.net.name='Net-(U3-FB)';p.symbol_pin.no_connect=False;a.Pack(p)
 print('UPDATE',api.update(d,[f]).updated_items[0].status)
 nets=api.request(bc.GetNets(board=d),bc.NetsResponse);print('NEWNET EXISTS',any(n.name=='Net-(U3-FB)' for n in nets.nets))
 new=next(x for x in api.items(d,[enums.KOT_PCB_FOOTPRINT]) if x.reference_field.text.text.text=='U3')
 print('FOOTPRINT',xy(new.position));print([(unpack(a).number,xy(unpack(a).position),unpack(a).net.name) for a in new.definition.items if a.Is(board.Pad.DESCRIPTOR)][:3])
finally:api.end(d,c,'Probe footprint net update',drop=True)
