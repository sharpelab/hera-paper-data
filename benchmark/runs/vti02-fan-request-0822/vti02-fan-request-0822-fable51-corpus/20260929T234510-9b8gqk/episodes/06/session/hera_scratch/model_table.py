"""Model F(n), m*(n) table for ABAB / ABCA over the D=0 electron fan window (n in 1e12 cm^-2 -> m^-2 for the solver)."""
import sys; sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
import numpy as np, json
from fs_count_b0 import abab_fs, abab_mstar, abca_fs, abca_mstar
h_e = 4.135667e-15
rows = []
for n in [-1.2, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.2]:
    FL = h_e / 4 * abs(n) * 1e16; nm = n * 1e16
    EF, orbs = abab_fs(nm); ms = abab_mstar(nm)
    EFa, topo, ncomp, nfreq, Fa = abca_fs(nm); Fa_, ma = abca_mstar(nm)
    ab = [(round(F, 2), round(m, 3)) for (F, k), (F2, m) in zip(orbs, ms)]
    rows.append(dict(n=n, FL=round(FL, 2), abab=ab, abca=(round(float(Fa), 2), round(float(ma), 3), topo, int(ncomp))))
    frac = " ".join(f"{F/FL:.2f}" for F, m in ab)
    print(f"n={n:+.2f}  F_L={FL:5.2f}  ABAB (F, m*): {ab}  frac {frac}  | ABCA F={Fa:.2f} ({Fa/FL:.2f}F_L) m*={ma:.3f} {topo}/{ncomp}")
json.dump(rows, open("hera_scratch/model_table.json", "w"), indent=1)
