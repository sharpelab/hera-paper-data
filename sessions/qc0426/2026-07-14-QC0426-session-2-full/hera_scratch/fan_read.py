"""Run 7 fan — per-column FFT stack, F(n) traces, partition test."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.constants import h, e as qe
from hera.analysis import open_run, fan_grids, resistance_grids, sdh_fft

run = open_run("data/7")
fg = fan_grids(run)
rg = resistance_grids(fg)
B = np.asarray(fg.slow)                    # 126 rows
ns_design = np.linspace(2.0, 6.3, 51)      # design densities (1e12 cm^-2, geometry scale)
SCALE = 1.07                                # Hall-pinned global scale (runs 5/6)
ns_true = ns_design * SCALE
F_L_line = (h / (4 * qe)) * ns_true * 1e16  # T

R1 = np.asarray(rg.R["sr1"])               # (n_B, n_fast)
R2 = np.asarray(rg.R["sr2"])
print("grids:", R1.shape, "B", B[0], "->", B[-1])

# FFT stack (per column), full window above onset
fr, spec1 = sdh_fft(R1, B, b_range=(1.4, 8.0), bg_degree=5, log=False)
_, spec2 = sdh_fft(R2, B, b_range=(1.4, 8.0), bg_degree=5, log=False)
print("spec:", spec1.shape, "df =", fr[1]-fr[0])

# normalize columns for display
S1 = spec1 / spec1.max(axis=1, keepdims=True)
S2 = spec2 / spec2.max(axis=1, keepdims=True)

fig, axes = plt.subplots(1, 2, figsize=(15, 6), sharey=False)
for ax, S, nm in ((axes[0], S1, "sr1"), (axes[1], S2, "sr2")):
    pm = ax.pcolormesh(fr, ns_true, S, cmap="magma", shading="auto", vmax=1.0)
    ax.plot(F_L_line, ns_true, "c--", lw=1.2, label="F_L(n) Hall-pinned")
    ax.plot(F_L_line * 0.5, ns_true, "c:", lw=0.8, label="F_L/2")
    ax.set_xlim(0, 120); ax.set_xlabel("F (T)")
    ax.set_title(f"{nm} per-column |FFT| (norm)")
    ax.legend(fontsize=8, loc="upper left")
axes[0].set_ylabel("n_true (1e12 cm^-2)")
fig.suptitle("run 7 - per-column SdH FFT stack vs F_L line")
fig.tight_layout(); fig.savefig("hera_scratch/fan_fftstack.png", dpi=110)

# peak tables for representative columns
for ci in (50, 44, 38, 32, 26, 20, 14, 8, 2):
    mag = spec1[ci]
    pk, _ = find_peaks(mag, height=mag.max() * 0.15, distance=3)
    print(f"sr1 n={ns_true[ci]:.2f}: F_L={F_L_line[ci]:.1f} |",
          " ".join(f"{fr[p]:.1f}({mag[p]/mag.max():.2f})" for p in pk))
print("saved hera_scratch/fan_fftstack.png")
