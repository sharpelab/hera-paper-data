"""SdH spot checks runs 6 (electron n=+3.2e12, 0->10 T) and 7 (hole n=-1.2e12, 10->0.3 T): raw R(B), onset/tones, FFT in 1/B."""
import sys, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, sdh_fft, sdh_onset, SdhOnsetError, luttinger_frequency
e_ = 1.602176634e-19; h_ = 6.62607015e-34
fig, ax = plt.subplots(3, 2, figsize=(13, 11))
for j, (rid, n12) in enumerate([(6, 3.2), (7, -1.2)]):
    r = open_run(f"data/{rid}"); ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); I = r.col("sr0_X") / ch["sr0"].gain; R = np.abs((r.col("sr1_X") / ch["sr1"].gain) / I)
    o = np.argsort(B); B, R, I = B[o], R[o], I[o]
    T = r.col("T_sample")
    FL = luttinger_frequency(abs(n12) * 1e16)
    print(f"\n=== run {rid}: n = {n12:+.2f}e12, F_L = {FL:.1f} T; B {B.min():.2f}..{B.max():.2f} ({len(B)} pts); R {R.min():.1f}..{R.max():.0f} Ohm; "
          f"I {I.min()*1e9:.2f}..{I.max()*1e9:.2f} nA; T {T.min():.3f}..{T.max():.3f} K; interrupted={r.interrupted}")
    nu = abs(n12) * 1e16 * h_ / (e_ * B)
    ax[0, j].plot(B, R, "-", lw=0.8); ax[0, j].set_xlabel("B (T)"); ax[0, j].set_ylabel("|Rxx| (Ohm)"); ax[0, j].set_title(f"run {rid}: n = {n12:+.1f}e12, D = 0 (raw)")
    # local extrema (smoothed) above 1 T with filling factors
    from scipy.ndimage import gaussian_filter1d
    from scipy.signal import find_peaks
    m = B > 1.0; Bs, Rs = B[m], gaussian_filter1d(R[m], 1.5)
    mins, _ = find_peaks(-Rs, prominence=5); maxs, _ = find_peaks(Rs, prominence=5)
    print(" Rxx minima (B, nu, R):", ", ".join(f"({Bs[k]:.2f}, {abs(n12)*1e16*h_/(e_*Bs[k]):.1f}, {Rs[k]:.0f})" for k in mins))
    print(" Rxx maxima (B, nu, R):", ", ".join(f"({Bs[k]:.2f}, {abs(n12)*1e16*h_/(e_*Bs[k]):.1f}, {Rs[k]:.0f})" for k in maxs))
    for k in mins: ax[0, j].annotate(f"{abs(n12)*1e16*h_/(e_*Bs[k]):.1f}", (Bs[k], Rs[k]), fontsize=7, color="r")
    # sdh_onset
    try:
        so = sdh_onset(R, B, r_full_scale=50e-6 / 10e-9, b_lo=1.0)
        print(so.summary())
    except SdhOnsetError as ex:
        print(" sdh_onset:", ex)
    # FFT in 1/B over a few windows
    for (blo, bhi), c in [((1.5, 10.0), "C0"), ((3.0, 10.0), "C1"), ((5.0, 10.0), "C2")]:
        try:
            f, sp = sdh_fft(R[:, None], B, b_range=(blo, bhi), nfft=4096, bg_degree=5, log=False)
            sp = sp[0]; sel = (f > 2) & (f < 80)
            pk, _ = find_peaks(sp[sel], prominence=0.1 * sp[sel].max())
            fp = f[sel][pk]; ap = sp[sel][pk]; o2 = np.argsort(-ap)[:5]
            print(f" FFT {blo}-{bhi} T: peaks (T, amp): " + ", ".join(f"({fp[i]:.1f}, {ap[i]:.2g})" for i in o2))
            ax[1, j].plot(f[sel], sp[sel] / sp[sel].max(), c, lw=0.8, label=f"{blo}-{bhi} T")
        except Exception as ex:
            print(f" FFT {blo}-{bhi}: {ex}")
    ax[1, j].axvline(FL, color="k", ls=":", label=f"F_L = {FL:.1f} T"); ax[1, j].legend(fontsize=7); ax[1, j].set_xlabel("F (T)"); ax[1, j].set_ylabel("|FFT| (norm)")
    ax[1, j].set_title("SdH FFT in 1/B (poly5 bg removed in B)")
    # detrended R vs 1/B
    m = B > 1.5; p = np.polyfit(B[m], R[m], 5); ax[2, j].plot(1 / B[m], R[m] - np.polyval(p, B[m]), lw=0.8)
    ax[2, j].set_xlabel("1/B (1/T)"); ax[2, j].set_ylabel("dR (Ohm)"); ax[2, j].set_title("detrended, B > 1.5 T")
fig.tight_layout(); fig.savefig("hera_scratch/sdh_spots_6_7.png", dpi=110); print("saved hera_scratch/sdh_spots_6_7.png")
