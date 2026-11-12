"""SdH spot checks runs 6 (e, n=+3.2e12) and 7 (h, n=-1.2e12): raw R(B), onset, FFT windows, LL minima."""
import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, summarize_run, sdh_onset, sdh_fft, luttinger_frequency, SdhOnsetError
import scipy.constants as c
out = {}
for rid, n12 in [(6, 3.2), (7, -1.2)]:
    r = open_run(f"data/{rid}"); print("="*70); print(summarize_run(r))
    B = r.col("magnet_field"); I = r.col("sr0_X") / r.metadata["measurement_config"]["sr0_gain"]
    R = r.col("sr1_X") / I; T = r.col("T_sample")
    o = np.argsort(B); B, R, I, T = B[o], R[o], I[o], T[o]
    FL = luttinger_frequency(abs(n12) * 1e16); print(f"n={n12:+.2f}e12  F_L={FL:.2f} T  R(B~0.3)={R[np.argmin(abs(B-0.3))]:.1f}  Rmax={R.max():.0f} at {B[np.argmax(R)]:.2f} T  T {T.min():.3f}-{T.max():.3f} K  I {I.min()*1e9:.2f}-{I.max()*1e9:.2f} nA")
    nu = abs(n12) * 1e16 * c.h / (c.e * B[B > 0.5])
    # LL minima at high B: local minima of R for B>3
    m = B > 3; pk, _ = find_peaks(-R[m], prominence=0.15 * np.ptp(R[m]))
    print("R minima (B>3 T): " + ", ".join(f"B={B[m][p]:.2f} nu={abs(n12)*1e16*c.h/(c.e*B[m][p]):.1f}" for p in pk))
    pk2, _ = find_peaks(R[m], prominence=0.15 * np.ptp(R[m]))
    print("R maxima (B>3 T): " + ", ".join(f"B={B[m][p]:.2f} nu={abs(n12)*1e16*c.h/(c.e*B[m][p]):.1f}" for p in pk2))
    try:
        on = sdh_onset(R, B, b_lo=0.3, r_full_scale=50e-6 / 10e-9); print(on.summary()); onset = on.onset_b
    except SdhOnsetError as e:
        print("SdhOnsetError:", e); onset = None
    fig, ax = plt.subplots(2, 2, figsize=(14, 8))
    ax[0, 0].plot(B, R, lw=0.7); ax[0, 0].set_xlabel("B (T)"); ax[0, 0].set_ylabel("Rxx sr1 (Ohm)"); ax[0, 0].set_title(f"run {rid}: n={n12:+.1f}e12, D=0 — raw")
    ax[0, 1].plot(1 / B[B > 1], R[B > 1], lw=0.7); ax[0, 1].set_xlabel("1/B (1/T)"); ax[0, 1].set_ylabel("Rxx"); ax[0, 1].set_title("vs 1/B (B>1 T)")
    for j, (lo, hi) in enumerate([(1.5, 10), (1.5, 5), (2.5, 6), (4, 10)]):
        if onset: lo = max(lo, onset) if j == 0 else lo
        sel = (B >= lo) & (B <= hi)
        for deg in (3, 5, 7):
            f, sp = sdh_fft(R[sel][:, None], B[sel], b_range=(lo, hi), bg_degree=deg, log=False, nfft=4096)
            s = sp[0]; keep = f > 2; s = s / s[keep].max()
            pks, _ = find_peaks(s, prominence=0.08, height=0.1); pks = [p for p in pks if f[p] > 2]
            top = sorted(pks, key=lambda p: -s[p])[:6]
            print(f"  FFT [{lo:.2f},{hi}] deg{deg}: dF={1/(1/lo-1/hi):.2f} T  peaks: " + ", ".join(f"{f[p]:.1f}T({s[p]:.2f},{f[p]/FL:.2f}FL)" for p in sorted(top)))
            if deg == 5: ax[1, 0].plot(f, s + 0.6 * j, lw=0.8, label=f"[{lo:.1f},{hi}] deg5")
        ax[1, 0].axvline(FL, color="k", ls=":", lw=1)
    ax[1, 0].set_xlim(0, 1.6 * FL); ax[1, 0].set_xlabel("F (T)"); ax[1, 0].set_ylabel("|FFT| norm (offset)"); ax[1, 0].legend(fontsize=7); ax[1, 0].set_title(f"FFT in 1/B; F_L={FL:.1f} T")
    # background-subtracted trace
    sel = B > 1.2; cf = np.polyfit(B[sel], R[sel], 5); dR = R[sel] - np.polyval(cf, B[sel])
    ax[1, 1].plot(B[sel], dR, lw=0.7); ax[1, 1].set_xlabel("B (T)"); ax[1, 1].set_ylabel("dRxx (deg-5 bg removed)"); ax[1, 1].set_title("oscillatory part")
    fig.tight_layout(); fig.savefig(f"hera_scratch/spot_run{rid}.png", dpi=110)
