import json, sys
from pathlib import Path
import numpy as np
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB
sys.path.insert(0,str(Path.home()/'measurement_env/hera/models/tetralayer_fs_count'))
from fs_count_b0 import abab_fs
blo=1.017617880804576
nlo,nhi=2.8,3.2
fsmall=abab_fs(nlo*1e16)[1][0][0]
bhi=1/(1/blo-5/fsmall)
# Sample measured candidate high-order content too, to prevent folding it into the pocket band.
fny=130.0*1.05
nb=int(np.ceil((1/blo-1/bhi)*2*fny))+1
nn=int(np.ceil((nhi-nlo)*2*10.33916924*1.2/blo))+1
B=field_invB(blo,bhi,nb);ns=np.linspace(nlo,nhi,nn)
CAL=dict(c_tg=.002796,c_bg=.002161,n_offset=-.0894,D_offset=-.013)
vt,vb=calc_gate_voltages(ns,np.zeros(nn),**CAL)
ncheck,dcheck=calc_nD(vt,vb,**CAL)
assert np.allclose(ncheck,ns) and np.max(np.abs(dcheck))<1e-12
assert vt.min()>=-.3 and vt.max()<=1 and vb.min()>=-1.3 and vb.max()<=2
assert np.max(np.abs(np.diff(1/B)))<=1/(2*fny)
for n in (nlo,nhi): print('ABAB model n, F',n,[float(x[0]) for x in abab_fs(n*1e16)[1]])
design=dict(B_lo=blo,B_hi=bhi,N_B=nb,N_n=nn,n_lo=nlo,n_hi=nhi,delta_invB=float(np.max(np.abs(np.diff(1/B)))),delta_n=float(np.max(np.diff(ns))),delta_F=float(1/(1/blo-1/bhi)),CAL=CAL,gate_ranges=[vt[[0,-1]].tolist(),vb[[0,-1]].tolist()],ramp_min=bhi*7.3,estimate_min=1.1*(bhi*438+nb*(nn*3.2+6.1))/60)
print(json.dumps(design,indent=2));Path('hera_scratch/fan_design.json').write_text(json.dumps(design,indent=2))
