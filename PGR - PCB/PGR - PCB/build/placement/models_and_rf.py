exec(open('build/placement/refine.py').read().split('changes=')[0])
import math
s=open('build/placement/place.py').read();exec(s[s.index('coord_names='):s.index('updated=[]')])
f=clone(fs['U5']);ox,oy=xy(f.position)
for fld in [f.reference_field,f.value_field,f.datasheet_field,f.description_field]:transform(fld,ox,oy,109,59.5,0)
for child in f.definition.items:
 z=unpack(child);transform(z,ox,oy,109,59.5,0)
 if isinstance(z,board.Footprint3DModel):
  z.filename='${KICAD10_3DMODEL_DIR}/RF_Module.3dshapes/ESP32-WROOM-32E.step';z.offset.y_nm=2.99
 if isinstance(z,board.BoardGraphicShape) and z.layer==board.BL_F_SilkS:
  # Overhanging module graphics belong on fabrication, not on non-existent baseboard.
  geo=z.shape.WhichOneof('geometry')
  if geo=='segment' and (z.shape.segment.start.y_nm<50300000 or z.shape.segment.end.y_nm<50300000):z.layer=board.BL_F_Fab
  if geo=='polygon' and any(n.point.y_nm<50300000 for p in z.shape.polygon.polygons for n in p.outline.nodes):z.layer=board.BL_F_Fab
 child.Pack(z)
f.position.CopyFrom(v(109,59.5));updates=[f]
for ref,folder,filename in [('Q1','SS8050-G','SS8050-G.step'),('Q2','SS8050-G','SS8050-G.step'),('Q6','SS8050-G','SS8050-G.step'),('Q7','SS8050-G','SS8050-G.step'),('Q3','FS8205A','FS8205A.step'),('D3','LESD5D5.0CT1G','LESD5D5.0CT1G.step'),('D4','LESD5D5.0CT1G','LESD5D5.0CT1G.step'),('D5','LESD5D5.0CT1G','LESD5D5.0CT1G.step')]:
 f=clone(fs[ref]);model=board.Footprint3DModel(filename='${KIPRJMOD}/footprints/'+folder+'/'+filename,visible=True,opacity=1);model.scale.x_nm=model.scale.y_nm=model.scale.z_nm=1
 f.definition.items.add().Pack(model);updates.append(f)
a.update(d,updates);a.save(d);print('Updated actual ESP32-E model with matching 2.99mm origin offset; antenna fully beyond baseboard edge')
