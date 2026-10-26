exec(open('build/solar-layout/apply_layout.py').read().split('root=ET.parse')[0])
ids=json.loads(Path('build/solar-layout/new-ids.json').read_text());new=[];updates={};removed=[]
def track(net,pts,width=.2,layer=board.BL_F_Cu,key=None):
 for i,(p,q) in enumerate(zip(pts,pts[1:])):
  x=board.Track(id=types.KIID(value=uid()),start=v(*p),end=v(*q),width=types.Distance(value_nm=round(width*1e6)),layer=layer,net=board.Net(name=net),locked=types.LS_UNLOCKED);new.append(x)
  if key:ids[f'{key}-{i}']=x.id.value
# Keep R30's copper more than 0.5 mm from the outline.
r=movefp(fps['R30'],(232.8,143.7));field(r,(235.6,143.6),.8);r.datasheet_field.text.text.text='';put(r)
r=clone(fps['R1']);r.datasheet_field.text.text.text='';put(r)
r=clone(fps['J12']);r.datasheet_field.text.text.text='';put(r)
# Explicit ground connections on the two pads whose surrounding pours are constrained.
for ref,num in [('U1','4'),('R2','1')]:
 f=clone(fps[ref])
 for c in f.definition.items:
  if c.Is(board.Pad.DESCRIPTOR):
   p=unpack(c)
   if p.number==num:p.pad_stack.zone_settings.zone_connection=board.ZCS_FULL;c.Pack(p)
 put(f)
def alter(key,start=None,end=None):
 t=clone(byid[ids[key]])
 if start:t.start.CopyFrom(v(*start))
 if end:t.end.CopyFrom(v(*end))
 put(t)
alter('EN1-back-0',end=(229.6,138.05));alter('EN1-back-1',start=(229.6,138.05),end=(229.6,140.3));alter('EN1-back-2',start=(229.6,140.3),end=(230.3,141.0))
via=clone(byid[ids['TMR-chip-via']]);via.position.CopyFrom(v(235.225,138.4));put(via)
alter('TMR-front-0',end=(234.825,138.8));alter('TMR-front-1',start=(234.825,138.8),end=(235.225,138.4));removed.append(ids['TMR-front-2'])
alter('TMR-back-0',start=(235.225,138.4),end=(235.225,142.325));alter('TMR-back-1',start=(235.225,142.325))
alter('TMR-R30-0',end=(233.875,143.45));alter('TMR-R30-1',start=(233.875,143.45),end=(233.625,143.7))
alter('R30-ground-0',start=(231.975,143.7),end=(231.1,143.7));alter('R30-ground-1',start=(231.1,143.7))
alter('NTC-extension-0',end=(197.2,134.0));alter('NTC-extension-1',start=(197.2,142.15))
track('/BAT_NTC',[(197.2,134.0),(197.2,142.15)],.254,board.BL_In2_Cu,key='NTC-middle')
# The connector's plated holes require a detour in the original back-side LED route.
removed+=['138ad79a-5465-47d3-b1ab-bbdcc0980fdc','4d6b8cce-f4d8-4593-a9d6-064a7007999e']
track('IO18',[(205.695,127.955),(202.2,131.45),(188.0,131.45),(188.0,133.8)],.254,board.BL_B_Cu,key='IO18-detour')
# Keep all parts of the grouped logo together and clear of the buzzer.
logo=next(f for f in items if isinstance(f,board.FootprintInstance) and f.reference_field.text.text.text=='G***' and xy(f.position)[0]<220);put(movefp(logo,(198.333003,104.65)))
shapes=a.items(d,[enums.KOT_PCB_SHAPE]);shape=clone(next(x for x in shapes if x.id.value=='2a2d019b-2168-46e6-b682-b96746bf314c'));shift_geom(shape,0,104.65-131.276009);put(shape)
for x in items:
 if isinstance(x,board.BoardText) and x.id.value=='32ee160c-2717-4fa4-8464-2c06f2d9924a':
  x=clone(x);x.text.position.CopyFrom(v(192.125,135.1));x.text.attributes.angle.value_degrees=0;x.text.attributes.size.CopyFrom(v(.8,.8));put(x)
 if isinstance(x,board.BoardText) and x.text.text=='1 TS  2 GND':
  x=clone(x);x.text.attributes.size.CopyFrom(v(.8,.8));put(x)
c=a.begin(d)
try:a.delete(d,removed);a.update(d,list(updates.values()));a.create(d,new);a.end(d,c,'Resolve connector crossing, charger clearances, ground returns and assembly labels')
except:a.end(d,c,'Rollback routing refinement',drop=True);raise
a.request(bc.RefillZones(board=d),Empty);a.save(d)
Path('build/solar-layout/new-ids.json').write_text(json.dumps(ids,indent=2));print('Saved refined layout')
