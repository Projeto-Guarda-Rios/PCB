from client import *
api=API();d=api.open(types.DOCTYPE_SCHEMATIC);items=api.items(d,[enums.KOT_SCH_LINE]);updates=[]
for x in items:
 if x.type==sch.SLT_WIRE and any(xy(p) in [(146.05,163.83),(146.05,172.72)] for p in [x.start,x.end]):
  for p in [x.start,x.end]:
   if p.x_nm==146050000:p.x_nm=149860000
  updates.append(x)
assert len(updates)==3,len(updates)
c=api.begin(d)
try:api.update(d,updates);api.end(d,c,'Keep feedback wire clear of capacitor labels')
except:api.end(d,c,'Rollback feedback wire spacing',drop=True);raise
api.save(d)
