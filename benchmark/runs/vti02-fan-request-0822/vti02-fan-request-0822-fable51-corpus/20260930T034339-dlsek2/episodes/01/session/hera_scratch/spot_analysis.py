"""Spot-check read for runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12): raw R(B), onset, FFT vs F_L."""
import numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, scipy.constants as c, warnings
from hera.analysis import open_run, resolve_channels, sdh_onset, sdh_fft, SdhOnsetError, summarize_run
FL = lambda n: c.h/(4*c.e)*abs(n)*1e16
runs = {6: 3.2, 7: -1.2}
fig, ax = plt.subplots(3, 2, figsize=(14, 12))
for j, (rid, n) in enumerate(runs.items()):
    r = open_run(f"data/{rid}")
    print("="*90); print(summarize_run(r))
    ch = {cc.cid: cc for cc in resolve_channels(r.metadata)}
    B = r.col("magnet_field"); I = r.col("sr0_X")/ch["sr0"].gain; R = (r.col("sr1_X")/ch["sr1"].gain)/I
    o = np.argsort(B); B, R, I = B[o], R[o], I[o]
    T = r.col("T_sample")
    print(f"run {rid}: n={n:+.1f}e12  F_L={FL(n):.2f} T  B {B.min():.2f}-{B.max():.2f} ({len(B)} pts)  R {R.min():.1f}..{R.max():.1f} Ohm  I {I.min()*1e9:.2f}-{I.max()*1e9:.2f} nA  T {T.min():.3f}-{T.max():.3f} K  interrupted={r.interrupted}")
    Rabs = np.abs(R)
    ax[0, j].plot(B, R, lw=0.7); ax[0, j].set_title(f"run {rid}: n={n:+.1f}e12, D=0 — raw R(B) (signed)"); ax[0, j].set_xlabel("B (T)"); ax[0, j].set_ylabel("Rxx (Ohm)")
    # onset
    rfs = 50e-6/10e-9
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            on = sdh_onset(R, B, r_full_scale=rfs)
            for ww in w: print("  warn:", ww.message)
        print(on.summary())
        onset = on.onset_b
    except SdhOnsetError as e:
        print("SdhOnsetError:", e); onset = None
    # bg-subtracted trace (deg 5 in B) above 1 T for the eye
    m = B > 1.0
    cf = np.polyfit(B[m], R[m], 5); dR = R[m] - np.polyval(cf, B[m])
    ax[1, j].plot(1/B[m], dR, lw=0.7); ax[1, j].set_xlabel("1/B (1/T)"); ax[1, j].set_ylabel("dRxx (deg-5 bg removed)"); ax[1, j].set_title(f"run {rid}: dR vs 1/B (B>1 T); onset_b={onset}")
    if onset: ax[1, j].axvline(1/onset, color="r", ls="--")
    # FFT windows
    for lo, col in ((onset or 1.5, "k"), (max((onset or 1.5), 2.5), "C1"), (4.0, "C2")):
        try:
            f, sp = sdh_fft(R[:, None], B, b_range=(lo, B.max()), bg_degree=5, log=False, nfft=2048)
            s = sp[0]/sp[0].max(); ax[2, j].plot(f, s, color=col, lw=0.9, label=f"B {lo:.2f}-{B.max():.0f} T, dF={1/(1/lo-1/B.max()):.2f} T")
            from scipy.signal import find_peaks
            pk, pr = find_peaks(s, prominence=0.05)
            pk = sorted(pk, key=lambda p: -s[p])[:8]
            print(f"  FFT [{lo:.2f},{B.max():.1f}] dF={1/(1/lo-1/B.max()):.2f}: peaks " + ", ".join(f"{f[p]:.1f}T({s[p]:.2f})" for p in pk))
        except Exception as e: print("  fft err", lo, e)
    for k, lab in ((1, "F_L"), (0.72, "0.72F_L"), (0.28, "0.28F_L")):
        ax[2, j].axvline(k*FL(n), color="gray", ls=":", lw=0.8); ax[2, j].text(k*FL(n), 1.0, lab, fontsize=7, rotation=90, va="top")
    ax[2, j].set_xlim(0, 2.2*FL(n)); ax[2, j].set_xlabel("F (T)"); ax[2, j].set_ylabel("FFT amp (norm)"); ax[2, j].legend(fontsize=7); ax[2, j].set_title(f"run {rid}: 1/B FFT; F_L={FL(n):.1f} T")
fig.tight_layout(); fig.savefig("hera_scratch/spot_runs67.png", dpi=110); print("saved hera_scratch/spot_runs67.png")
