# Run 7 fan — full step-4/5 analysis (scratch iteration)
import sys

sys.path.insert(0, r"C:\Users\DGG\measurement_env\hera\models\trilayer_fs_count")
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from hera.analysis import fan_grids, resistance_grids, sdh_fft, luttinger_frequency

fan = fan_grids("data/7")
rg = resistance_grids(fan)
B = fan.slow                       # (141,) 0.77 -> 8
ns = np.linspace(-0.5, -3.5, 101)  # e12 cm^-2, fast-axis design vector
FLnom = luttinger_frequency(np.abs(ns) * 1e16)  # T

CEIL = {"sr1": 25e3 * 0.95, "sr2": 10e3 * 0.95}
results = {}
for ch in ("sr1", "sr2"):
    R = rg.R[ch]                   # (141, 101)
    clipped = R.max(axis=0) > CEIL[ch]
    f, spec = sdh_fft(R, B, b_range=(0.95, 8.0))   # per-column FFT, all columns
    results[ch] = dict(f=f, spec=spec, clipped=clipped)
    print(f"{ch}: {clipped.sum()} clipped columns (n = "
          f"{ns[clipped].min() if clipped.any() else '—'}..{ns[clipped].max() if clipped.any() else '—'})")

# --- FFT map (the money plot): |n| vs F, log amplitude
fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
for ax, ch in zip(axes, ("sr1", "sr2")):
    f, spec = results[ch]["f"], results[ch]["spec"]
    m = f <= 60
    pm = ax.pcolormesh(np.abs(ns), f[m], spec[:, m].T, shading="auto", cmap="magma")
    ax.plot(np.abs(ns), FLnom, "c--", lw=1, label="F_L (nominal)")
    ax.plot(np.abs(ns), 1.07 * FLnom, "c:", lw=1, label="1.07×F_L")
    ax.set_xlabel("|n| (10^12 cm^-2)")
    ax.set_title(ch)
    ax.legend(fontsize=7, loc="upper left")
    plt.colorbar(pm, ax=ax)
axes[0].set_ylabel("F (T)")
fig.suptitle("run 7 fan: per-column 1/B FFT (log amp), hole side D=0")
fig.tight_layout()
fig.savefig("hera_scratch/fan_fftmap.png", dpi=110)

# --- branch extraction: per column, peaks in [2, 55] T
def col_peaks(f, s, fmin=2.0, fmax=55.0, k=5):
    m = (f >= fmin) & (f <= fmax)
    fi, si = f[m], s[m]
    pk = (si[1:-1] > si[:-2]) & (si[1:-1] > si[2:])
    idx = np.where(pk)[0] + 1
    idx = idx[np.argsort(si[idx])[::-1][:k]]
    return [(fi[i], si[i]) for i in idx]

fig2, ax2 = plt.subplots(figsize=(8, 6))
branch = {"light": [], "heavy": [], "fl": []}
for ci in range(101):
    if results["sr2"]["clipped"][ci]:
        continue
    f, s = results["sr2"]["f"], results["sr2"]["spec"][ci]
    pks = col_peaks(f, s)
    FL = FLnom[ci]
    for fp, amp in pks:
        ax2.plot(abs(ns[ci]), fp, "k.", ms=max(1.5, min(6, amp * 2)), alpha=0.5)
        if fp < 0.35 * FL and fp < 10:
            branch["light"].append((abs(ns[ci]), fp, amp))
        elif 0.6 * FL < fp < 1.0 * FL:
            branch["heavy"].append((abs(ns[ci]), fp, amp))
        elif 1.0 * FL <= fp < 1.35 * FL:
            branch["fl"].append((abs(ns[ci]), fp, amp))
ax2.plot(np.abs(ns), FLnom, "b--", lw=1, label="F_L nominal")
ax2.plot(np.abs(ns), 1.07 * FLnom, "b:", lw=1, label="1.07×F_L")

# --- model curves (ABA pair + ABC singleton), D=0
try:
    from fs_count_b0 import aba_fs, abc_fs
    nmod = np.linspace(0.5, 3.5, 25) * 1e16   # m^-2 (electron); hole side by symmetry flag
    aba_F = []
    for nt in nmod:
        _, fss = aba_fs(-nt)   # hole side: negative density
        aba_F.append(sorted(F for F, kF in fss))
    lens = {len(x) for x in aba_F}
    print("ABA FS counts along n:", lens)
    fml = [x[0] if len(x) > 1 else np.nan for x in aba_F]
    fbl = [x[-1] for x in aba_F]
    ax2.plot(nmod / 1e16, fml, "g-", lw=1.5, label="ABA ML (model)")
    ax2.plot(nmod / 1e16, fbl, "g--", lw=1.5, label="ABA BL (model)")
    abc_F = []
    for nt in nmod:
        out = abc_fs(-nt)
        # abc_fs return: inspect once
        abc_F.append(out)
    print("abc_fs sample:", abc_F[0], abc_F[12])
except Exception as e:
    print("model overlay failed:", e)

ax2.set_xlabel("|n| (10^12 cm^-2)")
ax2.set_ylabel("F (T)")
ax2.set_ylim(0, 55)
ax2.legend(fontsize=7)
ax2.set_title("run 7: sr2 peak set vs model Onsager curves (D=0, hole)")
fig2.tight_layout()
fig2.savefig("hera_scratch/fan_branches.png", dpi=110)

# --- scale pin from the F_L-band tone + Luttinger partition
fl_arr = np.array(branch["fl"])
if len(fl_arr):
    lam = np.median(fl_arr[:, 1] / (FLnom[np.searchsorted(np.abs(ns), fl_arr[:, 0]).clip(0, 100)]))
    print(f"global scale from F_L-band tone: lambda = {lam:.3f}")
hv = np.array(branch["heavy"]); lt = np.array(branch["light"])
print(f"branch counts: light {len(lt)}, heavy {len(hv)}, fl {len(fl_arr)}")
print("saved fan_fftmap.png, fan_branches.png")
