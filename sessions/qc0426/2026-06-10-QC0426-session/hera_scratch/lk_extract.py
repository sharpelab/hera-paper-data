"""LK ladder extraction — runs on whatever ladder files exist.

For each run id given (or auto-discover >= 8): per-sweep mean/std of T,
FFT in 1/B over the common 3-6 T band, amplitudes of f_low (8-22 T) and
f_main (40-75 T) for sr1 and sr2. Prints the A(T) table; with >= 3 elevated
points, fits LK masses per branch.

Base anchors: run 6 (3->6) and run 7 partial (6->~4.6) at ~1.21 K.
"""
import json
import os
import sys
import numpy as np
from scipy.signal import find_peaks
from scipy.optimize import curve_fit

eps0, e = 8.8541878128e-12, 1.602176634e-19
KB = 14.694  # X = KB * T * (m*/m_e) / B  (LK argument)

def spectrum(rid):
    m = json.load(open(f"data/{rid}/metadata.json"))
    f = f"data/{rid}/data.tsv.gz" if os.path.exists(f"data/{rid}/data.tsv.gz") else f"data/{rid}/data.tsv"
    arr = np.loadtxt(f)
    if arr.ndim == 1 or arr.shape[0] < 60:
        return None
    d = {c: arr[:, i] for i, c in enumerate(m["columns"])}
    B = d["mag"]
    sel = (B >= 3.0) & (B <= 6.0)
    if sel.sum() < 60:
        return None
    Tcol = next((c for c in d if "sample_temperature" in c), None)
    T = d[Tcol][sel] if Tcol else np.full(sel.sum(), np.nan)
    out = {"rid": rid, "Tmean": np.nanmean(T), "Tstd": np.nanstd(T),
           "interrupted": m.get("interrupted")}
    invB = 1.0 / B[sel]
    M = 512
    u = np.linspace(invB.min(), invB.max(), M)
    freqs = np.fft.rfftfreq(M, u[1] - u[0])
    o = np.argsort(invB)
    I = d["sr0_X"][sel] / (-1e6)
    for chan in ("sr1_X", "sr2_X"):
        R = np.abs(d[chan][sel] / I)
        yi = np.interp(u, invB[o], np.log10(np.maximum(R[o], 1)))
        yi -= np.polyval(np.polyfit(u, yi, 3), u)
        s = np.abs(np.fft.rfft(yi * np.hanning(M)))
        def amp(lo, hi):
            ms = (freqs > lo) & (freqs < hi)
            return s[ms].max(), freqs[ms][np.argmax(s[ms])]
        a_low, f_low = amp(8, 22)
        a_main, f_main = amp(40, 75)
        out[chan] = dict(a_low=a_low, f_low=f_low, a_main=a_main, f_main=f_main)
    return out

rids = [int(x) for x in sys.argv[1:]] or [r for r in range(6, 20)
                                          if os.path.exists(f"data/{r}/metadata.json")]
rows = []
for rid in rids:
    try:
        r = spectrum(rid)
    except Exception as ex:
        print(f"run {rid}: skip ({ex})")
        continue
    if r:
        rows.append(r)
        s1 = r["sr1_X"]
        print(f"run {r['rid']}: T = {r['Tmean']:6.3f} +- {r['Tstd']:5.3f} K | "
              f"sr1 f_low {s1['f_low']:5.1f} T A={s1['a_low']:5.2f} | "
              f"f_main {s1['f_main']:5.1f} T A={s1['a_main']:5.2f}"
              f"{' [INTERRUPTED]' if r['interrupted'] else ''}")

# LK fits per branch (sr1), if >= 4 T-points
if len(rows) >= 4:
    Bbar = 4.2  # band-average field for the LK argument (1/B-mean of 3-6 T)
    def lk(T, A0, m):
        X = KB * T * m / Bbar
        return A0 * X / np.sinh(np.maximum(X, 1e-9))
    Ts = np.array([r["Tmean"] for r in rows])
    print("\nLK mass fits (sr1, Bbar = 4.2 T):")
    for key, label in [("a_low", "f_low"), ("a_main", "f_main")]:
        A = np.array([r["sr1_X"][key] for r in rows])
        try:
            popt, pcov = curve_fit(lk, Ts, A, p0=[A.max(), 0.04],
                                   bounds=([0, 0.005], [np.inf, 0.5]))
            err = np.sqrt(np.diag(pcov))[1]
            print(f"  {label}: m* = {popt[1]:.4f} +- {err:.4f} m_e")
        except Exception as ex:
            print(f"  {label}: fit failed ({ex})")
    print("readout: m*(f_main)/m*(f_low) >= 2 -> ABA two-pocket; ~1 -> same-mass (region scenario)")
