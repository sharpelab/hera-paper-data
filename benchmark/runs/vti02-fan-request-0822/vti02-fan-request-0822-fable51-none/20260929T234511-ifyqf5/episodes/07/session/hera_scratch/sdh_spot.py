"""SdH read of spot checks 6 (e, n=+3.2e12) and 7 (h, n=-1.2e12): sdh_onset tones + sdh_fft spectrum, vs Luttinger F_L."""
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, sdh_fft, sdh_onset, luttinger_frequency
fig, ax = plt.subplots(2, 2, figsize=(13, 8))
for k, (rid, n12) in enumerate(((6, 3.2), (7, -1.2))):
    r = open_run(f"data/{rid}"); ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); I = r.col("sr0_X") / ch["sr0"].gain; R = np.abs((r.col("sr1_X") / ch["sr1"].gain) / I)
    o = np.argsort(B); B, R = B[o], R[o]
    FL = luttinger_frequency(abs(n12) * 1e16)
    print(f"\n=== run {rid}: n = {n12:+.1f}e12 -> F_L(full density, 4-fold) = {FL:.1f} T; F_L/2 = {FL/2:.1f}, F_L/4 = {FL/4:.1f}")
    try:
        on = sdh_onset(R, B, b_lo=0.5, r_full_scale=50e-6 / 10e-9)
        print(on.summary())
    except Exception as e:
        print("sdh_onset:", type(e).__name__, e)
    for lo, hi in ((1.0, 10.0), (2.0, 10.0), (4.0, 10.0)):
        m = (B >= lo) & (B <= hi)
        f, sp = sdh_fft(R[m][:, None], B[m], nfft=2048, bg_degree=5, log=False)
        sp = sp[0]; sel = f > 2
        pk = np.argsort(sp[sel])[::-1][:6]
        print(f"  FFT window {lo}-{hi} T: top peaks (T: amp) " + ", ".join(f"{f[sel][p]:.1f}:{sp[sel][p]:.2g}" for p in sorted(pk, key=lambda p: f[sel][p])))
        if lo == 1.0:
            ax[k, 1].plot(f, sp, label=f"{lo}-{hi} T")
        else:
            ax[k, 1].plot(f, sp, alpha=0.6, label=f"{lo}-{hi} T")
    ax[k, 1].axvline(FL, color="k", ls="--", lw=0.8, label=f"F_L {FL:.1f} T"); ax[k, 1].axvline(FL / 2, color="gray", ls=":", lw=0.8)
    ax[k, 1].set_xlim(0, 80); ax[k, 1].set_xlabel("SdH frequency (T)"); ax[k, 1].legend(fontsize=7); ax[k, 1].set_title(f"run {rid} FFT (linear R, poly5 bg)")
    # detrended trace vs 1/B
    m = B >= 1.0
    bg = np.polyval(np.polyfit(B[m], R[m], 5), B[m])
    ax[k, 0].plot(1 / B[m], R[m] - bg, lw=0.7); ax[k, 0].set_xlabel("1/B (1/T)"); ax[k, 0].set_ylabel("dR (Ohm)"); ax[k, 0].set_title(f"run {rid} detrended, B>1 T")
fig.tight_layout(); fig.savefig("hera_scratch/sdh_spot_6_7.png", dpi=100); print("saved")
