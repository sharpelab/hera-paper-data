"""SdH spot checks: run 6 (electron, n=+3.2e12, 0->10 T) and run 7 (hole, n=-1.2e12, 10->0.3 T).
Raw first, then onset + FFT per trace, peak list vs Luttinger F_L."""
import numpy as np, matplotlib, warnings
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, sdh_fft, sdh_onset, GateCalibration, luttinger_frequency
from scipy.signal import find_peaks

SENS = 50e-6
out = {}
fig, ax = plt.subplots(3, 2, figsize=(13, 11))
for col, (rid, nlab, n12) in enumerate([(6, "electron", 3.2), (7, "hole", -1.2)]):
    r = open_run(f"data/{rid}")
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); I = r.col("sr0_X") / ch["sr0"].gain
    V = r.col("sr1_X") / ch["sr1"].gain
    R = np.abs(V / I)
    o = np.argsort(B); B, R, I = B[o], R[o], I[o]
    FS = SENS / 10e-9
    t = r.col("time"); dt = np.diff(np.sort(t))
    print(f"run {rid} ({nlab} n={n12:+.1f}e12): {len(B)} pts, B {B.min():.3f}-{B.max():.3f}; R {R.min():.1f}-{R.max():.1f} Ohm "
          f"(FS {FS:.0f}, max frac {R.max()/FS:.2f}); I {I.min()*1e9:.2f}-{I.max()*1e9:.2f} nA; "
          f"Itg {r.col('k_2400_tg_curr').min()*1e12:+.0f}..{r.col('k_2400_tg_curr').max()*1e12:+.0f} pA, "
          f"Ibg {r.col('k_2400_bg_curr').min()*1e12:+.0f}..{r.col('k_2400_bg_curr').max()*1e12:+.0f} pA; "
          f"T {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f}; wall {(t.max()-t.min())/60:.1f} min, median dt {np.median(dt):.2f} s")
    for b in (0.3, 1, 2, 3, 5, 7, 10):
        k = np.argmin(abs(B - b)); print(f"   R({B[k]:.2f} T) = {R[k]:.1f}")
    ax[0, col].plot(B, R, lw=0.7); ax[0, col].set_title(f"run {rid} raw Rxx B_1-B_2, {nlab} n={n12:+.1f}e12, D=0")
    ax[0, col].set_xlabel("B (T)"); ax[0, col].set_ylabel("|Rxx| (Ohm)")
    # background-subtracted in B (poly 5 in B, log R) for B > 1
    m = B > 1.0
    lr = np.log10(R[m]); bg = np.polyval(np.polyfit(B[m], lr, 7), B[m]); d = lr - bg
    ax[1, col].plot(1 / B[m], d, lw=0.7); ax[1, col].set_xlabel("1/B (1/T)"); ax[1, col].set_ylabel("dlog10 R (poly7 in B)")
    try:
        on = sdh_onset(R, B, b_lo=0.5, r_full_scale=FS)
        print(on.summary())
        out[rid] = on
    except Exception as e:
        print("  sdh_onset:", type(e).__name__, e)
    for (blo, bhi), ls in [((1.5, 10), "-"), ((3, 10), "--"), ((5, 10), ":")]:
        f, sp = sdh_fft(R[:, None], B, b_range=(blo, bhi), nfft=4096, bg_degree=5)
        sp = sp[0]; ax[2, col].plot(f, sp / sp[(f > 3)].max(), ls, lw=0.8, label=f"{blo}-{bhi} T")
        sel = f > 2.5
        pk, pr = find_peaks(sp[sel], prominence=0.08 * sp[sel].max())
        ff = f[sel][pk]; aa = sp[sel][pk] / sp[sel].max()
        o2 = np.argsort(-aa)[:6]
        print(f"   FFT {blo}-{bhi} T (dF~{1/(1/blo-1/bhi):.1f} T): peaks " + ", ".join(f"{ff[j]:.1f}T({aa[j]:.2f})" for j in o2))
    FL = abs(n12) * 1e16 * 6.62607e-34 / (4 * 1.602177e-19)
    ax[2, col].axvline(FL, color="k", ls="--", lw=0.8, label=f"F_L {FL:.1f} T")
    ax[2, col].set_xlim(0, 60 if n12 > 0 else 30); ax[2, col].set_xlabel("F (T)"); ax[2, col].legend(fontsize=7)
    print(f"   F_L = {FL:.2f} T")
fig.tight_layout(); fig.savefig("hera_scratch/spots_run6_7.png", dpi=90)
