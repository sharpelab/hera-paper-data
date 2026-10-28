import sys,json
from pathlib import Path
import numpy as np
from scipy.constants import h,e
from hera.analysis import open_run,sdh_onset
from sharpelab_nb.gates import calc_gate_voltages,calc_nD
sys.path.insert(0,str(Path.home()/'measurement_env/hera/models/tetralayer_fs_count'))
from fs_count_b0 import abab_fs
r=open_run('data/6'); B=r.col('magnet_field'); R=r.col('sr1_X')/(r.col('sr0_X')/-1e6)
for degree in [3,5,7]:
 o=sdh_onset(R,B,b_lo=.6,b_hi=5,bg_degree=degree,r_full_scale=5000)
 print('LOCAL ONSET degree',degree,o.onset_b)
print('FULL WINDOW',sdh_onset(R,B,r_full_scale=5000).summary())
cal=json.loads(Path('hera_scratch/cal_run5.json').read_text())
lo,hi=1.0,6.0
nmin,nmax=2.8,3.2
# Include 20% scale uncertainty in n-axis criterion and in F_L band.
FL=h/(4*e)*nmax*1e16
fguard=132.0 # observed run-6 high-field content ~130 T, avoid aliases into pocket band
nb=int(np.ceil(2*fguard*(1/lo-1/hi)))+1
nn=int(np.ceil((nmax-nmin)*1.2/(4*e/h*lo/1e16/2)))+1
ns=np.linspace(nmin,nmax,nn)
vt,vb=calc_gate_voltages(ns,np.zeros(nn),cal['c_tg'],cal['c_bg'],cal['n_offset'],cal['D_offset'])
print('MODEL')
for n in [nmin,3.,nmax]:
 fs=[float(f) for f,k in abab_fs(n*1e16)[1]]
 print(n,fs,'cycles',np.array(fs)*(1/lo-1/hi),'FL',h/(4*e)*n*1e16)
print('GRID',nb,nn,'N',nb*nn,'delta_n',ns[1]-ns[0],'delta_invB',(1/lo-1/hi)/(nb-1),'FLmax',FL,'deltaF',1/(1/lo-1/hi))
print('GATES',vt.min(),vt.max(),vb.min(),vb.max(),'roundtrip max D',max(abs(calc_nD(vt,vb,cal['c_tg'],cal['c_bg'],cal['n_offset'],cal['D_offset'])[1])))
r5=open_run('data/5');dt=np.diff(r5.col('time')); point=np.median(dt[dt<2])-1+3
flyback=(np.ptp(vt)+np.ptp(vb))/.005*.006
# field settle=3; extra slow delay=1; measured read overhead=.10; add paired-gate writes/read channels margin to .20.
point=max(point,3.20)
seconds=hi/.137*60+nb*(nn*point+flyback+3+1)
print('TIME point',point,'flyback',flyback,'fieldmin',hi/.137,'basehours',seconds/3600,'+10%',seconds*1.1/3600)
Path('hera_scratch/fan_design.json').write_text(json.dumps(dict(nmin=nmin,nmax=nmax,Blo=lo,Bhi=hi,N_B=nb,N_n=nn,fguard=fguard,point_s=point,estimate_hours=seconds*1.1/3600),indent=2))
