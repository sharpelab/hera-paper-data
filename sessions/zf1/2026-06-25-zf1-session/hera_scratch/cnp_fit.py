"""CNP-ridge slope extraction from the survey gatemap (cnp-and-dline-calibration).
Map orientation: V_tg SLOW (rows), V_bg FAST. Per slow row, locate the 4T Rxx
(sr830_3, 30-31) maximum across the fast V_bg axis = CNP position; fit
V_bg_ridge vs V_tg. Slope dV_bg/dV_tg along the CNP = -c_tg/c_bg.
"""
import json, sys
import numpy as np
from scipy.ndimage import gaussian_filter1d

run = sys.argv[1] if len(sys.argv) > 1 else "data/4"
md = json.load(open(f"{run}/metadata.json")); cols = md["columns"]
a = np.genfromtxt(f"{run}/data.tsv", delimiter="\t", invalid_raise=False)
a = a[~np.isnan(a).any(axis=1)]
ix = {}; [ix.setdefault(c, j) for j, c in enumerate(cols)]
vtg = a[:, ix["k_tg_volt"]]; vbg = a[:, ix["k_bg_volt"]]
R3 = (a[:, ix["sr830_3_X"]] / 100) / 1e-9   # 4T 30-31
R2 = (a[:, ix["sr830_2_X"]] / 100) / 1e-9   # 2T 5-4 (cross-check)

def ridge(vtg, vbg, R, label):
    rows = np.unique(np.round(vtg, 3))
    pts = []
    excl_edge = 0
    for vt in rows:
        m = np.round(vtg, 3) == vt
        if m.sum() < 10: continue
        bg = vbg[m]; r = R[m]
        o = np.argsort(bg); bg = bg[o]; r = r[o]
        rs = gaussian_filter1d(r, 2)
        k = np.argmax(rs)
        # edge-clip guard: CNP not located if max at fast-axis edge
        if k <= 1 or k >= len(bg) - 2:
            excl_edge += 1; continue
        # require a real peak (CNP must rise above the row's metallic floor)
        if rs[k] < 3 * np.median(rs) or rs[k] < 200:
            continue
        pts.append((vt, bg[k]))
    pts = np.array(pts)
    if len(pts) < 5:
        print(f"  {label}: only {len(pts)} ridge pts (edge-excluded {excl_edge}) — insufficient")
        return None
    vt, vb = pts[:, 0], pts[:, 1]
    # iterative outlier rejection on the linear fit
    keep = np.ones(len(vt), bool)
    for _ in range(3):
        c = np.polyfit(vt[keep], vb[keep], 1)
        res = vb - np.polyval(c, vt)
        s = np.std(res[keep])
        keep = np.abs(res) < 2 * s
    c = np.polyfit(vt[keep], vb[keep], 1)
    slope, intc = c
    resid = vb[keep] - np.polyval(c, vt[keep])
    print(f"  {label}: {keep.sum()}/{len(vt)} ridge rows (edge-excl {excl_edge}); "
          f"dV_bg/dV_tg = {slope:+.4f}, intercept {intc:+.3f} V, "
          f"resid RMS {np.std(resid)*1e3:.1f} mV")
    # convention: slope = -c_tg/c_bg  ->  c_tg/c_bg = -slope ; prior t_bg/t_tg=20/23.6=0.847
    print(f"       => c_tg/c_bg = {-slope:.4f}  (prior t_bg/t_tg = {20/23.6:.4f})")
    return slope, intc, pts, keep

print(f"rows={len(a)}  V_tg {vtg.min():+.2f}..{vtg.max():+.2f}")
ridge(vtg, vbg, R3, "4T(30-31)")
ridge(vtg, vbg, R2, "2T(5-4) [contact-contaminated cross-check]")
