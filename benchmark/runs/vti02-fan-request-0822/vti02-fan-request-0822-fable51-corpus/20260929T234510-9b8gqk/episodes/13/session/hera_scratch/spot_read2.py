import numpy as np, warnings
from pathlib import Path
from scipy.signal import find_peaks
from hera.analysis import open_run, sdh_onset, sdh_fft
warnings.simplefilter("ignore")
H_4E = 6.62607015e-34/(4*1.602176634e-19)
def load(rid):
    r = open_run(Path("data")/str(rid)); B = r.col("magnet_field"); R = (r.col("sr1_X"))/(r.col("sr0_X")/(-1e6))
    o = np.argsort(B); return B[o], R[o], r.col("T_sample")[o]
for rid, n12, blo in [(6, 3.2, 1.0), (7, -1.2, 0.3)]:
    B, R, T = load(rid); FL = H_4E*abs(n12)*1e16
    print(f"\n===== run {rid} n={n12:+.1f} F_L={FL:.1f} T; T_sample vs B: ", ", ".join(f"{b:.0f}T:{t:.3f}" for b,t in [(B[np.argmin(abs(B-x))], T[np.argmin(abs(B-x))]) for x in (0.5,2,4,6,8,10)]))
    on = sdh_onset(R, B, b_lo=blo, r_full_scale=50e-6/10e-9); print(on.summary())
    for lo, hi in [(1.0, 3.0), (1.5, 5.0), (3.0, 6.0), (5.0, 10.0), (1.5, 10.0), (2.5, 10.0)]:
        m = (B >= lo) & (B <= hi)
        f, spec = sdh_fft(R[m][:, None], B[m], b_range=(lo, hi), bg_degree=5, log=False)
        sp = spec[0]; pk, pr = find_peaks(sp, prominence=0.05*sp.max())
        top = sorted(zip(sp[pk], f[pk]), reverse=True)[:7]
        dF = 1/(1/lo - 1/hi)
        print(f"  win [{lo},{hi}] dF={dF:.2f}: " + ", ".join(f"{ff:.1f}T({a/top[0][0]:.2f})" for a, ff in top))
    # bg-subtracted amplitude by field band
    m = B >= 1.0; p = np.polyfit(B[m], R[m], 5); dR = R[m] - np.polyval(p, B[m]); Bm = B[m]
    print("  dR rms by band:", ", ".join(f"{lo}-{hi}T: {np.std(dR[(Bm>=lo)&(Bm<hi)]):.1f} Ohm" for lo, hi in [(1,2),(2,3),(3,4),(4,6),(6,8),(8,10)]))
    print(f"  R by band (min/max):", ", ".join(f"{lo}-{hi}: {R[(B>=lo)&(B<hi)].min():.0f}/{R[(B>=lo)&(B<hi)].max():.0f}" for lo, hi in [(0,1),(1,3),(3,6),(6,8),(8,10.1)]))
