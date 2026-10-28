import numpy as np, sys, warnings; warnings.filterwarnings("ignore")
sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
from hera.analysis import luttinger_frequency
import fs_count_b0 as m
print(" n12   F_L   ABAB orbits (F T, m*/me)                 F/F_L          ABCA (F, m*)")
for n in [1.0, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.8, 3.2, 3.4, -1.2]:
    FL = float(luttinger_frequency(abs(n) * 1e16)); ab = m.abab_mstar(n * 1e16); ca = m.abca_mstar(n * 1e16)
    print(f"{n:5.1f} {FL:6.2f}  " + "  ".join(f"({F:5.2f},{ms:.3f})" for F, ms in ab).ljust(40) +
          " " + " ".join(f"{F/FL:.3f}" for F, _ in ab).ljust(14) + f"  ({ca[0]:.2f},{ca[1]:.3f})")
