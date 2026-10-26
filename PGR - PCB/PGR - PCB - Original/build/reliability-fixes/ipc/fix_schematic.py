from client import *
api=API();d=api.open(types.DOCTYPE_SCHEMATIC)
items=api.items(d,[enums.KOT_SCH_SYMBOL,enums.KOT_SCH_LINE,enums.KOT_SCH_JUNCTION,enums.KOT_SCH_NO_CONNECT,enums.KOT_SCH_GLOBAL_LABEL])
byid={x.id.value:x for x in items}
remove=['e8277ffa-b677-4824-9be3-475b7abeb209','f3b1f3ed-0b84-4303-abcc-09ecdd4005aa','1749de95-7dee-467e-80ad-a30db3031b33','5fd22d30-bdc7-44f3-96cc-1da349914056','ca866afb-937c-47fd-aa32-c274ff2f5d99','aec856e3-84da-478c-af66-ada54d9bc87d','446c0fc6-b3f3-4630-8fe9-ec514006c052']
labels=[x for x in items if isinstance(x,sch.GlobalLabel) and xy(x.position)==(147.32,-181.61)]
assert len(labels)==1,labels
assert labels[0].text.text=='+5V_PROGRAM',labels
remove.append(labels[0].id.value)
assert all(x in byid for x in remove)
new=[]
def wire(a,b):new.append(sch.SchematicLine(id=types.KIID(value=str(uuid.uuid4())),start=v(*a),end=v(*b),type=sch.SLT_WIRE))
def junction(p):new.append(sch.Junction(id=types.KIID(value=str(uuid.uuid4())),position=v(*p)))
wire((137.16,170.18),(146.05,170.18));wire((146.05,170.18),(146.05,172.72));wire((146.05,172.72),(152.4,172.72))
wire((127,177.8),(127,179.07));junction((127,179.07))
wire((149.86,-180.34),(152.4,-180.34));junction((152.4,-180.34))
c=api.begin(d)
try:
 print('DELETE',api.delete(d,remove))
 api.create(d,new)
 api.end(d,c,'Correct boost feedback and ground pad; bypass CP2102N internal regulator')
except:
 api.end(d,c,'Rollback schematic correction',drop=True);raise
api.save(d);print('Saved canonical schematic')
