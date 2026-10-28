"""Run 9 fan: per-column FFT spectrogram, tone tracking, Luttinger partition,
Onsager forward-model overlay (scratch)."""
import sys
import numpy as np


import matplotlib.pyplot as plt
from hera.analysis import open_run, fan_grids, resistance_grids, sdh_fft, luttinger_frequency, summarize_run
sys.path.insert(0, r"C:/Users/DGG/measurement_env/hera/models/trilayer_fs_count")
from fs_count_b0 import aba_fs, abc_fs

run = open_run("data/9")
print(summarize_run(run))
assert not run.interrupted

fg = fan_grids(run)
rg = resistance_grids(fg, channels=["sr1", "sr2"])
B = fg.slow
o = np.argsort(B)
Bs = B[o]
ns_label = np.linspace(2.0, 6.2, 81)
SCALE = 1.106                      # electron-side pinned scale
ns_true = ns_label * SCALE         # 1e12 cm^-2
T = fg.grid("T_sample")
print(f"T_sample over fan: {T.min():.3f}-{T.max():.3f} K")

# per-column FFT (uniform-1/B record, no resample)
spec = {}
for ch in ("sr1", "sr2"):
    R = np.abs(rg.R[ch])[o]
    f, s = sdh_fft(R, Bs, b_range=(1.2, 8.0), nfft=4096)
    spec[ch] = (f, s)

# model curves over the fan window
n_grid = np.linspace(ns_true[0], ns_true[-1], 60)
aba_ml, aba_bl, abc_f = [], [], []
for n12 in n_grid:
    _, orb = aba_fs(n12 * 1e16)
    Fs = sorted(Fk[0] for Fk in orb)
    aba_ml.append(Fs[0]); aba_bl.append(Fs[-1])
    _, _, _, _, Ft = abc_fs(n12 * 1e16)
    abc_f.append(Ft)
FL = np.array([float(luttinger_frequency(n12 * 1e16)) for n12 in n_grid])

fig, axes = plt.subplots(1, 2, figsize=(15, 6), sharey=True)
for ax, ch in zip(axes, ("sr1", "sr2")):
    f, s = spec[ch]
    m = f < 160
    pc = ax.pcolormesh(f[m], ns_true, s[:, m], shading="auto", cmap="magma")
    ax.plot(np.array(aba_ml), n_grid, "c--", lw=1.2, label="ABA ML (model)")
    ax.plot(np.array(aba_bl), n_grid, "c-.", lw=1.2, label="ABA BL (model)")
    ax.plot(np.array(abc_f), n_grid, "g-", lw=1.2, label="ABC singleton (model)")
    ax.plot(FL, n_grid, "w:", lw=1.2, label="F_L")
    ax.set_xlabel("F (T)"); ax.set_title(f"{ch} per-column FFT")
    ax.legend(fontsize=7, loc="upper left")
    fig.colorbar(pc, ax=ax)
axes[0].set_ylabel("n_true (1e12 cm^-2, scale 1.106x)")
fig.suptitle("run 9 fan: per-column SdH FFT vs forward-model Onsager curves (single global rescale 1.106)")
fig.tight_layout(); plt.show()

# quantitative tone tracks: strongest peak in model-guided bands per column
def track(f, s, centers, halfw):
    out = np.full(len(centers), np.nan)
    for i, (c, h) in enumerate(zip(centers, halfw)):
        m = (f > c - h) & (f < c + h)
        if m.sum() > 3:
            sp = s[i][m]
            j = sp.argmax()
            if sp[j] > 2.0 * np.median(s[i][(f > 20) & (f < 150)]):
                out[i] = f[m][j]
    return out

ml_c = np.interp(ns_true, n_grid, aba_ml)
bl_c = np.interp(ns_true, n_grid, aba_bl)
fl_c = np.interp(ns_true, n_grid, FL)
res = {}
for ch in ("sr1", "sr2"):
    f, s = spec[ch]
    tr_ml = track(f, s, ml_c, np.full(81, 6.0))
    tr_bl = track(f, s, bl_c, 0.12 * bl_c)
    tr_fl = track(f, s, fl_c, np.minimum(0.08 * fl_c, (fl_c - bl_c) * 0.7))
    res[ch] = (tr_ml, tr_bl, tr_fl)
    ok = ~np.isnan(tr_ml) & ~np.isnan(tr_bl)
    part = (tr_ml + tr_bl)[ok] / fl_c[ok]
    print(f"{ch}: ML tracked {np.sum(~np.isnan(tr_ml))}/81, BL {np.sum(~np.isnan(tr_bl))}/81, "
          f"FL-tone {np.sum(~np.isnan(tr_fl))}/81; partition (ML+BL)/F_L = "
          f"{np.nanmean(part):.3f} +/- {np.nanstd(part):.3f} over {ok.sum()} cols")

# harmonic screen on the ML family: does the '2xML' band track exactly 2x the ML track?
fig2, ax2 = plt.subplots(figsize=(8, 5))
for ch, mk in (("sr1", "o"), ("sr2", "s")):
    tr_ml, tr_bl, tr_fl = res[ch]
    ax2.plot(ns_true, tr_ml, mk, ms=3, label=f"{ch} ML-band")
    ax2.plot(ns_true, tr_bl, mk, ms=3, mfc="none", label=f"{ch} BL-band")
    ax2.plot(ns_true, tr_fl, mk, ms=2, alpha=0.5, label=f"{ch} FL-band")
ax2.plot(ns_true, ml_c, "c--", lw=1); ax2.plot(ns_true, bl_c, "c-.", lw=1)
ax2.plot(ns_true, fl_c, "k:", lw=1)
ax2.set_xlabel("n_true (1e12)"); ax2.set_ylabel("F (T)"); ax2.legend(fontsize=7)
fig2.suptitle("tracked tone families vs model curves")
fig2.tight_layout(); plt.show()

