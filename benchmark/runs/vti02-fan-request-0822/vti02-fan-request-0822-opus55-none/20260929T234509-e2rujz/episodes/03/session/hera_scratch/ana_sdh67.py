import numpy as np, json, warnings
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run, resolve_channels, sdh_fft, sdh_onset
out = {}
fig, ax = plt.subplots(2, 3, figsize=(16, 8))
for k, rid in enumerate([6, 7]):
    r = open_run(f"data/{rid}")
    print(f"=== run {rid}"); print(summarize_run(r))
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field") if "magnet_field" in r.cols else r.col_at(1)
    I = r.col("sr0_X") / ch["sr0"].gain
    R = np.abs((r.col("sr1_X") / ch["sr1"].gain) / I)
    o = np.argsort(B); B, R = B[o], R[o]
    print(f"B {B.min():.3f}-{B.max():.3f} ({len(B)} pts); R {R.min():.1f}-{R.max():.1f} Ohm; R(B<0.1)={R[B<0.1].mean():.1f}; I {I.mean()*1e9:.2f} nA; "
          f"T {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f}; Itg {np.ptp(r.col('k_2400_tg_curr'))*1e12:.0f} pA ptp")
    fs_R = 50e-6/10e-9
    print(f"max frac of FS: {R.max()/fs_R:.3f}")
    ax[k,0].plot(B, R, lw=.7); ax[k,0].set_title(f"run {rid} raw Rxx"); ax[k,0].set_xlabel("B (T)")
    for bl in [(1.5,10),(2.5,10),(4,10)]:
        f, sp = sdh_fft(R[:,None], B, b_range=bl, nfft=4096, bg_degree=5)
        sp = sp[0]; m = f>2
        pk = np.argsort(sp[m])[::-1]
        from scipy.signal import find_peaks
        p,_ = find_peaks(sp[m]); p = p[np.argsort(sp[m][p])[::-1]][:6]
        print(f"  FFT b_range {bl}: peaks F = " + ", ".join(f"{f[m][i]:.1f}T({sp[m][i]/sp[m].max():.2f})" for i in p))
        if bl==(1.5,10): ax[k,1].plot(f[m], sp[m]); ax[k,1].set_xlim(0,60); ax[k,1].set_title(f"run {rid} FFT 1.5-10 T")
    try:
        on = sdh_onset(R, B, r_full_scale=fs_R, b_lo=0.5)
        print(on.summary())
    except Exception as e:
        print("onset err", e)
    # detrended vs 1/B
    sel = B>1
    c = np.polyfit(B[sel], np.log10(R[sel]), 5); d = np.log10(R[sel]) - np.polyval(c, B[sel])
    ax[k,2].plot(1/B[sel], d, lw=.7); ax[k,2].set_xlabel("1/B"); ax[k,2].set_title(f"run {rid} detrended log R vs 1/B")
fig.tight_layout(); fig.savefig("hera_scratch/sdh67.png", dpi=90)
