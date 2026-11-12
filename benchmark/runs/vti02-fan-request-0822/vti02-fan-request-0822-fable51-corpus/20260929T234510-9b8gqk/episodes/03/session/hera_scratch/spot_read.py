"""sdh-spot-check read on runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12): raw, onset, FFT vs F_L."""
import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt, warnings
from hera.analysis import open_run, summarize_run, sdh_onset, sdh_fft, SdhOnsetError, luttinger_frequency
I_BIAS = 1.0 / 100e6
out = {}
fig, axs = plt.subplots(3, 2, figsize=(13, 11))
for col, (rid, n12) in enumerate([(6, 3.2), (7, -1.2)]):
    r = open_run(f"data/{rid}"); print(f"\n===== run {rid}  n = {n12:+.2f}e12 =====\n{summarize_run(r)}")
    B = r.col("magnet_field"); R = r.col("sr1_X") / I_BIAS
    o = np.argsort(B); B, R = B[o], R[o]
    try: FL = luttinger_frequency(abs(n12) * 1e16)
    except Exception as e: FL = 4.1357e-15 / 4 * abs(n12) * 1e16; print("luttinger_frequency fallback", e)
    print(f"F_L = {FL:.2f} T ; R(B~0.5) = {np.interp(0.5,B,R):.1f} Ohm, R(10T) = {R[-1]:.1f} Ohm, max {R.max():.1f} (FS 5000)")
    ax = axs[0, col]; ax.plot(B, R, lw=0.7); ax.set_title(f"run {rid} raw Rxx, n={n12:+.1f}e12, D=0"); ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx (Ohm)")
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        try:
            on = sdh_onset(R, B, r_full_scale=50e-6 / I_BIAS)
            print(on.summary()); out[rid] = on
            onset = on.onset_b
        except SdhOnsetError as e:
            print("SdhOnsetError:", e); onset = None
        for ww in w: print("  warn:", ww.message)
    # background-subtracted trace (deg 5 in B) above 1 T
    m = B >= 1.0; cf = np.polyfit(B[m], R[m], 5); dR = R[m] - np.polyval(cf, B[m])
    ax = axs[1, col]; ax.plot(1 / B[m], dR, lw=0.7); ax.set_xlabel("1/B (1/T)"); ax.set_ylabel("dRxx (Ohm), deg-5 bg >1 T"); ax.set_title("bg-subtracted vs 1/B")
    if onset: ax.axvline(1 / onset, color="r", ls="--", label=f"onset {onset:.2f} T"); ax.legend()
    # FFT in several windows
    ax = axs[2, col]
    for lo in ([onset] if onset else []) + [2.0, 3.0, 4.0]:
        if lo is None or lo >= 9: continue
        f, S = sdh_fft(R[:, None], B, b_range=(lo, B.max()), bg_degree=5, log=False, nfft=4096)
        S = S[0]; sel = (f > 2) & (f < 120)
        ax.plot(f[sel], S[sel] / S[sel].max(), lw=0.8, label=f"B>{lo:.2f} T")
        # peaks
        from scipy.signal import find_peaks
        pk, pr = find_peaks(S[sel], prominence=0.08 * S[sel].max())
        print(f"  FFT window [{lo:.2f},{B.max():.1f}] dF={1/(1/lo-1/B.max()):.2f} T: peaks " + ", ".join(f"{f[sel][p]:.1f}T({S[sel][p]/S[sel].max():.2f}, {f[sel][p]/FL:.2f}F_L)" for p in pk))
    ax.axvline(FL, color="k", ls=":", label=f"F_L={FL:.1f}"); ax.axvline(0.72 * FL, color="g", ls=":", label="0.72 F_L"); ax.axvline(0.28 * FL, color="g", ls="-.", label="0.28 F_L")
    ax.set_xlabel("F (T)"); ax.set_ylabel("|FFT| norm"); ax.legend(fontsize=7); ax.set_title("SdH FFT in 1/B")
fig.tight_layout(); fig.savefig("hera_scratch/spot_read.png", dpi=110); print("saved hera_scratch/spot_read.png")
