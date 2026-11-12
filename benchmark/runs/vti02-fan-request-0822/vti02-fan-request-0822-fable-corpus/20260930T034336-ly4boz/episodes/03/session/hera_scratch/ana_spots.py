"""Spot-check read: runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12).
Raw MR, sdh_onset, sdh_fft vs F_L, per the sdh-spot-check recipe step 6."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run, sdh_onset, sdh_fft, SdhOnsetError, luttinger_frequency

BASE = "/home/hera/measurements/zack/20260822-vti-02/data"

for rid, nset, label in [(6, +3.2e12, "electron"), (7, -1.2e12, "hole")]:
    run = open_run(f"{BASE}/{rid}")
    print(f"===== run {rid} ({label}, n={nset:+.2e}) =====")
    print(summarize_run(run))
    B = run.col("magnet_field")
    sr1x = run.col("sr1_X")
    # gain-divided: sr1 gain 1 (unity), I_bias from config
    mc = run.meta.get("measurement_config", {})
    ibias = None
    # derive I_bias from drive: bias channel sr1 oscillator over 100 MOhm
    # hera-watch reads it from metadata; use amplitude snapshot if present
    try:
        amp = run.meta["instruments"]["sr1"]["snapshot"]["parameters"]["amplitude"]["value"]
        ibias = amp / 1e8
    except Exception:
        pass
    print("sr1 amplitude-derived I_bias:", ibias)
    R = sr1x / ibias if ibias else sr1x
    sens = None
    try:
        sens = run.meta["instruments"]["sr1"]["snapshot"]["parameters"]["sensitivity"]["value"]
    except Exception:
        pass
    print("sr1 sensitivity:", sens)
    print(f"B: {B.min():.3f}..{B.max():.3f} T, {len(B)} pts; R: {np.nanmin(R):.1f}..{np.nanmax(R):.1f} Ohm")
    print(f"T_sample: {np.nanmin(run.col('T_sample')):.3f}..{np.nanmax(run.col('T_sample')):.3f} K")
    for gc in ("k_2400_tg_curr", "k_2400_bg_curr"):
        g = run.col(gc)
        print(f"{gc}: med {np.nanmedian(g)*1e12:+.0f} pA, extremes {np.nanmin(g)*1e12:+.0f}/{np.nanmax(g)*1e12:+.0f} pA")

    FL = luttinger_frequency(abs(nset))
    print(f"F_L = {FL:.1f} T")

    # sort ascending in B for analysis (run 7 descends)
    idx = np.argsort(B)
    Bs, Rs = B[idx], R[idx]

    rfs = (sens / ibias) if (sens and ibias) else None
    try:
        on = sdh_onset(Rs, Bs, r_full_scale=rfs)
        print(on.summary())
        onset = on.onset_b
    except SdhOnsetError as e:
        print("SdhOnsetError:", e)
        onset = None

    fig, ax = plt.subplots(2, 2, figsize=(12, 7))
    ax[0, 0].plot(Bs, Rs, lw=0.6)
    ax[0, 0].set(xlabel="B (T)", ylabel="Rxx (Ohm)", title=f"run {rid} raw MR ({label})")
    # background-subtracted view
    if onset:
        for cut, a in [(onset, ax[0, 1]), (max(onset * 1.3, onset + 0.5), ax[1, 1])]:
            m = Bs >= cut
            freqs, spec = sdh_fft(Rs[m][:, None], Bs[m], b_range=(cut, Bs.max()), bg_degree=5)
            a.plot(freqs, spec[0], lw=0.8)
            a.axvline(FL, color='r', ls='--', label=f"F_L={FL:.1f} T")
            a.set(xlabel="F (T)", ylabel="|FFT|", xlim=(0, 1.6 * FL), title=f"FFT cutoff {cut:.2f} T")
            a.legend()
            pk = freqs[np.argmax(spec[0][freqs > 2])]
        # deltaR view
        m = Bs >= onset
        p = np.polyfit(Bs[m], Rs[m], 5)
        ax[1, 0].plot(Bs[m], Rs[m] - np.polyval(p, Bs[m]), lw=0.6)
        ax[1, 0].set(xlabel="B (T)", ylabel="dRxx (Ohm)", title=f"bg-subtracted above onset {onset:.2f} T")
    fig.tight_layout()
    fig.savefig(f"/home/hera/measurements/zack/20260822-vti-02/hera_scratch/spot_run{rid}.png", dpi=110)
    print()
