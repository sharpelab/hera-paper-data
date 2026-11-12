"""Run 8 FS-count fan: per-column FFT vs F_L, harmonic screen, Luttinger partition.

Order matters and follows the investigation: extract tones -> SCREEN HARMONICS ->
then test templates. Without the screen a naive best-summing-pair search pairs a
fundamental with its own 2nd harmonic, and in a high-field-only record it pairs
the partner with the breakdown/sum tone.
"""
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import scipy.constants as cst
from scipy.signal import find_peaks

from hera.analysis import (open_run, summarize_run, fan_grids, resistance_grids,
                           sdh_fft, luttinger_frequency)

BASE = "C:/Users/DGG/VTI_local_data/zack/20260825-vti-02/data"
SCRATCH = "C:/Users/DGG/VTI_local_data/zack/20260825-vti-02/hera_scratch"
RID = int(sys.argv[1]) if len(sys.argv) > 1 else 8
BLO = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0     # optional low-B cutoff
DN_DVTG, DN_DVBG, V_TG_CNP = 1.570e12, 1.307e12, 0.0203

fg = fan_grids(open_run(f"{BASE}/{RID}"))
def G(n): return fg.data[:, fg.cols.index(n)].reshape(fg.nrows, fg.nfast)
rg = resistance_grids(fg, channels=["sr1"])
R = np.abs(rg.R["sr1"]); B = G("magnet_field")[:, 0]
ncol = (DN_DVTG * (G("k_2400_tg_volt")[0] - V_TG_CNP)
        + DN_DVBG * G("k_2400_bg_volt")[0]) / 1e12
blo = max(B.min(), BLO) if BLO else B.min()
bhi = B.max()
ib = 1.0 / np.array([bhi, blo])
dF = 1.0 / abs(ib[0] - ib[1])
print(f"{fg.nrows} rows, B {B.min():.3f}..{B.max():.3f} T; window {blo:.2f}-{bhi:.2f} T "
      f"-> 1/B span {abs(ib[0]-ib[1]):.4f}, dF = {dF:.2f} T")
print(f"{fg.nfast} density columns, n {ncol.min():.2f}..{ncol.max():.2f} e12 cm^-2")


def tones_of(tr):
    f, sp = sdh_fft(tr[:, None], B, b_range=(blo, bhi), bg_degree=5)
    p = sp[0]
    k = f > 2.0
    f, p = f[k], p[k]
    d = max(1, int(round(dF / (f[1] - f[0]))))
    pk, pr = find_peaks(p, distance=d, prominence=0.12 * np.ptp(p))
    if not len(pk):
        return None
    o = np.argsort(pr["prominences"])[::-1][:5]
    return f[pk[o]], pr["prominences"][o]


def screen(f, a, tol=0.10):
    """Drop tones at k>=2 times a STRONGER tone (k integer within tol)."""
    order = np.argsort(a)[::-1]
    keep, kept_f = [], []
    for i in order:
        harmonic = False
        for g in kept_f:
            if g > 1e-9:
                m = f[i] / g
                if m >= 1.8 and abs(m - round(m)) < tol:
                    harmonic = True
                    break
        if not harmonic:
            keep.append(i)
            kept_f.append(f[i])
    keep = np.array(sorted(keep, key=lambda i: -a[i]))
    return f[keep], a[keep]


rows = []
for j in range(fg.nfast):
    t = tones_of(R[:, j])
    if t is None:
        rows.append(None)
        continue
    f, a = t
    fs, as_ = screen(f, a)
    rows.append(dict(n=ncol[j], F_L=luttinger_frequency(abs(ncol[j]) * 1e16),
                     f=f, a=a, fs=fs, as_=as_))

print()
print("=== per column, after harmonic screen ===")
print(f"{'n(e12)':>7} {'F_L':>6} {'kept tones (T)':>28} {'dom/F_L':>8} {'sum/F_L':>9} {'frac_lo':>8}")
part, nclose, ncols = [], 0, 0
for d in rows:
    if d is None:
        continue
    ncols += 1
    f = d["fs"]
    dom = f[0] / d["F_L"]
    best = None
    for i in range(len(f)):
        for j2 in range(i + 1, len(f)):
            ssum = f[i] + f[j2]
            e = abs(ssum / d["F_L"] - 1.0)
            if best is None or e < best[0]:
                best = (e, min(f[i], f[j2]), max(f[i], f[j2]), ssum)
    if best is None:
        print(f"{d['n']:>7.2f} {d['F_L']:>6.1f} {str([round(x,1) for x in f]):>28} {dom:>8.3f}")
        continue
    e, lo, hi, ssum = best
    ok = e < 0.08
    nclose += ok
    if ok:
        part.append((d["n"], lo / ssum, hi / ssum, lo, hi))
    print(f"{d['n']:>7.2f} {d['F_L']:>6.1f} {str([round(x,1) for x in f]):>28} {dom:>8.3f} "
          f"{ssum/d['F_L']:>9.3f} {lo/ssum:>8.3f} {'OK' if ok else ''}")

print()
print(f"Luttinger sum closes (<8%) in {nclose}/{ncols} columns after the harmonic screen")
part = np.array(part) if part else np.zeros((0, 5))
if len(part):
    print(f"partner fraction {part[:,1].min():.3f}..{part[:,1].max():.3f} over n "
          f"{part[:,0].min():.2f}..{part[:,0].max():.2f}")
    print("  ABAB-4L model 0.16-0.22 over this n range; trilayer ML+BL 0.02-0.05")
doms = np.array([d["fs"][0] / d["F_L"] for d in rows if d is not None])
print(f"dominant tone / F_L: median {np.median(doms):.3f}, "
      f"range {doms.min():.3f}..{doms.max():.3f}")
print("  ABCA singleton template -> 1.00 | ABAB heavy -> 0.72-0.79")
np.save(f"{SCRATCH}/fan8_part.npy", part)
