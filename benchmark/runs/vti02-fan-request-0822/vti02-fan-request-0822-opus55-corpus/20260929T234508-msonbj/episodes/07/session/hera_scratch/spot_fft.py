"""Runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12) — sdh-spot-check read.
Raw MR, onset (sdh_onset), FFT (sdh_fft) vs F_L and the model templates."""
import warnings
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, luttinger_frequency, SdhOnsetError

SPOTS = {6: dict(n=3.2e12, label="electron n=+3.2e12"), 7: dict(n=-1.2e12, label="hole n=-1.2e12")}
out = {}
fig, ax = plt.subplots(3, 2, figsize=(12, 11))
for j, (rid, sp) in enumerate(SPOTS.items()):
    r = open_run(f"data/{rid}")
    B = r.col("magnet_field"); I = r.col("sr0_X") / -1e6; V = r.col("sr1_X") / 1.0
    R = V / I
    I_nom = 1.0 / 100e6
    sens = r.meta.get("instruments", {})
    FL = float(luttinger_frequency(sp["n"] * 1e4))
    o = np.argsort(B); B, R, I, V = B[o], R[o], I[o], V[o]
    print(f"=== run {rid} {sp['label']}: F_L = {FL:.2f} T; B {B.min():.2f}-{B.max():.2f}, N={len(B)}")
    print(f"  I drain med {np.median(I)*1e9:.3f} nA (min {I.min()*1e9:.3f}, max {I.max()*1e9:.3f}); "
          f"R(B~0) {R[:3].mean():.1f} Ohm, R max {R.max():.1f} at B={B[R.argmax()]:.2f}, V max {np.abs(V).max()*1e6:.2f} uV (sens 50 uV)")
    print(f"  T_sample {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f} K; I_tg max {np.abs(r.col('k_2400_tg_curr')).max()*1e12:.0f} pA, I_bg max {np.abs(r.col('k_2400_bg_curr')).max()*1e12:.0f} pA")
    ax[0, j].plot(B, R, lw=0.8); ax[0, j].set_title(f"run {rid} raw Rxx — {sp['label']}"); ax[0, j].set_xlabel("B (T)"); ax[0, j].set_ylabel("R (Ohm)")
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        try:
            on = sdh_onset(R, B, r_full_scale=50e-6 / I_nom, b_lo=max(0.3, B.min()))
            print(on.summary())
            out[rid] = on
        except SdhOnsetError as e:
            print("  SdhOnsetError:", e); on = None
        for ww in w: print("  warn:", ww.message)
    # bg-subtracted
    m = B > 1.0
    p = np.polyfit(B[m], R[m], 5); dR = R[m] - np.polyval(p, B[m])
    ax[1, j].plot(1 / B[m], dR, lw=0.7); ax[1, j].set_xlabel("1/B (1/T)"); ax[1, j].set_ylabel("dR (Ohm), poly5 in B, B>1 T")
    for lo in (1.0, 1.5, 2.0, 3.0):
        f, S = sdh_fft(R[:, None], B, b_range=(lo, B.max()), bg_degree=5, log=False, nfft=4096)
        S = S[0]; sel = (f > 2) & (f < 1.6 * FL)
        pk = []
        from scipy.signal import find_peaks
        ii, _ = find_peaks(S[sel], prominence=0.08 * S[sel].max())
        fs, ss = f[sel][ii], S[sel][ii]
        oo = np.argsort(-ss)[:6]
        print(f"  FFT b_lo={lo}: peaks " + ", ".join(f"{fs[k]:.1f} T ({ss[k]/ss.max():.2f})" for k in oo))
        ax[2, j].plot(f, S / S[sel].max(), lw=0.8, label=f"b_lo {lo}")
    ax[2, j].axvline(FL, c="k", ls="--", label="F_L"); ax[2, j].set_xlim(0, 1.6 * FL); ax[2, j].set_ylim(0, 1.2)
    ax[2, j].legend(fontsize=7); ax[2, j].set_xlabel("F (T)")
plt.tight_layout(); plt.savefig("hera_scratch/spot_fft.png", dpi=90)
