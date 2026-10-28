import numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from hera.analysis import open_run, summarize_run, resolve_channels, sdh_fft, sdh_onset, luttinger_frequency
D = Path(__file__).resolve().parent.parent / "data"
fig, ax = plt.subplots(3, 2, figsize=(13, 11))
for j, rid in enumerate([6, 7]):
    r = open_run(D / str(rid))
    print(f"==== run {rid}"); print(summarize_run(r)); print("tags:", r.tags)
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col(r.swept_axis) if r.swept_axis in r.cols else r.col_at(1)
    I = r.col("sr0_X") / ch["sr0"].gain
    R = np.abs((r.col("sr1_X") / ch["sr1"].gain) / I)
    X1 = r.col("sr1_X")
    sens = r.meta.get("instruments", {})
    o = np.argsort(B); B, R, X1, I = B[o], R[o], X1[o], I[o]
    print(f"B {B.min():.3f}-{B.max():.3f}, R {R.min():.1f}-{R.max():.1f} Ohm, R(Bmin) {R[0]:.1f}, R(Bmax) {R[-1]:.1f}, "
          f"|sr1_X| max {np.abs(X1).max()*1e6:.2f} uV (sens 50 uV), I {I.min()*1e9:.2f}-{I.max()*1e9:.2f} nA, "
          f"T {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f}")
    print(f"I_tg {r.col('k_2400_tg_curr').min()*1e12:+.0f}..{r.col('k_2400_tg_curr').max()*1e12:+.0f} pA, I_bg {r.col('k_2400_bg_curr').min()*1e12:+.0f}..{r.col('k_2400_bg_curr').max()*1e12:+.0f} pA")
    ax[0, j].plot(B, R, lw=0.7); ax[0, j].set_title(f"run {rid} raw R(B)"); ax[0, j].set_xlabel("B (T)"); ax[0, j].set_ylabel("R (Ohm)")
    # background-subtracted
    m = B > 1.0
    cf = np.polyfit(B[m], np.log10(R[m]), 5); dr = np.log10(R[m]) - np.polyval(cf, B[m])
    ax[1, j].plot(1 / B[m], dr, lw=0.7); ax[1, j].set_xlabel("1/B (1/T)"); ax[1, j].set_title("log R - poly5(B), B>1 T")
    for blo in (1.5, 2.0, 3.0, 4.0):
        f, sp = sdh_fft(R[:, None], B, b_range=(blo, B.max()), nfft=4096)
        sp = sp[0]
        k = (f > 2) & (f < 80)
        pk = np.argsort(sp[k])[::-1]
        ff = f[k]; ss = sp[k]
        # local maxima
        from scipy.signal import find_peaks
        pp, _ = find_peaks(ss, prominence=ss.max() * 0.08)
        top = sorted(pp, key=lambda p: -ss[p])[:6]
        print(f"  FFT b>{blo}: peaks " + ", ".join(f"{ff[p]:.1f} T ({ss[p]/ss.max():.2f})" for p in top))
        if blo == 2.0:
            ax[2, j].plot(f, sp / sp[(f > 2)].max(), lw=0.8); ax[2, j].set_xlim(0, 80); ax[2, j].set_xlabel("F (T)")
    try:
        on = sdh_onset(R, B, r_full_scale=50e-6 / 10e-9)
        print(on.summary())
    except Exception as e:
        print("onset err:", e)
    print("n_spot/F_L:", [t for t in r.tags])
fig.tight_layout(); fig.savefig(Path(__file__).parent / "sdh67.png", dpi=90)
