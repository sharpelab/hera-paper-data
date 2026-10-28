# Partition robustness (investigation step 5.1): per column find
#   f_light (2-8 T band), and the two strongest tones in the heavy band
#   [0.55*lam*FL, 1.2*lam*FL]; test f_light + f_heavy_lower = lam*FL(n).
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from hera.analysis import fan_grids, resistance_grids, sdh_fft, luttinger_frequency

fan = fan_grids("data/7")
rg = resistance_grids(fan)
B = fan.slow
ns = np.linspace(-0.5, -3.5, 101)
FLnom = luttinger_frequency(np.abs(ns) * 1e16)
LAM = 1.064

rows = []
for ch, ceil in (("sr1", 23.75e3), ("sr2", 9.5e3)):
    R = rg.R[ch]
    f, spec = sdh_fft(R, B, b_range=(0.95, 8.0))
    df = f[1] - f[0]
    for ci in range(101):
        if R[:, ci].max() > ceil or abs(ns[ci]) < 1.0:
            continue
        s = spec[ci]
        FL = LAM * FLnom[ci]
        def top_peaks(fmin, fmax, k=2):
            m = (f >= fmin) & (f <= fmax)
            fi, si = f[m], s[m]
            pk = (si[1:-1] > si[:-2]) & (si[1:-1] > si[2:])
            idx = np.where(pk)[0] + 1
            idx = idx[np.argsort(si[idx])[::-1][:k]]
            return sorted([(fi[i], si[i]) for i in idx])
        lp = top_peaks(2.0, min(8.0, 0.45 * FL), k=1)
        hp = top_peaks(0.55 * FL, 1.2 * FL, k=2)
        if not lp or len(hp) < 1:
            continue
        fl_ = lp[0][0]
        if len(hp) == 2:
            fbl, fsum = hp[0][0], hp[1][0]
        else:
            fbl, fsum = hp[0][0], np.nan
        rows.append((ch, abs(ns[ci]), FL, fl_, fbl, fsum))

arr = [(r[1], r[2], r[3], r[4], r[5]) for r in rows]
arr = np.array(arr)
resid_pair = (arr[:, 2] + arr[:, 3]) - arr[:, 1]        # (f_ML + f_BL) - lam*FL
resid_sum = arr[:, 4] - arr[:, 1]                       # f_upper - lam*FL
print(f"columns tested: {len(arr)} (both channels, unclipped, |n|>=1)")
print(f"pair partition (f_ML + f_BL) - lam*FL: median {np.nanmedian(resid_pair):+.2f} T, "
      f"IQR {np.nanpercentile(resid_pair,25):+.2f}..{np.nanpercentile(resid_pair,75):+.2f}")
print(f"upper tone - lam*FL:                   median {np.nanmedian(resid_sum):+.2f} T, "
      f"IQR {np.nanpercentile(resid_sum,25):+.2f}..{np.nanpercentile(resid_sum,75):+.2f}")
frac2 = np.mean(~np.isnan(arr[:, 4]))
print(f"columns with TWO resolved heavy-band tones: {100*frac2:.0f}%")

fig, ax = plt.subplots(figsize=(8, 5))
ax.scatter(arr[:, 0], resid_pair, s=8, alpha=0.6, label="(f_ML+f_BL) − λF_L")
ax.scatter(arr[:, 0], resid_sum, s=8, alpha=0.6, label="f_upper − λF_L")
ax.axhline(0, color="k", lw=0.7)
ax.axhline(1.7, color="r", lw=0.5, ls=":")
ax.axhline(-1.7, color="r", lw=0.5, ls=":", label="±2δF")
ax.set_xlabel("|n| (10^12 cm^-2)")
ax.set_ylabel("residual (T)")
ax.legend(fontsize=8)
ax.set_title(f"run 7: Luttinger partition residuals, λ = {LAM}")
fig.tight_layout()
fig.savefig("hera_scratch/fan_partition.png", dpi=110)
print("saved fan_partition.png")
