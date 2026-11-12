import numpy as np
from hera.analysis import open_run,sdh_onset,resolve_channels
r=open_run('data/6'); ch={c.cid:c for c in resolve_channels(r.meta)}; R=(r.col('sr1_X')/ch['sr1'].gain)/(r.col('sr0_X')/ch['sr0'].gain); B=r.col('magnet_field')
for lo in (.05,.1,.2,.3,.8,1.):
 for degree in (3,5,7):
  try:
   on=sdh_onset(R,B,b_lo=lo,bg_degree=degree,r_full_scale=5000)
   print(lo,degree,'onset',on.onset_b,'tones',[(round(t.freq,2),round(t.onset_b,2),t.censored,t.near_residual) for t in on.tones])
  except Exception as e: print(e)
