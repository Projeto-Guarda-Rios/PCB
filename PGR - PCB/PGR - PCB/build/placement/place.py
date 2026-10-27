from pathlib import Path
import sys,json,math,uuid
sys.path.insert(0,str(Path('build/reliability-fixes/ipc').resolve()))
import client;client.SOCKET='/tmp/pgr-placement.sock'
from client import *
a=API();d=a.open(types.DOCTYPE_PCB)
source=json.loads(Path('build/placement/source-items.json').read_text());fs={}
for entry in source:
 f=board.FootprintInstance();json_format.ParseDict(entry,f);fs[f.reference_field.text.text.text]=f
placements={}
def put(ref,x,y,angle=0):
 assert ref not in placements,ref
 placements[ref]=(x,y,angle)
# Perimeter connections. The JST connectors mate vertically; their latch sides face out.
for r,x,y,t in [('BT1',65,55,0),('J10',79,55,0),('J12',141,55,0),('J7',153,77,90),('J8',153,92,90),('J11',153,114,90),('J9',52.75,91,270),('J13',62,128,90),('J14',81,128,90),('JP1',95,128,90),('J1',112,129,90)]:put(r,x,y,t)
# Battery current path, cell protection, and low-current switch control.
for r,x,y,t in [('F1',65,64,0),('Q4',70,64,180),('Q9',74.5,64,0),('R53',72.5,61.5,0),('SW4',59.5,70,0),('U6',62.5,76,0),('Q3',69,76,0),('R11',63,72.5,0),('R17',62.5,80,0),('C12',59,76,90),('Q7',68.5,69,0),('R54',65,69.5,0),('D13',72,69,0),('R73',75.5,69,0)]:put(r,x,y,t)
# Solar polarity protection and charger. Local bypass and programming parts surround U1.
for r,x,y,t in [('Q5',82,63,0),('U1',80,74,0),('C11',76,74,0),('C5',82.5,70,270),('R1',78.5,70.5,270),('R72',80,70,90),('R2',84,73,0),('R30',83,76.5,90),('R31',76,70.5,90),('R19',84.5,79,0),('R20',84.5,81.5,0),('D9',88,58,90),('D10',92,58,90),('R21',88,62,90),('R24',92,62,90)]:put(r,x,y,t)
# 5V boost. Input and output capacitor groups stay on opposite sides of its switching loop.
for r,x,y,t in [('U3',78,86,0),('L1',73.5,84.75,0),('C13',82,83.5,90),('C14',73,88,180),('C18',73,92.5,180),('C19',73,97,180),('R22',83,88.5,90),('R23',86,89.5,90),('C15',80.5,91,90),('R32',86,83,0),('R33',86,86,90),('R34',89,86,90)]:put(r,x,y,t)
# USB limiting and source selector.
for r,x,y,t in [('U11',65,100.5,0),('C35',61.5,100.5,90),('C21',68.5,100.5,90),('R37',68.5,103.5,90),('U7',82,96,180),('C10',79,96,90),('C22',86.5,96.5,0),('R38',82,100,90),('R39',85,100,90),('R40',88,100,90)]:put(r,x,y,t)
# 3.3V regulator feeds the ESP32 from the left, below the RF keepout.
for r,x,y,t in [('IC1',93,74,0),('L2',88.5,75,180),('C8',96.5,75,90),('C9',88.5,70,180),('R35',96.5,71.5,90),('R36',99.5,73.5,90),('U12',95.5,66,0),('C20',92.5,66,90)]:put(r,x,y,t)
# ESP32 antenna overhang at the top. All decoupling remains on the component side.
for r,x,y,t in [('U5',109,62,0),('C7',97.5,54.5,0),('C6',94,56,90),('C2',97.5,58.5,90),('R10',94.5,61,90),('R12',121.5,70,90),('R25',121.5,73.5,90),('Q1',104,80,0),('Q2',109,80,0),('R15',104,83.5,90),('R16',109,83.5,90),('SW1',107,119,0),('SW2',97,119,0),('R9',107,115,90)]:put(r,x,y,t)
# Temperature interlock near the cell probe, separated from the switching stages.
for r,x,y,t in [('U13',136,64,0),('U14',143,64,0),('C25',136,60.5,90),('C26',143,60.5,90),('R45',132,68,90),('R46',135,69.5,90),('R47',135,73,90),('R48',143,69.5,90),('R49',143,73,90),('R50',146.5,69.5,90),('R51',150,69.5,90),('Q8',148,64,0),('C27',151.5,63.5,90)]:put(r,x,y,t)
for r,x,y,t in [('R66',124,61,90),('R67',124,64.5,90),('C29',124,68,90),('R68',127.5,62,90),('C30',127.5,65.5,90),('R69',124,73,90),('C31',127.5,73,90),('R70',131,73,90),('R71',134.5,77,90)]:put(r,x,y,t)
# Modem power and UART isolation at its cable entry.
for r,x,y,t in [('U9',137,88,0),('C36',133.5,87,90),('C23',140.5,88,90),('R41',140.5,91.5,90),('R43',133.5,91,90),('C32',146.5,89.5,0),('C33',146.5,94,0),('U15',132,81.5,0),('C28',132,78.5,0),('R60',128.5,80,90),('R61',137,82,90),('R62',124.5,80,90),('R63',124.5,83.5,90)]:put(r,x,y,t)
# AquaNode power protection and RS485 transceiver, terminating at the right-hand connector.
for r,x,y,t in [('U10',137,107,0),('C37',133.5,106,90),('C24',140.5,107,90),('R42',140.5,110.5,90),('R44',133.5,110.5,90),('C34',146,109,0),('U8',137,118,0),('R3',144,114.5,90),('D6',147,119,0),('C17',142,112,0),('R18',130.5,121,90),('R28',127,121,90),('R29',127,117.5,90)]:put(r,x,y,t)
# USB protection sits immediately behind the connector, before the USB-UART bridge.
for r,x,y,t in [('U4',64,91,0),('D4',58.5,90,90),('D5',58.5,92,90),('D3',57.5,96,90),('C1',58,99,90),('R4',60.5,85,90),('R5',57.5,85,90),('C3',67.5,87,90),('C4',63.5,86,0),('R6',68,90.5,0),('R7',68,93,90),('R8',64,95.5,0)]:put(r,x,y,t)
for r,x,y,t in [('BZ1',110,101,0),('Q6',105,101,0),('D14',110,110,0),('R64',101.5,100,90),('R65',101.5,103.5,90),('D7',109,88,90),('R13',106,88,0),('D8',116,88,90),('R14',113,88,0)]:put(r,x,y,t)
for r,x,y in [('TP1',62,111),('TP2',70,111),('TP3',78,111),('TP4',86,111),('TP5',62,118),('TP6',70,118),('TP7',78,118),('TP8',86,118)]:put(r,x,y)
assert set(fs)==set(placements),(set(fs)-set(placements),set(placements)-set(fs))
def uid():return types.KIID(value=str(uuid.uuid4()))
coord_names={'position','start','mid','end','center','top_left','bottom_right','point','control1','control2','control_1','control_2','radius_point'}
def transform(m,ox,oy,nx,ny,delta):
 c=math.cos(math.radians(delta));s=math.sin(math.radians(delta))
 for fd,val in m.ListFields():
  if fd.message_type is None:continue
  for z in (val if fd.label==fd.LABEL_REPEATED else [val]):
   if fd.message_type.full_name==types.Vector2.DESCRIPTOR.full_name and fd.name in coord_names:
    x=z.x_nm/1e6-ox;y=z.y_nm/1e6-oy;z.CopyFrom(v(nx+x*c+y*s,ny-x*s+y*c))
   elif fd.message_type.full_name==types.Angle.DESCRIPTOR.full_name and fd.name=='angle':z.value_degrees=(z.value_degrees+delta)%360
   else:transform(z,ox,oy,nx,ny,delta)
