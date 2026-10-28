import json, gzip, os, sys
import numpy as np
from hera.analysis import GateCalibration
cal = GateCalibration.from_thicknesses(23.6e-9, 20e-9, 0, n_offset=-0.362e11*1e4)

def load(run):
    md = json.load(open(f"{run}/metadata.json")); cols = md["columns"]
    p = f"{run}/data.tsv"; f = gzip.open(p+".gz","rt") if os.path.exists(p+".gz") else open(p)
    a = np.genfromtxt(f, delimiter="\t", invalid_raise=False); f.close()
    a = a[~np.isnan(a).any(axis=1)]; ix = {}; [ix.setdefault(c,j) for j,c in enumerate(cols)]
    return a, ix, md["comments"]

for run in sys.argv[1:]:
    if not os.path.exists(f"{run}/metadata.json"):
        print(f"{run}: absent"); continue
    a, ix, com = load(run)
    vtg = a[:, ix["k_tg_volt"]]; vbg = a[:, ix["k_bg_volt"]]
    n, D = cal.n_D(vtg, vbg); n = n/1e4/1e11; D = D/1e9
    R3 = (a[:, ix["sr830_3_X"]]/100)/1e-9
    R2 = (a[:, ix["sr830_2_X"]]/100)/1e-9
    Dtag = com[2] if len(com) > 2 else "?"
    print(f"\n=== {run}: {Dtag} ===  ({len(a)} pts, D={D.min():.3f}..{D.max():.3f})")
    for a0, b0 in [(0,-1),(-1,-2),(-2,-3),(-3,-4),(-4,-5),(-5,-6),(-6,-7),(-7,-8.1)]:
        m = (n < a0) & (n >= b0)
        if m.any():
            print(f"  n∈[{b0:.0f},{a0:.0f}): R3 min {R3[m].min():6.1f} med {np.median(R3[m]):6.1f} max {R3[m].max():7.1f} Ω")
    aw = n < -1   # away from CNP
    if aw.sum() == 0:
        print("  (in progress — no n<-1 rows yet)"); continue
    j = np.argmin(R3[aw])
    print(f"  >>> min R3 (n<-1): {R3[aw][j]:.1f} Ω at n={n[aw][j]:.2f}e11, D={D[aw][j]:.2f}")
