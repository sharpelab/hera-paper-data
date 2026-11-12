"""Model F(n) / m*(n) table for the fan design window (electron side) and the two spot densities."""
import sys, importlib.util, numpy as np
p = "/home/hera/measurement_env/hera/models/tetralayer_fs_count/fs_count_b0.py"
spec = importlib.util.spec_from_file_location("fs", p); fs = importlib.util.module_from_spec(spec); spec.loader.exec_module(fs)
import scipy.constants as c
FL = lambda n: abs(n)*1e16*c.h/(4*c.e)
print(f"{'n(e12)':>7} {'F_L':>6} | ABAB orbits F (T) [m*/me] | ABCA F, topo, m*")
for n in [-1.2, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0, 3.2, 3.27]:
    try:
        EF, orbs = fs.abab_fs(n*1e16); ms = fs.abab_mstar(n*1e16)
        ab = ", ".join(f"{F:5.1f}[{m:.3f}]" for (F, k), (F2, m) in zip(orbs, ms))
        frac = "/".join(f"{F/FL(n):.2f}" for F, k in orbs)
    except Exception as e: ab = f"ERR {e}"; frac = ""
    try:
        EF2, topo, ncomp, nfreq, Ft = fs.abca_fs(n*1e16); Ft2, m2 = fs.abca_mstar(n*1e16)
        ac = f"{Ft:5.1f} T {topo} ncomp {ncomp} m* {m2:.3f}"
    except Exception as e: ac = f"ERR {e}"
    print(f"{n:7.2f} {FL(n):6.1f} | {ab}  frac {frac} | {ac}")
