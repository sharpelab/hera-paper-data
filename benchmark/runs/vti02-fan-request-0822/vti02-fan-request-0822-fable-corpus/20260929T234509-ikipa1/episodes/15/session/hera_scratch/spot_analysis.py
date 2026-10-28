"""SdH spot checks, runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12) — onset + FFT read.

sdh-spot-check step 6: onset from sdh_onset (bg-subtracted, tracked tones),
FFT via sdh_fft (poly bg in B, FFT in 1/B), tones read against F_L = (h/4e)n.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run, sdh_onset, sdh_fft, luttinger_frequency, SdhOnsetError

BASE = "/home/hera/measurements/zack/20260822-vti-02/data"
I_BIAS = None  # from metadata

runs = {6: dict(n=3.2, label="electron n=+3.2e12"), 7: dict(n=-1.2, label="hole n=-1.2e12")}

fig, axes = plt.subplots(2, 3, figsize=(16, 8))

for i, (rid, info) in enumerate(runs.items()):
    run = open_run(f"{BASE}/{rid}")
    print(f"===== run {rid}: {info['label']} =====")
    print(summarize_run(run))
    B = run.col("magnet_field")
    mc = run.meta["measurement_config"]
    # I_bias from bias channel amplitude / bias resistor — hera-watch convention
    # sr1 unity gain; R = X / I_bias
    import json
    sens = None
    x = run.col("sr1_X")
    # bias: sr1 drive amplitude / 100 MOhm. Amplitude lives in instrument snapshot.
    amp = run.meta["instruments"]["sr1"]["snapshot"]["parameters"]["amplitude"]["value"]
    i_bias = amp / mc["bias_resistor"]
    R = x / i_bias
    order = np.argsort(B)
    B, R = B[order], R[order]
    T = run.col("T_sample")
    print(f"I_bias = {i_bias*1e9:.2f} nA; B {B.min():.3f}..{B.max():.3f} T, {len(B)} pts; T {T.min():.3f}-{T.max():.3f} K")
    print(f"R range: {R.min():.1f} .. {R.max():.1f} Ohm")
    F_L = luttinger_frequency(info["n"] * 1e16)  # n in m^-2 -> T (check helper units)
    print(f"F_L = {F_L:.2f} T")
    r_fs = 50e-6 / i_bias
    try:
        on = sdh_onset(R, B, r_full_scale=r_fs)
        print(on.summary())
        onset = on.onset_b
    except SdhOnsetError as e:
        print(f"SdhOnsetError: {e}")
        onset = None
    # raw trace
    ax = axes[i, 0]
    ax.plot(B, R, lw=0.6)
    ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx (Ohm)"); ax.set_title(f"run {rid} raw — {info['label']}")
    if onset:
        ax.axvline(onset, color="r", ls="--", lw=0.8)
    # bg-subtracted
    ax = axes[i, 1]
    m = B > 0.3
    p = np.polyfit(B[m], R[m], 5)
    dR = R[m] - np.polyval(p, B[m])
    ax.plot(B[m], dR, lw=0.6)
    ax.set_xlabel("B (T)"); ax.set_ylabel("dRxx (Ohm)"); ax.set_title("bg-subtracted (deg-5 in B)")
    if onset:
        ax.axvline(onset, color="r", ls="--", lw=0.8)
    # FFT above onset
    ax = axes[i, 2]
    lo = onset if onset else 1.0
    for cut in [lo, lo * 1.2, lo * 1.5]:
        try:
            freqs, spec = sdh_fft(R[:, None], B, b_range=(cut, B.max()))
            ax.plot(freqs, spec[0], lw=0.8, label=f"cut {cut:.2f} T")
        except Exception as e:
            print(f"fft cut {cut:.2f}: {e}")
    ax.axvline(abs(F_L), color="k", ls=":", lw=1, label=f"F_L={abs(F_L):.1f} T")
    ax.set_xlabel("F (T)"); ax.set_ylabel("FFT amp"); ax.set_xlim(0, abs(F_L) * 1.6)
    ax.legend(fontsize=7); ax.set_title("FFT in 1/B")
    print()

fig.tight_layout()
fig.savefig("/home/hera/measurements/zack/20260822-vti-02/hera_scratch/spot_checks_67.png", dpi=110)
print("saved spot_checks_67.png")
