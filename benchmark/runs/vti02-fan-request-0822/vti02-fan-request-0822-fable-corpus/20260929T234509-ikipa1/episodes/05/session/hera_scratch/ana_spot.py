"""SdH spot-check read: runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12).

Per sdh-spot-check Verify: onset from background-subtracted data (sdh_onset),
FFT in 1/B (sdh_fft) with cutoff >= onset, tones vs F_L.
Model refs (fs_count_b0, from md_spot_e/h): e-side F_L=33.1 T, ABAB pair ~7.5/25.6,
ABCA 33.1; h-side F_L=12.4 T, ABAB ~5.3/7.1, ABCA 12.4.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run, sdh_onset, sdh_fft, SdhOnsetError

RUNS = {
    6: dict(label="electron n=+3.2e12", F_L=33.1, sens=50e-6),
    7: dict(label="hole n=-1.2e12", F_L=12.4, sens=50e-6),
}

fig, axs = plt.subplots(len(RUNS), 3, figsize=(15, 4 * len(RUNS)))

for row, (rid, info) in enumerate(RUNS.items()):
    run = open_run(f"data/{rid}")
    print(f"=== run {rid} — {info['label']} ===")
    print(summarize_run(run))
    B = run.col("magnet_field")
    # R = (V_sr1/gain) / (I_drain), I from the measured sr0 current channel
    from hera.analysis import resolve_channels, current_channel
    chans = resolve_channels(run.meta)
    cur = current_channel(chans)
    v = [c for c in chans if c.cid == "sr1"][0]
    I = run.col(cur.col) / cur.gain
    R = np.abs((run.col(v.col) / v.gain) / I)
    i_med = np.nanmedian(np.abs(I))
    print(f"I_drain median = {i_med*1e9:.3f} nA")
    # sort ascending in B
    order = np.argsort(B)
    B, R = B[order], R[order]
    # keep B > 0.05 to avoid zero-field clutter
    m = B > 0.05
    B, R = B[m], R[m]
    print(f"B {B.min():.3f}..{B.max():.3f} T, {len(B)} pts; R min/med/max = "
          f"{np.nanmin(R):.1f}/{np.nanmedian(R):.1f}/{np.nanmax(R):.1f} Ohm")

    r_fs = info["sens"] / i_med  # sensitivity over measured drive current
    try:
        on = sdh_onset(R, B, r_full_scale=r_fs)
        print(on.summary())
        onset = on.onset_b
    except SdhOnsetError as e:
        print("SdhOnsetError:", e)
        on, onset = None, None

    ax = axs[row, 0]
    ax.plot(B, R, lw=0.6)
    ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx (Ohm)")
    ax.set_title(f"run {rid} raw — {info['label']}")
    if onset:
        ax.axvline(onset, color="r", ls="--", lw=0.8)

    # background-subtracted vs 1/B
    if onset:
        cut = max(onset, B.min())
        for j, cutoff in enumerate([cut, cut * 1.25]):
            freqs, spec = sdh_fft(R[:, None], B, b_range=(cutoff, B.max()), bg_degree=5)
            s = spec[0]
            axs[row, 2].plot(freqs, s / s.max(), lw=0.8,
                             label=f"cutoff {cutoff:.2f} T")
        axs[row, 2].axvline(info["F_L"], color="k", ls=":", label=f"F_L {info['F_L']} T")
        axs[row, 2].set_xlim(0, 1.6 * info["F_L"])
        axs[row, 2].set_xlabel("F (T)"); axs[row, 2].set_ylabel("|FFT| (norm)")
        axs[row, 2].legend(fontsize=7)
        # delta-R panel
        msk = B >= cut
        p = np.polyfit(B[msk], R[msk], 5)
        dR = R[msk] - np.polyval(p, B[msk])
        axs[row, 1].plot(1.0 / B[msk], dR, lw=0.6)
        axs[row, 1].set_xlabel("1/B (1/T)"); axs[row, 1].set_ylabel("dRxx (Ohm)")
        # print top peaks
        freqs, spec = sdh_fft(R[:, None], B, b_range=(cut, B.max()), bg_degree=5)
        s = spec[0]
        pk = [i for i in range(1, len(s) - 1) if s[i] > s[i-1] and s[i] > s[i+1]]
        pk = sorted(pk, key=lambda i: -s[i])[:8]
        print("top FFT peaks (F [T], rel amp):",
              [(round(float(freqs[i]), 2), round(float(s[i] / s.max()), 3)) for i in sorted(pk, key=lambda i: freqs[i])])
        dF = 1.0 / (1.0 / cut - 1.0 / B.max())
        print(f"record resolution dF = {dF:.2f} T (cutoff {cut:.2f}, Bmax {B.max():.2f})")
    print()

fig.tight_layout()
fig.savefig("hera_scratch/spot_checks.png", dpi=110)
print("saved hera_scratch/spot_checks.png")
