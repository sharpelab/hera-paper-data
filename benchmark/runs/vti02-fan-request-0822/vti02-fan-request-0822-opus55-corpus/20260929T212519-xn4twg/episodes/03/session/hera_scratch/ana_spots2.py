import numpy as np, sys, warnings
sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
from hera.analysis import open_run, sdh_onset, sdh_fft
import fs_count_b0 as m
def load(rid):
    r = open_run(f"data/{rid}"); B = r.col("magnet_field"); R = r.col("sr1_X") / (r.col("sr0_X") / -1e6)
    o = np.argsort(B); return B[o], R[o]
B6, R6 = load(6)
on = sdh_onset(R6, B6, b_lo=1.0, r_full_scale=5000); print("run6 b_lo=1.0:\n", on.summary())
B7, R7 = load(7)
on7 = sdh_onset(R7, B7, b_lo=0.5, r_full_scale=5000); print("run7 b_lo=0.5:\n", on7.summary())
# noise estimate: high-pass residual in 1-2 T (run6) at 10 mT
msk = (B6 > 1) & (B6 < 2); d = np.diff(R6[msk]); print(f"run6 point-to-point noise 1-2 T: {np.std(d)/np.sqrt(2):.2f} Ohm rms; R median {np.median(R6[msk]):.1f}")
msk = (B7 > 1) & (B7 < 2); d = np.diff(R7[msk]); print(f"run7 point-to-point noise 1-2 T: {np.std(d)/np.sqrt(2):.2f} Ohm rms")
# model tables
for n in [1.5, 1.8, 2.0, 2.2, 2.5, 2.8, 3.0, 3.2, -0.6, -0.9, -1.2]:
    ab = m.abab_mstar(n); FL = abs(n) * 1e16 * 4.1357e-15 / 4
    try: ca = m.abca_mstar(n)
    except Exception as e: ca = (np.nan, np.nan)
    print(f"n={n:+.1f}: F_L {FL:5.1f}; ABAB " + ", ".join(f"{f:.1f}T/{ms:.3f}" for f, ms in ab) + f"; ABCA {ca[0]:.1f}T/{ca[1]:.3f}")
