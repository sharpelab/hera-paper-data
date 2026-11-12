import numpy as np, json
from scipy.constants import h,e
from sharpelab_nb.gates import calc_gate_voltages,calc_nD
blo=1.0309096913954; bhi=7.1
# Preserve spot-check inverse-field resolution at 1 T; refine above 3.5 T for its high harmonics.
u1=np.linspace(1/blo,1/3.5,int(np.ceil((1/blo-1/3.5)/(.01/1.01)))+1)
u2=np.linspace(1/3.5,1/bhi,int(np.ceil((1/3.5-1/bhi)/(.5/143)))+1)
B=1/np.r_[u1,u2[1:]]
N=int(np.ceil(.4/(4*e/h*blo/1e16/2)))+1
ns=np.linspace(2.8,3.2,N); cal=json.load(open('hera_scratch/cal_run5.json'))
vt,vb=calc_gate_voltages(ns,np.zeros(N),*[cal[k] for k in ['c_tg','c_bg','n_offset','D_offset']])
print('B rows',len(B),'n points',N,'Npt',len(B)*N,'du',np.max(abs(np.diff(u1))),np.max(abs(np.diff(u2))),'dn',ns[1]-ns[0],'gates',vt[[0,-1]],vb[[0,-1]])
# Run 5: 1.0985 s incl 1 s dwell, 5.77 s transition incl slow delay 3 s.
# Added gate/readbacks budget: .3 s/pt; dual flyback + slow delay + magnet settle budget 7 s/row.
print('grid min',len(B)*N*3.3/60,'ramp min',bhi*7.3,'rows min',len(B)*7/60,'total+10pct',(len(B)*N*3.3/60+bhi*7.3+len(B)*7/60)*1.1)
print('full n -1.27..3.27 N',int(np.ceil(4.54/(4*e/h*blo/1e16/2)))+1)
