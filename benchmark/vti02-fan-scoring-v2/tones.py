import sys, json, numpy as np
sys.path.insert(0, '.')
import fs_count_b0 as m
out = {}
for sgn in (1, -1):
    for a in np.round(np.arange(0.3, 4.01, 0.1), 2):
        n = sgn * a
        ef, orbs = m.abab_fs(n * 1e16)  # 1e12 cm^-2 -> m^-2
        out[f"{n:.1f}"] = [list(map(float, o)) for o in orbs]
json.dump(out, open(sys.argv[1], 'w'), indent=0)
