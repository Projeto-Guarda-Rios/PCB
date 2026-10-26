from pathlib import Path
import os,concurrent.futures,subprocess
p=Path.cwd();out=p/'build/solar-layout';cli='/home/dauwt/.backplane-bend/kicad/10.0.6/bin/kicad-cli'
env=os.environ|{'KICAD10_SYMBOL_DIR':'/usr/share/kicad/symbols','KICAD10_FOOTPRINT_DIR':'/usr/share/kicad/footprints','KICAD10_3DMODEL_DIR':'/usr/share/kicad/3dmodels','KICAD9_3DMODEL_DIR':'/usr/share/kicad/3dmodels'}
jobs={
 'drc-final':['pcb','drc','--format','json','--refill-zones','--schematic-parity','-o',str(out/'drc-final.json')],
 'layers-final':['pcb','export','svg','--layers','F.Cu,B.Cu,In1.Cu,In2.Cu,F.Silkscreen,F.Courtyard','--mode-multi','--page-size-mode','2','--exclude-drawing-sheet','-o',str(out/'layers-final')],
 'render-final':['pcb','render','--output',str(out/'board-oblique.png'),'--width','1800','--height','1400','--background','transparent','--quality','basic','--preset','follow_pcb_editor','--rotate','25,0,30'],
 'render-top':['pcb','render','--output',str(out/'board-top.png'),'--width','2200','--height','1500','--background','transparent','--quality','basic','--preset','follow_pcb_editor']}
def run(k,cmd):
 r=subprocess.run([cli,*cmd,str(p/'PGR.kicad_pcb')],env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);(out/(k+'.log')).write_text(r.stdout);print(k,r.returncode,flush=True)
 if r.returncode:raise RuntimeError(k)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(lambda kv:run(*kv),jobs.items()))
