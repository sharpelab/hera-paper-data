"""Runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12) — sdh-spot-check read.

Raw first, then onset + FFT. Feeds the landau-fan design: B_lo (measured onset),
Delta(1/B), which side is cleaner, tone frequencies vs F_L.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run, sdh_onset, sdh_fft, luttinger_frequency

DIR = "/home/hera/measurements/zack/20260822-vti-02/data"
SPOTS = {6: ("electron", +3.2), 7: ("hole", -1.2)}

out = {}
fig, axes = plt.subplots(3, 2, figsize=(13, 12))

for j, (rid, (side, n12)) in enumerate(SPOTS.items()):
    run = open_run(f"{DIR}/{rid}")
    print(f"########## run {rid} — {side}, n = {n12:+.2f}e12 ##########")
    print(summarize_run(run))
    mc = run.meta["measurement_config"]
    B = run.col("magnet_field")
    V = run.col("sr1_X") / 1.0                      # sr1_gain = 1 (unity)
    I = run.col("sr0_X") / mc["sr0_gain"]           # -1e6 preamp
    R = V / I
    T = run.col("T_sample")
    itg, ibg = run.col("k_2400_tg_curr"), run.col("k_2400_bg_curr")
    keep = B > 0.05            # 1/B is taken downstream; B = 0 poisons sdh_onset's scans
    B, R, T, itg, ibg, I = (a[keep] for a in (B, R, T, itg, ibg, I))
    order = np.argsort(B)
    B, R, T = B[order], R[order], T[order]
    I_bias = np.median(np.abs(I))
    print(f"N = {len(B)}, B {B.min():.3f} -> {B.max():.3f} T, "
          f"dB median {np.median(np.diff(B))*1e3:.1f} mT")
    print(f"R: {np.abs(R).min():.1f} .. {np.abs(R).max():.1f} Ohm (B=0 end {np.abs(R)[0]:.1f}); "
          f"I_bias = {I_bias*1e9:.3f} nA")
    print(f"T_sample {T.min():.3f}-{T.max():.3f} K; |I_tg|max {np.abs(itg).max():.2e}, "
          f"|I_bg|max {np.abs(ibg).max():.2e} A")

    n_si = abs(n12) * 1e12 * 1e4                    # cm^-2 -> m^-2
    F_L = float(luttinger_frequency(n_si))
    print(f"F_L = (h/4e)*n = {F_L:.2f} T")

    # --- onset (measured, not eyeballed) ---
    r_fs = 50e-6 / 1.0 / I_bias                     # sensitivity / gain / I_bias
    try:
        on = sdh_onset(np.abs(R), B, r_full_scale=r_fs, b_lo=float(B.min()))
        print(on.summary())
        onset_b, clip = on.onset_b, on.clip_high_b
    except Exception as e:
        print(f"sdh_onset FAILED: {type(e).__name__}: {e}")
        on, onset_b, clip = None, None, None

    # --- FFT over the usable record ---
    b_hi = float(clip) if clip else float(B.max())
    cut = onset_b if onset_b else 1.5
    freqs, spec = sdh_fft(np.abs(R)[:, None], B, b_range=(cut, b_hi), bg_degree=5)
    sp = spec[0]
    dF = 1.0 / (1.0 / cut - 1.0 / b_hi)
    print(f"FFT window {cut:.2f}-{b_hi:.2f} T  ->  dF = {dF:.2f} T")
    # top peaks
    from scipy.signal import find_peaks
    pk, _ = find_peaks(sp)
    pk = pk[np.argsort(sp[pk])[::-1]][:8]
    print("  peaks (T, rel amp, f/F_L):")
    for p in sorted(pk, key=lambda p: freqs[p]):
        print(f"    {freqs[p]:8.2f}  {sp[p]/sp[pk].max():6.3f}   {freqs[p]/F_L:6.3f}")

    out[rid] = dict(side=side, n12=n12, F_L=F_L, onset=onset_b, clip=clip,
                    dF=dF, B=B, R=R, freqs=freqs, sp=sp, r_fs=r_fs, I_bias=I_bias)

    # --- plots: raw, background-subtracted vs 1/B, FFT ---
    ax = axes[0, j]
    ax.plot(B, np.abs(R), lw=0.8)
    ax.axhline(r_fs, ls=":", c="r", label=f"full scale {r_fs:.0f} $\\Omega$")
    if onset_b:
        ax.axvline(onset_b, ls="--", c="g", label=f"onset {onset_b:.2f} T")
    ax.set(xlabel="B (T)", ylabel="|R| ($\\Omega$)",
           title=f"run {rid} raw — {side}, n={n12:+.2f}e12")
    ax.legend(fontsize=7)

    ax = axes[1, j]
    m = (B >= cut) & (B <= b_hi)
    bg = np.polyval(np.polyfit(B[m], np.abs(R)[m], 5), B[m])
    ax.plot(1.0 / B[m], np.abs(R)[m] - bg, lw=0.8)
    ax.set(xlabel="1/B (1/T)", ylabel="$\\Delta R$ ($\\Omega$)",
           title=f"run {rid} bg-subtracted (deg 5, {cut:.2f}-{b_hi:.2f} T)")

    ax = axes[2, j]
    ax.plot(freqs, sp, lw=1.0)
    ax.axvline(F_L, ls="--", c="k", label=f"$F_L$ = {F_L:.1f} T")
    for frac, lab in ((0.72, "0.72"), (0.28, "0.28")):
        ax.axvline(frac * F_L, ls=":", c="C3", label=f"ABAB {lab}$F_L$")
    ax.set(xlabel="F (T)", ylabel="|FFT| (a.u.)", xlim=(0, max(1.6 * F_L, 20)),
           title=f"run {rid} FFT in 1/B  ($\\delta F$ = {dF:.1f} T)")
    ax.legend(fontsize=7)

plt.tight_layout()
plt.savefig("/home/hera/measurements/zack/20260822-vti-02/hera_scratch/spot_67.png", dpi=110)
print("\nwrote spot_67.png")

# --- fan design arithmetic ---
print("\n===== fan design numbers =====")
for rid, d in out.items():
    print(f"run {rid} ({d['side']}): onset {d['onset']}, clip {d['clip']}, dF {d['dF']:.2f} T, "
          f"F_L {d['F_L']:.2f} T, R full scale {d['r_fs']:.0f} Ohm")
