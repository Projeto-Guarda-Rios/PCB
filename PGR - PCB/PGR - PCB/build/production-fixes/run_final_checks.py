from pathlib import Path
import os,subprocess,sys
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
CLI='/home/dauwt/.backplane-bend/kicad/10.0.6/bin/kicad-cli'
env=os.environ|{'KICAD10_SYMBOL_DIR':'/usr/share/kicad/symbols','KICAD10_FOOTPRINT_DIR':'/usr/share/kicad/footprints'}
for name,args in [('version',['--version']),('erc-final',['sch','erc','--severity-all','--format','json','--output',str(OUT/'erc-final.json'),str(ROOT/'PGR.kicad_sch')]),('net-export',['sch','export','netlist','--format','kicadxml','--output',str(OUT/'netlist-final.xml'),str(ROOT/'PGR.kicad_sch')]),('svg-final',['sch','export','svg','--output',str(OUT/'svg-final'),str(ROOT/'PGR.kicad_sch')])]:
 p=subprocess.run([CLI,*args],cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);(OUT/(name+'.log')).write_text(p.stdout);p.check_returncode()
subprocess.run([sys.executable,str(OUT/'verify_final.py')],cwd=ROOT,check=True)
