import numpy as np, warnings; warnings.filterwarnings("ignore")
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_fft
fig, ax = plt.subplots(2, 2, figsize=(13, 7))
for k, rid in enumerate((6, 7)):
    r = open_run(f"data/{rid}"); B = r.col("magnet_field"); I = r.col("sr0_X")/-1e6; R = r.col("sr1_X")/I
    o = np.argsort(B); B, R = B[o], R[o]
    for j, (lo, hi) in enumerate(((1.0, 3.0), (1.0, 6.0))):
        s = (B >= lo) & (B <= hi); p = np.polyfit(B[s], R[s], 4); d = R[s] - np.polyval(p, B[s])
        ax[j, k].plot(1/B[s], d, lw=0.7); ax[j, k].set_title(f"run {rid}: dR, deg-4 bg over B [{lo},{hi}] T"); ax[j, k].set_xlabel("1/B")
        f, S = sdh_fft(R[:, None], B, b_range=(lo, hi), bg_degree=4, nfft=4096, log=False)
        m = f > 2; sp = S[0]; pk = [i for i in range(1, len(sp)-1) if m[i] and sp[i] > sp[i-1] and sp[i] > sp[i+1] and sp[i] > 0.2*sp[m].max()]
        print(rid, (lo, hi), "peaks:", ", ".join(f"{f[i]:.1f}({sp[i]/sp[m].max():.2f})" for i in pk[:8]))
fig.tight_layout(); fig.savefig("hera_scratch/spot_lowB.png", dpi=100)
