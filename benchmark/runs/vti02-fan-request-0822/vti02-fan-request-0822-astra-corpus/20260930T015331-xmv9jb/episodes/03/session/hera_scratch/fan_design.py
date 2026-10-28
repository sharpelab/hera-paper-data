import sys,json
import numpy as np
from scipy.constants import h,e
from sharpelab_nb.gates import calc_gate_voltages
from hera.analysis import open_run,sdh_onset
sys.path.insert(0,'/home/hera/measurement_env/hera/models/tetralayer_fs_count')
from fs_count_b0 import abab_fs
r=open_run('data/7'); B=r.col('magnet_field'); R=r.col('sr1_X')/(r.col('sr0_X')/-1e6)
on=sdh_onset(R,B,r_full_scale=5000)
lo=on.onset_b; hi=6.0
span=1/lo-1/hi
ns=np.linspace(-1.2,-.95,9)
fl=h/(4*e)*abs(ns)*1e16
# Include observed 26.2-T harmonic, not only 12.4-T Luttinger fundamental.
fmax=26.3; nb=int(np.ceil(span*2*fmax))+1
cal=json.load(open('hera_scratch/cal_run5.json'))
vt,vb=calc_gate_voltages(ns,np.zeros(len(ns)),*[cal[k] for k in ('c_tg','c_bg','n_offset','D_offset')])
for n in ns:
 fs=[float(f) for f,k in abab_fs(n*1e16)[1]]
 print('model',n,fs,'periods',np.array(fs)*span,'split',fs[1]-fs[0])
print('DESIGN',dict(Blo=lo,Bhi=hi,NB=nb,Nn=len(ns),du=span/(nb-1),deltaF=1/span,nstep=abs(ns[1]-ns[0]),n_nyquist=4*e/h*lo/1e16/2,Vtg=[vt.min(),vt.max()],Vbg=[vb.min(),vb.max()],grid_min=nb*len(ns)*3.2/60,ramp_min=hi/.137,turn_min=nb*4/60,estimate_min=1.1*(nb*len(ns)*3.2/60+hi/.137+nb*4/60+2)))
