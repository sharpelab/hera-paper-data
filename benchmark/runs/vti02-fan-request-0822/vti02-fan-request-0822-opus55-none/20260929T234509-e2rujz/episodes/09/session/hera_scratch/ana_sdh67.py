import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, current_channel, sdh_fft, sdh_onset, summarize_run
out = {}
fig, ax = plt.subplots(3, 2, figsize=(12, 11))
for j, rid in enumerate([6, 7]):
    r = open_run(f"../data/{rid}")
    print(summarize_run(r))
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col(r.swept_axis) if r.swept_axis in r.cols else r.col_at(1)
    I = r.col("sr0_X") / ch["sr0"].gain
    R = np.abs((r.col("sr1_X") / ch["sr1"].gain) / I)
    o = np.argsort(B); B, R, I = B[o], R[o], I[o]
    print(f"run {rid}: B {B.min():.2f}-{B.max():.2f}, R {R.min():.1f}-{R.max():.1f} Ohm, I {I.min()*1e9:.2f}-{I.max()*1e9:.2f} nA, sr1 X max {np.abs(r.col('sr1_X')).max()*1e6:.1f} uV")
    print("  R at B=", {b: round(float(np.interp(b, B, R)),1) for b in [0.3,1,2,3,5,7,9,10]})
    print("  T range", r.col("T_sample").min(), r.col("T_sample").max(), " Itg", r.col("k_2400_tg_curr").min()*1e12, r.col("k_2400_tg_curr").max()*1e12)
    ax[0, j].plot(B, R, lw=0.7); ax[0, j].set_title(f"run {rid} raw Rxx"); ax[0, j].set_xlabel("B (T)")
    try:
        on = sdh_onset(R, B, r_full_scale=50e-6/10e-9)
        print(on.summary())
    except Exception as e:
        print("onset err", e)
    for lo in [1.0, 2.0, 3.0]:
        f, sp = sdh_fft(R[:, None], B, b_range=(lo, B.max()), nfft=4096, bg_degree=5)
        sp = sp[0]; m = f > 2
        pk = np.argsort(sp[m])[::-1][:6]
        print(f"  FFT b>{lo}: top freqs", [(round(float(f[m][k]),1), round(float(sp[m][k]),3)) for k in sorted(pk, key=lambda k: -sp[m][k])])
        if lo == 1.0:
            ax[1, j].plot(f, sp); ax[1, j].set_xlim(0, 80); ax[1, j].set_xlabel("F (T)"); ax[1, j].set_title(f"run {rid} FFT (B>1)")
    # detrended vs 1/B
    sel = B > 1.0
    y = np.log10(R[sel]); cf = np.polyfit(B[sel], y, 5); d = y - np.polyval(cf, B[sel])
    ax[2, j].plot(1/B[sel], d, lw=0.7); ax[2, j].set_xlabel("1/B"); ax[2, j].set_title(f"run {rid} detrended log R")
fig.tight_layout(); fig.savefig("sdh67.png", dpi=90)
