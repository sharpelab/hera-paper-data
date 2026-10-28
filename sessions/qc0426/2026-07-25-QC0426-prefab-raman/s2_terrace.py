import sys
sys.path.insert(0, "/home/zack/sharpelab/measurement-env/hera/models/raman_stacking")
import numpy as np
from raman_io import load_wip
from metrics import fit_band
from map_tools import per_pixel_metrics, two_population_split

ds = {d["caption"]: d for d in load_wip("/data/sharpelab/hera-data/raman-qc0426/04_3LGr.wip")}
d = ds["Scan LA--009--Spec.Data 1"]
wn, ii, nx, ny = d["wn"], d["ii"], d["nx"], d["ny"]
pm = per_pixel_metrics(wn, ii)
fw = pm["fwhm"]
thick = np.isfinite(fw) & (fw > 45)
labels, centers = two_population_split(np.where(thick, fw, np.nan))
# thickness proxies per cluster: 2D amp, G amp, Si peak (520) amp
n = ii.shape[1]
g_amp = np.full(n, np.nan); si_amp = np.full(n, np.nan)
for j in np.where(thick)[0]:
    y = ii[:, j]
    g = fit_band(wn, y, (1500., 1650.))
    if g: g_amp[j] = g["amp"]
    s = fit_band(wn, y, (490., 545.))
    if s: si_amp[j] = s["amp"]
for k in (0,1):
    sel = labels==k
    print(f"cluster{k} (fwhm {centers[k]:.1f}): 2Damp {np.nanmean(pm['amp'][sel]):.0f}±{np.nanstd(pm['amp'][sel]):.0f}  "
          f"Gamp {np.nanmean(g_amp[sel]):.0f}±{np.nanstd(g_amp[sel]):.0f}  "
          f"Siamp {np.nanmean(si_amp[sel]):.0f}±{np.nanstd(si_amp[sel]):.0f}  "
          f"G/2D {np.nanmean(g_amp[sel]/pm['amp'][sel]):.3f}")
# thin cluster for contrast
thin = np.isfinite(fw) & (fw <= 45)
print(f"thin pixels (fwhm<=45, n={thin.sum()}): 2Damp {np.nanmean(pm['amp'][thin]):.0f} fwhm {np.nanmean(fw[thin]):.1f}")
