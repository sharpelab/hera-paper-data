import numpy as np, sys, warnings; warnings.filterwarnings("ignore")
sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
from hera.analysis import open_run, sdh_onset, luttinger_frequency
import fs_count_b0 as m
r = open_run("data/6"); B = r.col("magnet_field"); R = r.col("sr1_X") / (r.col("sr0_X") / -1e6)
for blo in (1.0, 1.2):
    on = sdh_onset(R, B, b_lo=blo, r_full_scale=50e-6 / 9.9e-9)
    print(f"--- run 6 onset, b_lo={blo}"); print(on.summary())
r7 = open_run("data/7"); B7 = r7.col("magnet_field"); R7 = r7.col("sr1_X") / (r7.col("sr0_X") / -1e6)
print("--- run 7 onset b_lo=0.5"); print(sdh_onset(R7, B7, b_lo=0.5, r_full_scale=50e-6/9.9e-9).summary())
print("\n n12   F_L   ABAB orbits (F, m*)              ABCA (F, m*)")
for n in [1.2, 1.5, 1.8, 2.0, 2.4, 2.8, 3.2, 3.4]:
    FL = float(luttinger_frequency(n * 1e16))
    ab = m.abab_mstar(n)
    ca = m.abca_mstar(n)
    print(f"{n:4.1f} {FL:6.2f}  " + "  ".join(f"({F:5.2f},{ms:.3f})" for F, ms in ab) + f"   ({ca[0]:.2f},{ca[1]:.3f})")
