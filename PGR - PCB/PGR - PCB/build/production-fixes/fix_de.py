exec(open('build/production-fixes/inspect_design.py').read().split('api=API()')[0]);api=API();d=api.open(types.DOCTYPE_SCHEMATIC)
x=sch.LocalLabel(id=types.KIID(value=str(uuid.uuid4())),position=v(96.52,48.26),spin_style=sch.SLSS_RIGHT);x.text.text='IO22';x.text.position.CopyFrom(v(96.52,48.26));x.text.attributes.size.CopyFrom(v(1.27,1.27));x.text.attributes.visible=True
c=api.begin(d);api.create(d,[x]);api.end(d,c,'Retain GPIO22 on RS485 driver enable');api.save(d)
