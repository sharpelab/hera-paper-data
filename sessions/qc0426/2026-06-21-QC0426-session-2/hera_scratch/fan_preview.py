import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import fan_grids, resistance_grids, sdh_fft
import scipy.constants as cst

fan = fan_grids("data/5")
ci = {c: i for i, c in enumerate(fan.cols)}
G = fan.data.reshape(fan.nrows, fan.nfast, len(fan.cols))
Bax = G[:, 0, ci["magnet_field"]]                 # slow B values
rg = resistance_grids(fan)
R1 = rg.R["sr1"]; R2 = rg.R["sr2"]                 # (nrows, 40)
n_vec = np.linspace(0.5e16, 3.5e16, 40)            # column densities
F_L = cst.h / (4 * cst.e) * n_vec
print(f"complete B-rows: {fan.nrows}, B {Bax.min():.2f}..{Bax.max():.2f} T")

order = np.argsort(Bax); Bs = Bax[order]
cutoff = max(2.6, Bs.min())
def col_peaks(R):
    Rs = R[order, :]
    f, mag = sdh_fft(Rs, Bs, b_range=(cutoff, Bs.max()), bg_degree=5)
    mag = np.asarray(mag)              # (nfreq, ncols)
    peaks = []
    for j in range(mag.shape[0]):
        m = mag[j, :]
        sel = f > 2.0
        peaks.append(f[sel][np.argmax(m[sel])])
    return np.array(peaks)

p1 = col_peaks(R1); p2 = col_peaks(R2)
print("clean cols (n>=1.5e12): F_peak vs F_L  (ratio ~1 => single pocket@F_L=ABC; <1 => below F_L)")
for j in range(len(n_vec)):
    if n_vec[j] >= 1.5e16:
        print(f"  n={n_vec[j]/1e16:+.2f}e12  F_L={F_L[j]:5.1f}T  sr1={p1[j]:5.1f}T (r{p1[j]/F_L[j]:.2f})  sr2={p2[j]:5.1f}T (r{p2[j]/F_L[j]:.2f})")

fig, ax = plt.subplots(figsize=(7, 5))
ax.plot(n_vec/1e16, F_L, "k--", label="F_L (single 4-fold pocket)")
ax.plot(n_vec/1e16, F_L/2, "k:", lw=0.8, label="F_L/2")
m = n_vec >= 1.5e16
ax.plot(n_vec[m]/1e16, p1[m], "o", color="C0", label="sr1 F_peak")
ax.plot(n_vec[m]/1e16, p2[m], "s", color="C1", label="sr2 F_peak")
ax.set_xlabel("n [10^12 cm^-2]"); ax.set_ylabel("F [T]"); ax.legend()
ax.set_title(f"PARTIAL fan F(n) preview ({fan.nrows}/96 rows, B>{cutoff:.1f}T, df~{1/(1/cutoff-1/Bs.max()):.1f}T)")
fig.tight_layout(); fig.savefig("hera_scratch/fan_preview.png", dpi=110)
print("saved hera_scratch/fan_preview.png")
