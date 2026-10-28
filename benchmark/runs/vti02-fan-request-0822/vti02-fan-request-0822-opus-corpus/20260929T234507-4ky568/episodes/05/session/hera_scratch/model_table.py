"""Model F(n), m*(n) across the accessible D=0 electron window -> fan design numbers."""
import sys, importlib.util
import numpy as np
from pathlib import Path
from hera.analysis import luttinger_frequency

# NOTE: tetralayer and trilayer model dirs BOTH contain fs_count_b0.py — a bare
# sys.path insert silently shadows one with the other. Load each by explicit path.
def _load(mod_name, path):
    spec = importlib.util.spec_from_file_location(mod_name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = m
    spec.loader.exec_module(m)
    return m

MODELS = Path.home() / "measurement_env/hera/models"
M = _load("tet_fs", MODELS / "tetralayer_fs_count/fs_count_b0.py")
T3 = _load("tri_fs", MODELS / "trilayer_fs_count/fs_count_b0.py")

ns = np.array([0.6, 0.8, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0, 3.27])
print(f"{'n(e12)':>7} {'F_L':>6} | {'ABAB Flight':>11} {'Fheavy':>7} {'f_l':>5} {'f_h':>5} "
      f"{'3xFl':>6} {'|Fh-3Fl|':>8} | {'m*l':>6} {'m*h':>6} | {'ABCA F':>7} {'m*':>7}")
rows = []
for n in ns:
    FL = float(luttinger_frequency(n * 1e16))
    try:
        _, orbs = M.abab_fs(n * 1e16)
        ms = dict((round(F, 3), m) for F, m in M.abab_mstar(n * 1e16))
        Fs = sorted(F for F, _ in orbs)
        Fl, Fh = Fs[0], Fs[-1]
        ml = ms[round(Fl, 3)]; mh = ms[round(Fh, 3)]
    except Exception as e:
        Fl = Fh = ml = mh = float("nan")
    try:
        _, topo, ncomp, nfreq, Fa = M.abca_fs(n * 1e16)
        _, ma = M.abca_mstar(n * 1e16)
    except Exception as e:
        Fa, ma, topo = float("nan"), float("nan"), str(e)[:20]
    print(f"{n:7.2f} {FL:6.2f} | {Fl:11.2f} {Fh:7.2f} {Fl/FL:5.3f} {Fh/FL:5.3f} "
          f"{3*Fl:6.2f} {abs(Fh-3*Fl):8.2f} | {ml:6.4f} {mh:6.4f} | {Fa:7.2f} {ma:7.4f}  {topo}")
    rows.append((n, FL, Fl, Fh, ml, mh, Fa, ma))

print("\n--- LK damping X/sinh(X), X = 14.69 m* T / B, at T_e = 8 K (rig card) ---")
def damp(m, T, B):
    X = 14.69 * m * T / B
    return X / np.sinh(X)
for n, FL, Fl, Fh, ml, mh, Fa, ma in rows:
    if not np.isfinite(mh):
        continue
    s = "  ".join(f"B={B}: l {damp(ml,8,B):.2f} h {damp(mh,8,B):.2f} abca {damp(ma,8,B):.3f}"
                 for B in (1.0, 2.0, 3.0, 5.0, 8.0))
    print(f"n={n:4.2f}  {s}")

print("\n--- sampling/resolution for candidate fan windows (F_max = F_L at n=3.27) ---")
FLmax = float(luttinger_frequency(3.27e16))
for Blo in (0.3, 0.5, 0.8, 1.0, 1.5, 2.0):
    for Bmax in (8.0, 10.0):
        span = 1 / Blo - 1 / Bmax
        dF = 1 / span
        dinvB_nyq = 1 / (2 * FLmax); dinvB_pref = 1 / (3 * FLmax)
        NB_nyq = int(np.ceil(span / dinvB_nyq)); NB_pref = int(np.ceil(span / dinvB_pref))
        dn_ray = 4 * 1.602176634e-19 / 6.62607015e-34 * Blo / 1e16  # e12 cm^-2
        print(f"B [{Blo:4.2f},{Bmax:4.1f}]  1/B span {span:5.3f}  dF {dF:5.2f} T  "
              f"N_B(2x) {NB_nyq:4d} (3x) {NB_pref:4d}  ray dn {dn_ray:6.4f}e12 -> "
              f"N_n(2/ray) over 2.3e12 = {int(np.ceil(2.3/(dn_ray/2)))}")