updated=[]
for ref,(x,y,angle) in placements.items():
 f=clone(fs[ref]);ox,oy=xy(f.position);delta=angle-f.orientation.value_degrees
 for fld in [f.reference_field,f.value_field,f.datasheet_field,f.description_field]:transform(fld,ox,oy,x,y,delta)
 for item in f.definition.items:
  z=unpack(item);transform(z,ox,oy,x,y,delta);item.Pack(z)
 f.position.CopyFrom(v(x,y));f.orientation.value_degrees=angle;f.locked=types.LS_UNLOCKED
 f.reference_field.visible=True;f.reference_field.text.text.attributes.visible=True;f.reference_field.text.text.attributes.angle.value_degrees=0;f.reference_field.text.text.attributes.size.CopyFrom(v(1,1));f.reference_field.text.text.attributes.stroke_width.value_nm=150000
 f.value_field.visible=False;updated.append(f)
# The board's 1.5mm corner chamfers leave all four mounting bosses intact.
new=[]
outline=[(51.5,50),(158.5,50),(160,51.5),(160,133.5),(158.5,135),(51.5,135),(50,133.5),(50,51.5)]
for p,q in zip(outline,outline[1:]+outline[:1]):
 z=board.BoardGraphicShape(id=uid(),layer=board.BL_Edge_Cuts);z.shape.segment.start.CopyFrom(v(*p));z.shape.segment.end.CopyFrom(v(*q));z.shape.attributes.stroke.width.value_nm=50000;new.append(z)
