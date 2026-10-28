"""First look at spot checks runs 6 (e, n=+3.2e12) and 7 (h, n=-1.2e12): raw R(B), onset, 1/B FFT."""
import numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from hera.analysis import open_run, summarize_run, sdh_onset, sdh_fft, SdhOnsetError, luttinger_frequency
D = Path("data")
fig, axs = plt.subplots(3, 2, figsize=(14, 11))
for j, (rid, n12) in enumerate([(6, 3.2), (7, -1.2)]):
    r = open_run(D / str(rid)); print("=" * 70); print(summarize_run(r)); print("cols:", r.cols)
    B = r.col("magnet_field"); I = r.col("sr0_X") / -1e6; V = r.col("sr1_X") / 1.0
    R = V / I
    o = np.argsort(B); B, R, I = B[o], R[o], I[o]
    print(f"run {rid}: B {B.min():.3f}-{B.max():.3f}, N={len(B)}, R {R.min():.1f}-{R.max():.1f} Ohm, I {I.min()*1e9:.3f}-{I.max()*1e9:.3f} nA")
    T = r.col("T_sample") if "T_sample" in r.cols else None
    if T is not None: print(f"  T_sample {T.min():.3f}-{T.max():.3f} K")
    try:
        FL = luttinger_frequency(n12 * 1e16)
    except Exception as e:
        FL = 4.1357e-15 * abs(n12) * 1e16 / 4; print("  luttinger_frequency err", e)
    print(f"  F_L = {FL:.2f} T")
    axs[0, j].plot(B, R, lw=0.6); axs[0, j].set_title(f"run {rid} raw R(B), n={n12:+.1f}e12"); axs[0, j].set_xlabel("B (T)"); axs[0, j].set_ylabel("Rxx (Ohm)")
    # onset
    try:
        on = sdh_onset(R, B, r_full_scale=50e-6 / 10e-9)
        print(on.summary())
        onset_b = on.onset_b
    except SdhOnsetError as e:
        print("  SdhOnsetError:", e); onset_b = None
    # background-subtracted view: poly deg 5 in B above 1 T
    m = B > 1.0
    p = np.polyfit(B[m], R[m], 5); dR = R[m] - np.polyval(p, B[m])
    axs[1, j].plot(1 / B[m], dR, lw=0.6); axs[1, j].set_xlabel("1/B (1/T)"); axs[1, j].set_ylabel("dR (Ohm), deg-5 bg in B, B>1T"); axs[1, j].set_title("bg-subtracted vs 1/B")
    # FFT for a few windows
    for lo, deg, c in [(1.5, 5, "C0"), (2.5, 5, "C1"), (3.5, 5, "C2"), (2.5, 3, "C3")]:
        try:
            f, S = sdh_fft(R[:, None], B, b_range=(lo, B.max()), bg_degree=deg)
            s = S[0]; s = s / s.max()
            axs[2, j].plot(f, s, c, lw=0.8, label=f"B>{lo} deg{deg}")
            top = np.argsort(s)[::-1]
            # simple local maxima
            from scipy.signal import find_peaks
            pk, _ = find_peaks(s, prominence=0.05)
            pk = sorted(pk, key=lambda k: -s[k])[:6]
            print(f"  FFT B>{lo} deg{deg}: peaks (T, rel) " + ", ".join(f"{f[k]:.1f}({s[k]:.2f})" for k in pk))
        except Exception as e:
            print("  sdh_fft err", lo, deg, e)
    axs[2, j].axvline(FL, color="k", ls="--", lw=0.8, label=f"F_L={FL:.1f}")
    axs[2, j].set_xlim(0, 1.5 * FL); axs[2, j].set_xlabel("F (T)"); axs[2, j].legend(fontsize=7)
fig.tight_layout(); fig.savefig("hera_scratch/spot_first_look.png", dpi=110); print("saved")
