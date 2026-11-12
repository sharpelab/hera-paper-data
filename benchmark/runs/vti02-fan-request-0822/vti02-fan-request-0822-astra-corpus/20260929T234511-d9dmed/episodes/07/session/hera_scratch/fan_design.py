import json, sys
from pathlib import Path
import numpy as np
from scipy.constants import h,e
from hera.analysis import field_invB
from sharpelab_nb.gates import calc_gate_voltages,calc_nD
sys.path.insert(0,str(Path.home()/'measurement_env/hera/models/tetralayer_fs_count'))
from fs_count_b0 import abab_fs
CAL=dict(c_tg=2.796e-3,c_bg=2.161e-3,n_offset=-.0894,D_offset=-.013)
B_lo,B_hi=.90,5.20
n_lo,n_hi=2.8,3.2
# Includes 20% density prior and second CNP's approximate +0.43 density shift,
# and second harmonics: design F_ceiling ~90 T, not only nominal F_L=33.1 T.
f_ceiling=2*(h/(4*e))*(n_hi+.43)*1e16*1.2
NB=int(np.ceil((1/B_lo-1/B_hi)*2*f_ceiling))+1
Nn=int(np.ceil((n_hi-n_lo)/(4*e/h*B_lo/1e16/2/1.2)))+1
ns=np.linspace(n_hi,n_lo,Nn); Bs=field_invB(B_lo,B_hi,NB)
vt,vb=calc_gate_voltages(ns,np.zeros(Nn),**CAL)
assert np.all((vt>=-.3)&(vt<=1)) and np.all((vb>=-1.3)&(vb<=2))
nr,dr=calc_nD(vt,vb,**CAL); assert np.allclose(ns,nr) and np.allclose(dr,0)
models={str(n):[float(f) for f,k in abab_fs(n*1e16)[1]] for n in [n_lo,3.,n_hi]}
periods=models[str(n_lo)][0]*(1/B_lo-1/B_hi)
eta=1.1*(NB*Nn*3.25+NB*5.5+B_hi/.137*60+60)/60
out=dict(N_B=NB,N_n=Nn,points=NB*Nn,B_lo=B_lo,B_hi=B_hi,n_lo=n_lo,n_hi=n_hi,delta_invB=float(abs(np.diff(1/Bs)[0])),delta_n=float(abs(np.diff(ns)[0])),nyquist_T=float(1/(2*abs(np.diff(1/Bs)[0]))),model_ABAB=models,partner_periods=periods,delta_F=1/(1/B_lo-1/B_hi),eta_min=eta,TG=[float(vt.min()),float(vt.max())],BG=[float(vb.min()),float(vb.max())],CAL=CAL)
print(json.dumps(out,indent=2)); Path('hera_scratch/fan_design.json').write_text(json.dumps(out,indent=2))
