from client import *
api=API();d=api.open(types.DOCTYPE_PCB);f=next(x for x in api.items(d,[enums.KOT_PCB_FOOTPRINT]) if x.reference_field.text.text.text=='R22');c=api.begin(d)
try:
 f.position.CopyFrom(v(211.5,143.1));api.update(d,[f])
 f=next(x for x in api.items(d,[enums.KOT_PCB_FOOTPRINT]) if x.reference_field.text.text.text=='R22')
 print('FOOTPRINT',xy(f.position));print([(unpack(a).number,xy(unpack(a).position)) for a in f.definition.items if a.Is(board.Pad.DESCRIPTOR)])
finally:api.end(d,c,'Probe footprint move',drop=True)
