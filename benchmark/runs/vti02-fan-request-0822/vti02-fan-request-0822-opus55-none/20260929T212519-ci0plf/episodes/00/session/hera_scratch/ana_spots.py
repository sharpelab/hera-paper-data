import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from pathlib import Path
from hera.analysis import open_run, resolve_channels, sdh_fft, sdh_onset, summarize_run, luttinger_frequency
D = Path("data")
fig, ax = plt.subplots(2, 2, figsize=(13, 8))
for k, (rid, n12) in enumerate([(6, 3.2), (7, -1.2)]):
    r = open_run(D / str(rid)); print(summarize_run(r))
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); I = r.col("sr0_X") / ch["sr0"].gain
    R = np.abs((r.col("sr1_X") / ch["sr1"].gain) / I)
    o = np.argsort(B); B, R, I = B[o], R[o], I[o]
    FL = float(luttinger_frequency(abs(n12) * 1e16))
    print(f"run {rid}: n={n12}e12 F_L={FL:.1f} T; R(0)={R[B<0.1].mean():.1f} R(max)={R.max():.1f} at {B[R.argmax()]:.2f} T; I {I.min()*1e9:.2f}-{I.max()*1e9:.2f} nA; "
          f"Itg {r.col('k_2400_tg_curr').min()*1e12:.0f}..{r.col('k_2400_tg_curr').max()*1e12:.0f} pA, Ibg {r.col('k_2400_bg_curr').min()*1e12:.0f}..{r.col('k_2400_bg_curr').max()*1e12:.0f} pA; T {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f}")
    ax[0, k].plot(B, R, lw=0.8); ax[0, k].set_title(f"run {rid} raw, n={n12}e12"); ax[0, k].set_xlabel("B (T)"); ax[0, k].set_ylabel("Rxx (Ohm)")
    try:
        on = sdh_onset(R, B, r_full_scale=50e-6 / 10e-9)
        print(on.summary())
        blo = max(on.onset_b, 1.0)
    except Exception as e:
        print("onset err", e); blo = 2.0
    for lo in sorted({blo, 2.0, 3.0, 4.0}):
        for deg in (3, 5):
            f, sp = sdh_fft(R[:, None], B, b_range=(lo, 10.0), nfft=4096, bg_degree=deg)
            sp = sp[0]; m = f > 2
            pk = np.argsort(sp[m])[::-1]
            from scipy.signal import find_peaks
            pp, _ = find_peaks(sp[m], prominence=0.1 * sp[m].max())
            top = sorted(pp, key=lambda p: -sp[m][p])[:5]
            print(f"  FFT B[{lo:.2f},10] deg{deg}: res {1/(1/lo-1/10):.2f} T; peaks " + ", ".join(f"{f[m][p]:.1f}T({sp[m][p]/sp[m].max():.2f})" for p in top) + f"  [F/F_L: " + ", ".join(f"{f[m][p]/FL:.2f}" for p in top) + "]")
    f, sp = sdh_fft(R[:, None], B, b_range=(max(blo, 1.5), 10.0), nfft=4096, bg_degree=5)
    ax[1, k].plot(f, sp[0]); ax[1, k].axvline(FL, color="r", ls="--", label=f"F_L={FL:.1f}"); ax[1, k].set_xlim(0, 60); ax[1, k].legend(); ax[1, k].set_xlabel("F (T)")
fig.tight_layout(); fig.savefig("hera_scratch/spots_67.png", dpi=90)
