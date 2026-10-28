"""Spot checks 6/7 re-read on the Nyquist-valid records + model F(n)/m*(n) table for the fan window."""
import sys, json, warnings
import numpy as np
warnings.filterwarnings("ignore")
sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
from hera.analysis import open_run, sdh_onset, sdh_fft, luttinger_frequency, SdhOnsetError
from fs_count_b0 import abab_fs, abab_mstar, abca_fs, abca_mstar

def load(rid):
    r = open_run(f"data/{rid}")
    B = r.col("magnet_field"); I = r.col("sr0_X") / r.meta["measurement_config"]["sr0_gain"]
    R = r.col("sr1_X") / I; o = np.argsort(B)
    return B[o], R[o], np.median(np.abs(I))

for rid, n12 in ((6, 3.2), (7, -1.2)):
    B, R, Ib = load(rid)
    FL = float(luttinger_frequency(abs(n12) * 1e16))
    # Nyquist-valid low edge: local dB/B^2 <= 1/(2 F_L)
    dB = np.gradient(B); ok = dB / B**2 <= 1 / (2 * FL)
    b_nyq = B[ok & (B > 0.2)].min()
    print(f"=== run {rid} n={n12:+.1f}e12 F_L={FL:.1f} T: record Nyquist-valid on F_L above B = {b_nyq:.2f} T; negative-R pts {np.sum(R<0)} (min {R.min():.1f} Ohm at B={B[np.argmin(R)]:.2f})")
    for blo in (b_nyq, 1.0, 1.5):
        try:
            on = sdh_onset(np.abs(R), B, b_lo=max(blo, b_nyq), r_full_scale=50e-6 / Ib)
            print(f"-- sdh_onset b_lo={max(blo,b_nyq):.2f}:"); print(on.summary())
        except SdhOnsetError as e:
            print("SdhOnsetError", e)

print("\n=== model table (u_D = 0): n, F_L, ABAB orbits (F, m*), ABCA (F, m*)")
tab = {}
for n12 in (-1.25, -1.0, -0.75, -0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.4):
    n = n12 * 1e16
    ab = abab_mstar(n); ca = abca_mstar(n)
    FL = float(luttinger_frequency(abs(n)))
    print(f"n={n12:+.2f}: F_L={FL:5.1f}  ABAB " + ", ".join(f"{F:5.1f}T/{m:.3f}" for F, m in ab) + f"   ABCA {ca[0]:5.1f}T/{ca[1]:.3f}")
    tab[n12] = dict(FL=FL, abab=ab, abca=[float(ca[0]), float(ca[1])])
json.dump(tab, open("hera_scratch/model_table_fan.json", "w"), indent=1, default=float)
