# SdH spot-check analysis: run 6 (electron, n=+3.2e12, B 0->10 T) and run 7 (hole, n=-1.2e12, B 10->0.3 T)
# per sdh-spot-check.md Verify + tetralayer-stacking-fs-count.md step 3/4 handoff.
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run, sdh_onset, sdh_fft, luttinger_frequency, SdhOnsetError

BASE = "/home/hera/measurements/zack/20260822-vti-02/data"

def analyze(fid, n_e12, label, sens=50e-6, i_bias=10e-9):
    run = open_run(f"{BASE}/{fid}")
    print(f"\n================ run {fid} — {label} (n = {n_e12:+.2f}e12) ================")
    print(summarize_run(run))
    B = run.col("magnet_field")
    X = run.col("sr1_X")
    gain = 1.0
    R = (X / gain) / i_bias
    # sort ascending in B (run 7 descends)
    idx = np.argsort(B)
    B, R = B[idx], R[idx]
    T = run.col("T_sample")[idx]
    print(f"interrupted: {run.interrupted}; B {B.min():.3f}..{B.max():.3f} T, {len(B)} pts; "
          f"T {T.min():.3f}-{T.max():.3f} K; R(Bmin)={R[0]:.1f} Ohm, R(Bmax)={R[-1]:.1f} Ohm, Rmax={R.max():.1f}")
    FL = luttinger_frequency(n_e12) if hasattr(np, "__x__") else None  # placeholder, computed below
    # F_L = (h/4e) n
    h_over_4e = 6.62607015e-34 / (4 * 1.602176634e-19)
    F_L = h_over_4e * abs(n_e12) * 1e16  # n in 1e12 cm^-2 = 1e16 m^-2
    print(f"F_L = {F_L:.1f} T")
    try:
        on = sdh_onset(R, B, r_full_scale=sens / i_bias)
        print(on.summary())
        onset = on.onset_b
    except SdhOnsetError as e:
        print(f"SdhOnsetError: {e}")
        on, onset = None, None
    # FFT with a couple of cutoffs (stability)
    fig, ax = plt.subplots(3, 1, figsize=(9, 10))
    ax[0].plot(B, R, lw=0.6)
    ax[0].set(xlabel="B (T)", ylabel="Rxx (Ohm)", title=f"run {fid} {label}: raw Rxx(B), n={n_e12:+.2f}e12")
    # background-subtracted view
    cuts = []
    if onset is not None:
        cuts = [onset, max(onset * 1.2, onset + 0.3)]
    else:
        cuts = [1.5, 2.5]
    m = B >= (cuts[0] * 0.8)
    p = np.polyfit(B[m], R[m], 5)
    dR = R[m] - np.polyval(p, B[m])
    ax[1].plot(B[m], dR, lw=0.6)
    ax[1].set(xlabel="B (T)", ylabel="dRxx (Ohm)", title=f"bg-subtracted (deg-5, B>{cuts[0]*0.8:.2f})")
    for c in cuts:
        try:
            freqs, spec = sdh_fft(R[:, None], B, b_range=(c, B.max()), bg_degree=5)
            sp = spec[0]
            sp = sp / sp.max() if sp.max() > 0 else sp
            ax[2].plot(freqs, sp, lw=0.9, label=f"cutoff {c:.2f} T")
        except Exception as e:
            print(f"sdh_fft(cutoff={c:.2f}) failed: {e}")
    ax[2].axvline(F_L, color="k", ls="--", lw=0.8, label=f"F_L={F_L:.1f} T")
    for fr, lab in [(0.72 * F_L, "0.72 F_L"), (0.28 * F_L, "0.28 F_L")]:
        ax[2].axvline(fr, color="gray", ls=":", lw=0.8)
        ax[2].text(fr, 0.95, lab, rotation=90, fontsize=7, va="top")
    ax[2].set(xlabel="F (T)", ylabel="norm. FFT amp", xlim=(0, F_L * 1.6),
              title=f"1/B FFT; F_L={F_L:.1f} T")
    ax[2].legend(fontsize=8)
    fig.tight_layout()
    out = f"/home/hera/measurements/zack/20260822-vti-02/hera_scratch/spot_run{fid}.png"
    fig.savefig(out, dpi=110)
    print(f"saved {out}")
    # print top FFT peaks for the widest window
    try:
        freqs, spec = sdh_fft(R[:, None], B, b_range=(cuts[0], B.max()), bg_degree=5)
        sp = spec[0]
        # simple peak pick
        from scipy.signal import find_peaks
        pk, props = find_peaks(sp, height=0.05 * sp.max(), distance=5)
        order = np.argsort(props["peak_heights"])[::-1][:8]
        print("top FFT peaks (F [T], rel amp):")
        for i in order:
            print(f"  {freqs[pk[i]]:8.2f} T   {props['peak_heights'][i]/sp.max():.3f}   (F/F_L = {freqs[pk[i]]/F_L:.3f})")
        if onset is not None:
            dF = 1.0 / (1.0 / onset - 1.0 / B.max())
            print(f"record resolution dF = {dF:.2f} T (onset {onset:.2f} -> {B.max():.1f} T)")
    except Exception as e:
        print(f"peak pick failed: {e}")
    return on

on6 = analyze(6, +3.2, "electron")
on7 = analyze(7, -1.2, "hole")
