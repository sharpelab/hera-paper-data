# Spot-check read: runs 6 (electron, n=+3.2e12, B 0->10 T) and 7 (hole, n=-1.2e12, B 10->0.3 T)
# sdh-spot-check step 6: raw R(B), sdh_onset, sdh_fft vs F_L, per investigation templates.
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, sdh_onset, sdh_fft, SdhOnsetError

BASE = "/home/hera/measurements/zack/20260822-vti-02/data"

# templates (model F(n) table, quoted in md_spot_e/h from the Step-2 feasibility calc)
TEMPL = {
    6: dict(n=3.2, FL=33.1, abab=(7.5, 25.6), abca=33.1),
    7: dict(n=-1.2, FL=12.4, abab=(5.3, 7.1), abca=12.4),
}

fig, axes = plt.subplots(3, 2, figsize=(13, 11))

for j, rid in enumerate((6, 7)):
    run = open_run(f"{BASE}/{rid}")
    ch = [c for c in resolve_channels(run.meta) if c.cid == "sr1"][0]
    print(f"=== run {rid} ===")
    print("channel:", ch)
    B = run.col("magnet_field")
    order = np.argsort(B)
    B = B[order]
    X = run.col("sr1_X")[order]
    mc = run.meta["measurement_config"]
    amp = run.meta["instruments"]["sr1"]["snapshot"]["parameters"]["amplitude"]["value"]
    ibias = amp / mc["bias_resistor"]
    R = X / ch.gain / ibias
    T = run.col("T_sample")
    print(f"B {B.min():.3f}..{B.max():.3f} T, {len(B)} pts; T {np.nanmin(T):.3f}-{np.nanmax(T):.3f} K")
    print(f"R(B~0.3): {R[np.argmin(np.abs(B-0.3))]:.1f} ohm; R max {R.max():.1f} ohm")
    # full-scale check: sens 50 uV, I_bias from channel
    r_fs = None
    if ibias:
        r_fs = 50e-6 / ibias
        print(f"I_bias {ibias:.3e} A, R full-scale {r_fs:.0f} ohm, max R / FS = {R.max()/r_fs:.2f}")

    # raw
    ax = axes[0, j]
    ax.plot(B, R, lw=0.5)
    ax.set_title(f"run {rid}: raw Rxx(B), n={TEMPL[rid]['n']:+.1f}e12, D=0")
    ax.set_xlabel("B (T)")
    ax.set_ylabel("Rxx (Ohm)")

    # onset
    try:
        on = sdh_onset(R, B, r_full_scale=r_fs)
        print(on.summary())
        onset = on.onset_b
    except SdhOnsetError as e:
        print("SdhOnsetError:", e)
        onset = None

    # FFT: cutoff at/above onset; stability: two cutoffs, two bg degrees
    ax2 = axes[1, j]
    ax3 = axes[2, j]
    # background-subtracted trace for visual onset
    msk = B >= 0.5
    pf = np.polyfit(B[msk], R[msk], 5)
    dR = R[msk] - np.polyval(pf, B[msk])
    ax2.plot(B[msk], dR, lw=0.5)
    ax2.set_title(f"run {rid}: dRxx (deg-5 bg removed)")
    ax2.set_xlabel("B (T)")

    if onset is not None:
        for co, deg, style in ((onset, 5, "-"), (max(onset * 1.3, onset + 0.3), 5, "--"), (onset, 7, ":")):
            f, spec = sdh_fft(R[:, None], B, b_range=(co, B.max()), bg_degree=deg, log=False)
            sp = spec[0] / np.nanmax(spec[0])
            ax3.plot(f, sp, style, lw=1, label=f"cut {co:.2f} T, deg {deg}")
        t = TEMPL[rid]
        ax3.axvline(t["FL"], color="k", lw=1, alpha=0.6)
        ax3.text(t["FL"], 1.0, "F_L", ha="left", va="top")
        for fa in t["abab"]:
            ax3.axvline(fa, color="tab:red", lw=1, alpha=0.5, ls="--")
        ax3.set_xlim(0, t["FL"] * 1.6)
        ax3.set_xlabel("F (T)")
        ax3.set_title(f"run {rid}: FFT in 1/B (F_L={t['FL']} T; red dashes ABAB pair)")
        ax3.legend(fontsize=7)
        # peak table
        f, spec = sdh_fft(R[:, None], B, b_range=(onset, B.max()), bg_degree=5, log=False)
        sp = spec[0]
        # simple local maxima above 10% of max, f > 2 T
        pk = [
            (f[i], sp[i])
            for i in range(2, len(f) - 2)
            if sp[i] == max(sp[max(0, i - 3) : i + 4]) and sp[i] > 0.05 * sp[f > 2].max() and f[i] > 2
        ]
        print("FFT peaks (F [T], rel amp):", [(round(a, 2), round(b / sp[f > 2].max(), 3)) for a, b in pk[:12]])
        if onset:
            print(f"record deltaF = {1.0/(1.0/onset - 1.0/B.max()):.2f} T")
    print()

fig.tight_layout()
fig.savefig("/home/hera/measurements/zack/20260822-vti-02/hera_scratch/spots_read.png", dpi=110)
print("saved spots_read.png")
