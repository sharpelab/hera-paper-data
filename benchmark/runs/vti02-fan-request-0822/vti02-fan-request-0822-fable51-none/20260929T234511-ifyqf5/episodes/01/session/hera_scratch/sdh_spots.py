"""Scratch: SdH read of spot checks run 6 (electron, n=+3.2e12) and run 7 (hole, n=-1.2e12)."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_fft, sdh_onset, SdhOnsetError, luttinger_frequency

def load(i):
    r = open_run(f"data/{i}")
    B = r.col("magnet_field"); I = r.col("sr0_X")/(-1e6); R = r.col("sr1_X")/I
    o = np.argsort(B); return B[o], R[o], r

fig, axs = plt.subplots(3, 2, figsize=(14, 12))
for k, (rid, n12) in enumerate([(6, 3.2), (7, -1.2)]):
    B, R, r = load(rid)
    FL = luttinger_frequency(abs(n12)*1e16)
    print(f"\n=== run {rid}: n = {n12:+.2f}e12, F_L (single FS, g=4) = {FL:.2f} T; pts {len(B)}, B {B.min():.2f}-{B.max():.2f}")
    axs[0, k].plot(B, R, lw=0.7); axs[0, k].set_title(f"run {rid} raw Rxx, n={n12:+.1f}e12 D=0"); axs[0, k].set_xlabel("B (T)"); axs[0, k].set_ylabel("Rxx (Ohm)")
    m = B > 0.29
    axs[1, k].plot(1/B[m], R[m], lw=0.7); axs[1, k].set_xlabel("1/B (1/T)"); axs[1, k].set_xlim(0, 1/1.0)
    # onset
    try:
        on = sdh_onset(R, B, r_full_scale=50e-6/10e-9)
        print(on.summary())
    except SdhOnsetError as e:
        print("sdh_onset failed:", e)
    # FFT in windows
    for (blo, bhi), c in [((1.0, 4.0), "C0"), ((1.5, 6.0), "C1"), ((2.0, 10.0), "C2"), ((4.0, 10.0), "C3")]:
        mm = (B >= blo) & (B <= bhi)
        if mm.sum() < 20: continue
        f, sp = sdh_fft(R[mm][:, None], B[mm], bg_degree=4, log=False, nfft=2048)
        sp = sp[0]; sel = (f > 1) & (f < 80)
        pk = f[sel][np.argsort(sp[sel])[::-1][:6]]
        print(f"  FFT window {blo}-{bhi} T: top peaks (T): {np.round(np.sort(pk),2)}")
        axs[2, k].plot(f, sp/sp[sel].max(), c, lw=0.8, label=f"{blo}-{bhi} T")
    axs[2, k].axvline(FL, color="k", ls="--", lw=0.8, label=f"F_L={FL:.1f}")
    for frac in (0.25, 0.5, 0.75): axs[2, k].axvline(FL*frac, color="gray", ls=":", lw=0.6)
    axs[2, k].set_xlim(0, 60); axs[2, k].set_xlabel("F (T)"); axs[2, k].legend(fontsize=7)
    # minima positions (candidates for QH) at high B
    from scipy.signal import find_peaks, savgol_filter
    mm = B > 1.0
    Rs = savgol_filter(R[mm], 7, 2)
    mins, _ = find_peaks(-Rs, prominence=max(5, 0.05*Rs.max()))
    Bm = B[mm][mins]
    nu_geo = abs(n12)*1e16*6.62607e-34/(1.602e-19*Bm)
    print("  Rxx minima (B, R, nu_geo-cal):", [(round(b,2), round(float(v),1), round(float(nu),1)) for b, v, nu in zip(Bm, Rs[mins], nu_geo) if b > 1.5])
    print("  Rxx maxima B>4 T:", np.round(B[mm][find_peaks(Rs, prominence=max(10, 0.1*Rs.max()))[0]], 2))
fig.tight_layout(); fig.savefig("hera_scratch/sdh_spots.png", dpi=110)
print("saved hera_scratch/sdh_spots.png")
