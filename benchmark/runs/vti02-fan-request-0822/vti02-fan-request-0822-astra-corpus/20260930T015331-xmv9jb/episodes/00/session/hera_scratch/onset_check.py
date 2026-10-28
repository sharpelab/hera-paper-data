from hera.analysis import *
import numpy as np
r=open_run('data/6'); R=r.col('sr1_X')/(r.col('sr0_X')/-1e6); B=r.col('magnet_field')
for hi in [4,6,10]:
 for deg in [3,5,7]:
  try:
   on=sdh_onset(R,B,b_lo=0.3,b_hi=hi,bg_degree=deg,r_full_scale=5000)
   print('hi/deg',hi,deg,on.summary())
  except Exception as e: print(type(e).__name__,str(e))
