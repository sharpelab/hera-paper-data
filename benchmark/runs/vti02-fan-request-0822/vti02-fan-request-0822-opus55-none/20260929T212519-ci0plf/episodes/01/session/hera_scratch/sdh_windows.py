import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, resolve_channels, sdh_fft
def load(rid):
    r = open_run(f"data/{rid}"); ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col_at(1); R = np.abs((r.col("sr1_X")/ch["sr1"].gain)/(r.col("sr0_X")/ch["sr0"].gain)); o = np.argsort(B); return B[o], R[o]
fig, ax = plt.subplots(2, 1, figsize=(9, 8))
for k, (rid, n) in enumerate(((6, 3.2), (7, -1.2))):
    B, R = load(rid); FL = abs(n)*1e16*6.62607e-34/(4*1.602177e-19)
    print(f"run {rid}: nominal n {n:+.1f}e12 -> F_L {FL:.1f} T")
    for (lo, hi) in ((1.0, 3.0), (1.3, 5.0), (1.0, 10.0), (3.0, 10.0), (5.0, 10.0)):
        for lg in (False,):
            f, S = sdh_fft(R[:, None], B, b_range=(lo, hi), nfft=8192, bg_degree=4, log=lg); S = S[0]
            sel = (f > 2) & (f < 75); pk, _ = find_peaks(S[sel], prominence=0.1*S[sel].max())
            res = 1/(1/lo - 1/hi)
            print(f"  [{lo:.1f},{hi:.1f}] T (dF {res:.1f} T): " + ", ".join(f"{f[sel][p]:.1f}({S[sel][p]/S[sel].max():.2f})" for p in pk))
            if (lo, hi) in ((1.3, 5.0), (3.0, 10.0)):
                ax[k].plot(f, S/S.max(), label=f"[{lo},{hi}] T")
    ax[k].axvline(FL, color="k", ls=":", label="F_L nominal"); ax[k].set_xlim(0, 75); ax[k].legend(); ax[k].set_title(f"run {rid}")
fig.tight_layout(); fig.savefig("hera_scratch/sdh_windows.png", dpi=80)
# run 6: QH minima -> filling factors (density scale check)
B, R = load(6); m = (B > 1.5)
pk, _ = find_peaks(-R[m], prominence=15, distance=8)
Bm = B[m][pk]; print("run6 minima B:", np.round(Bm, 2), "R:", np.round(R[m][pk], 1))
n_true = 30.0*4*1.602177e-19/6.62607e-34/1e16; print(f"n from 30.0 T tone: {n_true:.3f}e12 (nominal 3.2 -> scale {n_true/3.2:.3f})")
print("nu = n h/(eB) at minima (n from 30 T tone):", np.round(n_true*1e16*6.62607e-34/1.602177e-19/Bm, 1))
