"""FS-count forward-model table: ABAB / ABCA F(n), m*(n) over the session's D=0 n-window (both signs)."""
import sys, json
import numpy as np
sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
from fs_count_b0 import abab_fs, abab_mstar, abca_fs, abca_mstar
from hera.analysis import luttinger_frequency

rows = []
ns = list(np.round(np.arange(0.5, 3.30, 0.25), 3)) + [3.25] + list(-np.round(np.arange(0.5, 1.30, 0.25), 3))
for n12 in ns:
    n = n12 * 1e16
    FL = float(luttinger_frequency(n))
    try:
        EF, orbs = abab_fs(n); ms = abab_mstar(n)
        abab = [(round(F, 2), round(m, 3)) for F, m in ms]
    except Exception as e:
        abab = str(e)[:80]
    try:
        EF2, topo, ncomp, nfreq, Ft = abca_fs(n); Ft2, m2 = abca_mstar(n)
        abca = (round(Ft, 2), topo, round(m2, 3))
    except Exception as e:
        abca = str(e)[:80]
    rows.append(dict(n12=float(n12), FL=round(FL, 2), abab=abab, abca=abca))
    print(f"n={n12:+.2f}e12  F_L={FL:6.2f}  ABAB (F, m*)={abab}  ABCA (F, topo, m*)={abca}", flush=True)
json.dump(rows, open("/home/hera/measurements/zack/20260822-vti-02/hera_scratch/model_table.json", "w"), indent=1)
