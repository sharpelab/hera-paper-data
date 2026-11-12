import sys, warnings, numpy as np
from hera.analysis import open_run, resolve_channels, sdh_onset, sdh_fft
sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count"); import fs_count_b0 as m
def trace(rid):
    r = open_run(f"data/{rid}"); ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); R = np.abs((r.col("sr1_X")/ch["sr1"].gain)/(r.col("sr0_X")/ch["sr0"].gain)); o=np.argsort(B); return B[o], R[o]
B6, R6 = trace(6)
for blo, bhi in [(1.0, 10.0), (1.0, 7.4), (0.85, 10.0)]:
    s = (B6 >= blo) & (B6 <= bhi)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        on = sdh_onset(R6[s], B6[s], b_lo=blo, r_full_scale=5000)
    print(f"--- run 6 onset on [{blo},{bhi}]"); print(on.summary()); [print("   W:", x.message) for x in w]
B7, R7 = trace(7)
s = B7 >= 0.3
on7 = sdh_onset(R7[s], B7[s], r_full_scale=5000); 
# fine FFT peaks run 6 window [1.3, 7.4] (below QH hump) and [1.3,10]
for br in [(1.3, 7.4), (1.3, 10.0), (1.0, 4.0), (4.0, 10.0)]:
    fr, sp = sdh_fft(R6[:, None], B6, b_range=br, bg_degree=5, nfft=4096); s0 = sp[0]
    from scipy.signal import find_peaks
    pk, pr = find_peaks(s0, prominence=0.05*s0.max()); pk = pk[fr[pk] > 1.5]
    top = sorted(pk, key=lambda i: -s0[i])[:6]
    print(f"run6 FFT {br}: " + ", ".join(f"{fr[i]:.1f}T({s0[i]/s0.max():.2f})" for i in sorted(top)))
print("\nmodel F(n) (u_D=0), electron side, scale 1.0; F_L:")
for n in [1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0, 3.2, 3.4, 3.6]:
    ab = m.abab_fs(n*1e16)[1]; mm = m.abab_mstar(n*1e16); FL = 41.36*n/4
    print(f" n={n:4.2f}: F_L {FL:5.1f} | ABAB " + " / ".join(f"{f:5.2f}T(m*{x:.3f})" for (f,_),(_,x) in zip(ab, mm)) + f" | heavy/F_L {ab[-1][0]/FL:.3f} light/F_L {ab[0][0]/FL:.3f} ratio {ab[-1][0]/ab[0][0]:.2f}")
