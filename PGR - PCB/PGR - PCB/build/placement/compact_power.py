exec(open('build/placement/refine.py').read().split('changes=')[0])
import math
s=open('build/placement/place.py').read();exec(s[s.index('coord_names='):s.index('updated=[]')])
changes=[('C13',84.2,74,90),('U3',86.5,79,90),('L1',85.5,84,90),('C14',90.5,83,0),('C18',92,87.5,0),('C19',92,92,0),('U7',96,95,180),('C22',100.5,93.5,90),('C10',92.5,95.5,90),('IC1',95.5,74,0),('L2',91.5,75,180),('C8',99.6,77,90),('R35',98.5,71.8,90),('R36',102.5,73.5,90),('C9',91.5,70,90),('R22',90.5,79.5,90),('R23',93.5,79.5,270),('C15',87.5,71.5,90),('R32',87.5,65.5,0),('R33',87.5,68,90),('R34',90,64.5,90),('R19',98.5,86,0),('R20',98.5,89,0),('R38',95,99,90),('R39',98,99,90),('R40',104,95,90)]
updates=[]
for ref,x,y,angle in changes:
 f=clone(fs[ref]);ox,oy=xy(f.position);delta=angle-f.orientation.value_degrees
 for fld in [f.reference_field,f.value_field,f.datasheet_field,f.description_field]:transform(fld,ox,oy,x,y,delta)
 for child in f.definition.items:
  z=unpack(child);transform(z,ox,oy,x,y,delta);child.Pack(z)
 f.position.CopyFrom(v(x,y));f.orientation.value_degrees=angle;updates.append(f)
a.update(d,updates);a.save(d);print('Saved compact charger-to-boost power path and adjacent shared bypass capacitor')
