import numpy as np
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
TG_MIN,TG_MAX=-0.3,1.0
BG_MIN,BG_MAX=-1.3,2.0
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_vec=np.round(np.arange(-1.26,3.2601,0.04),4)
Vtg,Vbg=calc_gate_voltages(n_vec,np.zeros_like(n_vec),CAL["c_tg"],CAL["c_bg"],CAL["n_offset"],CAL["D_offset"])
M=0.005
keep=(Vtg>=TG_MIN+M)&(Vtg<=TG_MAX-M)&(Vbg>=BG_MIN+M)&(Vbg<=BG_MAX-M)
n2=n_vec[keep]
print("n",n2[0],n2[-1],len(n2), np.diff(n2).min(), np.diff(n2).max())
print("Vtg",Vtg[keep].min(),Vtg[keep].max(),"Vbg",Vbg[keep].min(),Vbg[keep].max())
B=np.unique(np.round(np.hstack(([0.0,0.5],np.arange(1.0,10.0001,0.15))),4))
print("B",len(B),B[:5],B[-3:])
print(repr(list(B)))
