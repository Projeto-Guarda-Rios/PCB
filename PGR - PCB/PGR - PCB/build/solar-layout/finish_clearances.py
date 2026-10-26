exec(open('build/solar-layout/apply_layout.py').read().split('root=ET.parse')[0])
updates={};new=[];removed=[]
via=clone(byid['a86a04c0-2165-46cf-a5df-b073ec45e74e']);via.position.CopyFrom(v(188.8,132.88));put(via)
for x in items:
 if isinstance(x,board.BoardText) and x.id.value=='32ee160c-2717-4fa4-8464-2c06f2d9924a':
  x=clone(x);x.text.position.CopyFrom(v(190,134.5));put(x)
logo=clone(next(f for f in items if isinstance(f,board.FootprintInstance) and f.reference_field.text.text.text=='G***' and xy(f.position)[0]<220));old=xy(logo.position);target=(198.333003,103.6);scale=.7
# The logo has no pads or electrical geometry. Scale its artwork to fit above the buzzer.
def affine(m):
 for fd,val in m.ListFields():
  if fd.message_type is None:continue
  vs=val if fd.label==fd.LABEL_REPEATED else [val]
  for z in vs:
   if fd.message_type.full_name==types.Vector2.DESCRIPTOR.full_name and fd.name in ['position','start','mid','end','center','radius_point','top_left','bottom_right','point']:
    x,y=xy(z);z.CopyFrom(v(target[0]+scale*(x-old[0]),target[1]+scale*(y-old[1])))
   elif fd.message_type.full_name==types.Vector2.DESCRIPTOR.full_name and fd.name=='size':z.x_nm=round(z.x_nm*scale);z.y_nm=round(z.y_nm*scale)
   else:affine(z)
logo.position.CopyFrom(v(*target))
for c in logo.definition.items:
 x=unpack(c);affine(x);c.Pack(x)
for f in [logo.reference_field,logo.value_field,logo.datasheet_field,logo.description_field]:affine(f)
put(logo)
shape=clone(next(x for x in a.items(d,[enums.KOT_PCB_SHAPE]) if x.id.value=='2a2d019b-2168-46e6-b682-b96746bf314c'));affine(shape);put(shape)
c=a.begin(d)
try:a.update(d,list(updates.values()));a.end(d,c,'Finish route clearances and fit the logo and header label around the new connector')
except:a.end(d,c,'Rollback final clearance cleanup',drop=True);raise
a.request(bc.RefillZones(board=d),Empty);a.save(d);print('Saved final clearance cleanup')
