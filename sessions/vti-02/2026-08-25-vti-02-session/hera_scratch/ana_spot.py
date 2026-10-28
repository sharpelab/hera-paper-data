"""SdH spot check read: onset + 1/B FFT per density, against the Luttinger F_L.

The read the investigation asks for: which tones are present at each (n, D=0),
where they sit relative to F_L = (h/4e)*n, and which side is cleaner.
"""
import sys
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import scipy.constants as cst
from scipy.signal import find_peaks

from hera.analysis import (open_run, summarize_run, fan_grids, resistance_grids,
                           sdh_fft, sdh_onset, SdhOnsetError, luttinger_frequency)

BASE = "C:/Users/DGG/VTI_local_data/zack/20260825-vti-02/data"
SCRATCH = "C:/Users/DGG/VTI_local_data/zack/20260825-vti-02/hera_scratch"
RID = int(sys.argv[1]) if len(sys.argv) > 1 else 7
SENS = 1e-4
# calibration measured this session (runs 5, 6)
DN_DVTG, DN_DVBG, V_TG_CNP = 1.570e12, 1.307e12, 0.0203

r = open_run(f"{BASE}/{RID}")
print(summarize_run(r))
fg = fan_grids(r)
def G(n): return fg.data[:, fg.cols.index(n)].reshape(fg.nrows, fg.nfast)
rg = resistance_grids(fg, channels=["sr1"])
R = rg.R["sr1"]                      # (n_B, n_fast) -- signed
B = G("magnet_field")[:, 0]
Vtg = G("k_2400_tg_volt")[0]; Vbg = G("k_2400_bg_volt")[0]
ncol = (DN_DVTG * (Vtg - V_TG_CNP) + DN_DVBG * Vbg) / 1e12     # 1e12 cm^-2
print(f"{fg.nrows} field rows, B {B.min():.3f}..{B.max():.3f} T; "
      f"{fg.nfast} densities: {np.round(ncol,2).tolist()} e12 cm^-2")
print(f"1/B record: {1/B.min():.4f} .. {1/B.max():.4f} 1/T  -> "
      f"dF = {1/(1/B.min() - 1/B.max()):.2f} T")

r_fs = SENS / np.abs(rg.current).mean()
print(f"\n{'n (e12)':>9} {'F_L (T)':>8} {'R med':>8} {'onset':>8}  tones, DOMINANT FIRST (rel. prominence)")
results = []
for j in range(fg.nfast):
    tr = np.abs(R[:, j])
    F_L = luttinger_frequency(abs(ncol[j]) * 1e16)      # SI density -> Tesla
    # onset
    try:
        on = sdh_onset(tr, B, r_full_scale=r_fs)
        onset_s = f"{on.onset_b:.2f} T"
        tones_on = [t.freq for t in on.tones]
    except SdhOnsetError as e:
        onset_s = "none"; tones_on = []
        print(f"   (n={ncol[j]:+.2f}: sdh_onset -> {type(e).__name__}: {e})")
    except Exception as e:
        onset_s = f"err"; tones_on = []
        print(f"   (n={ncol[j]:+.2f}: {type(e).__name__}: {e})")
    # FFT over the usable window
    cutoff = max(B.min(), 1.5)
    freqs, spec = sdh_fft(tr[:, None], B, b_range=(cutoff, B.max()), bg_degree=5)
    p = spec[0]
    keep = freqs > 1.0
    fr, pw = freqs[keep], p[keep]
    # distinct peaks, not adjacent bins of one peak: require separation >= dF,
    # the usable-record resolution 1/(1/B_lo - 1/B_hi)
    dF = 1.0 / (1.0 / cutoff - 1.0 / B.max())
    dbin = max(1, int(round(dF / (fr[1] - fr[0]))))
    pk, props = find_peaks(pw, distance=dbin, prominence=0.15 * np.ptp(pw))
    order = np.argsort(props["prominences"])[::-1][:4]
    top = fr[pk[order]] if len(pk) else np.array([])
    topa = props["prominences"][order] if len(pk) else np.array([])
    results.append(dict(n=ncol[j], F_L=F_L, freqs=fr, spec=pw, top=top,
                        amp=topa, onset=onset_s))
    print(f"{ncol[j]:>9.2f} {F_L:>8.1f} {np.median(tr):>8.1f} {onset_s:>8}  "
          + "  ".join(f"{t:.1f}T(x{a/topa.max():.2f})" for t, a in zip(top, topa)))

print("\n=== tones vs Luttinger F_L (the read) ===")
for d in results:
    if d["F_L"] <= 0:
        continue
    ratios = d["top"] / d["F_L"]
    print(f"  n={d['n']:+.2f}e12  F_L={d['F_L']:.1f} T   dominant f/F_L = {ratios[0]:.3f}"
          f"   all (dominant first) = " + "  ".join(f"{x:.3f}" for x in ratios))
    print(f"      ABCA template: one tone at 1.00 | ABAB: pair near 0.72/0.28 "
          f"(electron side runs ~0.73 at 6e12)")

fig, ax = plt.subplots(2, len(results), figsize=(3.6*len(results), 7.5), squeeze=False)
for j, d in enumerate(results):
    tr = np.abs(R[:, j])
    ax[0][j].plot(B, tr, lw=0.8)
    ax[0][j].set_xlabel("B (T)"); ax[0][j].set_ylabel(r"$R_{xx}$ ($\Omega$)")
    ax[0][j].set_title(f"n = {d['n']:+.2f}e12", fontsize=10); ax[0][j].grid(alpha=0.3)
    ax[1][j].plot(d["freqs"], d["spec"], lw=0.9)
    if d["F_L"] > 0:
        ax[1][j].axvline(d["F_L"], color="C3", ls="--", lw=1.1)
        ax[1][j].axvline(0.72*d["F_L"], color="C2", ls=":", lw=1.0)
        ax[1][j].axvline(0.28*d["F_L"], color="C2", ls=":", lw=1.0)
    ax[1][j].set_xlim(0, max(60, 1.6*d["F_L"]))
    ax[1][j].set_xlabel("F (T)"); ax[1][j].set_ylabel("FFT amp")
    ax[1][j].grid(alpha=0.3)
fig.suptitle("SdH spot check — red dashed = $F_L$=(h/4e)n, green dotted = ABAB 0.72/0.28", y=0.99)
fig.tight_layout(); fig.savefig(f"{SCRATCH}/spot.png", dpi=120)
print(f"\nwrote {SCRATCH}/spot.png")
