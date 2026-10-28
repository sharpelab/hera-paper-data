import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run, resolve_channels, sdh_fft, sdh_onset
out = {}
fig, ax = plt.subplots(2, 2, figsize=(12, 8))
for k, rid in enumerate([6, 7]):
    r = open_run(f"data/{rid}")
    print(f"=== run {rid} ===\n{summarize_run(r)}")
    print("comments:", r.meta["comments"])
    B = r.col(r.swept_axis) if r.swept_axis in r.cols else r.col_at(1)
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    I = r.col("sr0_X") / ch["sr0"].gain
    R = np.abs((r.col("sr1_X") / ch["sr1"].gain) / I)
    o = np.argsort(B); B, R = B[o], R[o]
    print(f"B {B.min():.3f}..{B.max():.3f}, N={len(B)}, R {R.min():.1f}..{R.max():.1f} Ohm, R(Bmin)={R[0]:.1f}, R(Bmax)={R[-1]:.1f}; I {I.min()*1e9:.2f}..{I.max()*1e9:.2f} nA")
    print(f"Igate tg {r.col('k_2400_tg_curr').min()*1e12:.0f}..{r.col('k_2400_tg_curr').max()*1e12:.0f} pA; T {r.col('T_sample').min():.3f}..{r.col('T_sample').max():.3f}")
    ax[0, k].plot(B, R, lw=0.7); ax[0, k].set_xlabel("B (T)"); ax[0, k].set_ylabel("Rxx (Ohm)"); ax[0, k].set_title(f"run {rid} raw")
    try:
        on = sdh_onset(R, B, b_lo=0.5, r_full_scale=50e-6/1e-8)
        print(on.summary())
    except Exception as e:
        print("sdh_onset:", type(e).__name__, e)
    for br, c in [((2.0, 10.0), "C0"), ((3.0, 10.0), "C1"), ((1.5, 10.0), "C2")]:
        f, sp = sdh_fft(R[:, None], B, b_range=br, nfft=4096, bg_degree=5)
        sp = sp[0]
        m = (f > 2) & (f < 80)
        ax[1, k].plot(f[m], sp[m], c, lw=0.8, label=f"{br}")
        pk = np.argsort(sp[m])[::-1]
        ff = f[m]; ss = sp[m]
        # local maxima
        from scipy.signal import find_peaks
        p, _ = find_peaks(ss, prominence=0.1 * ss.max())
        print(f"FFT b_range {br}: peaks " + ", ".join(f"{ff[i]:.1f}T({ss[i]/ss.max():.2f})" for i in p[np.argsort(-ss[p])][:6]))
    ax[1, k].set_xlabel("F (T)"); ax[1, k].legend(); ax[1, k].set_title(f"run {rid} FFT (log R, bg5)")
fig.tight_layout(); fig.savefig("hera_scratch/sdh_spots.png", dpi=110)
