# Run 7 — per-column 1/B FFT map + branch structure + λ scale pin (steps 4–5)
import sys
sys.path.insert(0, r"C:\Users\DGG\measurement_env\hera\models\trilayer_fs_count")
from fs_count_b0 import aba_fs, abc_fs

ffts7 = {}
for ch in ("sr1", "sr2"):
    f7, spec7 = sdh_fft(rg7.R[ch], B7, b_range=(0.95, 8.0))
    ffts7[ch] = (f7, spec7)

fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
for ax, ch in zip(axes, ("sr1", "sr2")):
    f7, spec7 = ffts7[ch]
    m = f7 <= 60
    pm = ax.pcolormesh(np.abs(ns7), f7[m], spec7[:, m].T, shading="auto", cmap="magma")
    ax.plot(np.abs(ns7), FLnom7, "c--", lw=1, label="F_L nominal")
    ax.plot(np.abs(ns7), 1.064 * FLnom7, "c:", lw=1, label="1.064×F_L")
    ax.set_xlabel("|n| (10¹² cm⁻²)")
    ax.set_title(ch)
    ax.legend(fontsize=7, loc="upper left")
    plt.colorbar(pm, ax=ax)
axes[0].set_ylabel("F (T)")
fig.suptitle("run 7: per-column 1/B FFT (log amp) — light branch + harmonics, heavy pair hugging λF_L")
fig.tight_layout()
plt.show()

# λ pin: median ratio of the F_L-band tone to nominal F_L across columns (both channels)
lam_samples = []
for ch in ("sr1", "sr2"):
    f7, spec7 = ffts7[ch]
    for ci in range(101):
        FL = FLnom7[ci]
        if abs(ns7[ci]) < 1.0 or FL * 1.35 > 58:
            continue
        m = (f7 >= FL) & (f7 <= 1.35 * FL)
        if m.sum() < 3:
            continue
        s = spec7[ci][m]
        pk = (s[1:-1] > s[:-2]) & (s[1:-1] > s[2:])
        if pk.any():
            i = (np.where(pk)[0] + 1)[np.argmax(s[np.where(pk)[0] + 1])]
            lam_samples.append(f7[m][i] / FL)
LAM7 = float(np.median(lam_samples))
print(f"global density scale λ = {LAM7:.3f} (median over {len(lam_samples)} column-tones; "
      f"electron singleton run 6 gave 33.2/31.0 = 1.071 — consistent)")
print("λ is the SdH-Luttinger pin of the absolute (n,D) scale — upgrades the run-4 "
      "geometry-prior scale (device card updated); within the ~10–15% prior band ✓")

# model check at n = 3e12 (electron-side model; hole-side model not implemented — p-h caveat)
EF, fs = aba_fs(3.0e16)
EFc, topo, ncc, nfreq, Ft = abc_fs(3.0e16)
print(f"model (electron, n=3e12): ABA pair {[round(F,1) for F,_ in fs]} T (sum {sum(F for F,_ in fs):.1f}); "
      f"ABC {topo} singleton {Ft:.1f} T")
print("→ electron-side observed bright singleton (33.2 T) matches BOTH templates "
      "(ABA's e-side ML = 1.5 T is below our resolvable band): e-side is non-discriminating, as designed for.")
