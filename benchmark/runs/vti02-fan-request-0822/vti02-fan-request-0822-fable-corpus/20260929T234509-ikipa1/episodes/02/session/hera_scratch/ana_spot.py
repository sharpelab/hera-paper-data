# Spot-check analysis: runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12)
# Raw MR + sdh_onset + sdh_fft, tones vs F_L and the fs_count model.
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import (open_run, summarize_run, sdh_onset, sdh_fft,
                           luttinger_frequency, resolve_channels, SdhOnsetError)

BASE = "/home/hera/measurements/zack/20260822-vti-02/data"
OUT = "/home/hera/measurements/zack/20260822-vti-02/hera_scratch"

fig, axes = plt.subplots(2, 3, figsize=(15, 8))

for row, (rid, nval, tag) in enumerate(((6, +3.2e12, "electron"), (7, -1.2e12, "hole"))):
    run = open_run(f"{BASE}/{rid}")
    print("=" * 70)
    print(f"RUN {rid} ({tag}, n = {nval:+.2e} cm^-2)")
    B = run.col("magnet_field")
    chans = resolve_channels(run.meta)
    print("channels:", [(c.cid, c.gain, c.label, c.is_current) for c in chans])
    g = {c.cid: c.gain for c in chans}
    I = run.col("sr0_X") / g["sr0"]          # measured drain current, A
    V = run.col("sr1_X") / g["sr1"]          # Rxx voltage, V
    R = V / I
    # sort ascending in B (run 7 descends)
    idx = np.argsort(B)
    B, R, I = B[idx], R[idx], I[idx]
    Ib = np.median(np.abs(I))
    print(f"I_bias measured (median |I|): {Ib*1e9:.3f} nA;  R(B~0) = {np.median(np.abs(R[:10])):.1f} ohm; R range {np.nanmin(R):.1f}..{np.nanmax(R):.1f}")
    F_L = luttinger_frequency(abs(nval) * 1e4)  # cm^-2 -> m^-2
    print(f"F_L = {float(F_L):.2f} T")

    r_fs = 50e-6 / Ib   # sr1 sensitivity 50 uV fixed for both runs
    try:
        on = sdh_onset(R, B, r_full_scale=r_fs)
        print(on.summary())
        onset = on.onset_b
    except SdhOnsetError as e:
        print("SdhOnsetError:", e)
        on, onset = None, None

    # raw MR
    ax = axes[row, 0]
    ax.plot(B, R, lw=0.6)
    ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx (ohm)")
    ax.set_title(f"run {rid} {tag}: raw Rxx(B)")
    if onset:
        ax.axvline(onset, color="r", ls="--", lw=0.8)

    # background-subtracted dRxx
    ax = axes[row, 1]
    sel = B > 0.5
    p = np.polyfit(B[sel], R[sel], 5)
    dR = R[sel] - np.polyval(p, B[sel])
    ax.plot(B[sel], dR, lw=0.6)
    ax.set_xlabel("B (T)"); ax.set_ylabel("dRxx (ohm)")
    ax.set_title("bg-subtracted (deg 5)")

    # FFT above onset
    ax = axes[row, 2]
    if onset:
        cutoffs = [onset, onset * 1.15, onset * 1.3]
    else:
        cutoffs = [1.5, 2.0, 2.5]
    for co in cutoffs:
        try:
            f, spec = sdh_fft(R[:, None], B, b_range=(co, float(B.max())), log=False)
            s = spec[0] / np.nanmax(spec[0])
            ax.plot(f, s, lw=0.8, label=f"cutoff {co:.2f} T")
        except Exception as e:
            print(f"fft cutoff {co:.2f}: {e}")
    ax.axvline(float(F_L), color="k", ls=":", label=f"F_L={float(F_L):.1f} T")
    ax.set_xlim(0, float(F_L) * 1.6)
    ax.set_xlabel("F (T)"); ax.set_ylabel("FFT amp (norm)")
    ax.set_title("SdH FFT in 1/B")
    ax.legend(fontsize=7)

fig.tight_layout()
fig.savefig(f"{OUT}/spot_checks_runs67.png", dpi=110)
print("saved", f"{OUT}/spot_checks_runs67.png")
