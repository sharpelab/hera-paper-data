"""SdH spot-check read: runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12), D=0.
Onset + tones via hera.analysis.sdh_onset, FFT via sdh_fft; tones vs F_L = (h/4e)n.
Design inputs for the Landau fan: onset -> B_lo, tones -> D(1/B), cleaner side."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, SdhOnsetError

H_4E = 6.62607015e-34 / (4 * 1.602176634e-19)   # T m^2
I_BIAS = 10e-9      # 1 Vrms drive? -> read from metadata below
SENS = 50e-6

fig, axs = plt.subplots(2, 3, figsize=(16, 8))
for row, (rid, n12) in enumerate([(6, +3.2), (7, -1.2)]):
    run = open_run(f"data/{rid}")
    ib = run.meta.get("measurement_config", {}).get("I_bias", None)
    B = run.col("magnet_field"); R = (run.col("sr1_X") / 1.0)
    # current from sr0 (transimpedance -1e6): I = sr0_X / 1e6
    I = np.abs(run.col("sr0_X") / 1e6)
    Rxx = run.col("sr1_X") / I  # proper 4T resistance using measured current
    idx = np.argsort(B); B, Rxx, I = B[idx], Rxx[idx], I[idx]
    FL = H_4E * abs(n12) * 1e16
    print(f"\n===== run {rid}: n = {n12:+.1f}e12, F_L = {FL:.1f} T =====")
    print(f"I measured: {I.mean()*1e9:.2f} nA (min {I.min()*1e9:.2f}); R range {Rxx.min():.0f}-{Rxx.max():.0f} Ohm")
    try:
        on = sdh_onset(Rxx, B, r_full_scale=SENS / I.mean())
        print(on.summary())
        onset = on.onset_b
    except SdhOnsetError as e:
        print(f"SdhOnsetError: {e}")
        onset = None
    axs[row, 0].plot(B, Rxx, lw=0.6)
    axs[row, 0].set_xlabel("B (T)"); axs[row, 0].set_ylabel("Rxx (Ohm)")
    axs[row, 0].set_title(f"run {rid} raw  n={n12:+.1f}e12")
    if onset:
        axs[row, 0].axvline(onset, color="r", ls="--", lw=0.8)
    # FFT over usable window (+ background-subtracted trace)
    blo = onset if onset else (1.0 if rid == 6 else 0.5)
    for j, cut in enumerate([blo, blo * 1.3]):
        m = B >= cut
        freqs, spec = sdh_fft(Rxx[:, None] if False else Rxx.reshape(-1, 1), B,
                              b_range=(cut, B.max()), bg_degree=5)
        sp = spec[0] / np.nanmax(spec[0])
        axs[row, 2].plot(freqs, sp, lw=0.8, label=f"cut {cut:.2f} T")
        if j == 0:
            pk = freqs[np.argmax(sp)]
            print(f"FFT cut {cut:.2f}: max peak at {pk:.1f} T; F_L = {FL:.1f}")
    # bg-subtracted trace vs 1/B
    m = B >= max(0.3, blo * 0.7)
    cf = np.polyfit(B[m], Rxx[m], 5)
    dR = Rxx[m] - np.polyval(cf, B[m])
    axs[row, 1].plot(1 / B[m], dR, lw=0.5)
    axs[row, 1].set_xlabel("1/B (1/T)"); axs[row, 1].set_ylabel("dRxx (Ohm)")
    axs[row, 1].set_title(f"run {rid} bg-subtracted (deg5, B>{max(0.3, blo*0.7):.2f})")
    axs[row, 2].axvline(FL, color="k", ls=":", lw=1, label=f"F_L {FL:.1f} T")
    axs[row, 2].axvline(0.72 * FL, color="b", ls=":", lw=0.8, label="0.72 F_L")
    axs[row, 2].axvline(0.28 * FL, color="g", ls=":", lw=0.8, label="0.28 F_L")
    axs[row, 2].set_xlim(0, 1.6 * FL); axs[row, 2].set_xlabel("F (T)")
    axs[row, 2].legend(fontsize=7); axs[row, 2].set_title(f"run {rid} FFT in 1/B")
fig.tight_layout()
fig.savefig("hera_scratch/spots_67.png", dpi=110)
print("\nsaved hera_scratch/spots_67.png")
