"""Landau-fan design arithmetic (landau-fan step 1 + landau-fan-vti cost regime).
Electron side, D = 0. Levers in recipe order: B_lo, n_max, N_n, B_max."""
import sys
sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
import numpy as np
from fs_count_b0 import abab_fs, abca_fs, abab_mstar
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
TG_MIN, TG_MAX = -0.3, 1.0
BG_MIN, BG_MAX = -1.3, 2.0
h, e = 6.62607015e-34, 1.602176634e-19
FL = lambda n12: abs(n12) * 1e16 * h / (4 * e)          # T, n in 1e12 cm^-2
f_partner = lambda n12: abab_fs(n12 * 1e16)[1][0][0]     # ABAB light orbit, T
f_heavy   = lambda n12: abab_fs(n12 * 1e16)[1][1][0]

# ---- n_max: the D = 0 line's electron end inside the validators
print("=== n_max (validator-limited) ===")
for n12 in (3.1, 3.2, 3.25, 3.27, 3.3):
    vtg, vbg = calc_gate_voltages(n12, 0.0, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
    ok = TG_MIN <= vtg <= TG_MAX and BG_MIN <= vbg <= BG_MAX
    print(f"  n={n12:.2f}e12 -> Vtg {vtg:+.4f}  Vbg {vbg:+.4f}   {'OK' if ok else 'OUT'}")

N_MAX = 3.20
F_MAX = FL(N_MAX)
print(f"\nn_max = {N_MAX}e12  ->  F_L = {F_MAX:.2f} T (fastest expected tone)")

# ---- B_lo sweep: n_lo from the >=5-period requirement on the ABAB partner
print("\n=== lever scan: B_lo -> n_lo, grid size, cost ===")
B_MAX = 10.0
dinvB = 1.0 / (3 * F_MAX)                       # prefer 1/3 Nyquist on F_L(n_max)
print(f"D(1/B) <= 1/(3*F_L) = {dinvB:.5f} 1/T   (Nyquist floor 1/(2*F_L) = {1/(2*F_MAX):.5f})")
T_PT = 1.40                                      # s/pt, run-5 calibrated 1.10 @ 1.0 s dwell -> 1.2 s dwell + 5-10% margin
for B_LO in (0.35, 0.40, 0.50, 0.60, 0.80, 1.00):
    W = 1 / B_LO - 1 / B_MAX
    dF = 1 / W
    need = 5.0 / W                               # partner freq needed for 5 periods
    # smallest n12 whose partner tone clears `need`
    grid = np.arange(1.0, 3.21, 0.01)
    fp = np.array([f_partner(x) for x in grid])
    n_lo = float(grid[np.argmax(fp >= need)]) if (fp >= need).any() else np.nan
    span = N_MAX - n_lo
    dn_ray = 4 * (e / h) * B_LO / 1e16           # ray spacing in 1e12 cm^-2 at B_lo
    N_n = int(np.ceil(span / (dn_ray / 2))) + 1  # >=2 pts per ray
    N_B = int(np.ceil(W / dinvB)) + 1
    pts = N_B * N_n
    hrs = (pts * T_PT + N_B * 3.5 + (B_MAX - B_LO) / 0.137 * 60) / 3600
    print(f"  B_lo {B_LO:.2f} T: W {W:.3f} 1/T, dF {dF:.2f} T, partner>= {need:.2f} T -> n_lo {n_lo:.2f}e12 "
          f"(span {span:.2f}) | N_B {N_B:3d} x N_n {N_n:3d} = {pts:6d} pts -> {hrs:.1f} h")

# ---- committed design
print("\n=== committed design ===")
B_LO, B_MAX, N_B, N_n = 0.50, 10.0, 190, 65
N_LO = 1.70
W = 1 / B_LO - 1 / B_MAX
B_vec = 1.0 / np.linspace(1 / B_LO, 1 / B_MAX, N_B)
dinv = np.diff(1 / B_vec)
ns = np.linspace(N_LO, N_MAX, N_n)
Vtgs, Vbgs = calc_gate_voltages(ns, np.zeros_like(ns), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print(f"B: {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, {N_B} rows, D(1/B) = {dinv.mean():.5f} +- {dinv.std():.2e} 1/T")
print(f"   dB: {np.diff(B_vec).min()*1e3:.1f} mT (low end) ... {np.diff(B_vec).max()*1e3:.0f} mT (high end)")
print(f"   Nyquist ceiling everywhere: {1/(2*dinv.mean()):.1f} T  vs  F_L(n_max) = {F_MAX:.2f} T "
      f"-> {1/(2*dinv.mean())/F_MAX:.2f}x headroom")
print(f"n: {ns[0]:.2f} -> {ns[-1]:.2f}e12, {N_n} cols, dn = {(ns[1]-ns[0])*1e12:.2e} cm^-2")
print(f"   ray spacing at B_lo = {4*(e/h)*B_LO/1e16:.4f}e12 -> {4*(e/h)*B_LO/1e16/(ns[1]-ns[0]):.2f} pts/ray (floor 2)")
print(f"   Vtg {Vtgs.min():+.4f} .. {Vtgs.max():+.4f} (limits {TG_MIN}, {TG_MAX})")
print(f"   Vbg {Vbgs.min():+.4f} .. {Vbgs.max():+.4f} (limits {BG_MIN}, {BG_MAX})")
nn, DD = calc_nD(Vtgs, Vbgs, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print(f"   roundtrip: n {nn.min():.3f}..{nn.max():.3f}, |D| max {np.abs(DD).max():.2e} V/nm")

print(f"\nresolution: dF = {1/W:.2f} T over the record")
print(f"{'n':>6} {'F_L':>7} {'ABAB f1':>8} {'ABAB f2':>8} {'FL-f2':>7} {'periods(f1)':>11} {'sep/2dF':>8} {'m*1':>6} {'m*2':>6}")
for n12 in (1.70, 2.0, 2.4, 2.8, 3.2):
    f1, f2 = f_partner(n12), f_heavy(n12)
    ms = abab_mstar(n12 * 1e16)
    print(f"{n12:6.2f} {FL(n12):7.2f} {f1:8.2f} {f2:8.2f} {FL(n12)-f2:7.2f} {W*f1:11.1f} {f1/(2/W):8.2f} "
          f"{ms[0][1]:6.4f} {ms[1][1]:6.4f}")

# cost
flyback_tg = (Vtgs.max() - Vtgs.min()) / 0.005 * 0.006
flyback_bg = (Vbgs.max() - Vbgs.min()) / 0.005 * 0.006
SLOW_DELAY = 2.0
turn = flyback_tg + flyback_bg + SLOW_DELAY
traverse = (B_MAX - B_LO) / 0.137 * 60
pts = N_B * N_n
print(f"\ncost: {pts} pts x {T_PT} s = {pts*T_PT/3600:.2f} h"
      f" + {N_B} rows x {turn:.1f} s turnaround = {N_B*turn/3600:.2f} h"
      f" + traverse {traverse/60:.2f} h  =>  {(pts*T_PT + N_B*turn + traverse)/3600:.2f} h")
print(f"   (traverse rides inside the rows on a blocking magnet -- it is the sum of the dB steps, "
      f"counted once: {traverse/60:.2f} h)")
