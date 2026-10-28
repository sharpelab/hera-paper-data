"""Run 3 full fan — nu bookkeeping.

Per B-row minima of Rxx (sr1, sr2), apparent filling nu = n/(eB/h),
clustered into ray families; integer quantization check; strength ranking;
Rxy plateau cross-check at minima.
"""
import json
import numpy as np
from scipy.signal import find_peaks
from scipy.ndimage import uniform_filter1d

eps0 = 8.8541878128e-12
e = 1.602176634e-19
c_tg = eps0 * 3 / 15.6e-9
NFAST = 121

m = json.load(open(r"data/3/metadata.json"))
arr = np.loadtxt(r"data/3/data.tsv")
cols = m["columns"]
nrows = arr.shape[0] // NFAST

def grid(name):
    return arr[: nrows * NFAST, cols.index(name)].reshape(nrows, NFAST)

B = grid("mag")[:, 0]
vtg = grid("DC_bias")[0]
n12 = 2 * c_tg * vtg / e * 1e-16
I = grid("sr0_X") / (-1e6)

found = {}  # (chan) -> list of (B, n_min, nu_app, prominence)
for chan in ("sr1_X", "sr2_X"):
    R = np.abs(grid(chan) / I)
    out = []
    for k in range(nrows):
        if B[k] < 3.0:
            continue
        logR = np.log10(np.maximum(uniform_filter1d(R[k], 3), 1e-2))
        pk, props = find_peaks(-logR, prominence=0.06)
        for j, p in zip(pk, props["prominences"]):
            if n12[j] < 0.2:
                continue
            nu = n12[j] * 41.356 / B[k]   # n[1e12 cm-2] -> nu
            out.append((B[k], n12[j], nu, p))
    found[chan] = np.array(out)
    print(f"{chan}: {len(out)} minima found at B >= 3 T")

# cluster apparent nu across rows
for chan, data in found.items():
    if not len(data):
        continue
    nus = data[:, 2]
    promw = data[:, 3]
    hist, edges = np.histogram(nus, bins=np.arange(0, 45, 0.25), weights=promw)
    centers = 0.5 * (edges[1:] + edges[:-1])
    top = np.argsort(hist)[::-1][:14]
    print(f"\n{chan} — strongest nu clusters (prominence-weighted):")
    for t in sorted(top):
        if hist[t] > 0.15:
            sel = (nus > edges[t]) & (nus <= edges[t + 1])
            print(f"  nu ~ {np.average(nus[sel], weights=promw[sel]):6.2f}  "
                  f"weight {hist[t]:5.2f}  rows {sel.sum()}")

# Rxy at sr1 minima (Hall plateau check)
Rxy = grid("sr3_X") / I
print("\nRxy at sr1 minima with B >= 5 T (expect h/nu e^2 = 25812.8/nu if quantized):")
data = found["sr1_X"]
for Bv, nv, nu, p in data[data[:, 0] >= 5.0]:
    k = np.argmin(np.abs(B - Bv))
    j = np.argmin(np.abs(n12 - nv))
    nu_round = round(nu)
    print(f"  B={Bv:4.2f} n={nv:5.2f} nu_app={nu:6.2f} (->{nu_round:3d})  "
          f"Rxy={Rxy[k, j]:9.1f}  h/(nu e^2)={25812.8/max(nu_round,1):8.1f}  prom={p:.2f}")
