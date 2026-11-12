import numpy as np, json, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, current_channel, sdh_fft, sdh_onset, summarize_run
fig, ax = plt.subplots(2, 3, figsize=(16, 8))
for k, rid in enumerate([6, 7]):
    r = open_run(f"data/{rid}")
    print(summarize_run(r)); print("cols", r.cols)
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col(r.swept_axis) if r.swept_axis in r.cols else r.col_at(1)
    idx = r.col_indices(r.swept_axis); print("B idx", idx)
    Bm = r.col_at(idx[-1])
    I = r.col("sr0_X")/ch["sr0"].gain; R = np.abs(r.col("sr1_X")/ch["sr1"].gain/I)
    o = np.argsort(Bm); Bm, R, I = Bm[o], R[o], I[o]
    print(f"run {rid}: B {Bm.min():.3f}-{Bm.max():.3f}, R {R.min():.1f}-{R.max():.1f} Ohm, I {I.min()*1e9:.2f}-{I.max()*1e9:.2f} nA, T {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f}")
    print(f"  sr1 sens FS (5kOhm@10nA) -> max frac {R.max()/5000:.2f}; I_tg {r.col('k_2400_tg_curr').min()*1e12:.0f}..{r.col('k_2400_tg_curr').max()*1e12:.0f} pA, I_bg {r.col('k_2400_bg_curr').min()*1e12:.0f}..{r.col('k_2400_bg_curr').max()*1e12:.0f} pA")
    ax[k,0].plot(Bm, R, lw=.7); ax[k,0].set_title(f"run {rid} raw R(B)"); ax[k,0].set_xlabel("B (T)"); ax[k,0].set_ylabel("Rxx (Ohm)")
    # detrended vs 1/B
    m = Bm > 1.5
    p = np.polyfit(Bm[m], np.log10(R[m]), 5); res = np.log10(R[m]) - np.polyval(p, Bm[m])
    ax[k,1].plot(1/Bm[m], res, lw=.7); ax[k,1].set_xlabel("1/B"); ax[k,1].set_title("log R minus deg-5 poly (B>1.5)")
    for br in [(1.5, 10), (3, 10), (5, 10)]:
        f, S = sdh_fft(R[:, None], Bm, b_range=br, nfft=4096)
        S = S[0]; sel = (f > 2) & (f < 80)
        pk = np.argsort(S[sel])[::-1][:6]
        print(f"  FFT {br}: top peaks F = " + ", ".join(f"{f[sel][j]:.1f}T({S[sel][j]:.2g})" for j in sorted(pk, key=lambda j: f[sel][j])))
        ax[k,2].plot(f[sel], S[sel], lw=.8, label=f"B {br}")
    ax[k,2].set_xlabel("F (T)"); ax[k,2].legend(); ax[k,2].set_title("sdh_fft")
    try:
        on = sdh_onset(R, Bm, b_lo=0.3, r_full_scale=5000)
        print(on.summary())
    except Exception as e:
        print("onset err", e)
fig.tight_layout(); fig.savefig("hera_scratch/sdh_spots.png", dpi=90)
