import numpy as np, sys
sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
import fs_count_b0 as m
for n in [1.4, 1.6, 1.8, 2.0, 2.2, 2.5, 2.8, 3.0, 3.2, 3.25, -0.6, -0.9, -1.2]:
    ab = m.abab_mstar(n * 1e16); FL = abs(n) * 1e16 * 4.1357e-15 / 4
    ca = m.abca_mstar(n * 1e16)
    print(f"n={n:+.2f}: F_L {FL:5.1f}; ABAB " + ", ".join(f"{f:.2f}T/{ms:.3f}" for f, ms in ab) + f"; ABCA {ca[0]:.1f}T/{ca[1]:.3f}")
