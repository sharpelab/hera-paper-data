import sys
from pathlib import Path
sys.path.insert(0,str(Path.home()/'measurement_env/hera/models/tetralayer_fs_count'))
from fs_count_b0 import abab_fs
from hera.analysis import open_run,resolve_channels,sdh_onset,luttinger_frequency
import numpy as np
r=open_run('data/6'); ch={c.cid:c for c in resolve_channels(r.meta)}
R=(r.col('sr1_X')/ch['sr1'].gain)/(r.col('sr0_X')/ch['sr0'].gain)
on=sdh_onset(R,r.col('magnet_field'),b_hi=4,r_full_scale=5000)
print('B onset',on.onset_b)
for n in (2.5,2.6,2.7,2.8,3.0,3.2,-1.,-1.1,-1.2,-1.25):
 fs=[f for f,k in abab_fs(n*1e16)[1]]
 print(n,fs, 'Bhi 5 partner periods',1/(1/on.onset_b-5/min(fs)) if min(fs)>5*on.onset_b else None)
