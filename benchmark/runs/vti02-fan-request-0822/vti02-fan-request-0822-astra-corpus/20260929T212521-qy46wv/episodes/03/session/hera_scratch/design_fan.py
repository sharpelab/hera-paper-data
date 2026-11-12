import json, sys
import numpy as np
from hera.analysis import field_invB, luttinger_frequency, open_run, sdh_onset, resolve_channels,current_channel
from sharpelab_nb.gates import calc_gate_voltages
sys.path.insert(0,'/home/hera/measurement_env/hera/models/tetralayer_fs_count')
from fs_count_b0 import abab_fs
r=open_run('data/6'); cs=resolve_channels(r.meta); cur=current_channel(cs); v=next(c for c in cs if c.cid=='sr1')
R=(r.col(v.col)/v.gain)/(r.col(cur.col)/cur.gain)
blo=float(sdh_onset(R,r.col('magnet_field'),b_hi=4,r_full_scale=5000).onset_b)
nlo,nhi=2.8,3.2
flo=float(abab_fs(nlo*1e16)[1][0][0]); bhi=np.ceil((1/(1/blo-5/flo))*100)/100
nb=int(np.ceil((1/blo-1/bhi)/.0035))+1
nn=int(np.ceil(2*(nhi-nlo)/(blo/float(luttinger_frequency(1e16)))))+1
bs=field_invB(blo,bhi,nb); ns=np.linspace(nlo,nhi,nn)
vt,vb=calc_gate_voltages(ns,0,.002796,.002161,-.0894,-.013)
x=dict(B_lo=blo,B_hi=float(bhi),N_B=nb,N_n=nn,du=float(np.max(abs(np.diff(1/bs)))),dn=float(ns[1]-ns[0]),deltaF=float(1/(1/blo-1/bhi)),F_L=float(luttinger_frequency(nhi*1e16)),gate_tg=[float(min(vt)),float(max(vt))],gate_bg=[float(min(vb)),float(max(vb))],model=[dict(n=n,F=[float(z[0]) for z in abab_fs(n*1e16)[1]]) for n in (2.8,3,3.2)])
x['partner_periods']=flo/x['deltaF'];x['ray_samples']=blo/float(luttinger_frequency(1e16))/x['dn'];x['ramp_min']=bhi*7.3
x['points_min']=nb*nn*3.15/60;x['row_min']=nb*4.5/60;x['priced_min']=1.15*(x['points_min']+x['row_min']+x['ramp_min']+2)
print(json.dumps(x,indent=2));open('hera_scratch/fan_design.json','w').write(json.dumps(x,indent=2))
