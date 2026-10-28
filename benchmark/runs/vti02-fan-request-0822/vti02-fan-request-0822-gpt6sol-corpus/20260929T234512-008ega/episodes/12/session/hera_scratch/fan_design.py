import json
import numpy as np
from scipy.constants import h, e
from sharpelab_nb.gates import calc_gate_voltages
from hera.analysis import field_invB

cal=json.load(open('hera_scratch/cal_run5.json'))
n=np.linspace(3.2,2.2,31)
B=field_invB(0.7,10.0,101)
Vtg,Vbg=calc_gate_voltages(n,np.zeros_like(n),cal['c_tg'],cal['c_bg'],cal['n_offset'],cal['D_offset'])
F_L=h/(4*e)*n*1e16
du=np.diff(1/B)
print('B',len(B),B[0],B[-1], 'du',np.min(abs(du)),np.max(abs(du)),'Nyq FL max',1/(2*F_L.max()),'samples FL',1/(F_L.max()*abs(du[0])))
print('n',len(n),n[0],n[-1],'dn',np.max(abs(np.diff(n))),'ray period at Blo',4*e*B[0]/h/1e16,'samples ray',4*e*B[0]/h/1e16/abs(np.diff(n)[0]))
print('gates TG',min(Vtg),max(Vtg),'BG',min(Vbg),max(Vbg))
print('F_L',F_L.min(),F_L.max(),'deltaF',1/(1/B[0]-1/B[-1]),'ABAB light at n=2.2 ~4.2T periods',4.2*(1/B[0]-1/B[-1]))
print('points',len(B)*len(n),'bare ramp min',(10-0.7)/(1/7.3),'ramp 0 to 0.7 min',0.7/(1/7.3),'grid at 2s/pt min',len(B)*len(n)*2/60)
