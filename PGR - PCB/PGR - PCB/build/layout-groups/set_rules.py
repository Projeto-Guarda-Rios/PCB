from pathlib import Path
import json
p=Path('PGR.kicad_pro');j=json.loads(p.read_text());r=j['board']['design_settings']['rules'];r.update({'min_clearance':.127,'min_track_width':.15,'min_via_annular_width':.15,'min_via_diameter':.6,'min_through_hole_diameter':.2,'min_copper_edge_clearance':.5,'min_hole_clearance':.2,'min_hole_to_hole':.25,'min_silk_clearance':.15,'min_text_height':1.,'min_text_thickness':.15})
d=j['board']['design_settings'];d['track_widths']=[0,.15,.2,.25,.3,.5,.75,1,1.5,2];d['via_dimensions']=[{'diameter':.6,'drill':.3},{'diameter':.7,'drill':.3},{'diameter':.8,'drill':.4}]
for c in j['net_settings']['classes']:
 c.update({'clearance':.15,'via_diameter':.6,'via_drill':.3})
 if c['name']=='Default':c['track_width']=.25
j['net_settings']['netclass_patterns']=[x for x in j['net_settings']['netclass_patterns'] if x.get('pattern') not in ['RXD0-','TXD0+']]
p.write_text(json.dumps(j,indent=2)+'\n')
print('Saved minima',r['min_clearance'],r['min_via_diameter'])
