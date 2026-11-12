"""CNP calibration — overlay figure + closure + calibration numbers."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from scipy.constants import epsilon_0, e as qe
from hera.analysis import open_run, fan_grids, resistance_grids, GateCalibration

run = open_run("data/4")
fg = fan_grids(run)
rg = resistance_grids(fg)
vbg = fg.slow
vtg = np.asarray(fg.grid("k_2400_tg_volt"))[0]
RAIL = 4.3e3

def extract(ch):
    R = np.asarray(rg.R[ch])
    ridge_v, keep = [], []
    for i in range(R.shape[0]):
        row = gaussian_filter1d(R[i], 2)
        j = int(np.argmax(row))
        railed = np.sum(R[i] > RAIL) >= 3
        if railed:
            idx = np.where(R[i] > RAIL)[0]
            if idx.max() - idx.min() < 20:
                j = int(np.round(idx.mean()))
            else:
                ridge_v.append(np.nan); keep.append(False); continue
        edge = j <= 2 or j >= len(row) - 3
        ridge_v.append(vtg[j]); keep.append(not edge)
    ridge_v = np.array(ridge_v); keep = np.array(keep)
    k = keep & np.isfinite(ridge_v)
    for _ in range(4):
        p = np.polyfit(vbg[k], ridge_v[k], 1)
        res = ridge_v - np.polyval(p, vbg)
        s = np.nanstd(res[k])
        k2 = keep & np.isfinite(ridge_v) & (np.abs(res) < 2 * s)
        if k2.sum() == k.sum(): break
        k = k2
    return ridge_v, k, p

fits = {ch: extract(ch) for ch in ("sr1", "sr2")}

# --- calibration: anchor c_tg at geometry (AFM 15.6 nm hBN), ratio from mean slope
c_tg = epsilon_0 * 3 / 15.6e-9
ratio = -np.mean([fits["sr1"][2][0], fits["sr2"][2][0]])
c_bg = ratio * c_tg
b = np.mean([fits["sr1"][2][1], fits["sr2"][2][1]])
n_cnp = c_tg * b / qe                       # m^-2 at (b, 0)
cal = GateCalibration(c_tg, c_bg, n_offset=-(-n_cnp))  # n_offset so n=0 on ridge
# careful with sign: n(Vtg,Vbg) = (c_tg Vtg + c_bg Vbg)/e + n_offset; want n=0 at Vtg=b,Vbg=0
n_offset = -c_tg * b / qe
cal = GateCalibration(c_tg, c_bg, n_offset=n_offset)

# closure: n along fitted ridge (sr-mean line)
vv = np.linspace(-2.6, 2.6, 53)
ridge_line = b - ratio * vv
n_resid, D_line = cal.n_D(ridge_line, vv)
print(f"ratio c_bg/c_tg = {ratio:.4f} (geometry prior 1.300, per-ch {-fits['sr1'][2][0]:.4f}/{-fits['sr2'][2][0]:.4f})")
print(f"c_tg = {c_tg:.4e} F/m^2 (anchor, geometry), c_bg = {c_bg:.4e} F/m^2 (ratio-calibrated)")
print(f"intercept b = {b:+.4f} V -> n_offset = {n_offset:.3e} m^-2 = {n_offset*1e-16:+.3f} e12 cm^-2")
print(f"closure: max|n| along ridge = {np.abs(n_resid).max()*1e-16:.4f} e12 cm^-2")
print(f"D along ridge spans {D_line.min()/1e9:.3f} .. {D_line.max()/1e9:.3f} V/nm")

# D=0 reach with validators (calc_gate_voltages units: n in 1e12 cm^-2, D in V/nm)
from sharpelab_nb.gates import calc_gate_voltages
n_off_e12 = n_offset * 1e-16
ns = np.linspace(-8, 8, 801)
Vt, Vb = calc_gate_voltages(ns, np.zeros_like(ns), c_tg, c_bg, n_offset=n_off_e12)
ok = (np.abs(Vt) <= 3.0) & (np.abs(Vb) <= 4.5)
print(f"D=0 realized n-window: {ns[ok].min():+.2f} .. {ns[ok].max():+.2f} e12 cm^-2")
for D0 in (0.2, 0.4):
    Vt, Vb = calc_gate_voltages(ns, D0 * np.ones_like(ns), c_tg, c_bg, n_offset=n_off_e12)
    ok = (np.abs(Vt) <= 3.0) & (np.abs(Vb) <= 4.5)
    print(f"D={D0} realized n-window: {ns[ok].min():+.2f} .. {ns[ok].max():+.2f} e12 cm^-2")

# --- figure: maps + ridge + fits
fig, axes = plt.subplots(1, 4, figsize=(19, 4.6), sharey=True)
for ax, ch in zip(axes[:2], ("sr1", "sr2")):
    R = np.asarray(rg.R[ch])
    pm = ax.pcolormesh(vtg, vbg, np.log10(np.clip(R, 10, None)), cmap="inferno", shading="auto")
    plt.colorbar(pm, ax=ax, label="log10 R (Ohm)")
    rv, k, p = fits[ch]
    ax.plot(rv[k], vbg[k], "c.", ms=3)
    ax.plot(np.polyval(p, vbg), vbg, "c-", lw=0.7)
    ax.set_title(f"{ch}: slope {p[0]:+.3f}, b {p[1]:+.3f} V")
    ax.set_xlabel("V_tg (V)"); ax.set_xlim(-3, 3)
I0 = np.asarray(rg.current) if not isinstance(rg.current, dict) else np.asarray(rg.current["sr0"])
pm = axes[2].pcolormesh(vtg, vbg, I0 * 1e9, cmap="viridis", shading="auto")
plt.colorbar(pm, ax=axes[2], label="I_drain (nA)")
axes[2].set_title("sr0 drain current"); axes[2].set_xlabel("V_tg (V)")
R3 = np.asarray(rg.R["sr3"])
pm = axes[3].pcolormesh(vtg, vbg, np.clip(R3, -50, 400), cmap="RdBu_r", shading="auto")
plt.colorbar(pm, ax=axes[3], label="R_xy (Ohm)")
axes[3].set_title("sr3 (Rxy @ B=0)"); axes[3].set_xlabel("V_tg (V)")
axes[0].set_ylabel("V_bg (V)")
fig.suptitle("run 4 — 0 T gatemap: CNP ridge + fits (cyan), drain current, Hall channel")
fig.tight_layout()
fig.savefig("hera_scratch/cnp_cal_map.png", dpi=110)
print("saved hera_scratch/cnp_cal_map.png")
