from pathlib import Path
from argparse import Namespace
import yaml,sexpdata as sx
from generators.tools import cli_args
root=Path.cwd();out=root/'build/larger-controls/generated'
cli_args.init(Namespace(dry_run=False,separate_outputs=False,output_dir_footprints=out,connector_config=str(root/"build/larger-controls/kicad-library-tools/src/generators/connector/conn_config_KLCv3.yaml")))
from kilibs.config import global_config
global_config.init()
from generators.connector.generator.spec import ConnectorSpec
from generators.connector.generator.footprint import create_footprints
src=root/'PGR-FootPrints.pretty/generation/CK_1101M2S3CBE2.yaml'
create_footprints(ConnectorSpec(id='CK_1101M2S3CBE2',spec=yaml.safe_load(src.read_text())), 'connector/generator')
p=next(out.rglob('*.kicad_mod'));f=sx.loads(p.read_text());f[1]='SW_Slide_CK_1101M2S3CBE2'
for z in f:
 if isinstance(z,list) and z:
  if str(z[0])=='property' and z[1]=='Value':z[2]=f[1]
  if str(z[0])=='model':z[1]='${KIPRJMOD}/PGR-3DModels/SW_Slide_CK_1101M2S3CBE2.step'
(root/'PGR-FootPrints.pretty'/f'{f[1]}.kicad_mod').write_text(sx.dumps(f)+'\n')
# Dimensionally representative model, not a manufacturer CAD model.
import cadquery as cq
body=cq.Workplane('XY').box(12.7,6.6,6.35,centered=(True,True,False))
lever=cq.Workplane('XY').box(3.86,3.86,5.08,centered=(True,True,False)).translate((-1.195,0,6.35))
assy=cq.Assembly();assy.add(body,name='housing',color=cq.Color(.65,.65,.68));assy.add(lever,name='actuator',color=cq.Color(.08,.08,.08))
for i,x in enumerate([-4.7,0,4.7]):assy.add(cq.Workplane('XY').box(1.27,.76,3.92,centered=(True,True,False)).translate((x,0,-3.92)),name=f'terminal{i+1}',color=cq.Color(.8,.7,.3))
assy.export(str(root/'PGR-3DModels/SW_Slide_CK_1101M2S3CBE2.step'))
print('Generated footprint with existing KiCad generic generator and representative 3D model')
