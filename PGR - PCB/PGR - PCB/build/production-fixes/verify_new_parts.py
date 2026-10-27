from helper import *
# MIC2007 CSLEW capacitor returns to VIN, as specified by Microchip, not ground.
for cap,rail in [('C21','+5V_PROGRAM'),('C23','+5V'),('C24','+5V')]:
 p=pin(ss[cap],'2')
 for x in items:
  if isinstance(x,sch.SchematicLine) and p in [xy(x.start),xy(x.end)]:deletes.add(x.id.value)
  if isinstance(x,sch.SchematicSymbolInstance) and x.reference_field.text.text.startswith('#PWR') and pin(x,'1')==(p[0],p[1]+2.54):deletes.add(x.id.value)
 label(rail,p)
# Give the load switches their local input bypass capacitance.
for ref,p,rail in [('C35',(345.44,238.76),'+5V_PROGRAM'),('C36',(472.44,238.76),'+5V'),('C37',(538.48,238.76),'+5V')]:passive(ref,p,'100nF',rail,'GND','C')
z=sym('C1');z.value_field.text.text='4.7uF';z.footprint_field.text.text='Capacitor_SMD:C_0805_2012Metric';field(z,'Rating','>=10V X7R; effective >=1uF at 5V')
# More than 200mV guaranteed bus bias even with two terminations and tolerances.
for ref in ['R18','R28']:z=sym(ref);z.value_field.text.text='470R';field(z,'Tolerance','1%');field(z,'Power_rating','0.1W')
text('U11/U9/U10: CSLEW capacitors connect to VIN, not ground.\nLocal input bypass shown above; place at each IC in layout.',(300.99,217.17),1.0)
commit('Match load-switch slew capacitors to the datasheet and strengthen RS485 idle margin')
