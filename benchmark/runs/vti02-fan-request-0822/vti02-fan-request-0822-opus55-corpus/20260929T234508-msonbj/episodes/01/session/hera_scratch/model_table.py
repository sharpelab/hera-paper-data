import sys, numpy as np
from pathlib import Path
sys.path.insert(0, str(Path.home() / "measurement_env/hera/models/tetralayer_fs_count"))
import fs_count_b0 as M
h, e = 6.62607015e-34, 1.602176634e-19
for n12 in (1.0, 1.5, 2.0, 2.5, 2.85, 3.0, 3.2, 3.25, -1.2, -1.0):
    n = n12 * 1e16; FL = abs(n) * h / (4 * e)
    ab = M.abab_fs(n)[1]; abm = M.abab_mstar(n); ac = M.abca_mstar(n)
    print(f"n {n12:+.2f}e12 F_L {FL:6.2f} | ABAB F {[round(f,2) for f,_ in ab]} (frac {[round(f/FL,3) for f,_ in ab]}) m* {[round(m,3) for _,m in abm]} | ABCA F {ac[0]:.2f} m* {ac[1]:.3f}")
