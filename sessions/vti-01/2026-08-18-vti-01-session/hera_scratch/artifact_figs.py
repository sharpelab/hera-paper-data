# Artifact figures — dark-styled, page palette (scratch)
import sys
import numpy as np
from pathlib import Path
sys.path.insert(0, str(Path.home() / "measurement_env/hera/models/trilayer_fs_count"))
from fs_count_b0 import aba_fs
from hera.analysis import open_run, sdh_fft
from scipy.signal import find_peaks
from scipy.optimize import curve_fit
import scipy.constants as cst
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

GROUND, SURF, INK, MUTED = "#101318", "#181d24", "#e8e6e1", "#9aa3ad"
AMBER, TEAL, VIOLET = "#cf7229", "#35a08a", "#a86ab0"
plt.rcParams.update({
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
    "text.color": INK, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.titlecolor": INK,
    "font.size": 11, "axes.grid": False,
})

NF = 53
r = open_run("data/19")
gr = lambda c: c[:len(c) // NF * NF].reshape(-1, NF)
B = gr(r.col("magnet_field"))[:, 0]
i_dr = gr(np.abs(r.col("sr0_X")) / 1e6)
ns = np.linspace(-0.70, -1.74, NF)
R1 = gr(r.col("sr1_X")) / i_dr

# ---- Fig 1: hero fan — per-column background-subtracted ΔRxx(B, n) ----
dR = np.empty_like(R1)
for j in range(NF):
    p = np.polyfit(B, R1[:, j], 5)
    dR[:, j] = R1[:, j] - np.polyval(p, B)
lim = np.percentile(np.abs(dR), 97)
fig, ax = plt.subplots(figsize=(10.5, 6.2))
pm = ax.pcolormesh(ns, B, dR / 1e3, shading="nearest", cmap="PuOr_r",
                   vmin=-lim / 1e3, vmax=lim / 1e3, rasterized=True)
cb = fig.colorbar(pm, ax=ax, pad=0.015, label="ΔR$_{xx}$ (kΩ)")
cb.outline.set_edgecolor(MUTED)
ax.set_xlabel("carrier density  n  (10$^{12}$ cm$^{-2}$)")
ax.set_ylabel("magnetic field  B  (T)")
ax.set_title("vti-01 · Landau fan · D = 0, hole side · 1.24 K · τ = 300 ms", pad=12)
fig.tight_layout(); fig.savefig("hera_scratch/art_fan_hero.png", dpi=170)
plt.close(fig)

# ---- Fig 2: per-column FFT map + branches + ABA model (λ = 1.14) ----
f, spec = sdh_fft(R1, B, b_range=(0.92, 5.0), bg_degree=4)
S = spec / spec.max(axis=1, keepdims=True)
tab = []
for j in range(NF):
    s = S[j]
    p, _ = find_peaks(s, prominence=0.12)
    pk = [(f[i], s[i]) for i in p]
    fA = max((x for x in pk if 5 < x[0] < 20), key=lambda t: t[1], default=(np.nan,) * 2)[0]
    fML = max((x for x in pk if 1.2 < x[0] < 5), key=lambda t: t[1], default=(np.nan,) * 2)[0]
    tab.append((ns[j], fML, fA))
tab = np.array(tab)
lam = 1.14
FLs = cst.h * np.abs(ns) * 1e16 / (4 * cst.e)
fig, ax = plt.subplots(figsize=(10.5, 5.6))
pm = ax.pcolormesh(ns, f, S.T, shading="nearest", cmap="magma", vmax=1, rasterized=True)
cb = fig.colorbar(pm, ax=ax, pad=0.015, label="per-column FFT (norm.)")
cb.outline.set_edgecolor(MUTED)
clean = np.abs(tab[:, 0]) < 1.47   # columns where the peak extraction is unambiguous
ax.plot(tab[clean, 0], tab[clean, 1], "^", color=TEAL, ms=5, mec=GROUND, mew=0.5, label="measured f$_{ML}$ (run 19)")
ax.plot(tab[clean, 0], tab[clean, 2], "o", color=TEAL, ms=5, mec=GROUND, mew=0.5, label="measured f$_{BL}$ (run 19)")
ax.plot([-1.74], [4.4], "D", color=AMBER, ms=7, mec=GROUND, mew=0.6, label="run 20 (δF = 0.72 T)")
ax.plot([-1.74], [16.4], "D", color=AMBER, ms=7, mec=GROUND, mew=0.6)
aba_ml, aba_bl = [], []
for n in ns:
    Fs = sorted(F for F, _ in aba_fs(n * lam * 1e16)[1])
    aba_ml.append(Fs[0] if len(Fs) > 1 else np.nan); aba_bl.append(Fs[-1])
ax.plot(ns, aba_ml, "-.", color=VIOLET, lw=1.6, label="ABA model f$_{ML}$ (n×1.14)")
ax.plot(ns, aba_bl, "--", color=VIOLET, lw=1.6, label="ABA model f$_{BL}$ (n×1.14)")
ax.plot(ns, lam * FLs, ":", color=INK, lw=1.2, label="1.14·F$_L$ (Luttinger)")
ax.set_ylim(0, 30); ax.set_xlabel("n (10$^{12}$ cm$^{-2}$)"); ax.set_ylabel("frequency F (T)")
leg = ax.legend(fontsize=8, loc="upper left", facecolor=SURF, edgecolor=MUTED, labelcolor=INK)
ax.set_title("Two Fermi surfaces: ML + BL branches vs the ABA (Bernal) model", pad=12)
fig.tight_layout(); fig.savefig("hera_scratch/art_fft_map.png", dpi=170)
plt.close(fig)

# ---- Fig 3: run-20 spectrum — ML confirmation at n = −1.74 ----
r20 = open_run("data/20")
B20 = r20.col("magnet_field")
i20 = np.abs(r20.col("sr0_X")) / 1e6
fig, ax = plt.subplots(figsize=(10.5, 4.4))
for ch, col, off, lbl in (("sr1", AMBER, 0.0, "sr1 (B$_{SD}$–L4)"),
                          ("sr3", TEAL, 1.15, "sr3 (L3–L2)")):
    fq, s = sdh_fft((r20.col(f"{ch}_X") / i20)[:, None], B20, b_range=(0.9, 5.0), bg_degree=5)
    y = s[0] / s[0].max() + off
    ax.plot(fq, y, color=col, lw=1.5)
    ax.text(28.5, off + 0.08, lbl, color=col, fontsize=9, ha="right")
for v, lbl in ((4.4, "f$_{ML}$"), (12.0, "f$_{BL}$−f$_{ML}$"), (16.4, "f$_{BL}$"), (20.6, "1.14·F$_L$")):
    ax.axvline(v, color=MUTED, ls=":", lw=0.8, alpha=0.7)
    ax.text(v - 0.25, 2.14, lbl, rotation=90, fontsize=8.5, color=INK, ha="right", va="top")
ax.set_xlim(0, 29); ax.set_ylim(-0.05, 2.3)
ax.set_xlabel("frequency F (T)"); ax.set_ylabel("FFT (norm., offset)")
ax.set_yticks([])
ax.set_title("ML pocket at n = −1.74×10$^{12}$: f$_{ML}$ + f$_{BL}$ = 20.8 T ≈ 1.14·F$_L$", pad=12)
fig.tight_layout(); fig.savefig("hera_scratch/art_ml.png", dpi=170)
plt.close(fig)

# ---- Fig 4: LK panel ----
B_EFF = 1 / ((1 / 2.0 + 1 / 5.0) / 2); C_LK = 14.69 / B_EFF
def amp_at(fq, s, F0, half=2.0):
    m = (fq > F0 - half) & (fq < F0 + half)
    return s[m].max()
Ts, aA, aH = [], [], []
for rid in range(12, 19):
    rr = open_run(f"data/{rid}")
    Bx = rr.col("magnet_field"); ii = np.abs(rr.col("sr0_X")) / 1e6
    fq, s = sdh_fft((rr.col("sr1_X") / ii)[:, None], Bx, b_range=(2.0, 5.0), bg_degree=4)
    Ts.append(np.mean(rr.col("T_sample"))); aA.append(amp_at(fq, s[0], 16.2)); aH.append(amp_at(fq, s[0], 8.1))
Ts, aA, aH = map(np.array, (Ts, aA, aH))
def lk(T, m, a0):
    X = C_LK * m * T
    return a0 * X / np.sinh(X)
fig, ax = plt.subplots(figsize=(10.5, 4.4))
Tf = np.linspace(0.8, 16, 200)
for amps, col, lbl in ((aA, AMBER, "f$_{BL}$ (16.4 T)"), (aH, VIOLET, "f$_{BL}$/2 modulation")):
    p, cov = curve_fit(lk, Ts, amps, p0=[0.08, amps[0] * 1.2], bounds=([0.001, 0], [1, np.inf]))
    ax.plot(Tf, lk(Tf, *p), color=col, lw=1.4)
    ax.plot(Ts, amps, "o", color=col, ms=7, mec=GROUND, mew=0.6)
    ax.text(Ts[2] + 0.4, amps[2] + 0.12, f"{lbl}:  m* = {p[0]:.3f}±{np.sqrt(cov[0,0]):.3f} m$_e$",
            color=col, fontsize=9.5)
ax.plot(Tf, lk(Tf, 0.108, aA[0] / (lk(1.25, 0.108, 1))), ls=":", color=MUTED, lw=1.2)
ax.text(5.6, 0.28, "ABC prediction (0.108 m$_e$) — excluded", color=MUTED, fontsize=8.5, rotation=-18)
ax.set_xlabel("temperature (K)"); ax.set_ylabel("SdH amplitude (arb.)")
ax.set_title("Lifshitz–Kosevich mass, n = −1.74×10$^{12}$, B$_{eff}$ = 2.9 T (runs 12–18)", pad=12)
fig.tight_layout(); fig.savefig("hera_scratch/art_lk.png", dpi=170)
plt.close(fig)
print("figures written")
