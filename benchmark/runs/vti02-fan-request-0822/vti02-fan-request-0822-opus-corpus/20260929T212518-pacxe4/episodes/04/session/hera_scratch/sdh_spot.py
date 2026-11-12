"""SdH spot-check read on runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12).
Onset via hera.analysis.sdh_onset, tones via sdh_fft; tones read against F_L = (h/4e)n."""
import sys, json, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run, sdh_onset, sdh_fft, luttinger_frequency

CAL = json.load(open("hera_scratch/cal_run5.json"))
SPOT = {6: (+3.2, "electron"), 7: (-1.2, "hole")}

fig, AX = plt.subplots(3, 2, figsize=(13, 11))
out = {}
for k, rid in enumerate([6, 7]):
    n_spot, side = SPOT[rid]
    run = open_run(f"data/{rid}")
    print(f"\n{'='*70}\nrun {rid} — {side}, n = {n_spot:+.2f}e12")
    print(summarize_run(run))
    B = run.col("magnet_field")
    # channel arithmetic per device card: R = (sr1_X/gain_sr1) / (sr0_X/gain_sr0)
    mc = run.meta.get("measurement_config", run.meta)
    v = run.col("sr1_X"); i = run.col("sr0_X")
    g1 = 1.0; g0 = -1e6
    R = (v / g1) / (i / g0)
    order = np.argsort(B)
    B, R = B[order], R[order]
    I_bias = np.nanmedian(np.abs(run.col("sr0_X") / g0))
    sens = 50e-6
    print(f"B {B.min():.3f}..{B.max():.3f} T, {len(B)} pts; R {np.nanmin(R):.1f}..{np.nanmax(R):.1f} Ohm; "
          f"I_bias {I_bias*1e9:.3f} nA; R_fullscale {sens/I_bias:.0f} Ohm; T {np.nanmin(run.col('T_sample')):.3f}-{np.nanmax(run.col('T_sample')):.3f} K")
    F_L = float(luttinger_frequency(abs(n_spot)))
    print(f"F_L = (h/4e)|n| = {F_L:.2f} T")

    try:
        on = sdh_onset(R, B, r_full_scale=sens / I_bias)
        print(on.summary())
        out[rid] = dict(onset_b=on.onset_b, onset_freq=on.onset_freq, clip_high_b=on.clip_high_b,
                        tones=[dict(freq=t.freq, onset_b=t.onset_b, censored=t.censored, marginal=t.marginal,
                                    n_periods=t.n_periods, harmonic_of=t.harmonic_of) for t in on.tones])
    except Exception as e:
        print(f"sdh_onset FAILED: {type(e).__name__}: {e}")
        on = None
        out[rid] = dict(error=f"{type(e).__name__}: {e}")

    # raw + background-subtracted
    ax = AX[0, k]; ax.plot(B, R, lw=0.7)
    ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx (Ohm)"); ax.set_title(f"run {rid} raw — {side}, n={n_spot:+.2f}e12")
    cut = on.onset_b if on else 1.0
    m = B >= cut
    bg = np.polyval(np.polyfit(B[m], R[m], 5), B[m])
    ax2 = AX[1, k]; ax2.plot(1 / B[m], R[m] - bg, lw=0.7)
    ax2.set_xlabel("1/B (1/T)"); ax2.set_ylabel("dRxx (Ohm)"); ax2.set_title(f"bg-subtracted (deg 5), B>{cut:.2f} T")

    # FFT at a few cutoffs
    ax3 = AX[2, k]
    for cutoff in sorted({round(cut, 2), 1.5, 2.5, 4.0}):
        if cutoff >= B.max() - 0.5: continue
        f, spec = sdh_fft(R[:, None], B, b_range=(cutoff, B.max()), bg_degree=5)
        s = spec[0]
        ax3.plot(f, s, lw=0.9, label=f"cut {cutoff:.2f} T")
        pk = [j for j in range(2, len(f) - 2) if s[j] == max(s[j - 2:j + 3]) and s[j] > np.percentile(s, 80)]
        pk = sorted(pk, key=lambda j: -s[j])[:6]
        dF = 1 / (1 / cutoff - 1 / B.max())
        print(f"  FFT cut {cutoff:.2f}-{B.max():.2f} T (dF={dF:.2f} T): peaks " +
              ", ".join(f"{f[j]:.1f}T({s[j]:.1f}, {f[j]/F_L:.2f}FL)" for j in pk))
    ax3.axvline(F_L, color="r", ls="--", lw=1, label=f"F_L={F_L:.1f} T")
    for frac, lbl in ((0.72, "ABAB .72"), (0.28, "ABAB .28")):
        ax3.axvline(frac * F_L, color="c", ls=":", lw=1, label=f"{lbl}={frac*F_L:.1f}T")
    ax3.set_xlim(0, 1.6 * F_L); ax3.set_xlabel("F (T)"); ax3.set_ylabel("|FFT| (log)")
    ax3.legend(fontsize=6); ax3.set_title(f"run {rid} 1/B FFT")

fig.tight_layout(); fig.savefig("hera_scratch/sdh_spot.png", dpi=110)
json.dump(out, open("hera_scratch/sdh_spot.json", "w"), indent=1, default=float)
print("\nwrote hera_scratch/sdh_spot.png + .json")
