from pathlib import Path
import sexpdata as sx,uuid,re
p=Path('build/production-fixes');S=sx.Symbol
selections=[('Regulator_Switching','TPS61230DRC','U3'),('Regulator_Switching','TLV62568DBV','IC1'),('Power_Management','TPS2116DRL','U7'),('Power_Management','MIC2007YM6','U9'),('Power_Supervisor','TPS3808DBV','U12'),('Comparator','MCP6566','U13'),('Transistor_FET','AO3401A','Q4'),('Transistor_FET','2N7002','Q8'),('Device','Fuse','F1'),('Diode','1N4148','D13'),('power','PWR_FLAG','#FLG01'),('74xGxx','74LVC2G126','U15'),('Connector_Generic','Conn_01x06','J13'),('Connector','TestPoint','TP1'),('Switch','SW_SPST','SW4')]
def children(node,key):return [a for a in node if isinstance(a,list) and a and str(a[0])==key]
def child(node,key):return next(a for a in node if isinstance(a,list) and a and str(a[0])==key)
def load(lib,name):
 r=sx.loads(Path('/usr/share/kicad/symbols/'+lib+'.kicad_sym').read_text());n=next(a for a in children(r,'symbol') if a[1]==name)
 ext=children(n,'extends')
 if ext:
  par=load(lib,ext[0][1]);old=par[1];par[1]=name
  for a in children(par,'symbol'):a[1]=a[1].replace(old+'_',name+'_')
  propnames={a[1] for a in children(n,'property')}
  par=[a for a in par if not isinstance(a,list) or not a or str(a[0])!='property' or a[1] not in propnames]
  par.extend([a for a in n[2:] if not isinstance(a,list) or str(a[0])!='extends' and str(a[0])!='symbol']);n=par
 return n
libsymbols=[];instances=[];rootid=str(uuid.uuid4())
for idx,(lib,name,ref) in enumerate(selections):
 n=load(lib,name);n[1]=lib+':'+name;libsymbols.append(n)
 units=sorted({int(a[1].split('_')[-2]) for a in children(n,'symbol') if a[1].split('_')[-2].isdigit() and int(a[1].split('_')[-2])>0}) or [1]
 for unit in units:
  x=40+idx*25;y=50+unit*30
  props=[]
  for a in children(n,'property'):
   if a[1] in ['Reference','Value','Footprint','Datasheet','Description']:
    b=sx.loads(sx.dumps(a));at=child(b,'at');at[1]=x;at[2]=y-10 if a[1]=='Reference' else y+12
    if a[1]=='Reference':b[2]=ref
    props.append(b)
  inst=[S('symbol'),[S('lib_id'),lib+':'+name],[S('at'),x,y,0],[S('unit'),unit],[S('in_bom'),S('yes')],[S('on_board'),S('yes')],[S('dnp'),S('no')],[S('uuid'),str(uuid.uuid4())],*props,[S('instances'),[S('project'),'templates',[S('path'),'/'+rootid,[S('reference'),ref],[S('unit'),unit]]]]]
  instances.append(inst)
r=[S('kicad_sch'),[S('version'),20250114],[S('generator'),S('eeschema')],[S('uuid'),rootid],[S('paper'),'A2'],[S('lib_symbols'),*libsymbols],*instances]
(p/'templates.kicad_sch').write_text(sx.dumps(r))
print('Prepared stock library templates:',len(instances))
