"""Run 6 (e, n=+3.2e12): onset + FFT on the uniformly-sampled 10 mT part only (B >= 1 T), window below the 8 T step."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, sdh_onset, sdh_fft

D = "/home/hera/measurements/zack/20260822-vti-02/data"
out = {}
for rid, lo_rec in ((6, 1.0), (7, 0.3)):
    r = open_run(f"{D}/{rid}")
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); I = r.col("sr0_X") / ch["sr0"].gain
    R = (r.col("sr1_X") / ch["sr1"].gain) / np.abs(I)
    o = np.argsort(B); B, R = B[o], R[o]
    m = B >= lo_rec - 1e-3; B, R = B[m], R[m]
    fs_v = 50e-6 / np.median(np.abs(I))
    for bhi in (7.8, 10.0):
        print(f"\n=== run {rid}: onset over [{lo_rec}, {bhi}] T")
        try:
            on = sdh_onset(R, B, b_lo=lo_rec, b_hi=bhi, r_full_scale=fs_v)
            print(on.summary())
        except Exception as e:
            print(type(e).__name__, e)
    fig, ax = plt.subplots(1, 1, figsize=(8, 4))
    for bl in ((1.0, 1.3, 1.6, 2.0) if rid == 6 else (0.7, 1.0, 1.3)):
        for bh in (7.8,):
            for deg in (3, 5, 7):
                f, sp = sdh_fft(R[:, None], B, b_range=(bl, bh), bg_degree=deg, log=False, nfft=2048)
                s = sp[0]
                pk = [i for i in range(1, len(s) - 1) if s[i] > s[i - 1] and s[i] > s[i + 1] and f[i] > 1.5]
                pk = sorted(pk, key=lambda i: -s[i])[:7]
                print(f"  FFT [{bl:.1f},{bh}] deg {deg}: dF={1/(1/bl-1/bh):.2f} T; " +
                      ", ".join(f"{f[i]:.1f}:{s[i]/s[pk[0]]:.2f}" for i in sorted(pk)))
                if deg == 5: ax.plot(f, s / s.max(), lw=0.8, label=f"[{bl},{bh}]")
    ax.set_xlim(0, 60 if rid == 6 else 30); ax.legend(); ax.set_xlabel("F (T)"); ax.set_title(f"run {rid} FFT, bg deg 5")
    fig.savefig(f"/home/hera/measurements/zack/20260822-vti-02/hera_scratch/spot{rid}_fft.png", dpi=90)
