"""Landau-fan design arithmetic (landau-fan-vti, step 1 cost-floor check)."""
import json
import numpy as np
from hera.analysis import field_invB, luttinger_frequency
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

CAL = json.load(open("hera_scratch/cal_run5.json"))
c_tg, c_bg, n_off, D_off = CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"]
h, e = 6.62607015e-34, 1.602176634e-19

N_LO, N_HI = 1.0, 3.2          # 1e12 cm^-2, electron side, D = 0
B_LO, B_HI = 0.8, 10.0
FL_max = luttinger_frequency(N_HI * 1e16)
print(f"F_L(n_max={N_HI}e12) = {FL_max:.2f} T ; F_L(n_min) = {luttinger_frequency(N_LO*1e16):.2f} T")

# --- B axis: uniform in 1/B, Nyquist on 2*F_L (the dominant tone's 2nd harmonic,
#     measured present in run 6 at rel. amp 0.16)
dinvB_target = 1.0 / (2 * 2 * FL_max)
span = 1 / B_LO - 1 / B_HI
N_B = int(np.ceil(span / dinvB_target)) + 1
B_vec = field_invB(B_LO, B_HI, N_B)
dinvB = np.diff(1 / B_vec)
print(f"N_B = {N_B}; d(1/B) = {abs(dinvB).max():.5f} 1/T -> Nyquist F = "
      f"{1/(2*abs(dinvB).max()):.1f} T = {1/(2*abs(dinvB).max())/FL_max:.2f} F_L")
print(f"B steps: {np.diff(B_vec).min()*1e3:.1f} mT (low end) -> {np.diff(B_vec).max():.3f} T (top)")
print(f"record: 1/B span {span:.3f} 1/T -> dF = {1/span:.2f} T")

# --- n axis: ray-Nyquist at B_LO
dn_ray = 4 * (e / h) * B_LO         # m^-2
N_n = int(np.ceil((N_HI - N_LO) * 1e16 / (dn_ray / 2))) + 1
ns = np.linspace(N_LO, N_HI, N_n)
step = (ns[1] - ns[0]) * 1e16
print(f"ray spacing at B_lo: {dn_ray/1e16:.4f}e12 cm^-2 ; N_n = {N_n}, "
      f"step {step/1e16:.4f}e12 -> {dn_ray/step:.2f} pts/ray")

Vtgs, Vbgs = calc_gate_voltages(ns, np.zeros_like(ns), c_tg, c_bg, n_off, D_off)
print(f"Vtg {Vtgs.min():+.4f} .. {Vtgs.max():+.4f} V ; Vbg {Vbgs.min():+.4f} .. {Vbgs.max():+.4f} V")
print(f"roundtrip n,D at ends: {calc_nD(Vtgs[0], Vbgs[0], c_tg, c_bg, n_off, D_off)} "
      f"{calc_nD(Vtgs[-1], Vbgs[-1], c_tg, c_bg, n_off, D_off)}")

# --- tone resolvability across the window (model F(n))
import sys
sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
from fs_count_b0 import abab_fs
print("\n n(e12)  F_L   ABAB partner/heavy  periods(partner)  heavy/F_L")
for n in (1.0, 1.4, 1.8, 2.2, 2.6, 3.0, 3.2):
    FL = luttinger_frequency(n * 1e16)
    fs = [o[0] for o in abab_fs(n * 1e16)[1]]
    lo, hi = min(fs), max(fs)
    print(f"{n:5.2f} {FL:6.2f}   {lo:6.2f} / {hi:6.2f}   {span*lo:6.2f}   {hi/FL:.3f}")

# --- wall clock
FAST_DELAY, SLOW_DELAY = 1.8, 1.0        # 6 tau (tau = 0.3 s, 24 dB/oct)
T_PT = FAST_DELAY + 0.25                 # measured overhead, run 5 calib (0.10 s) + margin
flyback = (Vtgs.max() - Vtgs.min()) / 5e-3 * 6e-3
row_over = SLOW_DELAY + flyback + 3.0    # + magnet driver settle_s per row
grid = N_B * (N_n * T_PT + row_over)
traverse = (B_HI - B_LO) / 0.137 * 60
position = B_LO / 0.137 * 60
tot = grid + traverse + position
print(f"\nflyback {flyback:.2f} s/row; row overhead {row_over:.1f} s")
print(f"grid {grid/3600:.2f} h + traverse {traverse/3600:.2f} h + position {position/60:.1f} min "
      f"= {tot/3600:.2f} h ; +10% = {tot*1.1/3600:.2f} h")
print(f"points {N_B*N_n}")
