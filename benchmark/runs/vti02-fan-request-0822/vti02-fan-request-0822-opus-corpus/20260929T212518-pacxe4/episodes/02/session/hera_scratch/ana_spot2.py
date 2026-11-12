"""Runs 6 & 7 — SdH spot checks, corrected read (F_L in m^-2, finer FFT, local-max peaks)."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, luttinger_frequency, SdhOnsetError

I_BIAS = 1.0 / 100e6
R_FS = 50e-6 / I_BIAS
SPOTS = {6: ("electron", +3.2), 7: ("hole", -1.2)}


def peaks(f, s, fmin=2.0, top=8):
    k = (f > fmin)
    ff, ss = f[k], s[k]
    loc = [(ff[i], ss[i]) for i in range(1, len(ff) - 1)
           if ss[i] > ss[i - 1] and ss[i] >= ss[i + 1]]
    loc.sort(key=lambda t: -t[1])
    return sorted(loc[:top])


fig, axes = plt.subplots(2, 3, figsize=(16, 8))
for row, (fid, (side, n12)) in enumerate(SPOTS.items()):
    run = open_run(f"data/{fid}")
    B = np.asarray(run.col("magnet_field"), float)
    R = np.asarray(run.col("sr1_X"), float) / I_BIAS
    o = np.argsort(B); B, R = B[o], R[o]
    F_L = float(luttinger_frequency(abs(n12) * 1e16))   # n in m^-2
    print(f"\n{'='*72}\nrun {fid} — {side}  n = {n12:+.2f}e12 cm^-2   F_L = {F_L:.2f} T")
    print(f"  R(B<0.1T) = {R[B < 0.1].mean() if (B<0.1).any() else float('nan'):.1f} Ohm; "
          f"R(0.3T) = {R[np.argmin(abs(B-0.3))]:.1f}; R(10T) = {R[-1]:.1f}; "
          f"max {R.max():.0f} = {100*R.max()/R_FS:.1f}% FS")

    on = sdh_onset(R, B, b_lo=max(0.3, B.min()), r_full_scale=R_FS)
    b_hi = on.clip_high_b or B.max()
    print(f"  onset_b = {on.onset_b:.3f} T, clip_high_b = {on.clip_high_b}")

    ax = axes[row, 0]
    ax.plot(B, R, lw=0.7)
    ax.axvline(on.onset_b, color="g", ls="--", lw=0.8, label=f"onset {on.onset_b:.2f} T")
    ax.set(xlabel="B (T)", ylabel=r"$R_{xx}$ ($\Omega$)",
           title=f"run {fid} raw — {side} n={n12:+.1f}e12, D=0")
    ax.legend(fontsize=7)

    # detrend in B over the analysis window, view in 1/B
    m = (B >= on.onset_b) & (B <= b_hi)
    dR = R[m] - np.polyval(np.polyfit(B[m], R[m], 5), B[m])
    ax = axes[row, 1]
    ax.plot(1.0 / B[m], dR, lw=0.8)
    ax.set(xlabel="1/B (1/T)", ylabel=r"$\Delta R_{xx}$ ($\Omega$)",
           title=f"run {fid} detrended (deg5 in B), {on.onset_b:.2f}-{b_hi:.1f} T")

    ax = axes[row, 2]
    for cut, col in ((round(on.onset_b, 2), "C0"), (1.5, "C1"), (3.0, "C2")):
        if cut >= b_hi - 1:
            continue
        f, spec = sdh_fft(R[:, None], B, b_range=(cut, b_hi), bg_degree=5,
                          nfft=8192, log=False)
        s = spec[0]
        ax.plot(f, s / s.max(), lw=0.9, color=col, label=f"cut {cut} T")
        dF = 1.0 / (1.0 / cut - 1.0 / b_hi)
        pk = peaks(f, s)
        print(f"  FFT {cut:.2f}-{b_hi:.1f} T  dF={dF:.2f} T:  "
              + ", ".join(f"{p:.1f}T({a/s.max():.2f})" for p, a in pk))
    ax.axvline(F_L, color="k", ls="--", lw=1.2, label=f"$F_L$={F_L:.1f}")
    ax.axvline(0.724 * F_L, color="g", ls=":", lw=1.0, label="0.72/0.28 $F_L$")
    ax.axvline(0.276 * F_L, color="g", ls=":", lw=1.0)
    ax.set(xlabel="F (T)", ylabel="norm amp", xlim=(0, 1.5 * F_L),
           title=f"run {fid} 1/B FFT")
    ax.legend(fontsize=7)

    print("  --- design numbers ---")
    print(f"   Nyquist: d(1/B) <= 1/(2F_L) = {1/(2*F_L):.5f} (prefer {1/(3*F_L):.5f}) 1/T")
    for bm in (6.0, 8.0, 10.0):
        print(f"   dF(onset {on.onset_b:.2f} -> {bm:.0f} T) = "
              f"{1.0/(1.0/on.onset_b - 1.0/bm):.2f} T")

plt.tight_layout(); plt.savefig("hera_scratch/spot_checks2.png", dpi=110)
print("\nwrote hera_scratch/spot_checks2.png")
