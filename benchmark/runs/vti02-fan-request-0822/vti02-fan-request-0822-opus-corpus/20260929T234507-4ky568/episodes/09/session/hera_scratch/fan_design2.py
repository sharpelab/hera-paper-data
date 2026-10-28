"""Landau-fan design (landau-fan step 1 + landau-fan-vti cost regime), electron side, D = 0.
Lever scan then the committed floored design."""
import numpy as np
from hera.analysis import field_invB
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
TG_MIN, TG_MAX, BG_MIN, BG_MAX = -0.3, 1.0, -1.3, 2.0
h, e = 6.62607015e-34, 1.602176634e-19
FL = lambda n12: abs(n12) * 1e16 * h / (4 * e)
tab = np.load("hera_scratch/abab_table.npy")           # n12, f_light, f_heavy (ABAB model)
f1 = lambda n12: float(np.interp(n12, tab[:, 0], tab[:, 1]))
f2 = lambda n12: float(np.interp(n12, tab[:, 0], tab[:, 2]))

N_MAX, B_MAX, T_PT, TURN = 3.20, 10.0, 2.00, 3.5       # s/pt (1.8 s dwell + 0.10 measured overhead + margin)
dinvB = 1.0 / (3 * FL(N_MAX))
print(f"F_L(n_max={N_MAX}) = {FL(N_MAX):.2f} T -> D(1/B) <= 1/3F_L = {dinvB:.5f} 1/T (Nyquist ceiling {1/(2*dinvB):.1f} T)\n")

print("=== lever scan (n_lo set by >=5 partner periods AND f1 >= 3.5 T out of the bg-residual band) ===")
print(" B_lo    W    dF   f1_need  n_lo  span   N_B  N_n    pts     h")
grid = np.arange(1.0, 3.21, 0.005)
fp = np.array([f1(x) for x in grid])
for B_LO in (0.35, 0.40, 0.50, 0.60, 0.70, 0.80, 1.00):
    W = 1 / B_LO - 1 / B_MAX
    need = max(5.0 / W, 3.5)
    n_lo = float(grid[np.argmax(fp >= need)]) if (fp >= need).any() else np.nan
    span = N_MAX - n_lo
    dn_ray = 4 * (e / h) * B_LO / 1e16
    N_n = int(np.ceil(span / (dn_ray / 2))) + 1
    N_B = int(np.ceil(W / dinvB)) + 1
    pts = N_B * N_n
    hrs = (pts * T_PT + N_B * TURN + (B_MAX - B_LO) / 0.137 * 60) / 3600
    print(f" {B_LO:.2f} {W:6.3f} {1/W:5.2f} {need:7.2f} {n_lo:6.2f} {span:5.2f} {N_B:5d} {N_n:4d} {pts:7d} {hrs:6.1f}")

print("\n=== COMMITTED ===")
B_LO, N_B, N_LO, N_n, SLOW_DELAY, FAST_DELAY = 0.70, 133, 2.10, 45, 2.0, 1.8
W = 1 / B_LO - 1 / B_MAX
B_vec = np.round(field_invB(B_LO, B_MAX, N_B), 4)
d = np.diff(1 / B_vec)
ns = np.linspace(N_LO, N_MAX, N_n)
Vtgs, Vbgs = calc_gate_voltages(ns, np.zeros_like(ns), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
nn, DD = calc_nD(Vtgs, Vbgs, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print(f"B: {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, {N_B} rows uniform-1/B; D(1/B) {d.mean():.5f} (spread {d.std():.1e})")
print(f"   dB {np.diff(B_vec).min()*1e3:.1f} mT (low edge) ... {np.diff(B_vec).max()*1e3:.0f} mT (high edge); "
      f"Nyquist ceiling {1/(2*d.max()):.1f} T = {1/(2*d.max())/FL(N_MAX):.2f}x F_L(n_max)")
print(f"n: {ns[0]:.2f} -> {ns[-1]:.2f}e12, {N_n} cols, dn {(ns[1]-ns[0]):.4f}e12; "
      f"ray spacing at B_lo {4*(e/h)*B_LO/1e16:.4f}e12 -> {4*(e/h)*B_LO/1e16/(ns[1]-ns[0]):.2f} pts/ray (floor 2)")
print(f"   Vtg {Vtgs.min():+.4f}..{Vtgs.max():+.4f} (lim {TG_MIN},{TG_MAX})  Vbg {Vbgs.min():+.4f}..{Vbgs.max():+.4f} (lim {BG_MIN},{BG_MAX})")
print(f"   roundtrip n {nn.min():.3f}..{nn.max():.3f}e12, max|D| {np.abs(DD).max():.1e} V/nm")
print(f"   in-validator: {bool((Vtgs>=TG_MIN).all() and (Vtgs<=TG_MAX).all() and (Vbgs>=BG_MIN).all() and (Vbgs<=BG_MAX).all())}")

print(f"\nrecord resolution dF = {1/W:.2f} T (half-record split: {2/W:.2f} T)")
print(f"{'n':>5} {'F_L':>6} {'f1':>6} {'f2':>6} {'3*f1':>6} {'|f2-3f1|':>8} {'/2dF':>5} {'periods(f1)':>11} {'FL-f2':>6}")
for x in (2.10, 2.4, 2.8, 3.2):
    sep = abs(f2(x) - 3 * f1(x))
    print(f"{x:5.2f} {FL(x):6.2f} {f1(x):6.2f} {f2(x):6.2f} {3*f1(x):6.2f} {sep:8.2f} {sep/(2/W):5.1f} {W*f1(x):11.1f} {FL(x)-f2(x):6.2f}")

fly = ((Vtgs.max() - Vtgs.min()) + (Vbgs.max() - Vbgs.min())) / 0.005 * 0.006
pts = N_B * N_n
trav = (B_MAX - B_LO) / 0.137 * 60
print(f"\ncost: {pts} pts x {T_PT} s = {pts*T_PT/3600:.2f} h | {N_B} rows x ({fly:.1f} s flyback + {SLOW_DELAY} s) "
      f"= {N_B*(fly+SLOW_DELAY)/3600:.2f} h | traverse {(B_MAX-B_LO):.1f} T / 0.137 T/min = {trav/60:.2f} h")
print(f"TOTAL ~ {(pts*T_PT + N_B*(fly+SLOW_DELAY) + trav)/3600:.2f} h")
np.save("hera_scratch/fan_Bvec.npy", B_vec)
