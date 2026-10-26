exec(open('build/solar-schematic/update_schematic.py').read().split('# Disconnect the old EN1')[0])
deletes=[];new=[];updates=[]
x=next(x for x in items if isinstance(x,sch.LocalLabel) and x.text.text=='PWR_OUT');deletes.append(x.id.value)
y=clone(next(x for x in items if isinstance(x,sch.GlobalLabel) and x.text.text=='PWR_OUT' and x.spin_style==sch.SLSS_LEFT));old=xy(y.position);pos=(203.2,67.31);delta=(pos[0]-old[0],pos[1]-old[1]);y.id.value=uid();y.position.CopyFrom(v(*pos));y.text.position.CopyFrom(v(*pos))
for f in [y.intersheet_refs_field,*y.fields]:
 p=xy(f.text.position);f.text.position.CopyFrom(v(p[0]+delta[0],p[1]+delta[1]))
new.append(y)
remove_wire((223.52,64.77),(236.22,64.77))
for x in items:
 if isinstance(x,sch.Junction) and xy(x.position)==(223.52,64.77):deletes.append(x.id.value)
 if isinstance(x,sch.SchematicSymbolInstance) and x.reference_field.text.text in ['#PWR082','#PWR083','#PWR084']:
  x=clone(x);x.lib_name=''
  for child in x.definition.items:
   if child.item.Is(sch.SchematicGraphicShape.DESCRIPTOR):
    shape=unpack(child.item)
    if shape.shape.WhichOneof('geometry')=='polygon':
     nodes=shape.shape.polygon.polygons[0].outline.nodes
     if len(nodes)==5:nodes.add().point.CopyFrom(v(0,1.27))
     child.item.Pack(shape)
  updates.append(x)
c=api.begin(d)
try:
 api.delete(d,deletes);api.update(d,updates);api.create(d,new);api.end(d,c,'Preserve standard ground symbols and remove obsolete control stub')
except:api.end(d,c,'Rollback schematic cleanup',drop=True);raise
api.save(d)
