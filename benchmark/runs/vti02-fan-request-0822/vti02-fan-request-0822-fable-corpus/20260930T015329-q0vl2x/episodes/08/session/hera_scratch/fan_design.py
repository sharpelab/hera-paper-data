"""Landau-fan design numbers (investigation step 2/4 + landau-fan step 1).

1. Global density-rescale pin on the run-6/7 tone set (single scale s).
2. Model F(n) table over the electron-side fan window (light-tone resolvability).
3. Grid: Delta(1/B) Nyquist at n_max, n-axis ray Nyquist at B_lo, deltaF, cost.
"""
import sys
import numpy as np

sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
import fs_count_b0 as fs
from hera.analysis import luttinger_frequency, field_invB

# --- measured fundamentals (sdh_onset, runs 6/7; harmonics screened Luttinger-aware) ---
meas = {
    +3.2e16: (7.11, 22.08),   # electron spot: light, heavy (22.08 un-flagged: dropping it breaks the sum)
    -1.2e16: (4.72, 6.59),    # hole spot: close balanced pair
}

# 1. single global density rescale s: model pair at s*n vs measured pair
def model_pair(n_SI):
    _, orbs = fs.abab_fs(n_SI)
    Fs = sorted(f for f, _ in orbs)
    return Fs

def cost(s):
    c = 0.0
    for n, (fl, fh) in meas.items():
        Fs = model_pair(s * n)
        if len(Fs) < 2:
            return np.inf
        c += ((Fs[0] - fl) / fl) ** 2 + ((Fs[-1] - fh) / fh) ** 2
    return c

ss = np.linspace(0.7, 1.3, 121)
cc = [cost(s) for s in ss]
s_best = ss[int(np.argmin(cc))]
print(f"global density rescale s = {s_best:.3f} (grid 0.7-1.3), cost {min(cc):.4f}")
for n, (fl, fh) in meas.items():
    Fs = model_pair(s_best * n)
    F_L = float(luttinger_frequency(abs(n)))
    print(f"  n={n/1e16:+.1f}e12: meas ({fl:.1f},{fh:.1f}) sum {fl+fh:.1f} | model@s*n ({Fs[0]:.1f},{Fs[-1]:.1f}) "
          f"| F_L={F_L:.1f}, sum/F_L={(fl+fh)/F_L:.2f}, partition {fl/(fl+fh):.2f}/{fh/(fl+fh):.2f}")

# 2. model F(n) over candidate electron window (as-calibrated densities)
print("\nmodel ABAB F(n) [electron side, at calibrated n, and at s*n]:")
print(" n(cal,e12)   F_light  F_heavy   F_light@s  F_heavy@s   F_L")
for n12 in (1.0, 1.2, 1.5, 2.0, 2.5, 3.0, 3.2):
    n = n12 * 1e16
    Fs = model_pair(n)
    Fss = model_pair(s_best * n)
    F_L = float(luttinger_frequency(n))
    a = f"{Fs[0]:7.2f} {Fs[-1]:8.2f}" if len(Fs) >= 2 else f"  {Fs}   "
    b = f"{Fss[0]:8.2f} {Fss[-1]:9.2f}" if len(Fss) >= 2 else f"  {Fss}    "
    print(f"  {n12:5.1f}     {a} {b} {F_L:8.1f}")

# masses for the LK step later
for n12 in (2.0, 3.2):
    print(f"m*(n={n12}e12):", [(round(f, 1), round(m, 3)) for f, m in fs.abab_mstar(n12 * 1e16)])

# 3. grid design
B_max = 10.0
F_fast = float(luttinger_frequency(3.2e16))          # fastest expected tone: F_L at n_max (scale-1, conservative)
for B_lo in (0.5, 0.7, 1.0):
    d_invB = 1.0 / (3.0 * F_fast)                    # 3 samples/period (prefer-1/3 Nyquist)
    span = 1.0 / B_lo - 1.0 / B_max
    N_B = int(np.ceil(span / d_invB)) + 1
    dF = 1.0 / span
    dn_ray = 4 * 1.602e-19 / 6.626e-34 * B_lo / 1e16  # ray spacing in 1e12 cm^-2 at B_lo
    print(f"\nB_lo={B_lo}: Delta(1/B)={d_invB:.5f} -> N_B={N_B}, deltaF={dF:.2f} T, "
          f"ray Dn@B_lo={dn_ray:.3f}e12 -> n-step <= {dn_ray/2:.3f}e12")

# candidate: n 1.2 -> 3.2, N_n from ray floor at chosen B_lo
for (B_lo, N_B) in ((0.7, None),):
    pass
