exec(open('build/solar-schematic/update_schematic.py').read().split('# Disconnect the old EN1')[0])
updates=[];new=[];deletes=[]
# Keep the remote-probe drawing clear of the AquaNode connector and protection diode.
for ref in ['J12','TH1','#PWR084']:
 s=syms[ref];p=xy(s.position);s=moved(s,(p[0]+20.32,p[1]-5.08))
 if ref=='J12':
  s.reference_field.text.attributes.angle.value_degrees=0;s.value_field.text.attributes.angle.value_degrees=0
 updates.append(s)
thermalpairs=[((161.29,93.98),(170.18,93.98)),((170.18,93.98),(170.18,95.25)),((161.29,91.44),(190.5,91.44)),((190.5,91.44),(190.5,105.41)),((190.5,105.41),(170.18,105.41)),((170.18,105.41),(170.18,102.87)),((190.5,105.41),(190.5,107.95))]
for x in items:
 if isinstance(x,sch.SchematicLine) and any({xy(x.start),xy(x.end)}=={a,b} for a,b in thermalpairs):
  x=clone(x)
  for p in [x.start,x.end]:a=xy(p);p.CopyFrom(v(a[0]+20.32,a[1]-5.08))
  updates.append(x)
 elif isinstance(x,sch.LocalLabel) and x.text.text=='BAT_NTC' and xy(x.position)==(161.29,93.98):
  x=clone(x);x.position.CopyFrom(v(181.61,88.9));x.text.position.CopyFrom(v(181.61,88.9));updates.append(x)
 elif isinstance(x,sch.Junction) and xy(x.position)==(190.5,105.41):
  x=clone(x);x.position.CopyFrom(v(210.82,100.33));updates.append(x)
 elif isinstance(x,sch.SchematicText):
  if x.text.text.startswith('REMOTE BATTERY TEMPERATURE'):p=(143.51,123.19)
  elif x.text.text.startswith('BATTERY / SOLAR POWER PATH'):p=(25.4,63.5)
  elif 'Ajustar conforme' in x.text.text:p=(151.13,73.66)
  else:continue
  x=clone(x);x.text.position.CopyFrom(v(*p))
  if 'Ajustar conforme' in x.text.text:
   x.text.text='ILIM is inactive in solar mode';x.text.attributes.size.CopyFrom(v(1.0,1.0));x.text.attributes.horizontal_alignment=enums.HA_LEFT;x.text.attributes.vertical_alignment=enums.VA_TOP;x.text.attributes.bold=False
  updates.append(x)
# Move EN2's ground annotation away from the input-current resistor fields.
s=moved(syms['#PWR082'],(187.96,71.12));updates.append(s)
for x in items:
 if isinstance(x,sch.SchematicLine) and {xy(x.start),xy(x.end)}=={(210.82,69.85),(198.12,69.85)}:
  x=clone(x);x.end.CopyFrom(v(187.96,69.85));updates.append(x)
 elif isinstance(x,sch.SchematicLine) and {xy(x.start),xy(x.end)}=={(198.12,69.85),(198.12,71.12)}:
  x=clone(x);x.start.CopyFrom(v(187.96,69.85));x.end.CopyFrom(v(187.96,71.12));updates.append(x)
c=api.begin(d)
try:api.update(d,updates);api.end(d,c,'Space charging-control annotations and remote battery-temperature wiring')
except:api.end(d,c,'Rollback drawing cleanup',drop=True);raise
api.save(d)
