# SdH spot-check read: raw MR -> onset -> FFT vs F_L, with stability sweep.
# usage: menv python hera_scratch/sdh_read.py <run_id> <F_L_Tesla> [tag]
import sys
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft

rid = int(sys.argv[1])
FL = float(sys.argv[2])
tag = sys.argv[3] if len(sys.argv) > 3 else f"run{rid}"
I_BIAS = 20e-9

r = open_run(f"data/{rid}")
B = r.col_at(1)
print(f"run {rid}: {len(B)} pts, B {B.min():.3f}..{B.max():.3f} T, interrupted={r.interrupted}")

fig, axes = plt.subplots(2, 2, figsize=(13, 8))
results = {}
for ch in ("sr1", "sr2"):
    R = r.col(f"{ch}_X") / I_BIAS
    on = sdh_onset(R, B)
    print(f"{ch}: onset_b={on.onset_b:.3f} T, clip_high_b={on.clip_high_b:.3f} T, "
          f"consensus_freq={on.consensus_freq:.1f} T")
    onset_b = on.onset_b if np.isfinite(on.onset_b) else 1.5
    if not np.isfinite(on.onset_b):
        print(f"{ch}: onset NaN (partial record?) — falling back to cutoff {onset_b} T")
    axes[0, 0].plot(B, R, lw=0.7, label=f"{ch} (onset {on.onset_b:.2f} T)")
    # FFT with stability sweep over bg_degree and low-B cutoff
    for deg, ls in ((3, ":"), (5, "-"), (7, "--")):
        for cut, alpha in ((onset_b, 1.0), (onset_b * 1.25, 0.5)):
            freqs, spec = sdh_fft(R[:, None], B, b_range=(cut, B.max()), bg_degree=deg)
            a = spec[0] / spec[0].max()
            if deg == 5 and alpha == 1.0:
                results[ch] = (freqs, a, on)
            axes[0, 1].plot(freqs, a + (0 if ch == "sr1" else 1.1), ls, lw=0.8, alpha=alpha,
                            color="C0" if ch == "sr1" else "C1")
    # peaks (main variant)
    freqs, a, on = results[ch]
    m = (freqs > 2) & (freqs < 1.6 * FL)
    from scipy.signal import find_peaks
    pk, props = find_peaks(a[m], height=0.05, prominence=0.03)
    fpk = freqs[m][pk]
    print(f"{ch} peaks (deg5, cut=onset): " +
          ", ".join(f"{f:.1f} T (h={h:.2f})" for f, h in zip(fpk, props['peak_heights'])))
    results[ch] = (freqs, a, on, fpk)

axes[0, 0].set_xlabel("B (T)"); axes[0, 0].set_ylabel("R (Ω)"); axes[0, 0].legend(fontsize=7)
axes[0, 0].set_title(f"{tag}: raw MR")
axes[0, 1].axvline(FL, color="k", lw=0.8, ls="--", label=f"F_L={FL:.0f} T")
axes[0, 1].axvline(FL / 2, color="gray", lw=0.5, ls=":")
axes[0, 1].set_xlabel("F (T)"); axes[0, 1].set_ylabel("FFT (norm, offset)")
axes[0, 1].set_xlim(0, 1.8 * FL); axes[0, 1].legend(fontsize=7)
axes[0, 1].set_title("FFT stability: deg 3/5/7 × cut onset/1.25×onset")

# background-subtracted traces vs 1/B (visual periodicity check)
for ch, ax in zip(("sr1", "sr2"), axes[1]):
    R = r.col(f"{ch}_X") / I_BIAS
    on = results[ch][2]
    msk = B >= (on.onset_b if np.isfinite(on.onset_b) else 1.5)
    p = np.polyfit(B[msk], R[msk], 5)
    dR = R[msk] - np.polyval(p, B[msk])
    ax.plot(1 / B[msk], dR, lw=0.6)
    ax.set_xlabel("1/B (1/T)"); ax.set_ylabel(f"ΔR {ch} (Ω)")
    ax.set_title(f"{ch}: bg-subtracted (deg 5)")
fig.suptitle(f"{tag} — SdH read, F_L = {FL:.1f} T")
fig.tight_layout()
out = f"hera_scratch/sdh_{tag}.png"
fig.savefig(out, dpi=120)
print("saved", out)
