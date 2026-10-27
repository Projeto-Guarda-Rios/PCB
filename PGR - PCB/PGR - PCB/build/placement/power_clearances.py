exec(open('build/placement/refine.py').read().split('changes=')[0])
import math
s=open('build/placement/place.py').read();exec(s[s.index('coord_names='):s.index('updated=[]')])
changes=[('IC1',96.2,74,0),('C8',100.3,77,270),('R35',99.5,71,90),('R36',103,73.5,90),('C5',83.5,69,270),('R2',78,78.5,90)]
updates=[]
for ref,x,y,angle in changes:
 f=clone(fs[ref]);ox,oy=xy(f.position);delta=angle-f.orientation.value_degrees
 for fld in [f.reference_field,f.value_field,f.datasheet_field,f.description_field]:transform(fld,ox,oy,x,y,delta)
 for child in f.definition.items:
  z=unpack(child);transform(z,ox,oy,x,y,delta);child.Pack(z)
 f.position.CopyFrom(v(x,y));f.orientation.value_degrees=angle;updates.append(f)
a.update(d,updates);a.save(d);print('Saved compact charger-to-boost power path and adjacent shared bypass capacitor')
