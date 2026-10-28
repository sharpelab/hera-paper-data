"""Run 3 Verify battery.

A) Aliasing: re-detect offset-family minima on 2x-decimated n-grid (both
   phases) and on B-row subsets — do slope/intercept survive?
B) N_M=0 vertical-series test: non-dispersing Rxx maxima at n 0.8-1.2?
C) Rxy plateau flatness at main-family vs offset-family minima.
"""
import json
import numpy as np
from scipy.signal import find_peaks
from scipy.ndimage import uniform_filter1d

eps0, e = 8.8541878128e-12, 1.602176634e-19
c_tg = eps0 * 3 / 15.6e-9
NFAST = 121

m = json.load(open(r"data/3/metadata.json"))
arr = np.loadtxt(r"data/3/data.tsv")
cols = m["columns"]
nrows = arr.shape[0] // NFAST
g = lambda nm: arr[: nrows * NFAST, cols.index(nm)].reshape(nrows, NFAST)
B = g("mag")[:, 0]
n12 = 2 * c_tg * g("DC_bias")[0] / e * 1e-16
I = g("sr0_X") / (-1e6)
R1 = np.abs(g("sr1_X") / I)
Rxy = g("sr3_X") / I


def detect(Rg, ngrid, Bsel, prom=0.05):
    out = []
    for k in range(nrows):
        if not Bsel[k]:
            continue
        logR = np.log10(np.maximum(uniform_filter1d(Rg[k], 3), 1e-2))
        pk, pr = find_peaks(-logR, prominence=prom)
        for j in pk:
            if ngrid[j] > 0.2:
                out.append((B[k], ngrid[j]))
    return np.array(out)


def fit_family(mins, seed_slope, seed_n0, tol=0.25):
    """Collect minima within tol(e12) of line, refit."""
    if not len(mins):
        return None
    d = np.abs(mins[:, 1] - (seed_slope * mins[:, 0] + seed_n0))
    sel = d < tol
    if sel.sum() < 4:
        return None
    s, n0 = np.polyfit(mins[sel, 0], mins[sel, 1], 1)
    return s / 0.024179, n0, sel.sum()


print("=== A) decimation / subsetting — offset family (seed nu'=16.5, n0=+0.44) "
      "and main family (nu=23.2, n0=+0.02) ===")
seeds = {"offset nu'~16.5": (16.46 * 0.024179, 0.438),
         "offset nu'~12.8": (12.78 * 0.024179, 0.515),
         "main  nu ~23.2": (23.18 * 0.024179, 0.023),
         "main  nu ~27.8": (27.76 * 0.024179, -0.014)}
variants = {
    "full grid          ": (R1, n12, B >= 4.0),
    "n-decimated even   ": (R1[:, ::2], n12[::2], B >= 4.0),
    "n-decimated odd    ": (R1[:, 1::2], n12[1::2], B >= 4.0),
    "B-rows even only   ": (R1, n12, (B >= 4.0) & (np.arange(nrows) % 2 == 0)),
    "B-rows odd only    ": (R1, n12, (B >= 4.0) & (np.arange(nrows) % 2 == 1)),
}
for vname, (Rg, ngrid, Bsel) in variants.items():
    mins = detect(Rg, ngrid, Bsel)
    line = [vname]
    for sname, (s, n0) in seeds.items():
        f = fit_family(mins, s, n0)
        line.append(f"{sname}: " + (f"nu={f[0]:5.2f} n0={f[1]:+.2f} ({f[2]}p)" if f else "LOST"))
    print(" | ".join(line))

print("\n=== B) N_M=0 vertical-series test: Rxx(B) at fixed n in 0.8-1.2 ===")
# a vertical chain = local maxima in B climbing at ~fixed n; compare against
# neighbouring n outside the predicted window (control at n~1.6-2.0)
for ncen in (0.85, 1.0, 1.15, 1.7):
    j = np.argmin(np.abs(n12 - ncen))
    colR = R1[:, j]
    hiB = B >= 4.0
    # detrend in B (remove smooth MR growth), look for bumps
    sm = uniform_filter1d(colR, 7)
    ratio = colR / np.maximum(sm, 1e-3)
    pk, pr = find_peaks(ratio[hiB], prominence=0.04)
    Bpk = B[hiB][pk]
    print(f"  n={n12[j]:5.2f}: max dev {ratio[hiB].max()-1:+.3f}, "
          f"bumps at B = {np.round(Bpk, 2)} (prom {np.round(pr['prominences'], 3)})")

print("\n=== C) Rxy flatness (dRxy/dn local slope vs classical) at minima, B=7.75-8 ===")
k = nrows - 1
for ncen, label in [(2.46, "offset family"), (2.94, "offset family"),
                    (3.63, "main family"), (1.07, "low-nu edge")]:
    j = np.argmin(np.abs(n12 - ncen))
    w = 3
    loc = np.polyfit(n12[j - w:j + w + 1], Rxy[k, j - w:j + w + 1], 1)[0]
    classical = -Rxy[k, j] / n12[j]  # d(B/ne)/dn = -B/(n^2 e) = -Rxy/n
    print(f"  n={n12[j]:5.2f} ({label}): dRxy/dn = {loc:8.1f} Ohm/e12, "
          f"classical {classical:8.1f} -> flatness ratio {loc/classical:5.2f} "
          f"(0 = plateau, 1 = classical)")
