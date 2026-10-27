import math
exec(open('build/placement/refine.py').read().split('changes=')[0])
s=open('build/placement/place.py').read();exec(s[s.index('coord_names='):s.index('updated=[]')])
updates=[]
for ref,x,y,angle in [('U6',61.8,76,0),('C12',57.5,76,90),('Q3',68.4,76,0),('R2',84,75,0),('R30',80.5,78,90),('R6',69.5,91,90)]:
 f=clone(fs[ref]);ox,oy=xy(f.position);delta=angle-f.orientation.value_degrees
 for fld in [f.reference_field,f.value_field,f.datasheet_field,f.description_field]:transform(fld,ox,oy,x,y,delta)
 for child in f.definition.items:
  z=unpack(child);transform(z,ox,oy,x,y,delta);child.Pack(z)
 f.position.CopyFrom(v(x,y));f.orientation.value_degrees=angle;updates.append(f)
a.update(d,updates);a.save(d)
print('Refined final physical clearances')
