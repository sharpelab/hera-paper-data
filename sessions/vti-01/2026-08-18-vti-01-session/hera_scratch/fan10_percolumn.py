# Run 10 per-column FFT read (scratch first)
import sys
import numpy as np
from pathlib import Path
sys.path.insert(0, str(Path.home() / "measurement_env/hera/models/trilayer_fs_count"))
from fs_count_b0 import aba_fs, abc_fs
from hera.analysis import open_run, sdh_fft
from scipy.signal import find_peaks
import scipy.constants as cst
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

NFAST = 53
r = open_run("data/10")
B_all = r.col("magnet_field")
i_dr = np.abs(r.col("sr0_X")) / 1e6
nrows = len(B_all) // NFAST
gr = lambda c: c[:nrows * NFAST].reshape(nrows, NFAST)
B = gr(B_all)[:, 0]
ns = np.linspace(-0.70, -1.74, NFAST)  # design n-vector (1e12 cm^-2)
print(f"rows {nrows}/71, B {B.min():.2f}-{B.max():.2f} T")

fig, axs = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
for ax, ch in zip(axs, ("sr1", "sr3")):
    R = gr(r.col(f"{ch}_X")) / gr(i_dr)
    f, spec = sdh_fft(R, B, b_range=(1.7, 5.0), bg_degree=5)
    S = spec / spec.max(axis=1, keepdims=True)          # per-column normalized
    pm = ax.pcolormesh(ns, f, S.T, shading="nearest", cmap="magma", vmax=1.0)
    # F_L line and harmonics of it
    FL = cst.h * np.abs(ns) * 1e16 / (4 * cst.e)
    ax.plot(ns, FL, "c--", lw=1, label="F_L (scale 1)")
    ax.plot(ns, 0.92 * FL, "c:", lw=1, label="0.92 F_L")
    # model branches
    aba1, aba2, abcF = [], [], []
    for n in ns:
        _, orb = aba_fs(n * 1e16)
        Fs = sorted(F for F, _ in orb)
        aba1.append(Fs[0] if len(Fs) > 1 else np.nan)
        aba2.append(Fs[-1])
        abcF.append(abc_fs(n * 1e16)[4])
    ax.plot(ns, aba1, "g-.", lw=1, label="ABA f_ML")
    ax.plot(ns, aba2, "g--", lw=1, label="ABA f_BL")
    ax.plot(ns, abcF, "m--", lw=1, label="ABC F_tot")
    ax.set_title(f"{ch}: per-column FFT"); ax.set_xlabel("n (1e12 cm^-2)")
    ax.set_ylim(0, 45)
axs[0].set_ylabel("F (T)"); axs[0].legend(fontsize=6, loc="upper left")
fig.tight_layout(); fig.savefig("hera_scratch/fan10_fftmap.png", dpi=110)

# peak table per column (sr1): fundamentals + partition test
print("\nn(e12)  peaks (F[T], rel amp)")
R = gr(r.col("sr1_X")) / gr(i_dr)
f, spec = sdh_fft(R, B, b_range=(1.7, 5.0), bg_degree=5)
rows_out = []
for j in range(NFAST):
    s = spec[j] / spec[j].max()
    p, _ = find_peaks(s, prominence=0.15)
    pk = [(f[i], s[i]) for i in p if 2 < f[i] < 45]
    rows_out.append((ns[j], pk))
for n, pk in rows_out[::4]:
    print(f"{n:+.2f}  " + "  ".join(f"{x:5.1f}({a:.2f})" for x, a in pk))
print("saved hera_scratch/fan10_fftmap.png")
