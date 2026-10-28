import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run, resolve_channels, sdh_onset, sdh_fft, luttinger_frequency
res = {}
fig, ax = plt.subplots(2, 3, figsize=(16, 8))
for k, rid in enumerate([6, 7]):
    r = open_run(f"data/{rid}"); print(summarize_run(r)); print(r.meta["columns"])
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col_at(1); I = r.col("sr0_X") / ch["sr0"].gain
    R = (r.col("sr1_X") / ch["sr1"].gain) / I
    Bm = r.col("magnet_field") if "magnet_field" in r.cols and r.col_indices("magnet_field").__len__()==1 else B
    o = np.argsort(B); B, R, I = B[o], R[o], I[o]
    print(f"run {rid}: B {B.min():.2f}-{B.max():.2f}, R {R.min():.1f}-{R.max():.1f} Ohm, I {I.min()*1e9:.2f}-{I.max()*1e9:.2f} nA; "
          f"I_tg {r.col('k_2400_tg_curr').min()*1e12:.0f}..{r.col('k_2400_tg_curr').max()*1e12:.0f} pA, T {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f}")
    sens = r.meta["instruments"] if False else None
    ax[k,0].plot(B, R, lw=0.7); ax[k,0].set_title(f"run {rid} R(B)"); ax[k,0].set_xlabel("B (T)")
    m = B > 1.0
    Rb = R[m]; Bb = B[m]; p = np.polyfit(Bb, Rb, 5); dR = Rb - np.polyval(p, Bb)
    ax[k,1].plot(Bb, dR, lw=0.7); ax[k,1].set_title("detrended (deg5 in B)")
    for br in [(2, 10), (4, 10), (6, 10)]:
        f, sp = sdh_fft(R[:, None], B, b_range=br, nfft=4096, bg_degree=5, log=False)
        sp = sp[0]; sel = f > 2
        top = np.argsort(sp[sel])[::-1][:6]
        print(f"  FFT b_range {br}: top peaks F = " + ", ".join(f"{f[sel][t]:.1f}T({sp[sel][t]:.2g})" for t in top))
        if br == (2, 10): ax[k,2].plot(f, sp, label=str(br))
        else: ax[k,2].plot(f, sp, label=str(br), alpha=0.7)
    ax[k,2].set_xlim(0, 80); ax[k,2].legend(); ax[k,2].set_xlabel("F (T)")
    try:
        on = sdh_onset(R, B, b_lo=0.5, r_full_scale=50e-6/10e-9)
        print(on.summary())
    except Exception as e: print("onset error:", e)
fig.tight_layout(); fig.savefig("hera_scratch/spot_runs67.png", dpi=90)
