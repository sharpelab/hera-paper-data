import sys, json, numpy as np
sys.path.insert(0,'/home/hera/measurement_env/hera/models/tetralayer_fs_count')
from fs_count_b0 import abab_fs
from hera.analysis import open_run, sdh_onset
from sharpelab_nb.gates import calc_gate_voltages
r=open_run('data/6'); B=r.col('magnet_field'); R=r.col('sr1_X')/(r.col('sr0_X')/-1e6)
on=sdh_onset(R,B,b_hi=5,f_min=4,r_full_scale=5000)
blo=on.onset_b
nlo,nhi=2.8,3.2
partner=abab_fs(nlo*1e16)[1][0][0]
bhi=np.ceil(1/(1/blo-5/partner)*10)/10
span=1/blo-1/bhi
# Observed 130 T upper tone, 10% margin: no alias into science band.
fmax=143.
nb=int(np.ceil(2*fmax*span))+1
# n-grid minimum for g=4 rays, including 20% lever-arm scale margin.
dnmax=blo/(10.33916924*2*1.2)
nn=int(np.ceil((nhi-nlo)/dnmax))+1
ns=np.linspace(nhi,nlo,nn)
cal=dict(c_tg=2.796e-3,c_bg=2.161e-3,n_offset=-.0894,D_offset=-.013)
vt,vb=calc_gate_voltages(ns,np.zeros(nn),**cal)
print(on.summary())
print('design',blo,bhi,nb,nn,'dInvB',span/(nb-1),'dn',(nhi-nlo)/(nn-1),'dF',1/span,'light periods',partner*span)
print('gates',vt.min(),vt.max(),vb.min(),vb.max())
print('ramp min',bhi*7.3,'grid min',nb*nn*3.12/60,'rows min',nb*5.5/60,'total with10%',(bhi*7.3+nb*nn*3.12/60+nb*5.5/60)*1.1)
out=dict(B_lo=blo,B_hi=bhi,N_B=nb,N_n=nn,n_lo=nlo,n_hi=nhi,frequency_ceiling=fmax,delta_f=1/span,partner_frequency=partner,cal=cal)
with open('hera_scratch/fan_design.json','w') as f:json.dump(out,f,indent=2)
