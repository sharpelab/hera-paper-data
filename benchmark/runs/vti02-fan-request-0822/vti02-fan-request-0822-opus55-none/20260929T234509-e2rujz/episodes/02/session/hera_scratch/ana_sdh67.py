import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt, json, warnings
from hera.analysis import open_run, summarize_run, resolve_channels, sdh_fft, sdh_onset, luttinger_frequency, GateCalibration
cal = json.load(open("hera_scratch/cal_run5.json"))
fig, ax = plt.subplots(3, 2, figsize=(13, 11))
for j, (rid, n12) in enumerate([(6, 3.2), (7, -1.2)]):
    r = open_run(f"data/{rid}"); print(summarize_run(r)); print("cols", r.cols)
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col(r.swept_axis) if r.swept_axis in r.cols else r.col_at(1)
    try: Brd = r.col("magnet_field")
    except Exception: Brd = B
    I = r.col("sr0_X") / ch["sr0"].gain
    R = np.abs(r.col("sr1_X") / ch["sr1"].gain / I)
    o = np.argsort(B); B, R, I = B[o], R[o], I[o]
    FL = luttinger_frequency(n12 * 1e16)
    print(f"run {rid}: n={n12}e12 F_L={float(FL):.2f} T; B {B.min():.2f}-{B.max():.2f}, R {R.min():.0f}-{R.max():.0f} Ohm; I {I.min()*1e9:.2f}-{I.max()*1e9:.2f} nA; T {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f}; "
          f"Itg {r.col('k_2400_tg_curr').min()*1e12:.0f}..{r.col('k_2400_tg_curr').max()*1e12:.0f} pA; Ibg {r.col('k_2400_bg_curr').min()*1e12:.0f}..{r.col('k_2400_bg_curr').max()*1e12:.0f}; sens FS {r.meta.get('instruments',{}) and ''}")
    for b in [0.3, 1, 2, 3, 4, 5, 6, 8, 10]:
        k = np.argmin(abs(B - b)); print(f"   B={B[k]:.2f}: R={R[k]:.1f}")
    ax[0, j].plot(B, R, lw=.8); ax[0, j].set_title(f"run {rid} raw Rxx, n={n12}e12 D=0"); ax[0, j].set_xlabel("B (T)")
    # background-subtracted
    m = B > 1.0
    cf = np.polyfit(B[m], np.log10(R[m]), 5); dR = np.log10(R[m]) - np.polyval(cf, B[m])
    ax[1, j].plot(1 / B[m], dR, lw=.8); ax[1, j].set_xlabel("1/B"); ax[1, j].set_title("log R minus deg-5 poly (B>1T)")
    for lo in [1.5, 2.0, 3.0]:
        f, S = sdh_fft(R[:, None], B, b_range=(lo, B.max()), nfft=4096)
        S = S[0]; sel = f > 2
        pk = np.argsort(S[sel])[::-1][:6]
        print(f"   FFT b>{lo}: top peaks (F, amp): " + ", ".join(f"{f[sel][p]:.1f}:{S[sel][p]:.3g}" for p in sorted(pk, key=lambda p: f[sel][p])))
        if lo == 1.5: ax[2, j].plot(f, S, lw=.8, label=f"B>{lo}")
    ax[2, j].axvline(float(FL), color="k", ls=":"); ax[2, j].set_xlim(0, 3 * float(FL)); ax[2, j].set_xlabel("F (T)"); ax[2, j].legend()
    try:
        so = sdh_onset(R, B, b_lo=0.5, r_full_scale=50e-6 / 1e-8)
        print(so.summary())
    except Exception as e:
        print("   sdh_onset:", type(e).__name__, e)
fig.tight_layout(); fig.savefig("hera_scratch/sdh67.png", dpi=90)
