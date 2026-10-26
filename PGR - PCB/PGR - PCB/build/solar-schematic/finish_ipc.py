exec(open('build/solar-schematic/update_schematic.py').read().split('# Disconnect the old EN1')[0])
t=clone(next(x for x in items if isinstance(x,sch.SchematicText) and x.text.text.startswith('BATTERY / SOLAR POWER PATH')));t.text.position.CopyFrom(v(25.4,75.565))
c=api.begin(d)
try:api.update(d,[t]);api.end(d,c,'Keep power-path documentation clear of connector pin labels')
except:api.end(d,c,'Rollback note placement',drop=True);raise
api.save(d)
# Confirm all intended values, pins and attributes survive reopening.
api.request(project.CloseDocument(document=d),Empty)
d=api.open(types.DOCTYPE_SCHEMATIC)
ss={s.reference_field.text.text:s for s in api.items(d,[enums.KOT_SCH_SYMBOL])}
assert ss['R1'].value_field.text.text=='2kR'
assert ss['R30'].value_field.text.text=='68kR'
assert ss['TH1'].attributes.exclude_from_board
assert ss['TH1'].attributes.exclude_from_position_files
assert ss['J12'].footprint_field.text.text=='Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical'
print('Reopened schematic; charge settings and remote-probe attributes persisted')
api.request(project.CloseDocument(document=d),Empty)
