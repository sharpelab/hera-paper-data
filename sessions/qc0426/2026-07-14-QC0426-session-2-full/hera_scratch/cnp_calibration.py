"""CNP-line calibration from run 4 (cnp-and-dline-calibration)."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from hera.analysis import open_run, fan_grids, resistance_grids, GateCalibration

run = open_run("data/4")
fg = fan_grids(run)
rg = resistance_grids(fg)
vbg = fg.slow                     # 61 rows
vtg = np.asarray(fg.grid("k_2400_tg_volt"))[0] if hasattr(fg, "grid") else None
# fast-axis vector: take from first row of the tg grid
vtg_grid = np.asarray(fg.grid("k_2400_tg_volt"))
vtg = vtg_grid[0]
print("grid:", vtg_grid.shape, "vbg:", vbg.shape, "vtg:", vtg[:3], "...", vtg[-3:])
print("R channels:", list(rg.R.keys()) if hasattr(rg.R, "keys") else type(rg.R))

RAIL = 4.3e3  # 2e-5 rail at 5 nA ~ 4.37 kOhm
results = {}
for ch in ("sr1", "sr2"):
    R = np.asarray(rg.R[ch])
    ridge_v, keep_rows = [], []
    for i in range(R.shape[0]):
        row = gaussian_filter1d(R[i], 2)
        j = int(np.argmax(row))
        railed = np.sum(R[i] > RAIL) >= 3
        edge = j <= 2 or j >= len(row) - 3
        # rail plateau: use center of plateau instead of argmax
        if railed:
            idx = np.where(R[i] > RAIL)[0]
            if idx.max() - idx.min() < 20:            # contiguous-ish plateau
                j = int(np.round(idx.mean()))
                edge = j <= 2 or j >= len(row) - 3
            else:
                ridge_v.append(np.nan); keep_rows.append(False); continue
        ridge_v.append(vtg[j])
        keep_rows.append(not edge)
    ridge_v = np.array(ridge_v); keep = np.array(keep_rows)
    # iterative robust fit
    k = keep & np.isfinite(ridge_v)
    for _ in range(4):
        p = np.polyfit(vbg[k], ridge_v[k], 1)
        res = ridge_v - np.polyval(p, vbg)
        s = np.nanstd(res[k])
        k_new = keep & np.isfinite(ridge_v) & (np.abs(res) < 2 * s)
        if k_new.sum() == k.sum(): break
        k = k_new
    results[ch] = dict(slope=p[0], intercept=p[1], resid_rms=float(np.nanstd(res[k])),
                       nrows=int(k.sum()), ridge=ridge_v, keep=k)
    print(f"{ch}: slope {p[0]:+.4f}, intercept {p[1]:+.4f} V, resid rms {np.nanstd(res[k])*1e3:.1f} mV, rows {k.sum()}/61")

# geometry prior ratio
print("geometry prior c_bg/c_tg = 15.6/12 =", 15.6/12)
