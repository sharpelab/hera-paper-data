import numpy as np, warnings
from hera.analysis import open_run, summarize_run, resolve_channels, sdh_fft, sdh_onset, luttinger_frequency, GateCalibration
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig, ax = plt.subplots(3, 2, figsize=(12, 10))
for j, rid in enumerate([6, 7]):
    r = open_run(f"data/{rid}")
    print(summarize_run(r)); print(r.cols)
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    Bcols = r.col_indices("magnet_field")
    B = r.col_at(Bcols[0])
    I = r.col("sr0_X")/ch["sr0"].gain
    R = np.abs((r.col("sr1_X")/ch["sr1"].gain)/I)
    o = np.argsort(B); B, R, I = B[o], R[o], I[o]
    print(f"run {rid}: B {B.min():.2f}-{B.max():.2f}, R(0.3-1T) {np.median(R[B<1]):.1f}, R max {R.max():.0f} at {B[np.argmax(R)]:.2f} T, I {I.min()*1e9:.2f}-{I.max()*1e9:.2f} nA, T {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f}")
    ig = r.col("k_2400_tg_curr"), r.col("k_2400_bg_curr")
    print(f"  I_tg {ig[0].min()*1e12:.0f}..{ig[0].max()*1e12:.0f} pA, I_bg {ig[1].min()*1e12:.0f}..{ig[1].max()*1e12:.0f} pA")
    ax[0, j].plot(B, R, lw=0.7); ax[0, j].set_title(f"run {rid} raw Rxx"); ax[0,j].set_xlabel("B (T)")
    # background-subtracted vs 1/B
    for br in [(1.5, 10), (3, 10), (5, 10)]:
        f, sp = sdh_fft(R[:, None], B, b_range=br, nfft=4096, bg_degree=5)
        sp = sp[0]
        m = f > 2
        pk = np.argsort(sp[m])[::-1]
        # local maxima
        from scipy.signal import find_peaks
        p, _ = find_peaks(sp, prominence=sp[m].max()*0.08)
        p = [q for q in p if f[q] > 2 and f[q] < 120]
        p = sorted(p, key=lambda q: -sp[q])[:6]
        print(f"  FFT {br}: peaks " + ", ".join(f"{f[q]:.1f}T({sp[q]/sp[m].max():.2f})" for q in p))
        if br == (1.5, 10):
            ax[2, j].plot(f, sp, label=str(br))
    ax[2, j].set_xlim(0, 80); ax[2,j].set_xlabel("F (T)"); ax[2,j].legend()
    sel = B > 1.0
    cf = np.polyfit(B[sel], np.log10(R[sel]), 5)
    dR = np.log10(R[sel]) - np.polyval(cf, B[sel])
    ax[1, j].plot(1/B[sel], dR, lw=0.7); ax[1, j].set_xlabel("1/B"); ax[1, j].set_title("log R - poly5(B)")
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            on = sdh_onset(R, B, r_full_scale=50e-6/1e-8)
        print(on.summary())
        for ww in w: print("  warn:", ww.message)
    except Exception as e:
        print("  onset error:", e)
fig.tight_layout(); fig.savefig("hera_scratch/spot_runs67.png", dpi=90)
cal = GateCalibration(2.796e-3, 2.161e-3, n_offset=-0.0894e16, D_offset=-0.013e9)
for n in [3.2, -1.2]:
    print(n, "F_L =", luttinger_frequency(n*1e16))
