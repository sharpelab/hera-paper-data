"""Dual overlay (investigation Verify, mandatory): 4L ABAB / ABCA vs 3L ABA / ABC.

Where do the families separate on the electron side, and where does the
harmonic hypothesis (f2 = 4 f1) cross them? Sets the fan's n window.
"""
import sys, numpy as np, scipy.constants as cst, importlib.util


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


M4 = _load("fs4", "/home/hera/measurement_env/hera/models/tetralayer_fs_count/fs_count_b0.py")
M3 = _load("fs3", "/home/hera/measurement_env/hera/models/trilayer_fs_count/fs_count_b0.py")

H, E = cst.h, cst.e
FL = lambda n12: H / (4 * E) * n12 * 1e16

hdr = f"{'n':>5} {'F_L':>6} | {'ABAB lt':>8} {'ABAB hv':>8} {'part':>5} | {'ABCA':>6} | {'ABA lt':>7} {'ABA hv':>7} {'part':>5} | {'4xlt(4L)':>8}"
print(hdr); print("-" * len(hdr))
for n in (1.4, 1.6, 2.0, 2.4, 2.8, 3.2):
    f4 = sorted(f for f, k in M4.abab_fs(n * 1e16)[1])
    f3 = sorted(f for f, k in M3.aba_fs(n * 1e16)[1])
    fL = FL(n)
    print(f"{n:5.2f} {fL:6.2f} | {f4[0]:8.2f} {f4[1]:8.2f} {f4[0]/sum(f4):5.3f} | {fL:6.2f} | "
          f"{f3[0]:7.2f} {f3[1]:7.2f} {f3[0]/sum(f3):5.3f} | {4*f4[0]:8.2f}")

print("\nObserved run 6 @ n_gated = 3.20: tones 7.3 and 29.4 T (sum 36.7 = 1.11 F_L),"
      "\n  partition 0.199 / 0.801;  comb members 14.8, 22.3, 43.7, 58.6, 88.4, 130.0 T.")
print("\nCandidate reads at n = 3.2 and what each predicts for f_small(n)/f_big(n) lower down:")
for n in (1.6, 2.0, 2.4, 2.8, 3.2):
    f4 = sorted(f for f, k in M4.abab_fs(n * 1e16)[1])
    f3 = sorted(f for f, k in M3.aba_fs(n * 1e16)[1])
    print(f"  n={n:4.2f}:  ABAB ({f4[0]:5.2f},{f4[1]:6.2f})   ABA ({f3[0]:5.2f},{f3[1]:6.2f})   "
          f"ABCA ({FL(n):6.2f})   harmonic-only (f1={f4[0]:5.2f}, 4f1={4*f4[0]:6.2f})")
