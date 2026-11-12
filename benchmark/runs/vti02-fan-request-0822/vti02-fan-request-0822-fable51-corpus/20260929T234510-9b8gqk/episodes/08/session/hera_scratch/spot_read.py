"""Spot-check read: runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12). Onset + FFT tones vs F_L."""
import sys, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run, sdh_onset, sdh_fft, SdhOnsetError, luttinger_frequency
from pathlib import Path
here = Path(__file__).resolve().parent.parent
out = {}
for rid, n12 in [(6, 3.2), (7, -1.2)]:
    run = open_run(here / "data" / str(rid))
    print(f"\n================ RUN {rid} ================")
    print(summarize_run(run))
    print("cols:", run.cols)
    B = run.col("magnet_field"); I = run.col("sr0_X") / -1e6; V = run.col("sr1_X")
    R = V / I
    order = np.argsort(B); B, R, I = B[order], R[order], I[order]
    T = run.col("T_sample"); print(f"T_sample {T.min():.3f}-{T.max():.3f} K; I_bias {I.mean()*1e9:.3f} nA; R range {R.min():.1f}..{R.max():.1f} Ohm")
    try:
        FL = luttinger_frequency(abs(n12) * 1e16)
    except Exception as e:
        FL = 4.1357e-15 * abs(n12) * 1e16 / 4  # h/(4e) * n
        print("luttinger_frequency call failed:", e)
    print(f"F_L(|n|={abs(n12)}e12) = {FL:.2f} T")
    try:
        on = sdh_onset(R, B, r_full_scale=50e-6 / 10e-9)
        print(on.summary())
        onset_b = on.onset_b
    except SdhOnsetError as e:
        print("SdhOnsetError:", e); onset_b = None
    except TypeError as e:
        print("sdh_onset TypeError:", e); on = sdh_onset(R, B); print(on.summary()); onset_b = on.onset_b
    # FFT ladder: several low cutoffs
    fig, ax = plt.subplots(3, 1, figsize=(10, 11))
    ax[0].plot(B, R, lw=0.6); ax[0].set_xlabel("B (T)"); ax[0].set_ylabel("Rxx (Ohm)"); ax[0].set_title(f"run {rid} raw Rxx(B), n={n12:+.1f}e12, D=0")
    cutoffs = [c for c in ([1.5, 2.0, 3.0, 4.0, 5.0] if rid == 6 else [1.0, 2.0, 3.0, 4.0]) if c < B.max() - 1]
    for c in cutoffs:
        for deg in (3, 5):
            try:
                freqs, spec = sdh_fft(R[:, None], B, b_range=(c, B.max()), bg_degree=deg)
                sp = spec[0] / spec[0].max()
                if deg == 5:
                    ax[2].plot(freqs, sp, lw=0.8, label=f"cut {c} T deg{deg}")
                # top peaks
                from scipy.signal import find_peaks
                pk, pr = find_peaks(sp, prominence=0.05)
                top = sorted(zip(sp[pk], freqs[pk]), reverse=True)[:6]
                print(f"  FFT cut {c:.1f} T deg {deg}: dF={1/(1/c-1/B.max()):.2f} T; peaks (amp,F): " + ", ".join(f"({a:.2f},{f:.1f})" for a, f in top))
            except Exception as e:
                print(f"  FFT cut {c} deg {deg} failed: {e}")
    # background-subtracted trace at the middle cutoff for the eye
    c = cutoffs[len(cutoffs)//2]; m = B >= c
    bg = np.polyval(np.polyfit(B[m], R[m], 5), B[m]); ax[1].plot(1/B[m], R[m]-bg, lw=0.6); ax[1].set_xlabel("1/B (1/T)"); ax[1].set_ylabel("dRxx (Ohm)"); ax[1].set_title(f"bg-subtracted (deg 5, B>{c} T) vs 1/B")
    ax[2].axvline(FL, color="k", ls="--", label=f"F_L={FL:.1f} T"); ax[2].set_xlim(0, 1.6*FL); ax[2].set_xlabel("F (T)"); ax[2].legend(fontsize=7)
    fig.tight_layout(); fig.savefig(here / "hera_scratch" / f"spot_run{rid}.png", dpi=110)
    out[rid] = dict(onset=onset_b, FL=FL)
print(out)
