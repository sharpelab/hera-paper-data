import numpy as np, warnings, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from hera.analysis import sdh_fft, sdh_onset, SdhOnsetError, luttinger_frequency
fig, ax = plt.subplots(2, 2, figsize=(13, 8))
for k, (rid, n12) in enumerate([(6, 3.2), (7, -1.2)]):
    B, R = np.load(f"hera_scratch/run{rid}_BR.npy")
    FL = luttinger_frequency(abs(n12) * 1e16)
    print(f"\n=== run {rid}: n = {n12:+.1f}e12 -> F_L(full, 4-fold) = {FL:.2f} T")
    for blo in [1.5, 2.5, 4.0]:
        m = B >= blo
        f, sp = sdh_fft(R[m][:, None], B[m], b_range=(blo, 10.0), nfft=2048, bg_degree=5, log=False)
        sp = sp[0]; sel = (f > 2) & (f < 80)
        pk = f[sel][np.argsort(sp[sel])[::-1][:6]]
        print(f"  FFT window B>{blo}: top peaks (T): {np.round(np.sort(pk), 1)}; max at {f[sel][np.argmax(sp[sel])]:.1f} T")
        if blo == 2.5:
            ax[1, k].plot(f, sp / sp[sel].max(), label=f"B>{blo}")
    ax[1, k].set_xlim(0, 80); ax[1, k].set_xlabel("F (T)"); ax[1, k].set_ylabel("FFT amp (norm)"); ax[1, k].axvline(FL, color="r", ls="--", label=f"F_L={FL:.1f}")
    ax[1, k].axvline(FL/2, color="orange", ls=":", label="F_L/2"); ax[1, k].axvline(FL/4, color="g", ls=":", label="F_L/4"); ax[1, k].legend(fontsize=7)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            o = sdh_onset(R, B, b_lo=0.5, r_full_scale=5000.0)
        print(o.summary())
    except SdhOnsetError as e:
        print("  sdh_onset failed:", e)
    # detrended trace
    m = B > 1.0
    bg = np.polyval(np.polyfit(B[m], R[m], 5), B[m])
    ax[0, k].plot(1 / B[m], R[m] - bg, lw=0.7); ax[0, k].set_xlabel("1/B (1/T)"); ax[0, k].set_ylabel("dR (Ohm)"); ax[0, k].set_title(f"run {rid} detrended (deg-5 in B, B>1 T)")
fig.tight_layout(); fig.savefig("hera_scratch/spot_sdh.png", dpi=110)
