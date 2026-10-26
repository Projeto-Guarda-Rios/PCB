import os,subprocess,concurrent.futures
from pathlib import Path
root=Path.cwd();out=root/'build/solar-schematic';cli='/home/dauwt/.backplane-bend/kicad/10.0.6/bin/kicad-cli'
env=os.environ|{'KICAD10_SYMBOL_DIR':'/usr/share/kicad/symbols','KICAD10_FOOTPRINT_DIR':'/usr/share/kicad/footprints'}
cmds={'netlist':['sch','export','netlist','--format','kicadxml','-o',str(out/'netlist-after.xml')], 'erc':['sch','erc','--format','json','-o',str(out/'erc-after.json')], 'svg':['sch','export','svg','-o',str(out/'svg')]}
def run(k,a):
 r=subprocess.run([cli,*a,str(root/'PGR.kicad_sch')],env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);(out/(k+'-after.log')).write_text(r.stdout);print(k,r.returncode)
with concurrent.futures.ThreadPoolExecutor() as pool:list(pool.map(lambda kv:run(*kv),cmds.items()))