# Reserve 9mm hardware envelopes at each M3 clearance hole, on every copper layer.
holes=[(55,55),(155,55),(55,130),(155,130)]
for idx,(x,y) in enumerate(holes,1):
 z=board.Zone(id=uid(),type=board.ZT_RULE_AREA,layers=[board.BL_F_Cu,board.BL_In1_Cu,board.BL_In2_Cu,board.BL_B_Cu]);z.name=f'M3 hardware H{idx} - 9mm clearance';z.rule_area_settings.keepout_copper=True;z.rule_area_settings.keepout_tracks=True;z.rule_area_settings.keepout_vias=True;z.rule_area_settings.keepout_pads=True;z.rule_area_settings.keepout_footprints=True
 poly=z.outline.polygons.add().outline;poly.closed=True
 for n in range(48):poly.nodes.add().point.CopyFrom(v(x+4.5*math.cos(2*math.pi*n/48),y+4.5*math.sin(2*math.pi*n/48)))
 z.border.style=board.ZBS_DIAGONAL_EDGE;z.border.pitch.value_nm=500000;new.append(z)
# Labels are kept on the drawing layer until the final silkscreen is reviewed.
def label(t,x,y,size=1,layer=board.BL_Dwgs_User):
 z=board.BoardText(id=uid(),layer=layer);z.text.text=t;z.text.position.CopyFrom(v(x,y));z.text.attributes.size.CopyFrom(v(size,size));z.text.attributes.stroke_width.value_nm=150000;z.text.attributes.horizontal_alignment=enums.HA_CENTER;z.text.attributes.vertical_alignment=enums.VA_CENTER;return z
new+=[label('PGR | placement draft | 110 x 85 mm | 4x M3',105,140,1.2),label('ANTENNA - keep clear of enclosure metal and cables',109,42,1.1),label('Programming / test access',81,106.5,1)]
for t,x,y in [('BAT',65,60),('SOLAR',80,60),('CELL NTC',141,60),('TAMPER',153,81.5),('MODEM',153,97),('AQUANODE',153,119.5),('JTAG',68,132),('UART',85,132),('RX SELECT',97,132),('EXPANSION',127,132)]:new.append(label(t,x,y,1,board.BL_F_SilkS))
for t,x,y in [('GND',62,114),('3V3',70,114),('5V',78,114),('SYS',86,114),('BAT',62,121),('MODEM',70,121),('NODE',78,121),('RESET',86,121)]:new.append(label(t,x,y,.9,board.BL_F_SilkS))
old=a.items(d,[enums.KOT_PCB_TEXT,enums.KOT_PCB_SHAPE,enums.KOT_PCB_TEXTBOX,enums.KOT_PCB_DIMENSION,enums.KOT_PCB_GROUP,enums.KOT_PCB_TRACE,enums.KOT_PCB_VIA])
c=a.begin(d)
try:
 if old:a.delete(d,[i.id.value for i in old])
 a.update(d,updated);a.create(d,new);a.end(d,c,'Place PGR components with edge access and four M3 hardware reservations')
except:a.end(d,c,'Rollback PCB placement',drop=True);raise
a.save(d)
Path('build/placement/positions.json').write_text(json.dumps(placements,indent=2))
print('Saved initial placement:',len(updated),'parts;',len(new),'outline/clearance/label items')
a.request(project.CloseDocument(document=d),Empty)
