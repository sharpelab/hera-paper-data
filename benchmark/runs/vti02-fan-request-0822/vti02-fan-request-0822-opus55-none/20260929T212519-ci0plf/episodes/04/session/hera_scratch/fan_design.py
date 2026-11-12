import numpy as np
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import luttinger_frequency
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
TG=(-0.3,1.0); BG=(-1.3,2.0)
ns=np.linspace(-2,4,6001); vt,vb=calc_gate_voltages(ns,0*ns,**CAL)
ok=(vt>=TG[0])&(vt<=TG[1])&(vb>=BG[0])&(vb<=BG[1]); print("D=0 window", ns[ok].min(), ns[ok].max())
n_vec=np.round(np.arange(-1.25,3.2501,0.05),4); vt,vb=calc_gate_voltages(n_vec,0*n_vec,**CAL)
print(len(n_vec), "fast pts; Vtg", vt.min(), vt.max(), "Vbg", vb.min(), vb.max(), "dVtg/pt", np.diff(vt).mean(), "dVbg/pt", np.diff(vb).mean())
# B grid
segA=1/np.arange(2.0,0.8-1e-9,-0.04)        # 0.5 -> 1.25 T
segB=1/np.arange(0.8,0.35355-1e-9,-0.0125)   # 1.25 -> 2.83
segC=np.arange(2.9,10.0+1e-9,0.1)
B=np.unique(np.round(np.hstack((segA,segB,segC)),4))
print(len(B),"rows", B[:4], B[-3:], "max d(1/B)", np.max(-np.diff(1/B)), "at B", B[np.argmax(-np.diff(1/B))])
for Bb in (0.5,1,1.25,2,2.83,3,5,10):
    i=np.argmin(abs(B-Bb)); print(f"  B~{Bb}: dB={B[min(i+1,len(B)-1)]-B[i]:.4f}, d(1/B)={1/B[i]-1/B[min(i+1,len(B)-1)]:.4f}")
nfast=len(n_vec); per_pt=1.10; row=nfast*per_pt+3.0+3.6+3.1
ramp=(B[-1]-B[0])/0.137*60
tot=len(B)*row+ramp+ B[0]/0.137*60 + 20
print(f"row {row:.0f}s; ramp {ramp/60:.0f} min; total {tot/3600:.2f} h; +8% {tot*1.08/3600:.2f} h")
print("F_L(n) at 3.25/-1.25:", luttinger_frequency(3.25e16), luttinger_frequency(1.25e16))
print("LL period in n per T (4-fold):", 4*1.602e-19/6.626e-34/1e16, "e12/T")
