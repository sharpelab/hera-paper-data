import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, sdh_fft, sdh_onset, luttinger_frequency, GateCalibration
cal = GateCalibration(2.796e-3, 2.161e-3, n_offset=-0.0894e16, D_offset=-0.013e9)
fig, ax = plt.subplots(3, 2, figsize=(13, 11))
for j, (rid, n12) in enumerate([(6, 3.2), (7, -1.2)]):
    r = open_run(f"data/{rid}"); ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); I = r.col("sr0_X")/ch["sr0"].gain; V = r.col("sr1_X")/ch["sr1"].gain
    R = V/I; Rabs = np.abs(R); o = np.argsort(B); B, R, Rabs = B[o], R[o], Rabs[o]
    P = r.col("sr1_P")[o]; T = r.col("T_sample")
    FL = luttinger_frequency(abs(n12)*1e16)
    print(f"run {rid}: n={n12:+.2f}e12 F_L={FL:.1f} T; B {B.min():.2f}-{B.max():.2f}; R signed {R.min():.1f}..{R.max():.1f} Ohm; "
          f"frac<0 {np.mean(R<0):.2f}; sr1 phase med {np.median(P):.1f} range {P.min():.0f}..{P.max():.0f}; T {T.min():.3f}-{T.max():.3f}")
    ax[0, j].plot(B, R, "-", lw=.8); ax[0, j].set_title(f"run {rid} raw signed Rxx n={n12:+}e12 D=0"); ax[0, j].set_xlabel("B (T)")
    ax2 = ax[0, j].twinx(); ax2.plot(B, P, "r-", lw=.4, alpha=.5)
    for blo in (1.5, 2.5, 4.0):
        m = B >= blo
        f, sp = sdh_fft(R[m][:, None], B[m], log=False, bg_degree=5, nfft=4096)
        sp = sp[0]; k = (f > 2) & (f < 60)
        pk = f[k][np.argsort(sp[k])[::-1][:6]]
        print(f"   FFT B>={blo}: top freqs {np.round(np.sort(pk),1)}")
        ax[1, j].plot(f, sp/sp[k].max(), label=f"B>={blo}")
    ax[1, j].set_xlim(0, 60); ax[1, j].axvline(FL, color="k", ls=":", label="F_L"); ax[1, j].legend(); ax[1, j].set_xlabel("F (T)")
    try:
        on = sdh_onset(R, B, r_full_scale=50e-6/10e-9)
        print(on.summary())
    except Exception as e: print("onset:", type(e).__name__, e)
    # detrended vs 1/B
    m = B > 1.0; cf = np.polyfit(B[m], R[m], 5); d = R[m]-np.polyval(cf, B[m])
    ax[2, j].plot(1/B[m], d, lw=.7); ax[2, j].set_xlabel("1/B"); ax[2, j].set_title("detrended (deg 5 in B)")
fig.tight_layout(); fig.savefig("hera_scratch/spot_runs67.png", dpi=90)
