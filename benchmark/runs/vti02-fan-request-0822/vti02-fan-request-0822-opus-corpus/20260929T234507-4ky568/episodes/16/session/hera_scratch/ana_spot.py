"""SdH spot checks, runs 6 (electron n=+3.2e12) and 7 (hole n=-1.2e12).
Raw -> background-subtracted -> onset -> FFT vs F_L.  Scratch iteration.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, luttinger_frequency, SdhOnsetError

RUNS = {6: ("electron", +3.20e12), 7: ("hole", -1.20e12)}
I_FS = 50e-6  # sr1 sensitivity 50 uV  -> R_fs = 50uV / I_bias


def load(idx):
    r = open_run(f"data/{idx}")
    B = r.col("magnet_field")
    V = r.col("sr1_X") / 1.0                      # sr1 gain = 1
    I = r.col("sr0_X") / (-1e6)                   # Ithaco gain
    R = V / I
    T = r.col("T_sample")
    itg, ibg = r.col("k_2400_tg_curr"), r.col("k_2400_bg_curr")
    o = np.argsort(B)
    return r, B[o], R[o], T[o], itg[o], ibg[o], I[o], V[o]


fig, axes = plt.subplots(3, 2, figsize=(13, 11))
out = {}
for col, (idx, (side, n_cm2)) in enumerate(RUNS.items()):
    r, B, R, T, itg, ibg, I, V = load(idx)
    n_m2 = abs(n_cm2) * 1e4
    F_L = float(luttinger_frequency(n_m2))
    I_bias = np.median(np.abs(I))
    R_fs = I_FS / I_bias
    print(f"\n===== run {idx} ({side}) n={n_cm2:.2e} cm^-2  F_L={F_L:.1f} T")
    print(f"  B {B.min():.3f}..{B.max():.3f} T, N={len(B)}")
    print(f"  I_bias(med) = {I_bias*1e9:.3f} nA ; R_fs = {R_fs:.0f} Ohm")
    print(f"  R: min {np.nanmin(R):.1f}  med {np.nanmedian(R):.1f}  max {np.nanmax(R):.1f} Ohm"
          f"  (max/R_fs = {np.nanmax(R)/R_fs*100:.1f}% FS)")
    print(f"  T_sample {np.nanmin(T):.3f}..{np.nanmax(T):.3f} K")
    print(f"  gate curr |tg| max {np.nanmax(np.abs(itg))*1e12:.0f} pA, "
          f"|bg| max {np.nanmax(np.abs(ibg))*1e12:.0f} pA")

    ax = axes[0, col]
    ax.plot(B, R, lw=0.7)
    ax.axhline(R_fs, color="r", ls=":", label=f"full scale {R_fs:.0f} $\\Omega$")
    ax.set(xlabel="B (T)", ylabel=r"$R_{xx}$ ($\Omega$)",
           title=f"run {idx} raw — {side}, n={n_cm2:.2e} cm$^{{-2}}$")
    ax.legend(fontsize=7)

    # background-subtracted, in 1/B
    m = B > 0.25
    Bb, Rb = B[m], R[m]
    bg = np.polyval(np.polyfit(Bb, Rb, 5), Bb)
    dR = Rb - bg
    ax = axes[1, col]
    ax.plot(1.0 / Bb, dR, lw=0.7)
    ax.set(xlabel="1/B (1/T)", ylabel=r"$\Delta R_{xx}$ ($\Omega$)",
           title=f"run {idx} bg-subtracted (deg 5, B>0.25 T)")

    # onset
    try:
        on = sdh_onset(Rb, Bb, r_full_scale=R_fs)
        print(on.summary())
        out[idx] = dict(onset_b=on.onset_b, clip=on.clip_high_b,
                        tones=[(t.freq, t.onset_b, t.censored, t.marginal,
                                t.harmonic_of) for t in on.tones])
    except SdhOnsetError as e:
        print(f"  sdh_onset FAILED: {e}")
        out[idx] = dict(error=str(e))

    # FFT over a few cutoffs
    ax = axes[2, col]
    for cutoff in (0.5, 1.0, 1.5, 2.5):
        if cutoff >= Bb.max():
            continue
        f, spec = sdh_fft(Rb[:, None], Bb, b_range=(cutoff, Bb.max()),
                          bg_degree=5, nfft=4096, log=False)
        s = spec[0]
        ax.plot(f, s / np.nanmax(s), lw=0.9, label=f"B>{cutoff} T")
    ax.axvline(F_L, color="k", ls="--", label=f"$F_L$={F_L:.1f} T")
    for frac, lbl in ((0.72, "0.72"), (0.28, "0.28")):
        ax.axvline(frac * F_L, color="g", ls=":", lw=0.9)
    ax.set(xlabel="F (T)", ylabel="|FFT| (norm)", xlim=(0, 1.6 * F_L),
           title=f"run {idx} FFT in 1/B (green: ABAB 0.72/0.28 $F_L$)")
    ax.legend(fontsize=7)

plt.tight_layout()
plt.savefig("hera_scratch/spot_runs67.png", dpi=120)
print("\nwrote hera_scratch/spot_runs67.png")
print(out)
