"""Runs 6 & 7 (sdh-spot-check, e-side n=+3.2e12 / h-side n=-1.2e12, D=0):
onset + 1/B FFT read, vs the FS-count model templates."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft

I_BIAS = 10e-9
R_FS = 50e-6 / I_BIAS  # 5 kOhm full scale, sr1 gain 1

runs = {}
for fid, tag, nspot in ((6, "electron n=+3.2e12", 3.2), (7, "hole n=-1.2e12", -1.2)):
    run = open_run(f"data/{fid}")
    print(f"=== run {fid} ({tag}) ===")
    print(sorted(run.cols))
    B = run.col("magnet_field")
    # sort ascending in B (run 7 descends)
    idx = np.argsort(B)
    B = B[idx]
    R = run.col("sr1_X")[idx] / I_BIAS
    T = run.col("T_sample")[idx]
    print(f"B {B.min():.3f}->{B.max():.3f} T, {len(B)} pts; R range {R.min():.1f}..{R.max():.1f} Ohm; "
          f"T {T.min():.3f}-{T.max():.3f} K; interrupted={run.interrupted}")
    runs[fid] = (B, R, tag, nspot)

for fid, (B, R, tag, nspot) in runs.items():
    print(f"\n=== run {fid} ({tag}) onset ===")
    try:
        on = sdh_onset(R, B, r_full_scale=R_FS)
        print(on.summary())
        onset_b = on.onset_b
    except Exception as e:
        print("SdhOnsetError:", e)
        onset_b = None

    fig, ax = plt.subplots(3, 1, figsize=(9, 11))
    ax[0].plot(B, R, lw=0.6)
    ax[0].set(xlabel="B (T)", ylabel="Rxx (Ohm)", title=f"run {fid} raw — {tag}")
    # bg-subtracted view
    m = B >= 0.5
    p = np.polyfit(B[m], R[m], 5)
    ax[1].plot(B[m], R[m] - np.polyval(p, B[m]), lw=0.6)
    ax[1].set(xlabel="B (T)", ylabel="dRxx (Ohm)", title="deg-5 poly-in-B removed")
    if onset_b:
        ax[1].axvline(onset_b, color="r", ls="--", label=f"onset {onset_b:.2f} T")
        ax[1].legend()

    # FFT with a few cutoffs (stability)
    for cut, col in ((onset_b or 1.0, "C0"), ((onset_b or 1.0) * 1.3, "C1"), ((onset_b or 1.0) * 1.6, "C2")):
        try:
            fr, sp = sdh_fft(R[:, None], B, b_range=(cut, B.max()), bg_degree=5, log=False)
            s = sp[0]
            ax[2].plot(fr, s / s.max(), color=col, lw=0.8, label=f"cut {cut:.2f} T")
            if col == "C1":
                # report top peaks
                from scipy.signal import find_peaks
                pk, props = find_peaks(s, height=0.03 * s.max(), distance=3)
                order = np.argsort(props["peak_heights"])[::-1][:8]
                print(f"run {fid} FFT peaks (cut {cut:.2f} T): " +
                      ", ".join(f"{fr[pk[i]]:.1f} T (h {props['peak_heights'][i]/s.max():.2f})" for i in order))
        except Exception as e:
            print(f"fft cut {cut:.2f}: {e}")
    ax[2].set(xlabel="F (T)", ylabel="norm. amp", xlim=(0, 60), title="1/B FFT vs low-B cutoff")
    ax[2].legend()
    fig.tight_layout()
    fig.savefig(f"hera_scratch/spot_run{fid}.png", dpi=110)
    print(f"saved hera_scratch/spot_run{fid}.png")
