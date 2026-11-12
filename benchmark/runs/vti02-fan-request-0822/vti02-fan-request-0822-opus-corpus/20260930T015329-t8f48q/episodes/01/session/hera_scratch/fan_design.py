"""Landau-fan design arithmetic (electron side, D = 0). Nyquist both axes,
dF vs the binding tone separation, dynamic range, wall-clock."""
import sys, numpy as np
sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
import fs_count_b0 as fsm
from hera.analysis import open_run, field_invB, luttinger_frequency
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
TG_MIN, TG_MAX = -0.3, 1.0
BG_MIN, BG_MAX = -1.3, 2.0

N_LO, N_HI = 1.00, 3.20           # 1e12 cm^-2
B_LO, B_HI = 1.0, 8.0
DINVB = 0.010                     # 1/T
N_B = int(round((1 / B_LO - 1 / B_HI) / DINVB)) + 1
N_N = 48
FAST_DELAY = 2.1                  # 7 tau at tau = 0.3 s, 24 dB/oct
T_PT = FAST_DELAY + 0.17          # run-5 calibrated read overhead (see below)

print("=== axis vectors ===")
B_vec = field_invB(B_LO, B_HI, N_B)
dinvb = np.diff(1 / B_vec)
print(f"B: {N_B} rows, {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T; "
      f"d(1/B) = {abs(dinvb).max():.5f} 1/T (uniform)")
print(f"  dB at low edge {abs(np.diff(B_vec))[0]*1e3:.1f} mT, at high edge {abs(np.diff(B_vec))[-1]*1e3:.0f} mT")
f_alias = 1 / (2 * abs(dinvb).max())
print(f"  alias-free to F = {f_alias:.1f} T   (need >= F_L(n_max) = {float(luttinger_frequency(N_HI*1e16)):.1f} T "
      f"and the 4x comb member ~29 T)")
dF = 1.0 / (1 / B_LO - 1 / B_HI)
print(f"  dF (record resolution) = {dF:.2f} T -> trust splits above 2dF = {2*dF:.2f} T")

ns = np.linspace(N_HI, N_LO, N_N)
dn = abs(ns[1] - ns[0])
ray = 4 * 1.602176634e-19 / 6.62607015e-34 * B_LO * 1e-4 / 1e12   # g*(e/h)*B in 1e12 cm^-2
print(f"n: {N_N} cols, {ns[0]:.2f} -> {ns[-1]:.2f}e12, dn = {dn:.4f}e12; "
      f"ray spacing at {B_LO} T = {ray:.4f}e12 -> {ray/dn:.2f} pts/ray (floor 2)")

Vtgs, Vbgs = calc_gate_voltages(ns, 0.0 * ns, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print(f"  Vtg {Vtgs.min():+.4f} .. {Vtgs.max():+.4f} V (limits {TG_MIN}, {TG_MAX})")
print(f"  Vbg {Vbgs.min():+.4f} .. {Vbgs.max():+.4f} V (limits {BG_MIN}, {BG_MAX})")
print(f"  headroom: TG {TG_MAX - Vtgs.max():+.4f} V, BG {BG_MAX - Vbgs.max():+.4f} V")
nr, Dr = calc_nD(Vtgs, Vbgs, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print(f"  roundtrip: n {nr.min():.3f}..{nr.max():.3f}, |D| max {np.abs(Dr).max():.2e} V/nm")

print("\n=== binding tone separation: real heavy F2(n) vs 3x the light tone ===")
print(" n(e12)   F_L    F1     F2    3*F1   |F2-3F1|   ratio   ok vs 2dF?")
for n in np.linspace(N_LO, N_HI, 12):
    _, orbs = fsm.abab_fs(n * 1e16)
    F = sorted(o[0] for o in orbs)
    sep = abs(F[1] - 3 * F[0])
    print(f"{n:6.2f} {sum(F):6.2f} {F[0]:6.2f} {F[1]:6.2f} {3*F[0]:6.2f}  {sep:8.2f}   {F[1]/F[0]:6.2f}   "
          f"{'OK' if sep > 2*dF else 'MERGED'}")

print("\n=== dynamic range: worst corner is low n x high B ===")
r6 = open_run("data/6"); R6 = np.abs(r6.col("sr1_X") / (1.0 / 100e6)); B6 = r6.col("magnet_field")
r7 = open_run("data/7"); R7 = np.abs(r7.col("sr1_X") / (1.0 / 100e6)); B7 = r7.col("magnet_field")
print(f"  run 6 (n=+3.2e12): R(B<0.1 T) = {R6[B6<0.1].max():.0f} Ohm, R_max = {R6.max():.0f} Ohm "
      f"(MR x{R6.max()/max(R6[B6<0.1].max(),1):.1f}); R(B<=8 T) max = {R6[B6<=8].max():.0f}")
print(f"  run 7 (n=-1.2e12): R(0.3 T) = {R7[0]:.0f} Ohm, R_max(10 T) = {R7.max():.0f} Ohm, "
      f"R(B<=8 T) max = {R7[B7<=8].max():.0f}")

# B = 0 anchor along the D = 0 line from the gatemap (run 5)
g5 = open_run("data/5")
vtg5, vbg5 = g5.col("k_2400_tg_volt"), g5.col("k_2400_bg_volt")
R5 = np.abs(g5.col("sr1_X") / (1.0 / 100e6))
n5, D5 = calc_nD(vtg5, vbg5, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
m = np.abs(D5) < 0.01
print("\n  B = 0 anchor along D = 0 (run 5 gatemap):")
for lo, hi in [(0.9, 1.1), (1.4, 1.6), (1.9, 2.1), (2.4, 2.6), (3.0, 3.25)]:
    sel = m & (n5 > lo) & (n5 < hi)
    if sel.sum():
        print(f"    n {lo}-{hi}e12: R = {np.median(R5[sel]):6.1f} Ohm (n={sel.sum()} pts)")
for sens in (50e-6, 100e-6):
    print(f"  sens {sens*1e6:.0f} uV -> full scale {sens/(1.0/100e6):.0f} Ohm")

print("\n=== wall-clock ===")
traverse = (B_HI - B_LO) / 0.137 * 60
settle = N_B * 3.0
# gate flyback: TG span / 5 mV * 6 ms (BG retraces concurrently on its own 2400)
fly = N_B * (abs(Vtgs[0] - Vtgs[-1]) / 0.005 * 0.006)
grid = N_B * N_N * T_PT
pos = (B_LO - 0.0) / 0.137 * 60
print(f"  grid      {N_B} x {N_N} x {T_PT:.2f} s = {grid/3600:5.2f} h")
print(f"  traverse  {B_HI-B_LO:.1f} T at 0.137 T/min = {traverse/3600:5.2f} h")
print(f"  settle    {N_B} x 3 s            = {settle/3600:5.2f} h")
print(f"  flyback   {N_B} x {fly/N_B:.2f} s          = {fly/3600:5.2f} h")
print(f"  ---------------------------------------")
print(f"  total (realistic, +8% over-run) = {(grid+traverse+settle+fly)*1.08/3600:5.2f} h "
      f"(+ {pos/60:.0f} min positioning to {B_LO} T)")
print(f"  run-5 timing calibration: 63 x 66 gatemap, fast_delay 1.0, 4873 s -> 1.172 s/pt incl. turnaround")
