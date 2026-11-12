# Spot-check analysis: runs 6 (electron, n=+3.2e12) & 7 (hole, n=-1.2e12), both D=0.
# Onset + tones + FFT vs F_L and the model table -> fan design inputs.
import sys
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from hera.analysis import (
    open_run, resolve_channels, sdh_onset, sdh_fft, luttinger_frequency, SdhOnsetError,
)

sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
import fs_count_b0 as fsm

DATA = "/home/hera/measurements/zack/20260822-vti-02/data"
I_BIAS = 1.0 / 100e6          # sr1 amplitude 1.0 V / 100 MOhm bias resistor
R_FS = 50e-6 / I_BIAS         # 5 kOhm full scale

runs = {
    6: dict(n=+3.2e16, label="electron n=+3.2e12"),   # m^-2
    7: dict(n=-1.2e16, label="hole n=-1.2e12"),
}

fig, axes = plt.subplots(2, 2, figsize=(13, 8))
for row, (rid, info) in enumerate(runs.items()):
    r = open_run(f"{DATA}/{rid}")
    B = r.col("magnet_field")
    ch = [c for c in resolve_channels(r.meta) if c.cid == "sr1"][0]
    R = r.col(ch.col) / ch.gain / I_BIAS
    order = np.argsort(B)
    B, R = B[order], R[order]

    FL = float(luttinger_frequency(info["n"]))
    print(f"\n=== run {rid} — {info['label']} ===  F_L = {FL:.1f} T")
    print(f"R range: {R.min():.1f} – {R.max():.1f} Ohm (FS {R_FS:.0f}); max/FS = {R.max()/R_FS:.2%}")

    try:
        on = sdh_onset(R, B, r_full_scale=R_FS)
        print(on.summary())
        info["onset"] = on
    except SdhOnsetError as e:
        print(f"SdhOnsetError: {e}")
        info["onset"] = None

    # raw
    ax = axes[row, 0]
    ax.plot(B, R, lw=0.6)
    ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx (Ohm)")
    ax.set_title(f"run {rid} raw — {info['label']}")

    # FFT above onset (and a half-window stability check)
    ax = axes[row, 1]
    b_lo = info["onset"].onset_b if info["onset"] else 1.5
    for cut, style in ((b_lo, "-"), (max(b_lo * 1.4, b_lo + 0.5), "--")):
        try:
            freqs, spec = sdh_fft(R[:, None], B, b_range=(cut, B.max()))
            ax.plot(freqs, spec[0], style, lw=1, label=f"cut {cut:.2f} T")
        except Exception as e:
            print(f"fft cut={cut:.2f}: {e}")
    ax.axvline(FL, color="k", ls=":", label=f"F_L {FL:.1f} T")
    # model tones
    n = info["n"]
    try:
        _, abab = fsm.abab_fs(n)
        for F, _ in abab:
            ax.axvline(F, color="tab:red", ls="--", alpha=0.6)
        print("ABAB orbits (F, kF):", [(round(F, 2)) for F, _ in abab],
              " masses:", [(round(F, 2), round(ms, 3)) for F, ms in fsm.abab_mstar(n)])
    except ValueError as e:
        print("abab:", e)
    try:
        ef, topo, ncomp, nfreq, Ftot = fsm.abca_fs(n)
        ax.axvline(Ftot, color="tab:green", ls="--", alpha=0.6)
        print(f"ABCA: topo={topo}, ncomp={ncomp}, nfreq={nfreq}, F_total={Ftot:.2f}; m* = {fsm.abca_mstar(n)[1]:.3f}")
    except ValueError as e:
        print("abca:", e)
    ax.set_xlim(0, FL * 1.6)
    ax.set_xlabel("F (T)"); ax.set_ylabel("FFT amp (log-detrended)")
    ax.legend(fontsize=7)
    ax.set_title(f"run {rid} FFT in 1/B (red=ABAB, green=ABCA)")

fig.tight_layout()
fig.savefig("/home/hera/measurements/zack/20260822-vti-02/hera_scratch/spots_67.png", dpi=110)
print("\nsaved hera_scratch/spots_67.png")
