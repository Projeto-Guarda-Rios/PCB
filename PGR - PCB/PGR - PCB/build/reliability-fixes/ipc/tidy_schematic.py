from client import *
api=API();d=api.open(types.DOCTYPE_SCHEMATIC);items=api.items(d,[enums.KOT_SCH_LINE]);remove=[]
oldpairs=[((137.16,170.18),(146.05,170.18)),((146.05,170.18),(146.05,172.72)),((146.05,172.72),(152.4,172.72))]
for x in items:
 if (xy(x.start),xy(x.end)) in oldpairs:remove.append(x.id.value)
assert len(remove)==3,remove
pts=[(137.16,170.18),(138.43,170.18),(138.43,163.83),(146.05,163.83),(146.05,172.72),(152.4,172.72)]
new=[sch.SchematicLine(id=types.KIID(value=str(uuid.uuid4())),start=v(*a),end=v(*b),type=sch.SLT_WIRE) for a,b in zip(pts,pts[1:])]
c=api.begin(d)
try:api.delete(d,remove);api.create(d,new);api.end(d,c,'Keep boost feedback wire clear of capacitor symbol and fields')
except:api.end(d,c,'Rollback schematic wire cleanup',drop=True);raise
api.save(d);print('Saved schematic wire cleanup')
