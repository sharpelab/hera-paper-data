"""Spot-check runs 6 (e-side, n=+3.2e12) and 7 (h-side, n=-1.2e12): raw, onset, FFT tones."""
import numpy as np, warnings, json
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run, sdh_onset, sdh_fft, SdhOnsetError, luttinger_frequency

out = {}
fig, axs = plt.subplots(2, 2, figsize=(13, 8))
for k, rid in enumerate((6, 7)):
    run = open_run(f"data/{rid}")
    print(f"===== run {rid} =====\n{summarize_run(run)}")
    print("cols:", run.cols)
    B = run.col("magnet_field"); X = run.col("sr1_X"); I = run.col("sr0_X") / -1e6
    R = X / I
    o = np.argsort(B); B, R, I = B[o], R[o], I[o]
    T = run.col("T_sample")
    print(f"T_sample {T.min():.3f}-{T.max():.3f} K; I_bias {np.median(I)*1e9:.3f} nA; R range {R.min():.1f}..{R.max():.1f} Ohm; R(B~0.3)={R[np.argmin(abs(B-0.3))]:.1f}")
    axs[0, k].plot(B, R, lw=0.7); axs[0, k].set_title(f"run {rid} raw Rxx (sr1/sr0)"); axs[0, k].set_xlabel("B (T)"); axs[0, k].set_ylabel("R (Ohm)")
    fs = 50e-6 / np.median(I)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        try:
            on = sdh_onset(R, B, r_full_scale=fs)
            print("ONSET:", on)
            out[rid] = {"onset_b": float(on.onset_b), "repr": repr(on)}
        except SdhOnsetError as e:
            print("SdhOnsetError:", e); out[rid] = {"error": str(e)}
        for ww in w: print("  warn:", ww.message)
    # FFT above ~2 T
    try:
        r = sdh_fft(R, B, b_lo=max(1.5, out[rid].get("onset_b", 1.5)))
        print("FFT:", r)
    except Exception as e:
        print("sdh_fft failed:", e)
        r = None
    axs[1, k].set_title(f"run {rid} FFT")
    if r is not None:
        try:
            F, P = r.F, r.P
        except Exception:
            F, P = r[0], r[1]
        axs[1, k].plot(F, P); axs[1, k].set_xlim(0, 60); axs[1, k].set_xlabel("F (T)")
fig.tight_layout(); fig.savefig("hera_scratch/spot_raw_fft.png", dpi=110)
json.dump(out, open("hera_scratch/spot_onset.json", "w"), indent=1, default=str)
print(json.dumps(out, indent=1, default=str))
