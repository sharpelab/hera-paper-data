import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from pathlib import Path
from hera.analysis import open_run, resolve_channels, sdh_fft, sdh_onset, luttinger_frequency
D = Path(__file__).resolve().parent.parent / "data"
out = {}
fig, ax = plt.subplots(3, 2, figsize=(13, 11))
for k, (rid, n12) in enumerate(((6, 3.2), (7, -1.2))):
    r = open_run(D / str(rid)); ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field")  # planned setpoint col (first) -- check duplicates
    idx = r.col_indices("magnet_field"); Bm = r.col_at(idx[-1])
    I = r.col("sr0_X") / ch["sr0"].gain; R = (r.col("sr1_X") / ch["sr1"].gain) / I
    P = r.col("sr1_P")
    o = np.argsort(Bm); Bs, Rs = Bm[o], R[o]
    FL = luttinger_frequency(abs(n12) * 1e16)
    print(f"run {rid}: n={n12:+.1f}e12  F_L={float(FL):.2f} T  pts {len(B)}  B {Bm.min():.3f}-{Bm.max():.3f}  "
          f"R(B<0.4)={np.median(R[Bm<0.4]):.1f}  R(B>9.6)={np.median(R[Bm>9.6]):.1f}  min R {R.min():.1f}  sr1 phase med {np.median(P):.1f} deg  T {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f}")
    ax[0, k].plot(Bs, Rs, lw=0.7); ax[0, k].set_title(f"run {rid} raw R(B), n={n12:+.1f}e12 D=0"); ax[0, k].set_xlabel("B (T)"); ax[0, k].set_ylabel("Rxx (Ohm)")
    ax[1, k].plot(1 / Bs[Bs > 1], Rs[Bs > 1], lw=0.7); ax[1, k].set_xlabel("1/B"); ax[1, k].set_ylabel("Rxx")
    for lo in (1.5, 2.5, 4.0):
        f, s = sdh_fft(Rs[:, None], Bs, b_range=(lo, 10), nfft=4096, bg_degree=5, log=False)
        s = s[0]; msk = (f > 2) & (f < 60)
        pk = np.argsort(s[msk])[::-1][:5]
        print(f"   FFT B[{lo},10]: top peaks (T): " + ", ".join(f"{f[msk][p]:.1f}({s[msk][p]:.2g})" for p in pk))
        if lo == 1.5: ax[2, k].plot(f, s, label=f"B {lo}-10")
    ax[2, k].axvline(float(FL), color="r", ls="--", label="F_L"); ax[2, k].axvline(float(FL)/2, color="r", ls=":")
    ax[2, k].set_xlim(0, 60); ax[2, k].legend(); ax[2, k].set_xlabel("F (T)")
    try:
        on = sdh_onset(Rs, Bs, r_full_scale=50e-6 / 10e-9)
        print(on.summary())
    except Exception as e:
        print("   onset:", type(e).__name__, e)
fig.tight_layout(); fig.savefig(Path(__file__).parent / "spot_runs67.png", dpi=90)
