"""Runs 6 & 7 — SdH spot-check read (electron n=+3.2e12, hole n=-1.2e12, D=0).

Raw R(B), background-subtracted dR vs 1/B, onset via sdh_onset, FFT via
sdh_fft with cutoff scan; tones read against F_L and the fs_count model.
"""
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from hera.analysis import (open_run, resolve_channels, current_channel,
                           sdh_onset, sdh_fft, luttinger_frequency,
                           SdhOnsetError)

DATA = "/home/hera/measurements/zack/20260822-vti-02/data"

for rid, nlab in [(6, +3.2e12), (7, -1.2e12)]:
    print(f"\n================ run {rid}  n = {nlab:+.2e} ================")
    run = open_run(f"{DATA}/{rid}")
    chans = resolve_channels(run.meta, include=["sr0", "sr1"])
    cur = current_channel(chans)
    v = [c for c in chans if c is not cur][0]
    B = np.asarray(run.col("magnet_field"), float)
    I = np.abs(np.asarray(run.col(cur.col), float) / cur.gain)
    R = np.abs((np.asarray(run.col(v.col), float) / v.gain) / I)
    order = np.argsort(B)
    B, R, I = B[order], R[order], I[order]
    print(f"I_bias med {np.median(I)*1e9:.2f} nA  R(B~0) {R[B<0.1].mean():.1f} Ohm  R_max {R.max():.1f}")
    mc = run.meta.get("measurement_config", {})
    sens = mc.get("sr1_sensitivity") or (mc.get("sensitivities") or {}).get("sr1")
    print("sr1 sensitivity from config:", sens)
    FL = float(luttinger_frequency(abs(nlab) * 1e4))  # nlab in cm^-2 -> m^-2
    print(f"F_L = {FL:.2f} T")

    rfs = (sens / v.gain) / np.median(I) if sens else None
    try:
        on = sdh_onset(R, B, r_full_scale=rfs)
        print(on.summary())
    except SdhOnsetError as e:
        print("SdhOnsetError:", e)
        on = None

    # FFT with two cutoffs around the onset
    fig, ax = plt.subplots(1, 3, figsize=(15, 4))
    ax[0].plot(B, R, lw=0.6)
    ax[0].set(xlabel="B (T)", ylabel="R_sr1 (Ohm)", title=f"run {rid} raw")
    # bg-subtracted
    m = B > 0.5
    p = np.polyfit(B[m], R[m], 5)
    dR = R[m] - np.polyval(p, B[m])
    ax[1].plot(1.0 / B[m], dR, lw=0.6)
    ax[1].set(xlabel="1/B (1/T)", ylabel="dR (Ohm)", title="bg-subtracted (deg5, B>0.5)")
    cuts = []
    if on is not None:
        cuts = [max(on.onset_b, 0.6), max(1.5 * on.onset_b, 1.0)]
    else:
        cuts = [1.5, 3.0]
    for c in cuts:
        f, spec = sdh_fft(R[:, None], B, b_range=(c, B.max()))
        ax[2].plot(f, spec[0], lw=0.8, label=f"cut {c:.2f} T")
    ax[2].axvline(FL, color="k", ls="--", lw=0.8, label="F_L")
    ax[2].set(xlabel="F (T)", xlim=(0, 1.6 * FL), title="FFT in 1/B")
    ax[2].legend(fontsize=7)
    fig.tight_layout()
    out = f"/home/hera/measurements/zack/20260822-vti-02/hera_scratch/spot_run{rid}.png"
    fig.savefig(out, dpi=110)
    print("saved", out)
