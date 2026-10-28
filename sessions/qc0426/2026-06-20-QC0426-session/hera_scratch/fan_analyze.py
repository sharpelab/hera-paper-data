import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, fan_grids, resistance_grids, sdh_fft
from sharpelab_nb import gates
h, e = 6.62607e-34, 1.602177e-19
C_TG, C_BG, N_OFF = 1.7027e-3, 2.2024e-3, -0.1445

r = open_run("data/3"); mc = r.meta["measurement_config"]
fg = fan_grids(r); rg = resistance_grids(fg)
B = np.asarray(fg.slow)                                  # (nB,) field rows
Vtg_grid = fg.grid("DC_bias")                            # (nB, nn)
Vtg = Vtg_grid[0]; Vbg = fg.grid("k_2400_volt")[0]       # fast-axis gate vectors
n_col = gates.calc_nD(Vtg, Vbg, C_TG, C_BG, N_OFF, 0.0)[0]   # 1e12 cm^-2 per column
F_L = (h / (4 * e)) * (np.abs(n_col) * 1e16)             # Luttinger line per column (T)
print(f"fan: B {B.min():.2f}-{B.max():.2f}T x {len(B)} | n {n_col.min():.2f}..{n_col.max():.2f}e12 x {len(n_col)}")

fig, axes = plt.subplots(2, 3, figsize=(17, 9))
for row, ch in enumerate(["sr1", "sr2"]):
    R = np.asarray(rg.R[ch])                              # (nB, nn) signed
    sens = mc.get(f"{ch}_sens", np.inf)
    # rail mask from raw X grid
    Xg = fg.grid(f"{ch}_X")
    Rabs = np.abs(R)
    # (a) raw fan heatmap (clip color)
    ax = axes[row, 0]
    pc = ax.pcolormesh(n_col, B, np.clip(Rabs, 0, 4000), shading="auto", cmap="inferno")
    ax.set_xlabel("n (1e12)"); ax.set_ylabel("B (T)"); ax.set_title(f"{ch} |Rxx|(n,B)"); fig.colorbar(pc, ax=ax)
    # (b) per-column SdH FFT -> F(n)
    f1, f2, fdom = [], [], []
    spec_stack = []
    for j in range(len(n_col)):
        col = R[:, j].copy()
        railed = np.abs(Xg[:, j]) > 0.88 * sens
        good = np.isfinite(col) & ~railed & (B >= 1.5)
        if good.sum() < 8:
            f1.append(np.nan); f2.append(np.nan); fdom.append(np.nan); spec_stack.append(None); continue
        Bc, Rc = B[good], col[good]
        freqs, spec = sdh_fft(Rc.reshape(-1, 1), Bc, b_range=(Bc.min(), Bc.max()), bg_degree=5)
        mag = spec[0]; m = (freqs > 6) & (freqs < 55)     # >6T: skip envelope artifact band
        fm, mm = freqs[m], mag[m]
        from scipy.signal import find_peaks
        pk, _ = find_peaks(mm, height=0.25 * mm.max())
        pk = sorted(pk, key=lambda i: -mm[i])
        fdom.append(fm[pk[0]] if pk else np.nan)
        f1.append(fm[pk[0]] if len(pk) >= 1 else np.nan)
        f2.append(fm[pk[1]] if len(pk) >= 2 else np.nan)
        spec_stack.append((fm, mm / mm.max()))
    f1, f2, fdom = np.array(f1), np.array(f2), np.array(fdom)
    # (c) F(n) vs F_L
    ax = axes[row, 1]
    ax.plot(n_col, F_L, "g-", lw=1.5, label="F_L=(h/4e)n")
    ax.plot(n_col, F_L / 2, "g:", lw=1, label="F_L/2")
    ax.scatter(n_col, f1, s=22, c="cyan", label="dom peak")
    ax.scatter(n_col, f2, s=14, c="magenta", label="2nd peak")
    ax.scatter(n_col, f1 + f2, s=10, c="orange", label="f1+f2")
    ax.set_xlabel("n (1e12)"); ax.set_ylabel("F (T)"); ax.set_title(f"{ch} F(n) vs Luttinger"); ax.legend(fontsize=7)
    # (d) FFT waterfall (freq vs n heatmap)
    ax = axes[row, 2]
    fgrid = np.linspace(6, 55, 120)
    Z = np.full((len(n_col), len(fgrid)), np.nan)
    for j, s in enumerate(spec_stack):
        if s is not None:
            Z[j] = np.interp(fgrid, s[0], s[1])
    pc = ax.pcolormesh(fgrid, n_col, Z, shading="auto", cmap="viridis")
    ax.plot(F_L, n_col, "w-", lw=1); ax.plot(F_L / 2, n_col, "w:", lw=1)
    ax.set_xlabel("SdH freq (T)"); ax.set_ylabel("n (1e12)"); ax.set_title(f"{ch} FFT(n) waterfall"); fig.colorbar(pc, ax=ax)
    print(f"{ch}: F_dom(n) = " + " ".join(f"{f:.0f}" for f in fdom[::3] if np.isfinite(f)))
    sel = np.isfinite(f1) & np.isfinite(f2)
    if sel.sum() > 3:
        print(f"{ch}: median (f1+f2)/F_L = {np.nanmedian((f1[sel]+f2[sel])/F_L[sel]):.2f}  | median f1/F_L = {np.nanmedian(f1[sel]/F_L[sel]):.2f}")
plt.tight_layout(); plt.savefig("hera_scratch/fan_analyze.png", dpi=110)
print("saved hera_scratch/fan_analyze.png")
