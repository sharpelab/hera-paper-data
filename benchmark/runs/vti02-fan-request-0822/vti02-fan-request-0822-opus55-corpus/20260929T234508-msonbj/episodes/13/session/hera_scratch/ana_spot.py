# SdH spot checks runs 6 (e, n=+3.2e12) and 7 (h, n=-1.2e12): raw MR, onset, FFT vs F_L + model tones.
import sys, warnings
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from hera.analysis import open_run, resolve_channels, sdh_onset, sdh_fft, luttinger_frequency, SdhOnsetError

D = Path(__file__).resolve().parent.parent / "data"
out = {}
fig, ax = plt.subplots(3, 2, figsize=(12, 11))
for j, (rid, n) in enumerate([(6, 3.2), (7, -1.2)]):
    r = open_run(D / str(rid))
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); o = np.argsort(B); B = B[o]
    I = (r.col("sr0_X") / ch["sr0"].gain)[o]
    R = ((r.col("sr1_X") / ch["sr1"].gain) / I)
    R = R if R.shape == B.shape else R
    R = np.abs(((r.col("sr1_X") / ch["sr1"].gain))[o] / I)
    T = r.col("T_sample")
    itg, ibg = r.col("k_2400_tg_curr"), r.col("k_2400_bg_curr")
    FL = luttinger_frequency(abs(n) * 1e16) if True else None
    print(f"\n=== run {rid} n={n:+.2f}e12: B {B.min():.2f}-{B.max():.2f}, R {R.min():.1f}-{R.max():.1f} Ohm, "
          f"I {I.min()*1e9:.3f}-{I.max()*1e9:.3f} nA, T {T.min():.3f}-{T.max():.3f} K, "
          f"Itg {itg.min()*1e12:+.0f}..{itg.max()*1e12:+.0f} pA, Ibg {ibg.min()*1e12:+.0f}..{ibg.max()*1e12:+.0f} pA; F_L = {FL:.2f} T")
    sens = 50e-6; Ibias = np.median(I)
    print(f"  R(B~0) {R[:3].mean():.1f}, R(10T) {R[-3:].mean():.1f}; full scale {sens/Ibias:.0f} Ohm -> max fs {R.max()/(sens/Ibias):.2f}")
    ax[0, j].plot(B, R, lw=0.7); ax[0, j].set_title(f"run {rid} raw Rxx, n={n:+.1f}e12, D=0"); ax[0, j].set_xlabel("B (T)"); ax[0, j].set_ylabel("Ohm")
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            on = sdh_onset(R, B, r_full_scale=sens / Ibias)
        for ww in w: print("  warn:", ww.message)
        print(on.summary())
        out[rid] = on
    except SdhOnsetError as e:
        print("  SdhOnsetError:", e); on = None
    # background-subtracted in B
    m = B > 0.5
    cf = np.polyfit(B[m], R[m], 5); dR = R[m] - np.polyval(cf, B[m])
    ax[1, j].plot(1 / B[m], dR, lw=0.6); ax[1, j].set_xlabel("1/B (1/T)"); ax[1, j].set_ylabel("dR (deg5 bg in B)")
    for lo in ([1.0, 1.5, 2.0, 3.0] if rid == 6 else [1.0, 1.5, 2.0, 3.0]):
        f, S = sdh_fft(R[:, None], B, b_range=(lo, B.max()), bg_degree=5, log=False)
        s = S[0]
        ax[2, j].plot(f, s / s[(f > 2)].max(), lw=0.8, label=f"B>{lo}")
        k = np.argsort(s * (f > 2))[::-1]
        # local maxima list
        pk = [i for i in range(1, len(s) - 1) if s[i] > s[i - 1] and s[i] > s[i + 1] and f[i] > 2]
        pk = sorted(pk, key=lambda i: -s[i])[:6]
        print(f"  FFT B>{lo}: peaks " + ", ".join(f"{f[i]:.1f}T({s[i]/s[pk[0]]:.2f})" for i in pk))
    ax[2, j].axvline(FL, color="k", ls="--", label="F_L")
    ax[2, j].set_xlim(0, 2.2 * FL); ax[2, j].legend(fontsize=7); ax[2, j].set_xlabel("F (T)")
fig.tight_layout(); fig.savefig(Path(__file__).parent / "spot_runs67.png", dpi=110)
