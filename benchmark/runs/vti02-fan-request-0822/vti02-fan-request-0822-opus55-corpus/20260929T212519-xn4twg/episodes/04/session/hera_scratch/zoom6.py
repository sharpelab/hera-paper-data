import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_fft
fig, ax = plt.subplots(3, 1, figsize=(11, 10))
for rid, c in ((6, "C0"), (7, "C1")):
    r = open_run(f"data/{rid}"); B = r.col("magnet_field"); R = r.col("sr1_X")/(r.col("sr0_X")/-1e6); o=np.argsort(B); B, R = B[o], R[o]
    for bl, bh, a in ((0.8, 4.0, ax[0] if rid==6 else ax[1]),):
        m = (B>=bl)&(B<=bh); cf=np.polyfit(B[m], R[m], 5); d = R[m]-np.polyval(cf,B[m])
        a.plot(1/B[m], d, c, lw=0.6); a.set_title(f"run {rid} bg-sub deg5 over [{bl},{bh}] T vs 1/B"); a.set_xlabel("1/B")
        f,S = sdh_fft(R[:,None], B, b_range=(bl,bh), bg_degree=5, nfft=8192, log=False)
        ax[2].plot(f, S[0]/S[0][f>2].max(), c, label=f"run {rid} [{bl},{bh}] linear R")
        # noise estimate: point-to-point diff
        print(rid, f"noise (pt-pt diff std/sqrt2) {np.std(np.diff(d))/np.sqrt(2):.2f} Ohm; bgsub rms {d.std():.2f}")
ax[2].set_xlim(0, 60); ax[2].legend(); fig.tight_layout(); fig.savefig("hera_scratch/zoom6.png", dpi=100)
