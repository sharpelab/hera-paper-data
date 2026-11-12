"""SdH spot checks: runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12). Raw + onset + FFT."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, luttinger_frequency

RUNS = {6: ("electron", +3.2), 7: ("hole", -1.2)}
fig, axes = plt.subplots(2, 3, figsize=(16, 8))

for k, (rid, (side, n12)) in enumerate(RUNS.items()):
    run = open_run(f"data/{rid}")
    inst = run.meta.get("instruments", {})
    amp = inst["sr1"]["snapshot"]["parameters"]["amplitude"]["value"]
    sens = inst["sr1"]["snapshot"]["parameters"]["sensitivity"]["value"]
    tau = inst["sr1"]["snapshot"]["parameters"]["time_constant"]["value"]
    slope = inst["sr1"]["snapshot"]["parameters"]["filter_slope"]["value"]
    Rbias = run.meta["measurement_config"]["bias_resistor"]
    I = amp / Rbias
    B = run.col("magnet_field")
    R = run.col("sr1_X") / 1.0 / I          # sr1 gain = 1 (device card)
    T = run.col("T_sample")
    o = np.argsort(B); B, R = B[o], R[o]
    r_fs = sens / I
    print(f"===== run {rid} ({side}, n={n12:+.2f}e12) =====")
    print(f"  drive {amp} V / {Rbias:.0e} = I_bias {I*1e9:.2f} nA; sens {sens} V -> R_fs {r_fs:.0f} Ohm; tau {tau} s, slope {slope}")
    print(f"  B {B.min():.3f}-{B.max():.3f} T, {len(B)} pts; T {np.nanmin(T):.3f}-{np.nanmax(T):.3f} K")
    print(f"  R: {R.min():.1f} .. {R.max():.1f} Ohm (B=0/low {R[0]:.1f}); max/R_fs = {R.max()/r_fs:.3f}")
    F_L = luttinger_frequency(abs(n12) * 1e12 * 1e4)   # cm^-2 -> m^-2
    print(f"  F_L = {F_L:.2f} T")

    ax = axes[k, 0]; ax.plot(B, R, lw=0.7); ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx (Ohm)")
    ax.set_title(f"run {rid} raw {side} n={n12:+.1f}e12")

    # onset
    try:
        on = sdh_onset(R, B, r_full_scale=r_fs)
        print(on.summary())
        print(f"  onset_b = {on.onset_b:.3f} T ; clip_high_b = {on.clip_high_b}")
    except Exception as e:
        on = None
        print("  sdh_onset FAILED:", type(e).__name__, e)

    cutoff = max(on.onset_b, 0.3) if on is not None else 1.0
    b_hi = on.clip_high_b if (on is not None and on.clip_high_b) else B.max()
    freqs, spec = sdh_fft(R[:, None], B, b_range=(cutoff, b_hi), bg_degree=5)
    s = spec[0]
    ax = axes[k, 1]
    ax.plot(freqs, s, lw=1.0)
    ax.axvline(F_L, color="r", ls="--", label=f"F_L={F_L:.1f} T")
    ax.axvline(0.72 * F_L, color="g", ls=":", label="0.72 F_L")
    ax.axvline(0.28 * F_L, color="b", ls=":", label="0.28 F_L")
    ax.set_xlim(0, 2.2 * F_L); ax.legend(fontsize=7)
    ax.set_title(f"run {rid} FFT, cutoff {cutoff:.2f}-{b_hi:.2f} T")
    ax.set_xlabel("F (T)")

    # background-subtracted trace vs 1/B
    from numpy.polynomial import polynomial as P
    m = (B >= cutoff) & (B <= b_hi)
    c = np.polyfit(B[m], R[m], 5)
    dR = R[m] - np.polyval(c, B[m])
    ax = axes[k, 2]; ax.plot(1 / B[m], dR, lw=0.7)
    ax.set_xlabel("1/B (1/T)"); ax.set_ylabel("dRxx (Ohm)"); ax.set_title(f"run {rid} bg-subtracted")

    # peak list
    from scipy.signal import find_peaks
    pk, _ = find_peaks(s, height=0.12 * s.max())
    print("  peaks (F [T], amp, F/F_L):")
    for p in sorted(pk, key=lambda i: -s[i])[:8]:
        print(f"    {freqs[p]:7.2f}  {s[p]:8.3f}  {freqs[p]/F_L:6.3f}")
    print(f"  dF resolution = {1/(1/cutoff - 1/b_hi):.2f} T")

fig.tight_layout(); fig.savefig("hera_scratch/spot_runs67.png", dpi=110)
print("saved hera_scratch/spot_runs67.png")
