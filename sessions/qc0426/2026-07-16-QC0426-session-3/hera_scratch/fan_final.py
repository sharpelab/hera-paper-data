# Final fan read: continuity-tracked branches, per channel; partition + overlay data.
import numpy as np, json
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import scipy.constants as cst
from hera.analysis import open_run, fan_grids, resistance_grids, sdh_fft

C_TG = cst.epsilon_0*3.0/15.6e-9; RATIO, N_OFF = 1.2839, -2.407e14
FLN = cst.h/(4*cst.e)*1e16
fan = fan_grids(open_run("data/9")); rg = resistance_grids(fan)
B = fan.slow[:fan.nrows]
vtg = fan.grid("k_2400_tg_volt")[0]; vbg = fan.grid("k_2400_bg_volt")[0]
n12 = ((C_TG*vtg + RATIO*C_TG*vbg)/cst.e + N_OFF)*1e-16   # negative (hole side)

out = {}
for ch in ("sr1", "sr2"):
    R = np.abs(rg.R[ch])[:fan.nrows]
    freqs, spec = sdh_fft(R, B, b_range=(1.8, 8.0), bg_degree=5)
    sn = spec/(spec.max(axis=1, keepdims=True)+1e-30)
    # per-column peak lists
    peaks = []
    for j in range(len(n12)):
        m = freqs > 3
        pk, pr = find_peaks(sn[j][m], height=0.10, prominence=0.05)
        peaks.append((freqs[m][pk], pr["peak_heights"]))
    # seed at the highest-|n| column: f_BL = strongest in (0.6,1.0)*F_L, f_ML strongest < 0.4*F_L
    order = np.argsort(-np.abs(n12))   # from high |n| down
    fML = np.full(len(n12), np.nan); fBL = np.full(len(n12), np.nan)
    j0 = order[0]; FL0 = FLN*abs(n12[j0])
    fp, hp = peaks[j0]
    selB = (fp > 0.55*FL0) & (fp < 1.0*FL0); selM = (fp < 0.4*FL0) & (fp > 4)
    if selB.any(): fBL[j0] = fp[selB][np.argmax(hp[selB])]
    if selM.any(): fML[j0] = fp[selM][np.argmax(hp[selM])]
    # walk down in |n| with continuity: expected slope ~ F/n locally
    for prev, j in zip(order[:-1], order[1:]):
        fp, hp = peaks[j]
        if len(fp) == 0: continue
        scale = abs(n12[j])/abs(n12[prev])
        for arr in (fML, fBL):
            if np.isfinite(arr[prev]):
                pred = arr[prev]*scale
                cand = np.abs(fp - pred) < np.maximum(2.5, 0.12*pred)
                if cand.any():
                    arr[j] = fp[cand][np.argmax(hp[cand])]
    ok = np.isfinite(fML) & np.isfinite(fBL)
    lam = np.nansum((fML[ok]+fBL[ok])*np.abs(n12[ok])) / np.nansum(FLN*n12[ok]**2)
    resid = (fML[ok]+fBL[ok]) - lam*FLN*np.abs(n12[ok])
    print(f"{ch}: branches on {ok.sum()}/{len(n12)} cols; lambda={lam:.4f}; "
          f"partition rms {np.sqrt(np.mean(resid**2)):.2f} T; "
          f"fML range {np.nanmin(fML):.1f}-{np.nanmax(fML):.1f} T; fBL {np.nanmin(fBL):.1f}-{np.nanmax(fBL):.1f} T")
    out[ch] = dict(n12=n12.tolist(), fML=fML.tolist(), fBL=fBL.tolist(),
                   lam=float(lam), rms=float(np.sqrt(np.mean(resid**2))), ncols=int(ok.sum()))
    # ML fraction vs n
    frac = fML[ok]/(fML[ok]+fBL[ok])
    print(f"{ch}: ML fraction {frac.min():.3f}..{frac.max():.3f} (mean {frac.mean():.3f}), "
          f"monotonic-in-|n| corr {np.corrcoef(np.abs(n12[ok]), frac)[0,1]:+.2f}")
json.dump(out, open("hera_scratch/fan_branches.json", "w"))
print("saved hera_scratch/fan_branches.json")
