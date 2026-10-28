"""SdH spot-check read: runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12).
Onset + tone content per sdh-spot-check step 6; feeds the fan design."""
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import (open_run, summarize_run, sdh_onset, sdh_fft,
                           SdhOnsetError, luttinger_frequency, fan_grids,
                           resistance_grids)

SENS = 50e-6  # sr1 sensitivity both runs

results = {}
for rid, nspot in ((6, 3.2e12), (7, -1.2e12)):
    print(f"\n================ run {rid} (n = {nspot/1e12:+.2f}e12 cm^-2) ================")
    run = open_run(f"data/{rid}")
    print(summarize_run(run))
    B = run.col("magnet_field")
    # 1D run: R = (sr1_X / gain 1) / I_meas, I_meas = sr0_X / (-1e6) (transimpedance)
    I = run.col("sr0_X") / (-1e6)
    R = np.abs(run.col("sr1_X") / 1.0 / I)
    idx = np.argsort(B)
    B, R, I = B[idx], R[idx], I[idx]
    print(f"B: {B.min():.3f} -> {B.max():.3f} T, {len(B)} pts; I_meas med {np.median(np.abs(I))*1e9:.2f} nA; "
          f"R(B~0) = {np.median(R[B < 0.2]):.1f} ohm, R(max) = {R.max():.1f} ohm")
    FL = luttinger_frequency(abs(nspot) * 1e4)  # cm^-2 -> m^-2
    print(f"F_L = {FL:.1f} T")

    try:
        on = sdh_onset(R, B, r_full_scale=SENS / np.median(np.abs(I)))
        print(on.summary())
        results[rid] = on
    except SdhOnsetError as e:
        print(f"SdhOnsetError: {e}")
        results[rid] = None

    # raw + background-subtracted plots
    fig, ax = plt.subplots(3, 1, figsize=(9, 9))
    ax[0].plot(B, R, lw=0.6)
    ax[0].set_xlabel("B (T)"); ax[0].set_ylabel("Rxx (ohm)")
    ax[0].set_title(f"run {rid}: raw Rxx(B), n = {nspot/1e12:+.2f}e12, F_L = {FL:.1f} T")
    # bg-subtracted (deg-5 in B, above 1 T)
    m = B >= 1.0
    p = np.polyfit(B[m], R[m], 5)
    dR = R[m] - np.polyval(p, B[m])
    ax[1].plot(B[m], dR, lw=0.6)
    ax[1].set_xlabel("B (T)"); ax[1].set_ylabel("dRxx (ohm)")
    # FFT above onset (or 1.5 T fallback)
    onb = results[rid].onset_b if results[rid] is not None else 1.5
    cut = max(onb, 1.0)
    freqs, spec = sdh_fft(R[:, None], B, b_range=(cut, B.max()))
    ax[2].plot(freqs, spec[0], lw=0.8)
    ax[2].axvline(FL, color="r", ls="--", label=f"F_L = {FL:.1f} T")
    ax[2].axvline(0.72 * FL, color="g", ls=":", label=f"0.72 F_L")
    ax[2].axvline(0.28 * FL, color="g", ls=":", label=f"0.28 F_L")
    ax[2].set_xlim(0, 1.6 * FL); ax[2].legend(); ax[2].set_xlabel("F (T)")
    ax[2].set_title(f"FFT in 1/B, window {cut:.2f}-{B.max():.1f} T")
    fig.tight_layout()
    fig.savefig(f"hera_scratch/spot_run{rid}.png", dpi=110)
    print(f"saved hera_scratch/spot_run{rid}.png")
