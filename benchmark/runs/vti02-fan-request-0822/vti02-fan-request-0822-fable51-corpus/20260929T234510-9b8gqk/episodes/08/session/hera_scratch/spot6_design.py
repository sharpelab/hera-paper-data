"""Run 6 design checks: fine-leg onset (B>=1 T), B-window split, and alias check of candidate uniform-1/B fan grids."""
import numpy as np, warnings, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, sdh_onset, sdh_fft, field_invB
from pathlib import Path
here = Path(__file__).resolve().parent.parent
run = open_run(here / "data/6")
B = run.col("magnet_field"); R = run.col("sr1_X") / (run.col("sr0_X") / -1e6)
o = np.argsort(B); B, R = B[o], R[o]
FS = 50e-6 / 10e-9
print("--- fine leg only (b_lo = 1.0 T) ---")
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    on = sdh_onset(R, B, b_lo=1.0, r_full_scale=FS)
    print(on.summary()); [print("  warn:", str(x.message)[:200]) for x in w]
print("--- b_lo = 1.5 T ---")
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    on2 = sdh_onset(R, B, b_lo=1.5, r_full_scale=FS); print(on2.summary()); [print("  warn:", str(x.message)[:200]) for x in w]

def peaks(freqs, sp, fmax=200, k=8):
    m = freqs <= fmax; f, s = freqs[m], sp[m] / sp[m].max()
    pk, _ = find_peaks(s, prominence=0.04)
    return ", ".join(f"{f[i]:.1f}({s[i]:.2f})" for i in sorted(pk, key=lambda i: -s[i])[:k])

print("\n--- B-window split (native 10 mT record, deg 5) ---")
for lo, hi in [(1.5, 4.0), (1.5, 6.0), (4.0, 10.0), (6.0, 10.0), (2.0, 10.0)]:
    fr, sp = sdh_fft(R[:, None], B, b_range=(lo, hi), bg_degree=5, nfft=4096)
    print(f"  [{lo},{hi}] T dF={1/(1/lo-1/hi):.2f}: {peaks(fr, sp[0])}")

print("\n--- alias check: run 6 resampled onto candidate fan grids (linear interp in B), FFT over the full grid ---")
fig, ax = plt.subplots(len([0.005, 0.0083, 0.0125, 0.0033]), 1, figsize=(10, 12), sharex=True)
for a, dinv in zip(ax, [0.0033, 0.005, 0.0083, 0.0125]):
    for blo in (1.0, 1.3):
        N = int(round((1/blo - 0.1) / dinv)) + 1
        Bg = field_invB(blo, 10.0, N); Rg = np.interp(Bg, B, R)
        fr, sp = sdh_fft(Rg[:, None], Bg, b_range=(blo, 10.0), bg_degree=5, nfft=4096)
        print(f"  d(1/B)={dinv} B_lo={blo}: N_B={N}, F_Nyq={1/(2*dinv):.0f} T: {peaks(fr, sp[0], fmax=1/(2*dinv))}")
        if blo == 1.0: a.plot(fr, sp[0]/sp[0].max(), lw=0.8, label=f"d(1/B)={dinv}, N={N}")
    a.axvline(33.1, color="k", ls="--", lw=0.8); a.set_xlim(0, 100); a.legend(fontsize=8)
ax[-1].set_xlabel("F (T)"); fig.suptitle("run 6 resampled onto uniform-1/B fan grids, 1->10 T"); fig.tight_layout(); fig.savefig(here/"hera_scratch/run6_alias_check.png", dpi=110)
