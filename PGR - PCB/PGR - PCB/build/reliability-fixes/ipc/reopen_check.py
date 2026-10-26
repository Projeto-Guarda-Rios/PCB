from client import *
api=API()
for kind in [types.DOCTYPE_PCB,types.DOCTYPE_SCHEMATIC]:
 d=api.open(kind);api.request(project.CloseDocument(document=d),Empty)
 d=api.open(kind)
 if kind==types.DOCTYPE_PCB:
  fs=api.items(d,[enums.KOT_PCB_FOOTPRINT]);f={i.reference_field.text.text.text:i for i in fs};assert len(fs)==81
  for ref,expected in [('U3',{'10':'Net-(U3-FB)','11':'GND'}),('R22',{'2':'Net-(U3-FB)'}),('R23',{'1':'Net-(U3-FB)'}),('U4',{'7':'+3.3V'})]:
   for a in f[ref].definition.items:
    if a.Is(board.Pad.DESCRIPTOR):
     p=unpack(a)
     if p.number in expected:assert p.net.name==expected[p.number]
  print('Board saved/reopened with all corrected pin nets intact')
 else:
  nets=api.request(sc.GetSchematicNetlist(document=d),sc.SchematicNetlistResponse)
  print('Schematic saved/reopened. Net count:',len(nets.nets))
 api.request(project.CloseDocument(document=d),Empty)
