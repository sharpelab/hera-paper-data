"""Model F(n), m*(n) on the electron side at true n = S * n_cal (S from run-6 QH minima)."""
import sys, json
sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
import numpy as np, fs_count_b0 as m
S = 0.906
rows = []
print(" n_cal  n_true  F_L    ABAB (F T, m*)                          ABCA (F, m*)")
for nc in [1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0, 3.25]:
    nt = nc * S * 1e16
    ab = m.abab_mstar(nt); ca = m.abca_mstar(nt)
    FL = nt * 4.135667e-15 / 4
    rows.append(dict(n_cal=nc, n_true=nc*S, FL=FL, abab=[(float(f), float(x)) for f, x in ab], abca=[float(ca[0]), float(ca[1])]))
    print(f"{nc:5.2f} {nc*S:6.3f} {FL:6.2f}  " + "  ".join(f"{f:6.2f} ({x:.3f})" for f, x in ab) + f"   | {ca[0]:6.2f} ({ca[1]:.3f})")
json.dump(rows, open("hera_scratch/model_table.json", "w"), indent=1)
