"""sdh-spot-check read: runs 6 (e, n=+3.2e12) and 7 (h, n=-1.2e12), D = 0. Raw R(B), then sdh_onset + FFT in 1/B, LL index guesses."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, sdh_onset, sdh_fft, luttinger_frequency, SdhOnsetError
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d

fig, ax = plt.subplots(3, 2, figsize=(14, 11))
for j, (rid, n12) in enumerate(((6, 3.2), (7, -1.2))):
    r = open_run(f"data/{rid}")
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); I = r.col("sr0_X") / ch["sr0"].gain
    R = (r.col("sr1_X") / ch["sr1"].gain) / I
    T = r.col("T_sample")
    o = np.argsort(B); B, R, I, T = B[o], R[o], I[o], T[o]
    FL = luttinger_frequency(abs(n12) * 1e16)
    print(f"\n=== run {rid}: n = {n12:+.1f}e12, F_L = {FL:.1f} T; R {R.min():.1f}..{R.max():.1f} Ohm; I {I.mean()*1e9:.2f} nA; T {T.mean():.3f} K; sign(R) {np.sign(np.median(R))}")
    Rs = np.abs(R)
    ax[0, j].plot(B, Rs, ".-", ms=2, lw=0.7); ax[0, j].set_xlabel("B (T)"); ax[0, j].set_ylabel("|Rxx| (Ohm)"); ax[0, j].set_title(f"run {rid}: n = {n12:+.1f}e12, D = 0 raw")
    # extrema on smoothed trace above 1.5 T
    m = B > 1.5; sm = gaussian_filter1d(Rs[m], 1.5)
    mins, _ = find_peaks(-sm, prominence=5); maxs, _ = find_peaks(sm, prominence=5)
    Bmin, Bmax = B[m][mins], B[m][maxs]
    print("Rxx minima at B =", np.round(Bmin, 2), " -> nu (4 F_L/B) =", np.round(4 * FL / Bmin, 1))
    print("Rxx maxima at B =", np.round(Bmax, 2), " -> nu =", np.round(4 * FL / Bmax, 1))
    ax[0, j].plot(Bmin, Rs[m][mins], "rv", ms=5); ax[0, j].plot(Bmax, Rs[m][maxs], "g^", ms=5)
    # 1/B plot
    ax[1, j].plot(1 / B[m], Rs[m], ".-", ms=2, lw=0.7); ax[1, j].set_xlabel("1/B (1/T)"); ax[1, j].set_ylabel("|Rxx|"); ax[1, j].set_title("vs 1/B (B > 1.5 T)")
    for k in range(1, 40):  # nu = 4k markers for F_L
        x = 4 * k / (4 * FL)
        if 1/10 < x < 1/1.5: ax[1, j].axvline(x, color="gray", lw=0.4, alpha=0.5)
    # onset + FFT
    for bhi in (10.0,):
        try:
            on = sdh_onset(Rs, B, b_hi=bhi, b_lo=1.0, r_full_scale=50e-6 / 10e-9)
            print(on.summary())
        except SdhOnsetError as e:
            print("sdh_onset:", e)
    for lo, hi, col in ((1.5, 10.0, "k"), (1.5, 5.0, "C0"), (3.0, 10.0, "C1")):
        f, sp = sdh_fft(Rs[:, None], B, b_range=(lo, hi), nfft=2048, bg_degree=5, log=False)
        sp = sp[0]; sel = (f > 2) & (f < 120)
        ax[2, j].plot(f[sel], sp[sel] / sp[sel].max(), col, lw=1, label=f"B {lo}-{hi} T")
        pk, _ = find_peaks(sp[sel], prominence=0.1 * sp[sel].max())
        print(f"FFT {lo}-{hi} T peaks (T): {np.round(f[sel][pk], 1)} rel amp {np.round(sp[sel][pk]/sp[sel].max(), 2)}")
    ax[2, j].axvline(FL, color="r", ls="--", lw=1, label=f"F_L = {FL:.1f} T (all carriers, 4-fold)")
    ax[2, j].axvline(FL / 2, color="r", ls=":", lw=1, label="F_L/2 (8-fold)"); ax[2, j].axvline(FL / 4, color="m", ls=":", lw=1, label="F_L/4 (16-fold)")
    ax[2, j].set_xlabel("F (T)"); ax[2, j].set_ylabel("FFT amp (norm)"); ax[2, j].legend(fontsize=7); ax[2, j].set_title("SdH FFT in 1/B (B-poly5 bg removed)")
fig.tight_layout(); fig.savefig("hera_scratch/sdh_spots.png", dpi=100); print("saved hera_scratch/sdh_spots.png")
