import numpy as np
from hera.analysis import open_run,sdh_onset
r=open_run('data/6'); B=r.col('magnet_field'); R=r.col('sr1_X')/(r.col('sr0_X')/-1e6)
for hi in [4,6,8,10]:
 for deg in [3,5,7]:
  try:
   on=sdh_onset(R,B,b_lo=0.3,b_hi=hi,bg_degree=deg,r_full_scale=5000)
   print('hi,deg',hi,deg, on.summary())
  except ValueError as e: print(hi,deg,e)
