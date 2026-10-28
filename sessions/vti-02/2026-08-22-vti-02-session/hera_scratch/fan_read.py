"""Fan read (partial or complete): re-form R(n, B), raw pcolormesh, per-column SdH FFT in 1/B, peak tracks F(n),
overlay ABAB / ABCA model curves under a global density scale; Luttinger sum per column."""
import sys, json, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import fan_grids, resistance_grids, sdh_fft, luttinger_frequency
from sharpelab_nb.gates import calc_nD
sys.path.insert(0, r"C:\Users\DGG\measurement_env\hera\models\tetralayer_fs_count")
import fs_count_b0 as fsm

rid = int(sys.argv[1]); scale = float(sys.argv[2]) if len(sys.argv) > 2 else 0.886
cal = json.load(open("hera_scratch/cal_run5.json"))
g = fan_grids(f"data/{rid}"); rg = resistance_grids(g); R = rg.R["sr1"]; B = g.slow
fs = g.meta["fast_setpoints"]; Vtg = np.asarray(fs[0]); Vbg = np.asarray(fs[1])
n12, D = calc_nD(Vtg, Vbg, cal["c_tg"], cal["c_bg"], cal["n_offset"], cal["D_offset"])
print(f"run {rid}: {g.nrows} rows (B {B.min():.2f}-{B.max():.2f} T) x {g.nfast} n-pts (n {n12.min():.2f}-{n12.max():.2f}e12, D {D.min():+.3f}..{D.max():+.3f}); R {np.nanmin(R):.0f}..{np.nanmax(R):.0f} Ohm")
fig, ax = plt.subplots(1, 3, figsize=(18, 5.5))
m = ax[0].pcolormesh(n12, B, R, shading="nearest", cmap="RdBu_r", vmin=-np.percentile(np.abs(R), 98), vmax=np.percentile(np.abs(R), 98))
fig.colorbar(m, ax=ax[0], label="R = X/I (Ohm)"); ax[0].set_xlabel("n (1e12)"); ax[0].set_ylabel("B (T)"); ax[0].set_title(f"run {rid} raw (signed, rho_xy admixture)")
# per-column FFT
if g.nrows >= 12:
    lo, hi = B.min(), min(B.max(), 6.0) if B.max() > 6.5 else B.max()
    f, spec = sdh_fft(R, B, b_range=(lo, hi), bg_degree=3 if g.nrows < 30 else 5, log=False, nfft=2048)
    spec = spec / spec[:, f > 2].max(axis=1, keepdims=True)
    m2 = ax[1].pcolormesh(f, n12, spec, shading="nearest", cmap="magma", vmin=0, vmax=1)
    ax[1].set_xlim(0, 60); ax[1].set_xlabel("F (T)"); ax[1].set_ylabel("n (1e12)"); ax[1].set_title(f"per-column |FFT| [{lo:.1f},{hi:.1f}] T, dF={1/(1/lo-1/hi):.1f} T")
    # model overlays: ABAB (light, heavy), ABCA singleton, trilayer for adjacent-N, vs n_true = scale * n_cal
    nn = np.linspace(max(n12.min(), 1.0), n12.max(), 25)
    FL = luttinger_frequency(scale * nn * 1e16)
    ab = np.array([[F for F, k in fsm.abab_fs(scale * x * 1e16)[1]][:2] for x in nn])
    tri = np.array([[F for F, k in fsm.bernal_fs(scale * x * 1e16, "ABA", fsm.ABA_TRI)[1]][:2] for x in nn]) if hasattr(fsm, "bernal_fs") else None
    ax[1].plot(FL, nn, "w--", lw=1, label=f"F_L x{scale}"); ax[1].plot(ab[:, 0], nn, "c-", lw=1, label="ABAB light/heavy"); ax[1].plot(ab[:, 1], nn, "c-", lw=1)
    ax[1].plot(ab.sum(axis=1), nn, "c:", lw=1, label="ABAB sum"); ax[1].plot(2 * ab[:, 0], nn, "y:", lw=0.8, label="2 x light")
    if tri is not None: ax[1].plot(tri[:, 0], nn, "g-", lw=0.8, label="trilayer ML+BL"); ax[1].plot(tri[:, 1], nn, "g-", lw=0.8)
    ax[1].legend(fontsize=7, loc="lower right")
    # peak tracks per column + Luttinger check
    print("col  n_cal  n_true   peaks(T, norm)                      sum of top two fundamentals vs F_L")
    tracks = []
    for j in range(0, g.nfast, max(1, g.nfast // 15)):
        s = spec[j]; pk = [(f[i], s[i]) for i in range(2, len(f) - 1) if s[i] > s[i-1] and s[i] > s[i+1] and s[i] > 0.25 and 3 < f[i] < 60]
        pk = sorted(pk, key=lambda p: -p[1])[:5]
        print(f"{j:3d}  {n12[j]:.2f}  {scale*n12[j]:.2f}   " + ", ".join(f"{a:.1f}({b:.2f})" for a, b in sorted(pk)) + f"   F_L={FL[np.argmin(abs(nn-n12[j]))]:.1f}")
        tracks.append((n12[j], pk))
    ax[2].plot(nn, FL, "k--", label=f"F_L x{scale}"); ax[2].plot(nn, ab[:, 0], "c-", label="ABAB"); ax[2].plot(nn, ab[:, 1], "c-"); ax[2].plot(nn, ab.sum(axis=1), "c:", label="ABAB sum"); ax[2].plot(nn, 2 * ab[:, 0], "y:", label="2x light")
    for j in range(g.nfast):
        s = spec[j]; pk = [(f[i], s[i]) for i in range(2, len(f) - 1) if s[i] > s[i-1] and s[i] > s[i+1] and s[i] > 0.25 and 3 < f[i] < 60]
        for a, b in pk: ax[2].plot(n12[j], a, "o", ms=3 + 4 * b, color="r", alpha=0.5)
    ax[2].set_xlabel("n_cal (1e12)"); ax[2].set_ylabel("F (T)"); ax[2].set_ylim(0, 60); ax[2].legend(fontsize=7); ax[2].set_title("measured peaks (size = strength) vs model")
fig.tight_layout(); fig.savefig(f"hera_scratch/fan_run{rid}.png", dpi=110); print(f"saved hera_scratch/fan_run{rid}.png")
