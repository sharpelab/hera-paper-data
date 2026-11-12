"""FFT stability sweep + harmonic screen (sdh-spot-check Verify).

A real tone sharpens and holds position as the 1/B record lengthens and across
reasonable extraction choices; an artifact wanders. A tone at an integer
multiple of a stronger fundamental is a harmonic unless its n-dependence says
otherwise. Both screens are mandatory before any frequency is claimed.
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

from hera.analysis import (open_run, fan_grids, resistance_grids, sdh_fft,
                           luttinger_frequency)

BASE = file_path
RID = 7
DN_DVTG, DN_DVBG, V_TG_CNP = 1.570e12, 1.307e12, 0.0203

fg = fan_grids(run(RID))
def G(n): return fg.data[:, fg.cols.index(n)].reshape(fg.nrows, fg.nfast)
rg = resistance_grids(fg, channels=["sr1"])
R = np.abs(rg.R["sr1"]); B = G("magnet_field")[:, 0]
ncol = (DN_DVTG * (G("k_2400_tg_volt")[0] - V_TG_CNP)
        + DN_DVBG * G("k_2400_bg_volt")[0]) / 1e12
print(f"B {B.min():.3f}..{B.max():.3f} T, {len(B)} rows; n = {np.round(ncol,2).tolist()}")


def tones(tr, blo, bhi, deg):
    f, sp = sdh_fft(tr[:, None], B, b_range=(blo, bhi), bg_degree=deg)
    p = sp[0]; k = f > 2.0
    f, p = f[k], p[k]
    dF = 1.0 / (1.0 / blo - 1.0 / bhi)
    d = max(1, int(round(dF / (f[1] - f[0]))))
    pk, pr = find_peaks(p, distance=d, prominence=0.15 * np.ptp(p))
    if not len(pk):
        return np.array([]), np.array([])
    o = np.argsort(pr["prominences"])[::-1][:5]
    return f[pk[o]], pr["prominences"][o] / pr["prominences"][o].max()


CUTS = [(1.5, B.max()), (2.0, B.max()), (2.5, B.max()), (3.0, B.max()),
        (1.5, 0.5 * (1.5 + B.max())), (0.5 * (1.5 + B.max()), B.max())]
DEGS = [3, 5, 7]

for j in range(fg.nfast):
    F_L = luttinger_frequency(abs(ncol[j]) * 1e16)
    print(f"\n{'='*74}\nn = {ncol[j]:+.2f}e12 cm^-2   F_L = {F_L:.1f} T")
    print(f"  model ABAB pair / ABCA singleton at this n: see fs_count_b0")
    print(f"  {'window (T)':>16} {'deg':>4} {'dF':>5}  tones (T, dominant first)")
    allt = []
    for (blo, bhi) in CUTS:
        for deg in DEGS:
            f, a = tones(R[:, j], blo, bhi, deg)
            dF = 1.0 / (1.0 / blo - 1.0 / bhi)
            allt.append((blo, bhi, deg, f, a))
            s = "  ".join(f"{x:.1f}({y:.2f})" for x, y in zip(f, a))
            print(f"  {blo:6.2f}-{bhi:5.2f} {deg:>4} {dF:>5.1f}  {s}")
    # stability: which frequencies recur across choices?
    pool = np.concatenate([t[3] for t in allt if len(t[3])])
    if len(pool):
        pool = np.sort(pool)
        clusters, cur = [], [pool[0]]
        for x in pool[1:]:
            if x - cur[-1] < 2.0:
                cur.append(x)
            else:
                clusters.append(cur); cur = [x]
        clusters.append(cur)
        print(f"  --- recurrence across {len(allt)} extraction choices ---")
        for c in sorted(clusters, key=len, reverse=True)[:6]:
            print(f"      F = {np.mean(c):6.2f} +/- {np.std(c):4.2f} T  "
                  f"seen {len(c):2d}/{len(allt)}  f/F_L = {np.mean(c)/F_L:.3f}")
        # harmonic screen against the most-recurrent tone
        base = np.mean(max(clusters, key=len))
        print(f"  --- harmonic screen vs the most-recurrent tone {base:.2f} T ---")
        for c in sorted(clusters, key=len, reverse=True)[:6]:
            m = np.mean(c) / base
            flag = "HARMONIC-LIKE" if abs(m - round(m)) < 0.12 and round(m) >= 2 else ""
            print(f"      F = {np.mean(c):6.2f} T  ratio {m:5.2f}  {flag}")
print("\nstability sweep done")
