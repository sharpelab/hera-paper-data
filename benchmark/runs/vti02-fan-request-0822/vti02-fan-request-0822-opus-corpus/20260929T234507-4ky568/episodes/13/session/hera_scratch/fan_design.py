"""Step 2/4 design table for the D = 0 electron-side Landau fan on vti-02.
Model F(n), m*(n) for ABAB / ABCA; then the landau-fan step-1 checks
(both-axis Nyquist, delta-F resolution, partner period count, cost)."""
import sys
import numpy as np
from hera.analysis import luttinger_frequency, field_invB

sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
import fs_count_b0 as m

E_OVER_H = 2.4179893e14      # 1/(T m^2)  -> ray spacing dn = g*(e/h)*B

print("=== model F(n), electron side, u_D = 0 (n in 1e12 cm^-2, F in T) ===")
print(f"{'n':>6} {'F_L':>7} | {'ABAB orbits (F, m*)':<44} {'part.':>13} | {'ABCA F':>7} {'m*':>6}")
tab = {}
for n12 in [1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0, 3.25]:
    n_si = n12 * 1e16
    FL = float(luttinger_frequency(n_si))
    _, orbs = m.abab_fs(n_si)
    ms = m.abab_mstar(n_si)
    s = ", ".join(f"{f:.2f}({mm:.3f})" for (f, _), (_, mm) in zip(orbs, ms))
    part = "/".join(f"{f/FL:.2f}" for f, _ in orbs)
    Fa, ma = m.abca_mstar(n_si)
    print(f"{n12:6.2f} {FL:7.2f} | {s:<44} {part:>13} | {Fa:7.2f} {ma:6.3f}")
    tab[n12] = dict(FL=FL, abab=[f for f, _ in orbs], mstar=[mm for _, mm in ms], abca=Fa)

# ---- design checks -------------------------------------------------------
N_MIN, N_MAX = 1.5, 3.25          # 1e12 cm^-2, electron side of the D = 0 line
B_MAX = 10.0                       # session field cap
print(f"\n=== fan design: n = {N_MIN} -> {N_MAX} e12, D = 0, B_max = {B_MAX} T ===")
FL_max = float(luttinger_frequency(N_MAX * 1e16))
print(f"F_L(n_max) = {FL_max:.2f} T  ->  Nyquist d(1/B) <= {1/(2*FL_max):.5f}, prefer {1/(3*FL_max):.5f} 1/T")

print(f"\n{'B_lo':>5} {'1/B span':>9} {'N_B(1/3)':>9} {'dF':>6} {'2dF':>6} "
      f"{'sep@nmax':>9} {'partner periods @ n_min':>24}")
for B_lo in (0.7, 1.0, 1.2, 1.5, 1.8, 2.0, 2.5):
    span = 1 / B_lo - 1 / B_MAX
    N_B = int(np.ceil(span / (1 / (3 * FL_max)))) + 1
    dF = 1 / span
    sep = tab[N_MAX]["FL"] - max(tab[N_MAX]["abab"])        # ABCA singleton vs ABAB heavy
    fp_lo = min(tab[N_MIN]["abab"])
    per = span * fp_lo
    print(f"{B_lo:5.2f} {span:9.4f} {N_B:9d} {dF:6.2f} {2*dF:6.2f} {sep:9.2f} "
          f"{per:9.1f}  (F_partner = {fp_lo:.2f} T)")

print("\n=== n-axis ray Nyquist (dn_ray = 4*(e/h)*B_lo) ===")
for B_lo in (1.0, 1.2, 1.5, 2.0):
    dn_ray = 4 * E_OVER_H * B_lo / 1e16          # 1e12 cm^-2
    N_n_floor = int(np.ceil(2 * (N_MAX - N_MIN) / dn_ray)) + 1
    print(f"  B_lo {B_lo:4.2f} T: dn_ray = {dn_ray:.4f}e12 -> N_n >= {N_n_floor} (2 pts/ray)")

print("\n=== cost (wall-clock) ===")
TRAVERSE_RATE = 0.137           # T/min bare
for B_lo, N_n, t_pt in [(1.2, 51, 2.05), (1.5, 51, 2.05), (1.5, 71, 2.05), (1.2, 71, 2.05),
                        (1.2, 51, 1.55), (1.5, 41, 2.05)]:
    span = 1 / B_lo - 1 / B_MAX
    N_B = int(np.ceil(span / (1 / (3 * FL_max)))) + 1
    trav = (B_MAX - B_lo) / TRAVERSE_RATE
    grid = N_B * N_n * t_pt / 60
    over = N_B * 5.0 / 60        # flyback + slow_delay per row
    print(f"  B_lo {B_lo} N_B {N_B:3d} N_n {N_n:3d} t_pt {t_pt}s: traverse {trav:.0f} min "
          f"+ grid {grid:.0f} min + row overhead {over:.0f} min = {(trav+grid+over)/60:.2f} h")
