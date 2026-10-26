exec(open('build/solar-layout/apply_layout.py').read().split('root=ET.parse')[0])
expected={'U1':{'1':'/BAT_NTC','5':'GND','6':'PWR_OUT','14':'Net-(U1-TMR)'},'R30':{'1':'GND','2':'Net-(U1-TMR)'},'J12':{'1':'/BAT_NTC','2':'GND'}}
a.save(d);a.request(project.CloseDocument(document=d),Empty);d=a.open(types.DOCTYPE_PCB)
fs={f.reference_field.text.text.text:f for f in a.items(d,[enums.KOT_PCB_FOOTPRINT])}
assert 'TH1' not in fs and all(ref in fs for ref in expected)
for ref,nets in expected.items():
 for child in fs[ref].definition.items:
  if child.Is(board.Pad.DESCRIPTOR):
   p=unpack(child)
   if p.number in nets:assert p.net.name==nets[p.number],(ref,p)
assert fs['R1'].value_field.text.text.text=='2kR'
assert fs['R30'].value_field.text.text.text=='68kR'
its=a.items(d,[enums.KOT_PCB_FOOTPRINT,enums.KOT_PCB_TRACE,enums.KOT_PCB_VIA,enums.KOT_PCB_ZONE,enums.KOT_PCB_SHAPE,enums.KOT_PCB_TEXT])
Path('build/solar-layout/items-final.json').write_text(json.dumps([json_format.MessageToDict(x,preserving_proto_field_name=True)|{'_type':x.DESCRIPTOR.name} for x in its],indent=2))
a.request(project.CloseDocument(document=d),Empty)
# Close the unused schematic context opened with the project without modifying it.
try:
 docs=a.request(editor.GetOpenDocuments(type=types.DOCTYPE_SCHEMATIC),editor.GetOpenDocumentsResponse)
 for sd in docs.documents:a.request(project.CloseDocument(document=sd),Empty)
except RuntimeError as e:
 if 'AS_UNHANDLED' not in str(e):raise
print('Reopened canonical board; all charger and remote-probe pad nets persisted')
