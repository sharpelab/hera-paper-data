import sys,json
import numpy as np
from scipy.constants import h,e
from hera.analysis import open_run,sdh_onset
from sharpelab_nb.gates import calc_gate_voltages
sys.path.insert(0,'/home/hera/measurement_env/hera/models/tetralayer_fs_count')
from fs_count_b0 import abab_fs
r=open_run('data/6'); b=r.col('magnet_field'); R=r.col('sr1_X')/(r.col('sr0_X')/-1e6)
o=sdh_onset(R,b,b_hi=5.,r_full_scale=5000)
lo=o.onset_b; nlo,nhi=2.7,3.2
pmin=float(abab_fs(nlo*1e16)[1][0][0]); hi=np.ceil(10/(1/lo-5/pmin))/10
FL=h/(4*e)*1e16; maxF=FL*1.2*(nhi+0.43); span=1/lo-1/hi
NB=int(np.ceil(span*3*maxF))+1; Nn=int(np.ceil((nhi-nlo)/(lo/FL/1.2/2)))+1
ns=np.linspace(nhi,nlo,Nn); cal=json.load(open('hera_scratch/cal_run5.json')); C={k:cal[k] for k in ['c_tg','c_bg','n_offset','D_offset']}
vt,vb=calc_gate_voltages(ns,np.zeros_like(ns),**C)
# Measured 1.102 s/pt at 1 s dwell in run 5. Allow extra paired ramp steps,
# added vaporizer read, and control hook: use 3.25 s at inherited 3 s settle.
raw=hi/.137*60+NB*(Nn*3.25+7.5)
obj=dict(nlo=nlo,nhi=nhi,Blo=lo,Bhi=hi,NB=NB,Nn=Nn,du=span/(NB-1),dn=(nhi-nlo)/(Nn-1),deltaF=1/span,Fmax=maxF,partner=pmin,cycles=pmin*span,TG=[float(vt.min()),float(vt.max())],BG=[float(vb.min()),float(vb.max())],raw_minutes=raw/60,realistic_minutes=raw*1.15/60,CAL=C)
print(o.summary()); print(json.dumps(obj,indent=2)); json.dump(obj,open('hera_scratch/fan_design.json','w'),indent=2)
