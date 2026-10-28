"""Forward-model F(n) / m*(n) for the fan design window (electron side, D=0).
Key design question: over what n does the ABAB heavy/light ratio move off 3.0
(the value the run-6 spot check sits at, where a real heavy pocket and the 3rd
harmonic of the light one are degenerate)?"""
import numpy as np
import sys
sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
import fs_count_b0 as M

print(f"{'n(e12)':>7} {'F_L':>7} | {'ABAB orbits (T)':>34} {'ratio':>6} {'f1/F_L':>7} {'f2/F_L':>7} "
      f"{'sum/F_L':>8} | {'ABCA F':>7} | {'m1':>6} {'m2':>6}")
for n in [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.2, 3.5, 4.0, 4.5, 5.0, 6.0, 7.0, 8.0]:
    F_L = abs(n) * 1e16 * 6.62607015e-34 / (4 * 1.602176634e-19)
    try:
        EF, orbs = M.abab_fs(n*1e16)
        fs = sorted([f for f, k in orbs])
        ms = M.abab_mstar(n*1e16)
        mm = {round(f, 2): m for f, m in ms}
        s = " ".join(f"{f:8.2f}" for f in fs)
        if len(fs) >= 2:
            f1, f2 = fs[0], fs[-1]
            ratio, r1, r2, rs = f2 / f1, f1 / F_L, f2 / F_L, sum(fs) / F_L
        else:
            f1 = f2 = fs[0]; ratio = r1 = r2 = rs = float("nan")
        m1 = [m for f, m in ms if abs(f - f1) < 1e-6]
        m2 = [m for f, m in ms if abs(f - f2) < 1e-6]
    except Exception as e:
        print(f"{n:7.1f} {F_L:7.2f} | ABAB err {e}")
        continue
    try:
        aEF, topo, ncomp, nfreq, Fa = M.abca_fs(n*1e16)
    except Exception as e:
        Fa, topo = float("nan"), str(e)[:20]
    print(f"{n:7.1f} {F_L:7.2f} | {s:>34} {ratio:6.2f} {r1:7.3f} {r2:7.3f} {rs:8.3f} | "
          f"{Fa:7.2f} | {(m1[0] if m1 else float('nan')):6.3f} {(m2[0] if m2 else float('nan')):6.3f}")
