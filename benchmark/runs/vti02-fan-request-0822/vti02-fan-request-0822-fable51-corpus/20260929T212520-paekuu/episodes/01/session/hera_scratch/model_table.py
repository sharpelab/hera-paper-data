import sys, numpy as np
sys.path.insert(0, '/home/hera/measurement_env/hera/models/tetralayer_fs_count')
import fs_count_b0 as m
from hera.analysis import luttinger_frequency
print("n[e12]  F_L   ABAB(F,m*)...   ABCA(F,m*)")
for n in [0.5,0.75,1.0,1.25,1.5,1.75,2.0,2.25,2.5,2.75,3.0,3.2,-0.5,-0.75,-1.0,-1.2]:
    try:
        ef, orbs = m.abab_fs(n*1e16); ms = m.abab_mstar(n*1e16)
        ab = ", ".join(f"{F:.2f}T/{mm:.3f}" for (F,_),(_,mm) in zip(orbs, ms))
    except Exception as e: ab = f"ERR {e}"
    try:
        F_tot, mm = m.abca_mstar(n*1e16); ac = f"{F_tot:.2f}T/{mm:.3f}"
    except Exception as e: ac = f"ERR {e}"
    FL = 4.1357e-15*abs(n)*1e16/4  # h/4e * n
    print(f"{n:+.2f}  {FL:6.2f}   ABAB [{ab}]   ABCA [{ac}]")
