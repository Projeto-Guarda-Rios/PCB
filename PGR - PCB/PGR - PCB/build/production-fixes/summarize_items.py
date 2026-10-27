exec(open('build/production-fixes/inspect_design.py').read().split('api=API()')[0])
api=API();d=api.open(types.DOCTYPE_SCHEMATIC);items=api.items(d,[enums.KOT_SCH_SYMBOL,enums.KOT_SCH_LINE,enums.KOT_SCH_JUNCTION,enums.KOT_SCH_GLOBAL_LABEL,enums.KOT_SCH_LABEL,enums.KOT_SCH_NO_CONNECT])
for s in items:
 if isinstance(s,sch.SchematicSymbolInstance):
  pins=[unpack(a.item) for a in s.definition.items if a.item.Is(sch.SchematicPin.DESCRIPTOR)]
  print(s.reference_field.text.text,s.value_field.text.text,'at',xy(s.position),'orientation',s.transform.orientation,'pins',[(x.number,x.name,xy(x.position)) for x in pins])
print('WIRES')
for x in items:
 if isinstance(x,sch.SchematicLine):print(x.id.value,xy(x.start),xy(x.end))
