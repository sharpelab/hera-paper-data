import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path.home()/'measurement_env/hera/models/tetralayer_fs_count'))
from fs_count_b0 import abab_fs,bernal_fs,ABA_TRI
for n in (2.,2.4,2.5,2.6,2.7,2.8,3.0,3.2,-1.2):
 f=[x[0] for x in abab_fs(n*1e16)[1]]
 tri=[x[0] for x in bernal_fs(n*1e16,seq='ABA',p=ABA_TRI)[1]]
 print(n,'ABAB',f,'ABA',tri,'Bhi for 5 cycles at lo1.02',1/(1/1.02-5/f[0]) if 1/1.02>5/f[0] else None)
