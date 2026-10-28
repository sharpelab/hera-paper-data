"""Fan design arithmetic: model F(n) on the electron side + Nyquist/cost floors."""
import sys, numpy as np, scipy.constants as cst
sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
import fs_count_b0 as M

H, E = cst.h, cst.e
FL = lambda n12: H / (4 * E) * abs(n12) * 1e16

print("n[1e12]   F_L     ABAB tones              ABCA    4x f_light  2x f_light")
for n in (1.0, 1.2, 1.5, 2.0, 2.4, 2.8, 3.2):
    _, orbs = M.abab_fs(n*1e16)
    fs = sorted(f for f, k in orbs)
    _, _, _, _, fabca = M.abca_fs(n*1e16)
    light = fs[0]
    print(f"{n:5.2f}  {FL(n):6.2f}   " + ", ".join(f"{f:6.2f}" for f in fs)
          + f"   sum {sum(fs):6.2f}" + f"   {fabca:6.2f}   {4*light:6.2f}   {2*light:6.2f}")

print("\nABAB m* (n, per orbit):")
for n in (1.2, 2.0, 3.2):
    print(f"  n={n}: ", [(round(f, 2), round(m, 4)) for f, m in M.abab_mstar(n*1e16)],
          " ABCA:", tuple(round(x, 3) for x in M.abca_mstar(n*1e16)))
