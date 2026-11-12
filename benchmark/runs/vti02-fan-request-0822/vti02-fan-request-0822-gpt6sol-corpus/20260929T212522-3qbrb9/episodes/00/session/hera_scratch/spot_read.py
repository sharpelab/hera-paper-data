"""Read the two in-session SdH spot checks before fan design."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, summarize_run, sdh_onset, sdh_fft, resolve_channels

fig, axes = plt.subplots(2, 2, figsize=(12, 8))
for j, rid in enumerate((6, 7)):
    r = open_run(f"data/{rid}")
    print(summarize_run(r))
    chans = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field")
    I_bias = (float(r.meta["instruments"]["sr1"]["snapshot"]["parameters"]["amplitude"]["value"])
              / float(r.meta["measurement_config"]["bias_resistor"]))
    R = r.col("sr1_X") / chans["sr1"].gain / I_bias
    drain = r.col("sr0_X") / chans["sr0"].gain
    T = r.col("T_sample")
    itg = r.col("k_2400_tg_curr")
    ibg = r.col("k_2400_bg_curr")
    print(f"run {rid}: I_bias={I_bias:.3e} A, R={R.min():.1f}..{R.max():.1f} Ohm, "
          f"drain={drain.min()*1e9:.2f}..{drain.max()*1e9:.2f} nA, "
          f"T={T.min():.3f}..{T.max():.3f} K, "
          f"I_tg={itg.min()*1e12:.0f}..{itg.max()*1e12:.0f} pA, "
          f"I_bg={ibg.min()*1e12:.0f}..{ibg.max()*1e12:.0f} pA")
    axes[j, 0].plot(B, R, lw=.8)
    axes[j, 0].set(xlabel="B (T)", ylabel="Rxx (Ohm)", title=f"run {rid}, raw")
    try:
        on = sdh_onset(R, B, r_full_scale=50e-6/I_bias)
        print(on.summary())
    except Exception as e:
        print(f"run {rid} onset error: {type(e).__name__}: {e}")
    for cutoff in ((1.5, 2.0, 2.5) if rid == 6 else (1.0, 2.0, 3.0)):
        try:
            freq, spec = sdh_fft(R[:, None], B, b_range=(cutoff, min(10, B.max())),
                                 nfft=2048, log=False)
            y = spec[0]
            peaks, _ = find_peaks(y, prominence=np.max(y)*.02, distance=8)
            peaks = sorted(peaks, key=lambda p: y[p], reverse=True)[:8]
            print(f"run {rid} FFT [{cutoff}, {min(10,B.max()):g}] peaks " +
                  ", ".join(f"{freq[p]:.2f} T/{y[p]:.2g}" for p in peaks))
            axes[j, 1].plot(freq, y, label=f"B>{cutoff:g}")
        except Exception as e:
            print(f"run {rid} FFT {cutoff:g} error: {e}")
    axes[j, 1].set(xlim=(0, 75), xlabel="SdH frequency (T)", ylabel="FFT amplitude", title=f"run {rid}")
    axes[j, 1].legend()
fig.tight_layout()
fig.savefig("hera_scratch/spot_reads.png", dpi=140)
