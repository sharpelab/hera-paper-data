"""Landau-fan design numbers (electron side, D=0).

Model F(n)/m*(n) table, worst-corner R, timing calibration, Nyquist / dF /
period checks per landau-fan.md step 1 + investigation step 2/4.
"""
import sys
import numpy as np

sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
from fs_count_b0 import abab_fs, abab_mstar, abca_fs

from hera.analysis import open_run, luttinger_frequency

BASE = "/home/hera/measurements/zack/20260822-vti-02"

print("== model F(n), electron side (units: n in cm^-2) ==")
for n12 in [1.0, 1.5, 2.0, 2.5, 3.0, 3.27]:
    n = n12 * 1e16
    FL = float(luttinger_frequency(n))
    EF, orbits = abab_fs(n)
    ms = abab_mstar(n)
    ab = ", ".join(f"F={F:.2f}" for F, kF in orbits)
    mm = ", ".join(f"m*={m:.3f}" for F, m in ms)
    try:
        _, topo, ncomp, nfreq, Ftot = abca_fs(n)
        abca = f"ABCA: {topo} x{ncomp} F={Ftot:.2f}"
    except Exception as e:
        abca = f"ABCA err: {e}"
    print(f" n={n12:.2f}e12  F_L={FL:5.2f}  ABAB[{ab} | {mm}]  {abca}")

print()
print("== worst-corner R + timing from runs 6/7 ==")
for rid in (6, 7):
    r = open_run(f"{BASE}/data/{rid}")
    B = r.col("magnet_field")
    I = r.col("sr0_X") / (-1e6)
    R = np.abs(r.col("sr1_X") / I)
    V = np.abs(r.col("sr1_X"))
    t = r.col("time")
    dur = r.meta["end_time"] - r.meta["start_time"]
    print(f" run {rid}: R max {R.max():.0f} Ohm at B={B[np.argmax(R)]:.2f}; "
          f"V_sr1 max {V.max()*1e6:.1f} uV (sens 50); I med {np.median(np.abs(I))*1e9:.2f} nA; "
          f"npts {len(B)}, wall {dur/60:.1f} min, {dur/len(B):.2f} s/pt")

# gatemap run 5 per-point (gate-stepping rate, the fan's fast axis analog)
r5 = open_run(f"{BASE}/data/5")
d5 = r5.meta["end_time"] - r5.meta["start_time"]
np5 = len(r5.col("time"))
print(f" run 5 (gatemap): {np5} pts, {d5/60:.1f} min, {d5/np5:.2f} s/pt (fast_delay in meta: {r5.meta.get('fast_delay', r5.meta.get('delay'))})")

print()
print("== fan grid checks ==")
B_lo, B_hi = 0.7, 10.0
span = 1 / B_lo - 1 / B_hi
n_max = 3.27e12
scale = 36.66 / 33.09  # global density scale from run 6 pair sum
F_fast = 36.66 / 33.09 * float(luttinger_frequency(n_max * 1e4))  # F_L at n_max, measured scale
F_2h = 2 * 28.9 * (n_max / 3.2e12)  # 2nd harmonic of heavy tone at n_max
for Ftarget, name in [(F_fast, "F_L(n_max)@scale"), (F_2h, "2xheavy(n_max)")]:
    dinvB_req = 1 / (3 * Ftarget)
    N = int(np.ceil(span / dinvB_req)) + 1
    print(f" Nyquist(1/3-period) on {name} = {Ftarget:.1f} T -> d(1/B) <= {dinvB_req:.5f} -> N_B >= {N}")
print(f" dF = 1/span = {1/span:.2f} T (window {B_lo}-{B_hi} T)")
# partner periods at claim-window edge n=2.0e12
EF, orb = abab_fs(2.0e16)
f_partner = min(F for F, k in orb) * scale
print(f" partner tone at n=2.0e12 (model x scale): {f_partner:.2f} T -> periods in window = {f_partner*span:.1f}")
EF, orb = abab_fs(1.0e16)
print(f" partner at n=1.0e12 (model): {[f'{F:.2f}' for F,k in orb]}")

# n-axis ray Nyquist at B_lo
g_eh = 4 * 2.41799e10  # cm^-2 per T
for Bread in (0.7, 1.0):
    dn_ray = g_eh * Bread
    print(f" ray spacing at B={Bread}: dn = {dn_ray/1e10:.1f}e10 cm^-2 -> >=2 pts/ray needs dn_grid <= {dn_ray/2/1e10:.1f}e10")

n_lo = 1.0e12
for N_n in (91, 101, 121):
    dn = (n_max - n_lo) / (N_n - 1)
    print(f" N_n={N_n}: dn_grid = {dn/1e10:.1f}e10 -> rows/ray at 0.7 T = {g_eh*0.7/dn:.2f}, at 1.0 T = {g_eh*1.0/dn:.2f}")

print()
print("== cost ==")
for N_B, N_n, tpt in [(150, 101, 2.05), (160, 101, 2.05), (150, 91, 2.05)]:
    grid = N_B * N_n * tpt
    traverse = (B_hi - B_lo) / 0.137 * 60
    turn = N_B * (2.0)
    print(f" N_B={N_B} N_n={N_n} t={tpt}: grid {grid/3600:.2f} h + traverse {traverse/60:.0f} min + turnaround {turn/60:.0f} min = {(grid+traverse+turn)/3600:.2f} h")
